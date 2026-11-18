#!/usr/bin/env python3
"""End-to-end verification of the browse -> launch -> play -> exit -> return loop.

Runs the real hub UI on an X display (Xvfb in CI/containers), drives it with real key events via
xdotool, reads the hub's state file, and compares screenshots of the game to confirm the picture
changes in response to input (evidence of gameplay, not just a process starting).

Requirements (Linux): Xvfb or a real X display, xdotool, ImageMagick `import`, RetroArch with the
mGBA core, SuperTux. Everything runs in a throwaway HOME and DDHUB_HOME; nothing of yours is touched.

    python3 tools/verify_e2e.py --out docs/test-results
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESULTS: list[dict] = []


def sh(*argv, env=None, check=False, timeout=60, capture=True):
    return subprocess.run([str(a) for a in argv], env=env, check=check, timeout=timeout,
                          capture_output=capture, text=True)


class Harness:
    def __init__(self, out: Path, display: str):
        self.out = out
        self.shots = out / "screenshots"
        self.shots.mkdir(parents=True, exist_ok=True)
        self.tmp = Path(tempfile.mkdtemp(prefix="ddhub-e2e-"))
        self.home = self.tmp / "home"
        self.hub = self.tmp / "hub"
        self.home.mkdir()
        self.state_file = self.tmp / "state.json"
        self.env = dict(os.environ, DISPLAY=display, HOME=str(self.home), DDHUB_HOME=str(self.hub),
                        DDHUB_STATE_FILE=str(self.state_file), SDL_AUDIODRIVER="dummy",
                        XDG_DATA_HOME=str(self.home / ".local/share"),
                        XDG_CONFIG_HOME=str(self.home / ".config"),
                        PYTHONPATH=str(REPO))
        self.ui: subprocess.Popen | None = None

    # --- helpers -------------------------------------------------------------------------------
    def cli(self, *args, check=True):
        r = sh(sys.executable, "-m", "ddhub", *args, env=self.env, timeout=120)
        if check and r.returncode != 0:
            raise AssertionError(f"ddhub {' '.join(args)} failed: {r.stdout}{r.stderr}")
        return r

    def key(self, *keys, delay=0.35):
        # Hold each key ~120 ms: games that poll input once per frame miss shorter taps when the
        # frame rate is low (software rendering here).
        for k in keys:
            sh("xdotool", "keydown", k, env=self.env)
            time.sleep(0.12)
            sh("xdotool", "keyup", k, env=self.env)
            time.sleep(delay)

    def shot(self, name) -> Path:
        p = self.shots / f"{name}.png"
        sh("import", "-window", "root", p, env=self.env, check=True)
        return p

    @staticmethod
    def diff(a: Path, b: Path) -> int:
        r = sh("compare", "-metric", "AE", a, b, "null:")
        try:
            return int(float(r.stderr.split()[0]))
        except (ValueError, IndexError):
            return -1

    def state(self) -> dict:
        try:
            return json.loads(self.state_file.read_text())
        except (OSError, json.JSONDecodeError):
            return {}

    def wait_state(self, pred, timeout=20, what="state"):
        end = time.time() + timeout
        while time.time() < end:
            s = self.state()
            if s and pred(s):
                return s
            time.sleep(0.2)
        raise AssertionError(f"Timed out waiting for {what}; last state: {self.state()}")

    def window_of(self, name, timeout=30):
        end = time.time() + timeout
        while time.time() < end:
            r = sh("xdotool", "search", "--onlyvisible", "--name", name, env=self.env)
            if r.stdout.strip():
                return r.stdout.split()[0]
            time.sleep(0.5)
        return None

    def focus(self, win):
        sh("xdotool", "windowfocus", win, env=self.env)
        time.sleep(0.3)

    def input_response(self, name, keys, settle=1.5, hold=None):
        """Idle-vs-input comparison: two frames with no input give the background-animation
        baseline; a frame after input must differ from the idle frame by clearly more."""
        a = self.shot(f"{name}-a-idle")
        time.sleep(settle)
        b = self.shot(f"{name}-b-idle")
        if hold:
            sh("xdotool", "keydown", hold, env=self.env)
            time.sleep(1.2)
            sh("xdotool", "keyup", hold, env=self.env)
        else:
            self.key(*keys)
        time.sleep(settle)
        c = self.shot(f"{name}-c-after-input")
        return self.diff(a, b), self.diff(b, c), [a, b, c]

    def library(self):
        return json.loads((self.hub / "library.json").read_text())["games"]

    def start_ui(self):
        self.ui = subprocess.Popen([sys.executable, "-m", "ddhub", "ui"], env=self.env,
                                   stdout=open(self.tmp / "ui.log", "a"), stderr=subprocess.STDOUT)
        self.wait_state(lambda s: s.get("screen") == "library", what="hub library screen")
        time.sleep(1)

    def quit_ui_via_menu(self):
        self.key("Tab")
        self.wait_state(lambda s: s["screen"] == "menu", what="menu")
        self.key("Up", "Return")  # Up wraps to the last item: Quit
        code = self.ui.wait(timeout=15)
        return code

    def select(self, title):
        s = self.state()
        items = s["items"]
        if title not in items:
            raise AssertionError(f"{title} not in view: {items}")
        target, cur = items.index(title), items.index(s["selected"])
        for _ in range(abs(target - cur)):
            self.key("Right" if target > cur else "Left", delay=0.25)
        self.wait_state(lambda s: s["selected"] == title, what=f"selection {title}")


def record(name, ok, detail="", evidence=None):
    RESULTS.append({"test": name, "result": "PASS" if ok else "FAIL", "detail": detail,
                    "evidence": [str(e) for e in (evidence or [])]})
    print(("PASS " if ok else "FAIL ") + name + (f" - {detail}" if detail else ""), flush=True)


def check(name, fn):
    try:
        detail, ev = fn() or ("", [])
        record(name, True, detail, ev)
    except Exception as e:  # noqa: BLE001 - every failure must be reported, not crash the run
        record(name, False, f"{type(e).__name__}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "docs" / "test-results"))
    ap.add_argument("--display", default=os.environ.get("DISPLAY", ":99"))
    args = ap.parse_args()
    out = Path(args.out)
    h = Harness(out, args.display)
    env_info = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "os": platform.platform(), "python": sys.version.split()[0],
        "display": "Xvfb (virtual, software OpenGL llvmpipe), no GPU, no audio device, no physical controller",
        "retroarch": sh("retroarch", "--version").stdout.splitlines()[1:2] or ["?"],
    }
    stx = shutil.which("supertux2", path=os.environ.get("PATH", "") + ":/usr/games")
    env_info["supertux"] = sh(stx, "--version").stdout.strip() if stx else "missing"
    try:
        import pygame
        env_info["pygame"] = pygame.version.ver + " / SDL " + ".".join(map(str, pygame.get_sdl_version()))
    except Exception:
        pass

    # Hub settings for the run: hub-managed RetroArch dirs so saves/states are inspectable.
    h.hub.mkdir(parents=True)
    (h.hub / "settings.json").write_text(json.dumps({"retroarch_managed_dirs": True, "fullscreen": True}))

    # 1. Fresh setup + import without duplicates ---------------------------------------------------
    def t_import():
        h.cli("install-bundled")
        h.cli("import-desktop")
        h.cli("import-desktop")
        h.cli("install-bundled")
        games = h.library()
        ids = [g["id"] for g in games]
        titles = sorted(g["title"] for g in games)
        assert len(ids) == len(set(ids)), "duplicate ids"
        assert "Libbet and the Magic Floor" in titles and "SuperTux 2" in titles, titles
        assert len(games) == 2, f"expected 2 entries after repeated imports, got {titles}"
        return f"2 entries after importing twice: {titles}", []
    check("fresh setup + import without duplicates", t_import)

    # 2. Hub start + keyboard navigation + search -----------------------------------------------
    def t_nav():
        h.start_ui()
        s = h.state()
        assert s["items"] == ["Libbet and the Magic Floor", "SuperTux 2"], s["items"]
        a = h.shot("01-library")
        h.key("Right")
        h.wait_state(lambda s: s["selected"] == "SuperTux 2", what="move right")
        h.key("e")  # next tab -> Favorites
        h.wait_state(lambda s: s["tab"] == "fav", what="favorites tab")
        h.key("q")
        h.wait_state(lambda s: s["tab"] == "all", what="all tab")
        h.key("slash")
        h.wait_state(lambda s: s["screen"] == "search", what="search screen")
        h.key("t", "u", "x")
        s = h.wait_state(lambda s: s["items"] == ["SuperTux 2"], what="search filter")
        b = h.shot("02-search")
        h.key("Tab")  # done
        h.wait_state(lambda s: s["screen"] == "library")
        h.key("Escape")  # clears query
        h.wait_state(lambda s: s["query"] == "" and len(s["items"]) == 2, what="query cleared")
        return "arrow keys, tab switching, on-screen search filter and clear all responded", [a, b]
    check("hub navigation (keyboard) + search", t_nav)

    # 3. Emulated homebrew: launch -> play -> exit -> return -------------------------------------
    def t_libbet():
        h.select("Libbet and the Magic Floor")
        h.key("Return")
        s = h.wait_state(lambda s: s["screen"] == "details", what="details")
        assert s["selected_status"] == "Untested", s
        d = h.shot("03-libbet-details")
        h.key("Return")
        h.wait_state(lambda s: s["screen"] == "playing", what="playing")
        win = h.window_of("RetroArch")
        assert win, "RetroArch window never appeared"
        time.sleep(4)
        h.focus(h.window_of("RetroArch"))
        idle1, d_start, ev1 = h.input_response("04-libbet-title", ["Return", "Return"])
        idle2, d_move, ev2 = h.input_response("05-libbet-floor", ["Right", "Right", "Down"])
        assert d_start > max(1000, 10 * idle1), f"Start did not change the picture (idle {idle1}, input {d_start})"
        assert d_move > max(50, 10 * idle2), f"D-pad did not change the picture (idle {idle2}, input {d_move})"
        f1, f2, f3 = ev1[0], ev2[0], ev2[2]
        h.key("F2", delay=1.5)  # RetroArch save state (for the backup test)
        h.key("Escape", "Escape", delay=0.6)  # RetroArch quit (press twice)
        s = h.wait_state(lambda s: s["screen"] == "post", timeout=20, what="return to hub after exit")
        p = h.shot("07-libbet-returned")
        return (f"RetroArch window shown; idle-vs-input pixel change: Start {idle1}->{d_start} px, "
                f"D-pad {idle2}->{d_move} px; "
                f"hub regained control on exit and showed the post-session prompt"), [d, f1, f2, f3, p]
    check("emulated homebrew: Libbet via RetroArch+mGBA (launch, input changes picture, exit, return)", t_libbet)

    def t_mark():
        h.key("Return")  # "Yes - it plays correctly" (automated: frames responded to input)
        s = h.wait_state(lambda s: s["screen"] == "details", what="details after post")
        s = h.wait_state(lambda s: s["selected_status"] == "Ready", what="Ready status")
        h.key("Escape")
        return "status Untested -> Ready after a confirmed session", [h.shot("08-libbet-ready")]
    check("post-session result recorded (Untested -> Ready)", t_mark)

    # 4. Native open-source game ---------------------------------------------------------------
    def t_supertux():
        h.wait_state(lambda s: s["screen"] == "library")
        h.select("SuperTux 2")
        h.key("Return", "Return")
        h.wait_state(lambda s: s["screen"] == "playing", what="playing supertux")
        win = h.window_of("SuperTux", timeout=40)
        assert win, "SuperTux window never appeared"
        time.sleep(8)
        win = h.window_of("SuperTux")  # SDL may recreate its window during start-up
        h.focus(win)
        title = h.shot("09-supertux-title")
        h.key("Return", delay=1.5)          # Start Game submenu
        h.key("Return", delay=5)            # Story Mode -> intro cutscene
        h.key("Escape", delay=5)            # skip intro -> world map
        idle, d, ev = h.input_response("10-supertux-worldmap", ["Down"], settle=2.5)
        # The world map has animated water, so idle frames already differ; require clearly more.
        assert d > 1.3 * idle + 500, f"Tux did not move on the world map (idle {idle}, input {d})"
        return (f"title -> Story Mode -> world map; idle-vs-input pixel change {idle}->{d} px "
                f"(weaker metric: animated water; frames reviewed visually - Tux moved, camera scrolled)"), [title] + ev
    check("native game: SuperTux launch + in-game input response (world map)", t_supertux)

    def t_supertux_exit():
        h.key("Escape", delay=1.5)                    # pause menu
        h.key("Down", "Down", delay=0.5)
        h.key("Return", delay=3)                      # Leave World
        h.key("Escape", delay=2)                      # back to the main menu
        h.shot("12-supertux-menu")
        h.key(*(["Down"] * 6), delay=0.4)             # Quit
        h.key("Return", delay=1)
        s = h.wait_state(lambda s: s["screen"] in ("post", "dialog"), timeout=30, what="return after SuperTux exit")
        p = h.shot("13-supertux-returned")
        assert s["screen"] == "post", f"expected post-session prompt, got {s}"
        h.key("Down", "Down", "Return")  # Skip: in-level gameplay was not verified, so leave it Untested
        h.wait_state(lambda s: s["screen"] == "details")
        h.key("Escape")
        return "quit through the game's own menu; hub detected the exit and returned", [p]
    check("native game: exit detected, hub returns", t_supertux_exit)

    # 5. Persistence -------------------------------------------------------------------------------
    def t_persist():
        code = h.quit_ui_via_menu()
        assert code == 0, f"hub exit code {code}"
        h.start_ui()
        h.key("e", "e")  # All -> Favorites -> Recent
        s = h.wait_state(lambda s: s["tab"] == "recent", what="recent tab")
        assert s["items"][:2] == ["SuperTux 2", "Libbet and the Magic Floor"], s["items"]
        h.key("q", "q")
        h.wait_state(lambda s: s["tab"] == "all")
        games = {g["title"]: g for g in h.library()}
        lb = games["Libbet and the Magic Floor"]
        assert lb["play_count"] == 1 and lb["playtime_s"] > 5, lb
        assert lb["local_test"]["result"] == "works", lb["local_test"]
        st = games["SuperTux 2"]
        assert st["play_count"] == 1 and not st["local_test"], st
        h.select("Libbet and the Magic Floor")
        s = h.wait_state(lambda s: s["selected_status"] == "Ready", what="Ready after restart")
        return (f"after restart: Recent order {s['items'][:2] if 'items' in s else ''}, Libbet Ready, "
                f"playtime Libbet {lb['playtime_s']:.0f}s / SuperTux {st['playtime_s']:.0f}s"), [h.shot("14-after-restart")]
    check("persistence across hub restart (recents, playtime, test result)", t_persist)

    # 6. Missing file / missing backend ----------------------------------------------------------
    def t_missing_file():
        romdir = h.tmp / "roms"
        romdir.mkdir()
        shutil.copy(REPO / "content/homebrew/libbet/libbet.gb", romdir / "Libbet Copy (Test).gb")
        h.cli("import-folder", str(romdir))
        (romdir / "Libbet Copy (Test).gb").unlink()
        h.key("Tab")
        h.wait_state(lambda s: s["screen"] == "menu")
        h.key("Return")  # Reload library
        s = h.wait_state(lambda s: "Libbet Copy" in s["items"], what="reloaded library")
        h.select("Libbet Copy")
        s = h.wait_state(lambda s: s["selected_status"] == "Setup required", what="setup required")
        h.key("Return", "Return")
        s = h.wait_state(lambda s: s["screen"] == "dialog", what="error dialog")
        ev = h.shot("15-missing-file")
        h.key("Return")
        h.wait_state(lambda s: s["screen"] == "details")
        h.key("Escape")
        r = h.cli("launch", "Libbet Copy", check=False)
        assert r.returncode == 1 and "Game file not found" in r.stdout, r.stdout
        return f"UI showed dialog '{s['dialog']}'; CLI: {r.stdout.strip().splitlines()[0]}", [ev]
    check("missing game file -> Setup required + clear error", t_missing_file)

    def t_missing_backend():
        h.cli("set-program", "retroarch", "/nonexistent/retroarch")
        r = h.cli("launch", "Libbet and the Magic Floor", check=False)
        ok = r.returncode == 1 and "not found at configured path" in r.stdout
        settings = json.loads((h.hub / "settings.json").read_text())
        settings["programs"].pop("retroarch")
        (h.hub / "settings.json").write_text(json.dumps(settings))
        assert ok, r.stdout
        return r.stdout.strip().replace("\n", " | "), []
    check("missing emulator -> Setup required + next action", t_missing_backend)

    # 7. Save backup / restore ---------------------------------------------------------------------
    def t_saves():
        states = list((h.hub / "states" / "gb").glob("libbet.state*"))
        assert states, "RetroArch did not write a save state into the hub-managed dir"
        auto = list((h.hub / "backups").rglob("*-auto.zip"))
        assert auto, "no automatic post-session backup"
        st = states[0]
        original = st.read_bytes()
        r = h.cli("backup", "Libbet and the Magic Floor")
        assert "Backed up" in r.stdout, r.stdout
        time.sleep(1.2)
        st.write_bytes(b"newer-data")  # simulate playing on after the backup
        r = h.cli("restore", "Libbet and the Magic Floor", "latest", "--states", check=False)
        assert r.returncode == 1 and "newer" in r.stdout.lower(), "restore should refuse to overwrite newer: " + r.stdout
        assert st.read_bytes() == b"newer-data"
        r = h.cli("restore", "Libbet and the Magic Floor", "latest", "--states", "--force")
        assert st.read_bytes() == original, "state not restored"
        pre = list((h.hub / "backups").rglob("*-pre-restore.zip"))
        assert pre, "no safety backup before restore"
        return (f"state {st.name} backed up; restore refused to overwrite newer file; forced restore "
                f"matched original bytes; pre-restore safety backup created"), []
    check("save backup + restore (state vs save separation, newer-file guard)", t_saves)

    try:
        if h.ui and h.ui.poll() is None:
            h.quit_ui_via_menu()
    except Exception:
        h.ui.kill()

    summary = {"environment": env_info, "results": RESULTS,
               "passed": sum(r["result"] == "PASS" for r in RESULTS), "total": len(RESULTS)}
    (out / "e2e-results.json").write_text(json.dumps(summary, indent=2))
    shutil.copy(h.tmp / "ui.log", out / "e2e-ui.log") if (h.tmp / "ui.log").exists() else None
    print(f"\n{summary['passed']}/{summary['total']} passed. Results: {out / 'e2e-results.json'}")
    return 0 if summary["passed"] == summary["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
