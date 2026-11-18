"""Steam: read installed games from libraryfolders.vdf + appmanifest_*.acf (read-only)."""

from __future__ import annotations

import os
import re
from pathlib import Path

from .. import paths
from ..library import Game

NON_GAMES = re.compile(r"^(Proton|Steam Linux Runtime|Steamworks Common|SteamVR|Steam Audio)", re.I)
_TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|([{}])')


def parse_vdf(text: str) -> dict:
    """Minimal parser for Valve's text KeyValues format."""
    tokens = []
    for line in text.splitlines():
        line = line.split("//", 1)[0] if not line.strip().startswith('"') else line
        for m in _TOKEN.finditer(line):
            tokens.append(m.group(1) if m.group(1) is not None else m.group(2))
    root: dict = {}
    stack = [root]
    key = None
    for tok in tokens:
        if tok == "{":
            new: dict = {}
            stack[-1][key] = new
            stack.append(new)
            key = None
        elif tok == "}":
            if len(stack) > 1:
                stack.pop()
        elif key is None:
            key = tok
        else:
            stack[-1][key] = tok.replace('\\\\', '\\')
            key = None
    return root


def steam_roots() -> list[Path]:
    home = Path.home()
    key = paths.os_key()
    if key == "windows":
        return [paths.expand(r"%PROGRAMFILES(X86)%\Steam"), paths.expand(r"%PROGRAMFILES%\Steam")]
    if key == "darwin":
        return [home / "Library/Application Support/Steam"]
    return [home / ".steam/steam", home / ".local/share/Steam",
            home / ".var/app/com.valvesoftware.Steam/.local/share/Steam"]


def _cover(root: Path, appid: str) -> str:
    cache = root / "appcache" / "librarycache"
    for p in (cache / appid / "library_600x900.jpg", cache / f"{appid}_library_600x900.jpg",
              cache / appid / "header.jpg", cache / f"{appid}_header.jpg"):
        if p.is_file():
            return str(p)
    return ""


def scan(roots: list[Path] | None = None) -> tuple[list[Game], list[str]]:
    games, warnings, seen = [], [], set()
    for root in roots or steam_roots():
        lf = root / "steamapps" / "libraryfolders.vdf"
        if not lf.is_file():
            continue
        try:
            data = parse_vdf(lf.read_text(encoding="utf-8", errors="replace"))
        except OSError as e:
            warnings.append(f"Could not read {lf}: {e}")
            continue
        folders = data.get("libraryfolders", {})
        libs = [Path(v["path"]) for v in folders.values() if isinstance(v, dict) and "path" in v] or [root]
        for lib in libs:
            for acf in sorted((lib / "steamapps").glob("appmanifest_*.acf")):
                try:
                    st = parse_vdf(acf.read_text(encoding="utf-8", errors="replace")).get("AppState", {})
                except OSError:
                    continue
                appid, name = st.get("appid"), st.get("name", "")
                if not appid or appid in seen or NON_GAMES.match(name):
                    continue
                seen.add(appid)
                games.append(Game(id=f"steam-{appid}", title=name, platform="pc", kind="native",
                                  path=f"steam:{appid}", backend="steam", source="steam",
                                  cover=_cover(root, appid),
                                  meta={"appid": appid, "installdir": str(lib / "steamapps/common" / st.get("installdir", ""))}))
    return games, warnings


def running_appid() -> str:
    """The Steam client publishes the currently running game id. Returns '' or '0' when idle."""
    if paths.os_key() == "windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                return str(winreg.QueryValueEx(k, "RunningAppID")[0])
        except OSError:
            return ""
    for root in steam_roots():
        reg = root.parent / "registry.vdf" if root.name == "steam" else root / "registry.vdf"
        for cand in (reg, Path.home() / ".steam/registry.vdf"):
            if cand.is_file():
                text = cand.read_text(encoding="utf-8", errors="replace")
                m = re.search(r'"RunningAppID"\s+"(\d+)"', text)
                if m:
                    return m.group(1)
    return ""
