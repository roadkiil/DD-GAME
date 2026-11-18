"""Linux: import installed native games from freedesktop .desktop entries (Categories=Game)."""

from __future__ import annotations

import configparser
import os
import shlex
import shutil
from pathlib import Path

from ..library import Game

FIELD_CODES = {"%f", "%F", "%u", "%U", "%i", "%c", "%k", "%d", "%D", "%n", "%N", "%v", "%m"}
# Emulators and launchers are not games themselves.
EXCLUDE_CATEGORIES = {"Emulator", "PackageManager", "Settings"}
EXCLUDE_IDS = {"steam", "retroarch", "com.valvesoftware.Steam", "org.libretro.RetroArch", "lutris",
               "com.heroicgameslauncher.hgl", "net.lutris.Lutris"}


def default_dirs() -> list[Path]:
    home = Path.home()
    data_home = Path(os.environ.get("XDG_DATA_HOME", home / ".local/share"))
    dirs = [data_home / "applications", data_home / "flatpak/exports/share/applications",
            Path("/var/lib/flatpak/exports/share/applications")]
    for d in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"):
        dirs.append(Path(d) / "applications")
    return dirs


def find_icon(name: str) -> str:
    if not name:
        return ""
    if os.path.isabs(name) and os.path.isfile(name):
        return name
    best = ""
    for base in (Path.home() / ".local/share/icons", Path("/usr/share/icons/hicolor"), Path("/usr/share/pixmaps")):
        if not base.is_dir():
            continue
        for sizes in ("512x512", "256x256", "128x128", "scalable", "64x64", "48x48", ""):
            for ext in (".png",):  # pygame cannot load svg reliably
                p = base / sizes / "apps" / (name + ext) if sizes else base / (name + ext)
                if p.is_file():
                    return str(p)
    return best


def _resolve(cmd: str) -> str:
    if os.path.isabs(cmd):
        return cmd
    search = os.environ.get("PATH", "") + os.pathsep + "/usr/games" + os.pathsep + "/usr/local/games"
    return shutil.which(cmd, path=search) or cmd


def parse_exec(exec_line: str) -> list[str]:
    try:
        argv = shlex.split(exec_line)
    except ValueError:
        return []
    return [a for a in argv if a not in FIELD_CODES]


def scan(dirs: list[Path] | None = None) -> tuple[list[Game], list[str]]:
    games, warnings, seen = [], [], set()
    for d in dirs or default_dirs():
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.desktop")):
            desktop_id = f.stem
            if desktop_id in seen or desktop_id in EXCLUDE_IDS:
                continue
            cp = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                cp.read(f, encoding="utf-8")
                e = cp["Desktop Entry"]
            except (configparser.Error, KeyError, UnicodeDecodeError):
                continue
            cats = set(filter(None, e.get("Categories", "").split(";")))
            if "Game" not in cats or cats & EXCLUDE_CATEGORIES:
                continue
            if e.get("NoDisplay", "false").lower() == "true" or e.get("Hidden", "false").lower() == "true":
                continue
            if e.get("Type", "Application") != "Application":
                continue
            argv = parse_exec(e.get("Exec", ""))
            if not argv:
                warnings.append(f"Skipped {f.name}: unreadable Exec line")
                continue
            seen.add(desktop_id)
            games.append(Game(
                id=f"desktop-{desktop_id}", title=e.get("Name", desktop_id), platform="pc", kind="native",
                path=_resolve(argv[0]),
                args=argv[1:], backend="native-exe", source="desktop", cwd=e.get("Path", ""),
                cover=find_icon(e.get("Icon", "")), meta={"description": e.get("Comment", ""),
                                                           "desktop_file": str(f)}))
    return games, warnings
