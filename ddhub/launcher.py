"""Build argv safely (no shell), start the game, and track it until it really exits."""

from __future__ import annotations

import os
import re
import signal
import subprocess
import time
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path

import psutil

from . import paths
from .backends import Context, retroarch_save_dirs
from .library import Game
from .readiness import Readiness, evaluate


class LaunchError(Exception):
    def __init__(self, message: str, action: str = ""):
        super().__init__(message)
        self.message = message
        self.action = action


_PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")


def _fill(token: str, values: dict[str, str]) -> str:
    def repl(m):
        key = m.group(1)
        if key not in values or values[key] == "":
            raise LaunchError(f"Launch template needs '{key}' but it is not available.",
                              "Check the game entry and backend definition.")
        return values[key]
    return _PLACEHOLDER.sub(repl, token)


def managed_retroarch_cfg(game: Game) -> Path:
    """Hub-owned RetroArch overrides passed with --appendconfig. retroarch.cfg is never touched."""
    cfg = paths.sub("retroarch") / "ddhub-managed.cfg"
    saves = paths.sub("saves") / game.platform
    states = paths.sub("states") / game.platform
    shots = paths.sub("screenshots")
    for d in (saves, states):
        d.mkdir(parents=True, exist_ok=True)
    cfg.write_text(
        "# Written by DD Hub for each launch. Delete freely.\n"
        f'savefile_directory = "{saves.as_posix()}"\n'
        f'savestate_directory = "{states.as_posix()}"\n'
        f'screenshot_directory = "{shots.as_posix()}"\n'
        'sort_savefiles_enable = "false"\n'
        'sort_savestates_enable = "false"\n',
        encoding="utf-8")
    return cfg


@dataclass
class LaunchPlan:
    argv: list[str]
    cwd: str | None
    tracking: str
    backend: str
    url: str = ""
    env: dict = field(default_factory=dict)


def build_plan(game: Game, ctx: Context, backend_id: str | None = None) -> tuple[LaunchPlan, Readiness]:
    r = evaluate(game, ctx, backend_id)
    if not r.launchable:
        first = r.problems[0] if r.problems else None
        raise LaunchError(first.message if first else f"{game.title} cannot be launched ({r.status}).",
                          first.action if first else "")
    b = ctx.catalog.backends[r.backend]
    rom = Path(game.path) if game.path else None
    values = {
        "rom": str(rom) if rom else "",
        "rom_dir": str(rom.parent) if rom else "",
        "rom_stem": rom.stem if rom else "",
        "core_path": r.core_path,
        "appid": str(game.meta.get("appid", "")),
        "url": game.path if game.path.startswith(("http://", "https://")) else "",
    }
    fullscreen = ctx.settings.get("fullscreen", True)
    prog = b["program"]

    if prog == "@browser":
        return LaunchPlan([], None, "manual", r.backend, url=values["url"]), r

    if prog == "@game":
        argv = [str(rom)] + list(game.extra_args) + list(game.args)
        cwd = game.cwd or str(rom.parent)
    else:
        rp = ctx.program(prog)
        argv = list(rp.argv_prefix)
        if fullscreen:
            argv += b.get("fullscreen_args", [])
        if prog == "retroarch" and ctx.settings.get("retroarch_managed_dirs"):
            argv += ["--appendconfig", str(managed_retroarch_cfg(game))]
        argv += list(game.extra_args)
        argv += [_fill(t, values) for t in b.get("args", [])]
        argv += list(game.args) if b["kind"] == "streaming" else []
        cwd = game.cwd or None
    return LaunchPlan(argv, cwd, b.get("tracking", "process"), r.backend), r


# --- Sessions ------------------------------------------------------------------------------------

@dataclass
class SessionResult:
    exit_code: int | None
    started: float
    ended: float
    error: str = ""
    action: str = ""
    log_path: str = ""
    stopped_by_hub: bool = False

    @property
    def duration(self) -> float:
        return self.ended - self.started


QUICK_FAIL_SECONDS = 3.0


