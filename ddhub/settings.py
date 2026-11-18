"""User settings with defaults. Unknown keys are preserved so hand edits are never lost."""

from __future__ import annotations

import copy
from pathlib import Path

from . import paths
from .store import load_json, save_json

DEFAULTS: dict = {
    "fullscreen": True,
    # Explicit executable paths, e.g. {"retroarch": "D:/Emu/RetroArch/retroarch.exe"}
    "programs": {},
    # Folders imported with `ddhub import-folder`; re-scanned by `ddhub rescan`.
    "rom_folders": [],
    # When true, RetroArch launched by the hub stores saves/states/screenshots under the hub's
    # own directories via --appendconfig (your retroarch.cfg is never modified). Off by default
    # so existing RetroArch saves keep loading from where they already are.
    "retroarch_managed_dirs": False,
    # Hold these controller buttons together to close a running game (fallback when the game
    # or emulator has no quit option of its own).
    "quit_combo": ["back", "start"],
    "quit_hold_seconds": 2.0,
    # Logical action -> controller buttons (SDL GameController names) and keyboard keys.
    "controls": {
        "accept":   {"buttons": ["a"], "keys": ["return", "space"]},
        "back":     {"buttons": ["b"], "keys": ["escape", "backspace"]},
        "favorite": {"buttons": ["x"], "keys": ["f"]},
        "search":   {"buttons": ["y"], "keys": ["/", "s"]},
        "prev_tab": {"buttons": ["leftshoulder"], "keys": ["q", "page up"]},
        "next_tab": {"buttons": ["rightshoulder"], "keys": ["e", "page down"]},
        "menu":     {"buttons": ["start"], "keys": ["m", "tab"]},
    },
    # platform -> backend id to use by default instead of the first entry in platforms.json
    "default_backends": {},
}


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


class Settings:
    def __init__(self, path: Path | None = None):
        self.path = path or (paths.hub_home() / "settings.json")
        self.data = _merge(DEFAULTS, load_json(self.path, {}))

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value) -> None:
        self.data[key] = value

    def save(self) -> None:
        save_json(self.path, self.data)
