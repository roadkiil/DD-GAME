"""Crash-safe JSON persistence (write to temp file, fsync, atomic rename, keep one .bak)."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any) -> Any:
    for candidate in (path, path.with_suffix(path.suffix + ".bak")):
        try:
            with open(candidate, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            continue
        except (json.JSONDecodeError, OSError):
            # Corrupt file: fall through to the backup copy.
            continue
    return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
    fd, tmp = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
