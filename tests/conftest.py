import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(autouse=True)
def hub_home(tmp_path, monkeypatch):
    monkeypatch.setenv("DDHUB_HOME", str(tmp_path / "hub"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "home" / ".config"))
    (tmp_path / "home").mkdir()
    return tmp_path / "hub"


@pytest.fixture
def ctx():
    from ddhub.backends import Context
    from ddhub.settings import Settings
    return Context(Settings())
