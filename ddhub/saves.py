"""Save backup / restore.

- In-game saves ("save": .srm, .sav, profile files) and emulator snapshots ("state": .state*)
  are tracked separately; restore touches saves only unless states are explicitly requested.
- Restore refuses to overwrite a file that is newer than the backed-up copy unless forced, and
  always takes a "pre-restore" safety backup of whatever it is about to replace.
- No claim of portability between backends: a backup records the backend it came from.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

from . import paths
from .backends import Context
from .launcher import save_dirs_for
from .library import Game
from .readiness import default_backend

SAVE_EXT = {".srm", ".sav", ".rtc", ".eep", ".fla", ".sra", ".mpk", ".mcr", ".dsv"}


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def find_files(game: Game, ctx: Context, backend_id: str | None = None) -> list[tuple[str, Path]]:
    bid = backend_id or default_backend(game, ctx)
    dirs = save_dirs_for(game, ctx, bid)
    stem = Path(game.path).stem if game.path else ""
    found: dict[Path, str] = {}
    native = set(paths.expand(s) for s in game.save_paths)
    for kind, dlist in dirs.items():
        for d in dlist:
            if not d.is_dir():
                continue
            if d in native:  # native game: everything in its save directory belongs to it
                for f in d.rglob("*"):
                    if f.is_file():
                        found.setdefault(f.resolve(), "save")
                continue
            for f in list(d.glob(f"{stem}.*")) + list(d.glob(f"*/{stem}.*")):
                if not f.is_file() or not stem:
                    continue
                ext = f.suffix.lower()
                if kind == "state" and (".state" in f.name or ext in (".png",)):
                    found.setdefault(f.resolve(), "state")
                elif kind == "save" and ext in SAVE_EXT:
                    found.setdefault(f.resolve(), "save")
    return sorted(((k, p) for p, k in found.items()), key=lambda t: str(t[1]))


@dataclass
class BackupInfo:
    path: Path
    created: float
    label: str
    files: int


def backup(game: Game, ctx: Context, label: str = "manual", backend_id: str | None = None) -> BackupInfo | None:
    files = find_files(game, ctx, backend_id)
    if not files:
        return None
    out_dir = paths.sub("backups") / game.id
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out = out_dir / f"{stamp}-{label}.zip"
    n = 1
    while out.exists():
        out = out_dir / f"{stamp}-{label}-{n}.zip"
        n += 1
    manifest = {"game_id": game.id, "title": game.title, "platform": game.platform,
                "backend": backend_id or default_backend(game, ctx), "created": time.time(),
                "label": label, "files": []}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for i, (kind, p) in enumerate(files):
            arc = f"{kind}/{i:03d}_{p.name}"
            st = p.stat()
            z.write(p, arc)
            manifest["files"].append({"arc": arc, "path": str(p), "kind": kind,
                                      "mtime": st.st_mtime, "size": st.st_size, "sha256": _sha(p)})
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
    return BackupInfo(out, manifest["created"], label, len(files))


def list_backups(game: Game) -> list[BackupInfo]:
    d = paths.hub_home() / "backups" / game.id
    out = []
    for z in sorted(d.glob("*.zip"), reverse=True) if d.is_dir() else []:
        try:
            with zipfile.ZipFile(z) as zf:
                m = json.loads(zf.read("manifest.json"))
            out.append(BackupInfo(z, m["created"], m.get("label", ""), len(m["files"])))
        except (zipfile.BadZipFile, KeyError, json.JSONDecodeError, OSError):
            continue
    return out


class RestoreConflict(Exception):
    def __init__(self, conflicts: list[str]):
        super().__init__("Newer files would be overwritten:\n" + "\n".join(conflicts))
        self.conflicts = conflicts


def restore(game: Game, ctx: Context, backup_path: Path, include_states: bool = False,
            force: bool = False) -> list[str]:
    with zipfile.ZipFile(backup_path) as zf:
        m = json.loads(zf.read("manifest.json"))
        if m.get("game_id") != game.id:
            raise ValueError("This backup belongs to a different game.")
        current_backend = default_backend(game, ctx)
        if m.get("backend") and m["backend"] != current_backend and not force:
            raise ValueError(f"Backup was made with '{m['backend']}' but the game now uses "
                             f"'{current_backend}'. Save formats may differ; use force to restore anyway.")
        entries = [e for e in m["files"] if include_states or e["kind"] == "save"]
        conflicts = []
        for e in entries:
            dest = Path(e["path"])
            if dest.exists() and dest.stat().st_mtime > e["mtime"] + 1 and _sha(dest) != e["sha256"]:
                conflicts.append(f"{dest} (current is newer than backup)")
        if conflicts and not force:
            raise RestoreConflict(conflicts)
        if any(Path(e["path"]).exists() for e in entries):
            backup(game, ctx, label="pre-restore", backend_id=m.get("backend"))
        restored = []
        for e in entries:
            dest = Path(e["path"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_name(dest.name + ".ddhub-tmp")
            with zf.open(e["arc"]) as src, open(tmp, "wb") as dst:
                dst.write(src.read())
            os.replace(tmp, dest)
            os.utime(dest, (e["mtime"], e["mtime"]))
            restored.append(str(dest))
    return restored