class Session:
    """A running game. Call poll() regularly; it returns a SessionResult once the game is gone."""

    def __init__(self, game: Game, plan: LaunchPlan, ctx: Context):
        self.game = game
        self.plan = plan
        self.ctx = ctx
        self.started = time.time()
        self.proc: subprocess.Popen | None = None
        self.tracked: dict[int, psutil.Process] = {}
        self.result: SessionResult | None = None
        self.stopped_by_hub = False
        self.log_path = paths.sub("logs") / f"{game.id}.log"
        self._steam_seen = False

    def start(self) -> None:
        if self.plan.tracking == "manual" and self.plan.url:
            if not webbrowser.open(self.plan.url):
                raise LaunchError("Could not open a web browser.", "Install a default browser, or open the URL yourself: " + self.plan.url)
            return
        log = open(self.log_path, "w", encoding="utf-8", errors="replace")
        log.write(f"# DD Hub launch {time.ctime()}\n# argv: {self.plan.argv!r}\n# cwd: {self.plan.cwd}\n")
        log.flush()
        kwargs = {}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
        env = dict(os.environ, **self.plan.env)
        try:
            self.proc = subprocess.Popen(self.plan.argv, cwd=self.plan.cwd, stdout=log, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL, env=env, **kwargs)
        except FileNotFoundError:
            raise LaunchError(f"Program not found: {self.plan.argv[0]}", "Reinstall it or fix its path in settings.json.")
        except PermissionError:
            raise LaunchError(f"Not allowed to run {self.plan.argv[0]}", "Check the file is executable.")
        except OSError as e:
            raise LaunchError(f"Could not start the game: {e}", "See the log: " + str(self.log_path))
        finally:
            log.close()
        try:
            self.tracked[self.proc.pid] = psutil.Process(self.proc.pid)
        except psutil.Error:
            pass

    def _refresh_tree(self) -> None:
        # POSIX: the game was started in its own session, so every process it spawns shares that
        # session id - even ones orphaned because their parent already exited (common launcher
        # pattern). Windows has no session ids; there we follow the parent/child tree.
        if os.name != "nt" and self.proc is not None:
            now = time.monotonic()
            if now - getattr(self, "_last_scan", 0) > 0.4:
                self._last_scan = now
                for p in psutil.process_iter(["pid"]):
                    if p.pid in self.tracked:
                        continue
                    try:
                        if os.getsid(p.pid) == self.proc.pid:
                            self.tracked[p.pid] = p
                    except (OSError, psutil.Error):
                        continue
        for p in list(self.tracked.values()):
            try:
                for c in p.children(recursive=True):
                    self.tracked.setdefault(c.pid, c)
            except psutil.Error:
                pass

    def _alive(self) -> list[psutil.Process]:
        alive = []
        for pid, p in list(self.tracked.items()):
            try:
                if p.is_running() and p.status() != psutil.STATUS_ZOMBIE:
                    alive.append(p)
                    continue
            except psutil.Error:
                pass
            self.tracked.pop(pid, None)
        return alive

    def poll(self) -> SessionResult | None:
        if self.result:
            return self.result
        if self.plan.tracking == "manual":
            return None  # only finish() ends a streaming session
        if self.proc is not None:
            self.proc.poll()  # reap the direct child so it does not linger as a zombie
        self._refresh_tree()
        if self.plan.tracking == "steam":
            return self._poll_steam()
        if self._alive():
            return None
        self._last_scan = 0  # never conclude "exited" from a rate-limited scan: rescan first
        self._refresh_tree()
        if self._alive():
            return None
        return self._finish(self.proc.returncode if self.proc else None)

    def _poll_steam(self) -> SessionResult | None:
        from .importers.steam import running_appid
        appid = str(self.game.meta.get("appid", ""))
        running = running_appid()
        if running == appid:
            self._steam_seen = True
            return None
        if not self._steam_seen:
            if time.time() - self.started > 120:
                return self._finish(None, "Steam did not report the game as running within 2 minutes.",
                                    "Open Steam and check for update/install prompts.")
            return None
        return self._finish(0)

    def _finish(self, code: int | None, error: str = "", action: str = "") -> SessionResult:
        ended = time.time()
        if not error and not self.stopped_by_hub and code not in (0, None) and ended - self.started < QUICK_FAIL_SECONDS:
            error = f"The game exited immediately (exit code {code})."
            action = "See the last lines of the log: " + str(self.log_path)
            tail = self.log_tail()
            if tail:
                error += "\n" + tail
        self.result = SessionResult(code, self.started, ended, error, action, str(self.log_path), self.stopped_by_hub)
        return self.result

    def finish(self) -> SessionResult:
        """End a manual (streaming) session, or force-collect a result."""
        return self.result or self._finish(0)

    def log_tail(self, lines: int = 4) -> str:
        try:
            text = self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return ""
        body = [l for l in text if not l.startswith("# ")]
        return "\n".join(body[-lines:])

    def stop(self, grace: float = 5.0) -> None:
        """Ask the game to close (SIGTERM / terminate), then force-kill whatever remains."""
        self.stopped_by_hub = True
        self._refresh_tree()
        procs = self._alive()
        for p in procs:
            try:
                p.send_signal(signal.SIGTERM) if os.name != "nt" else p.terminate()
            except psutil.Error:
                pass
        _, alive = psutil.wait_procs(procs, timeout=grace)
        for p in alive:
            try:
                p.kill()
            except psutil.Error:
                pass
        if self.proc:
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass


def run_blocking(game: Game, ctx: Context, backend_id: str | None = None, poll_s: float = 0.5) -> SessionResult:
    plan, _ = build_plan(game, ctx, backend_id)
    s = Session(game, plan, ctx)
    s.start()
    if plan.tracking == "manual":
        input("Streaming session opened. Press Enter here when you have finished playing... ")
        return s.finish()
    while True:
        res = s.poll()
        if res:
            return res
        time.sleep(poll_s)


def save_dirs_for(game: Game, ctx: Context, backend_id: str) -> dict[str, list[Path]]:
    """Where a backend keeps this game's saves (in-game) and states (emulator snapshots)."""
    b = ctx.catalog.backends.get(backend_id, {})
    out: dict[str, list[Path]] = {"save": [], "state": []}
    if b.get("program") == "retroarch":
        rp = ctx.program("retroarch")
        if ctx.settings.get("retroarch_managed_dirs"):
            out["save"].append(paths.hub_home() / "saves" / game.platform)
            out["state"].append(paths.hub_home() / "states" / game.platform)
        if rp:
            d = retroarch_save_dirs(rp)
            out["save"].append(d["save"])
            out["state"].append(d["state"])
        if game.path:
            out["save"].append(Path(game.path).parent)  # savefiles_in_content_dir
    for sp in game.save_paths:
        out["save"].append(paths.expand(sp))
    return out
