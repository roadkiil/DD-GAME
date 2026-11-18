"""Scan a folder of game files (ROMs/disc images) and map them to platforms by extension."""

from __future__ import annotations

import re
from pathlib import Path

from ..backends import AMBIGUOUS_EXTENSIONS, Catalog
from ..library import Game, file_game_id

COVER_EXT = (".png", ".jpg", ".jpeg", ".webp")
COVER_DIRS = ("covers", "boxart", "media/covers", "images")
SKIP_DIRS = {"covers", "boxart", "media", "images", "manuals", ".git"}


def clean_title(stem: str) -> str:
    t = re.sub(r"[\(\[][^\)\]]*[\)\]]", "", stem)  # drop (USA) [!] style tags
    t = re.sub(r"[_\.]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t or stem


def find_cover(rom: Path, root: Path) -> str:
    candidates = [rom.parent] + [rom.parent / d for d in COVER_DIRS] + [root / d for d in COVER_DIRS]
    for d in candidates:
        for ext in COVER_EXT:
            p = d / (rom.stem + ext)
            if p.is_file():
                return str(p)
    return ""


def _m3u_members(folder: Path) -> set[Path]:
    members = set()
    for m3u in folder.rglob("*.m3u"):
        try:
            for line in m3u.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    members.add((m3u.parent / line).resolve())
        except OSError:
            continue
    return members


def scan(folder: str | Path, catalog: Catalog, platform: str | None = None) -> tuple[list[Game], list[str]]:
    """Return (games, warnings). With `platform`, every file with an extension listed for that
    platform (or any file in an arcade/ambiguous folder) is imported as that platform."""
    root = Path(folder).expanduser().resolve()
    warnings: list[str] = []
    if not root.is_dir():
        return [], [f"Folder not found: {root}"]
    extmap = catalog.extension_map()
    ambiguous = AMBIGUOUS_EXTENSIONS
    if platform and platform not in catalog.platforms:
        return [], [f"Unknown platform '{platform}'."]
    allowed = set(catalog.platforms[platform].get("extensions", [])) | ambiguous if platform else set()
    skip = _m3u_members(root)
    games: list[Game] = []
    for f in sorted(root.rglob("*")):
        if not f.is_file() or any(part.lower() in SKIP_DIRS for part in f.relative_to(root).parts[:-1]):
            continue
        ext = f.suffix.lower()
        if f.resolve() in skip or ext in COVER_EXT:
            continue
        if platform:
            if ext not in allowed:
                continue
            if ext == ".bin" and f.with_suffix(".cue").exists():
                continue  # data track of a .cue image
            pid = platform
        else:
            pid = extmap.get(ext)
            if not pid:
                if ext in ambiguous:
                    warnings.append(f"Skipped {f.name}: '{ext}' is used by several systems; "
                                    f"import this folder with --platform.")
                continue
        games.append(Game(id=file_game_id(pid, f), title=clean_title(f.stem), platform=pid, kind="emulated",
                          path=str(f), source=f"folder:{root}", cover=find_cover(f, root)))
    return games, warnings
