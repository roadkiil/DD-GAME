"""Game library: entries, merge-on-import (no duplicates), favorites, recents, play stats."""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Iterable

from . import paths
from .store import load_json, save_json

# How a game is executed. Shown to the user so emulation, native and streaming are never confused.
KIND_LABELS = {
    "emulated": "Local emulation",
    "native": "Native PC",
    "streaming": "Streaming / cloud",
}


@dataclass
class Game:
    id: str
    title: str
    platform: str
    kind: str  # emulated | native | streaming
    path: str = ""  # ROM / executable / URL depending on backend
    backend: str = ""  # chosen launch method (backend id)
    source: str = "manual"  # folder:<dir> | steam | desktop | catalog | manual
    args: list[str] = field(default_factory=list)  # native: extra argv tokens
    extra_args: list[str] = field(default_factory=list)  # per-game backend options (graphics etc.)
    cwd: str = ""
    cover: str = ""
    favorite: bool = False
    added_at: float = 0.0
    last_played: float = 0.0
    play_count: int = 0
    playtime_s: float = 0.0
    save_paths: list[str] = field(default_factory=list)  # native games: where saves live
    meta: dict = field(default_factory=dict)  # developer, year, license, description, url
    local_test: dict = field(default_factory=dict)  # {result, backend, backend_version, date, notes}
    last_error: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Game":
        names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in names})

    def to_dict(self) -> dict:
        return asdict(self)


def file_game_id(platform: str, path: str | Path) -> str:
    norm = os.path.normcase(os.path.abspath(str(path)))
    return "f-" + hashlib.sha1(f"{platform}|{norm}".encode()).hexdigest()[:16]


# Fields the user owns: an import must never reset them.
USER_FIELDS = (
    "favorite", "last_played", "play_count", "playtime_s", "local_test", "backend",
    "extra_args", "cover", "added_at",
)


class Library:
    def __init__(self, path: Path | None = None):
        self.path = path or (paths.hub_home() / "library.json")
        raw = load_json(self.path, {"version": 1, "games": []})
        self.games: dict[str, Game] = {}
        for d in raw.get("games", []):
            try:
                g = Game.from_dict(d)
                self.games[g.id] = g
            except TypeError:
                continue  # skip malformed entries instead of refusing to start

    def save(self) -> None:
        save_json(self.path, {"version": 1, "games": [g.to_dict() for g in self.sorted()]})

    def sorted(self) -> list[Game]:
        return sorted(self.games.values(), key=lambda g: (g.title.lower(), g.platform))

    def get(self, game_id: str) -> Game | None:
        return self.games.get(game_id)

    def upsert(self, game: Game) -> str:
        """Insert or merge. Returns 'added' or 'updated'. User-owned fields survive re-import."""
        existing = self.games.get(game.id)
        if existing is None:
            if not game.added_at:
                game.added_at = time.time()
            self.games[game.id] = game
            return "added"
        for name in USER_FIELDS:
            val = getattr(existing, name)
            if val:
                setattr(game, name, val)
        if not game.cover and existing.cover:
            game.cover = existing.cover
        self.games[game.id] = game
        return "updated"

    def upsert_many(self, games: Iterable[Game]) -> dict[str, int]:
        stats = {"added": 0, "updated": 0}
        for g in games:
            stats[self.upsert(g)] += 1
        return stats

    def remove(self, game_id: str) -> None:
        self.games.pop(game_id, None)

    # --- views -------------------------------------------------------------
    def favorites(self) -> list[Game]:
        return [g for g in self.sorted() if g.favorite]

    def recent(self, limit: int = 20) -> list[Game]:
        played = [g for g in self.games.values() if g.last_played]
        return sorted(played, key=lambda g: g.last_played, reverse=True)[:limit]

    def platforms(self) -> list[str]:
        return sorted({g.platform for g in self.games.values()})

    def search(self, query: str = "", platform: str | None = None,
               games: Iterable[Game] | None = None) -> list[Game]:
        q = query.strip().lower()
        pool = list(games) if games is not None else self.sorted()
        out = []
        for g in pool:
            if platform and g.platform != platform:
                continue
            if q and q not in g.title.lower() and q not in g.platform.lower():
                continue
            out.append(g)
        return out

    def record_session(self, game_id: str, started: float, ended: float) -> None:
        g = self.games.get(game_id)
        if not g:
            return
        g.last_played = ended
        g.play_count += 1
        g.playtime_s += max(0.0, ended - started)
