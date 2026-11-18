"""Platform/backend/program definitions and their resolution on this machine.

Definitions ship in ddhub/data/*.json. Users can add or override entries without touching code by
creating extra_programs.json / extra_backends.json / extra_platforms.json in the hub directory.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from . import paths
from .settings import Settings
from .store import load_json


def _load(name: str) -> dict:
    base = load_json(paths.DATA_DIR / f"{name}.json", {})
    extra = load_json(paths.hub_home() / f"extra_{name}.json", {})
    merged = {**base, **extra}
    return {k: v for k, v in merged.items() if not k.startswith("_")}


# Container formats used by many systems: never guess a platform from these.
AMBIGUOUS_EXTENSIONS = {".iso", ".chd", ".cue", ".bin", ".zip", ".7z", ".rvz", ".img"}


class Catalog:
    """All static definitions, loaded once per hub session."""

    def __init__(self):
        self.programs = _load("programs")
        self.backends = _load("backends")
        self.platforms = _load("platforms")

    def platform_name(self, pid: str) -> str:
        return self.platforms.get(pid, {}).get("name", pid)

    def backends_for(self, platform: str) -> list[str]:
        listed = list(self.platforms.get(platform, {}).get("backends", []))
        # Also include any backend (e.g. user-added) declaring the platform.
        for bid, b in self.backends.items():
            if platform in b.get("platforms", []) and bid not in listed:
                listed.append(bid)
        return [b for b in listed if b in self.backends]

    def extension_map(self) -> dict[str, str]:
        """Extension -> platform, only for extensions that identify exactly one platform."""
        seen: dict[str, set[str]] = {}
        for pid, p in self.platforms.items():
            for ext in p.get("extensions", []):
                seen.setdefault(ext.lower(), set()).add(pid)
        return {ext: next(iter(pids)) for ext, pids in seen.items()
                if len(pids) == 1 and ext not in AMBIGUOUS_EXTENSIONS}


@dataclass
class ResolvedProgram:
    id: str
    argv_prefix: list[str]
    location: str
    via: str  # configured | path | file | flatpak
    flatpak_id: str = ""


@dataclass
class Context:
    """Per-session resolution cache, so the UI does not hit the filesystem every frame."""

    settings: Settings
    catalog: Catalog = field(default_factory=Catalog)
    _programs: dict = field(default_factory=dict)

    def program(self, prog_id: str) -> ResolvedProgram | None:
        if prog_id not in self._programs:
            self._programs[prog_id] = find_program(prog_id, self.catalog, self.settings)
        return self._programs[prog_id]

    def invalidate(self) -> None:
        self._programs.clear()
        _flatpak_installed.cache_clear()
        program_version.cache_clear()


@lru_cache(maxsize=64)
def _flatpak_installed(app_id: str) -> bool:
    exe = shutil.which("flatpak")
    if not exe:
        return False
    try:
        return subprocess.run([exe, "info", app_id], capture_output=True, timeout=10).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def find_program(prog_id: str, catalog: Catalog, settings: Settings) -> ResolvedProgram | None:
    configured = settings.get("programs", {}).get(prog_id)
    if configured:
        p = paths.expand(configured)
        if p.is_file():
            return ResolvedProgram(prog_id, [str(p)], str(p), "configured")
        return None  # an explicit path that is wrong must surface as an error, not be guessed past
    spec = catalog.programs.get(prog_id)
    if not spec:
        return None
    for cand in spec.get("find", {}).get(paths.os_key(), []):
        if cand.startswith("flatpak:"):
            app = cand.split(":", 1)[1]
            if _flatpak_installed(app):
                return ResolvedProgram(prog_id, ["flatpak", "run", app], f"flatpak {app}", "flatpak", app)
            continue
        expanded = paths.expand(cand)
        if os.sep in cand or "/" in cand or "\\" in cand:
            if expanded.is_file():
                return ResolvedProgram(prog_id, [str(expanded)], str(expanded), "file")
        else:
            found = shutil.which(cand) or (shutil.which(cand, path="/usr/games") if paths.os_key() == "linux" else None)
            if found:
                return ResolvedProgram(prog_id, [found], found, "path")
    return None


@lru_cache(maxsize=64)
def program_version(argv: tuple[str, ...], version_args: tuple[str, ...]) -> str:
    if not version_args:
        return "unknown"
    try:
        out = subprocess.run(list(argv) + list(version_args), capture_output=True, text=True, timeout=10,
                             stdin=subprocess.DEVNULL)
        text = (out.stdout or "") + (out.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    for line in text.splitlines():
        m = re.search(r"\d+\.\d+(\.\d+)?", line)
        if m and "version" in line.lower() or (m and len(line) < 80):
            return line.strip()[:120]
    return "unknown"


def version_of(ctx: Context, prog_id: str) -> str:
    rp = ctx.program(prog_id)
    if not rp:
        return "not installed"
    spec = ctx.catalog.programs.get(prog_id, {})
    return program_version(tuple(rp.argv_prefix), tuple(spec.get("version_args", [])))


# --- RetroArch specifics -----------------------------------------------------------------------

def _retroarch_cfg_candidates(rp: ResolvedProgram) -> list[Path]:
    home = Path.home()
    key = paths.os_key()
    if rp.via == "flatpak":
        return [home / ".var/app/org.libretro.RetroArch/config/retroarch/retroarch.cfg"]
    if key == "windows":
        return [Path(rp.location).parent / "retroarch.cfg"]
    if key == "darwin":
        return [home / "Library/Application Support/RetroArch/config/retroarch.cfg"]
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    return [xdg / "retroarch/retroarch.cfg"]


def read_retroarch_cfg(rp: ResolvedProgram) -> tuple[dict[str, str], Path | None]:
    """Read-only parse of retroarch.cfg ('key = "value"' lines). Never written by the hub."""
    for cfg in _retroarch_cfg_candidates(rp):
        if cfg.is_file():
            values = {}
            try:
                for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
                    m = re.match(r'\s*([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$', line)
                    if m:
                        values[m.group(1)] = m.group(2)
            except OSError:
                pass
            return values, cfg
    return {}, None


def _ra_dir(rp: ResolvedProgram, key: str, default_leaf: str) -> Path:
    values, cfg = read_retroarch_cfg(rp)
    raw = values.get(key, "default")
    base = cfg.parent if cfg else _retroarch_cfg_candidates(rp)[0].parent
    if raw and raw != "default":
        if raw.startswith(":"):  # RetroArch's "relative to the executable/config" syntax
            return Path(rp.location).parent / raw.lstrip(":\\/")
        return paths.expand(raw)
    return base / default_leaf


def retroarch_system_dir(rp: ResolvedProgram) -> Path:
    return _ra_dir(rp, "system_directory", "system")


def retroarch_save_dirs(rp: ResolvedProgram) -> dict[str, Path]:
    return {"save": _ra_dir(rp, "savefile_directory", "saves"),
            "state": _ra_dir(rp, "savestate_directory", "states")}


def core_filename(core: str) -> str:
    ext = {"windows": "dll", "darwin": "dylib"}.get(paths.os_key(), "so")
    return f"{core}_libretro.{ext}"


def find_core(rp: ResolvedProgram, core: str) -> Path | None:
    name = core_filename(core)
    home = Path.home()
    values, cfg = read_retroarch_cfg(rp)
    dirs: list[Path] = []
    if values.get("libretro_directory") and values["libretro_directory"] != "default":
        raw = values["libretro_directory"]
        dirs.append(Path(rp.location).parent / raw.lstrip(":\\/") if raw.startswith(":") else paths.expand(raw))
    key = paths.os_key()
    if rp.via == "flatpak":
        dirs.append(home / ".var/app/org.libretro.RetroArch/config/retroarch/cores")
    elif key == "windows":
        dirs.append(Path(rp.location).parent / "cores")
    elif key == "darwin":
        dirs.append(home / "Library/Application Support/RetroArch/cores")
    else:
        dirs += [home / ".config/retroarch/cores", Path("/usr/lib/x86_64-linux-gnu/libretro"),
                 Path("/usr/lib/aarch64-linux-gnu/libretro"), Path("/usr/lib/libretro"),
                 Path("/usr/local/lib/libretro")]
    for d in dirs:
        p = d / name
        if p.is_file():
            return p
    return None
