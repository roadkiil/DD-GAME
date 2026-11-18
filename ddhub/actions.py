"""Operations shared by the CLI and the fullscreen UI."""

from __future__ import annotations

import platform as pyplatform
import shutil
import time
from pathlib import Path

from . import paths
from .backends import Context, version_of
from .importers import desktop, folders, steam
from .library import Game, Library, file_game_id
from .readiness import default_backend
from .saves import backup, list_backups
from .store import load_json

AUTO_BACKUPS_KEPT = 10


def import_folder(lib: Library, ctx: Context, folder: str, platform: str | None, remember: bool = True) -> tuple[dict, list[str]]:
    games, warnings = folders.scan(folder, ctx.catalog, platform)
    stats = lib.upsert_many(games)
    if remember:
        entry = {"path": str(Path(folder).expanduser().resolve()), "platform": platform}
        if entry not in ctx.settings["rom_folders"]:
            ctx.settings["rom_folders"].append(entry)
            ctx.settings.save()
    lib.save()
    return stats, warnings


def rescan(lib: Library, ctx: Context) -> tuple[dict, list[str]]:
    total, warnings = {"added": 0, "updated": 0}, []
    for entry in ctx.settings["rom_folders"]:
        s, w = import_folder(lib, ctx, entry["path"], entry.get("platform"), remember=False)
        total = {k: total[k] + s[k] for k in total}
        warnings += w
    return total, warnings


def import_desktop(lib: Library) -> tuple[dict, list[str]]:
    games, warnings = desktop.scan()
    catalog = load_json(paths.DATA_DIR / "catalog.json", {})
    for g in games:  # attach catalog knowledge (license, save paths) to known titles
        for key, c in catalog.items():
            if key.startswith("_"):
                continue
            names = [c["title"]] + c.get("aliases", [])
            if g.title.lower() in (n.lower() for n in names):
                g.meta.update({k: c[k] for k in ("developer", "year", "code_license", "asset_license", "url") if k in c})
                g.save_paths = c.get("save_paths", {}).get(paths.os_key(), [])
    stats = lib.upsert_many(games)
    lib.save()
    return stats, warnings


def import_steam(lib: Library) -> tuple[dict, list[str]]:
    games, warnings = steam.scan()
    stats = lib.upsert_many(games)
    lib.save()
    return stats, warnings


def install_bundled(lib: Library) -> list[str]:
    """Add the freely distributable content that ships with the hub (no downloads)."""
    added = []
    catalog = load_json(paths.DATA_DIR / "catalog.json", {})
    for key, c in catalog.items():
        if key.startswith("_") or not c.get("bundled"):
            continue
        src = paths.REPO_DIR / c["bundled"]
        if not src.is_file():
            continue
        # Copy into the hub's own folder: emulators write saves next to the ROM, and the install
        # directory must stay clean (and may be read-only).
        dest_dir = paths.sub("content") / key
        dest_dir.mkdir(parents=True, exist_ok=True)
        p = dest_dir / src.name
        if not p.exists():
            shutil.copy2(src, p)
        for extra in ("LICENSE", src.with_suffix(".png").name):
            if (src.parent / extra).is_file():
                shutil.copy2(src.parent / extra, dest_dir / extra)
        cover = p.with_suffix(".png")
        g = Game(id=file_game_id(c["platform"], p), title=c["title"], platform=c["platform"], kind=c["kind"],
                 path=str(p), source="catalog", cover=str(cover) if cover.is_file() else "",
                 meta={k: c[k] for k in ("developer", "year", "code_license", "asset_license", "url", "description") if k in c})
        lib.upsert(g)
        added.append(g.title)
    lib.save()
    return added


def record_test(game: Game, ctx: Context, backend_id: str, result: str, notes: str = "") -> None:
    b = ctx.catalog.backends.get(backend_id, {})
    prog = b.get("program", "")
    ver = version_of(ctx, prog) if prog and not prog.startswith("@") else "n/a"
    if b.get("core"):
        ver += f" + core {b['core']}"
    game.local_test = {"result": result, "backend": backend_id, "backend_version": ver,
                       "date": time.strftime("%Y-%m-%d %H:%M"), "host": pyplatform.node(),
                       "os": pyplatform.platform(), "notes": notes}


def after_session(lib: Library, ctx: Context, game: Game, started: float, ended: float, backend_id: str) -> str:
    """Record playtime and take an automatic save backup. Returns a short status message."""
    lib.record_session(game.id, started, ended)
    msg = ""
    try:
        info = backup(game, ctx, label="auto", backend_id=backend_id)
        if info:
            msg = f"Saves backed up ({info.files} file{'s' if info.files != 1 else ''})."
            autos = [b for b in list_backups(game) if b.label == "auto"]
            for old in autos[AUTO_BACKUPS_KEPT:]:
                old.path.unlink(missing_ok=True)
    except OSError as e:
        msg = f"Save backup failed: {e}"
    lib.save()
    return msg


def find_game(lib: Library, ref: str) -> Game:
    if ref in lib.games:
        return lib.games[ref]
    matches = [g for g in lib.sorted() if ref.lower() in g.title.lower()]
    exact = [g for g in matches if g.title.lower() == ref.lower()]
    if len(exact) == 1:
        return exact[0]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"No game matches '{ref}'. Try `ddhub list`.")
    raise SystemExit("Ambiguous; use an id:\n" + "\n".join(f"  {g.id}  {g.title} [{g.platform}]" for g in matches))


def backend_choices(game: Game, ctx: Context) -> list[str]:
    opts = ctx.catalog.backends_for(game.platform)
    cur = default_backend(game, ctx)
    if cur and cur not in opts:
        opts.insert(0, cur)
    return opts
