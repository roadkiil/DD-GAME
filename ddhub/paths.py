"""Filesystem locations. Everything the hub writes lives under one user-scoped directory."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"
REPO_DIR = PACKAGE_DIR.parent


def os_key() -> str:
    """Return 'windows', 'darwin' or 'linux' - the keys used in backends.json."""
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "darwin"
    return "linux"


def hub_home() -> Path:
    """User data directory. Override with DDHUB_HOME (used by tests)."""
    override = os.environ.get("DDHUB_HOME")
    if override:
        base = Path(override)
    elif os_key() == "windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "DDHub"
    elif os_key() == "darwin":
        base = Path.home() / "Library" / "Application Support" / "DDHub"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "ddhub"
    base.mkdir(parents=True, exist_ok=True)
    return base


def sub(name: str) -> Path:
    p = hub_home() / name
    p.mkdir(parents=True, exist_ok=True)
    return p


def expand(path: str) -> Path:
    """Expand ~ and %VAR%/$VAR in a configured path."""
    return Path(os.path.expandvars(os.path.expanduser(path)))
