"""Readiness: can this game be launched here, and has it actually been verified here?

Ready          - every checkable prerequisite is present AND a session on this machine with this
                 backend was confirmed as playable by the user.
Setup required - something checkable is missing (emulator, core, BIOS, game file, account app).
Untested       - prerequisites look present, but nobody has confirmed it plays on this machine.
Unsupported    - no integrated way to run this platform/backend here.

Upstream compatibility (what emulator projects report) is kept separate in `upstream`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .backends import Context, find_core, retroarch_system_dir
from .library import Game

READY = "Ready"
SETUP = "Setup required"
UNTESTED = "Untested"
UNSUPPORTED = "Unsupported"


@dataclass
class Problem:
    message: str
    action: str


@dataclass
class Readiness:
    status: str
    backend: str = ""
    problems: list[Problem] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    upstream: str = "unknown"
    core_path: str = ""

    @property
    def launchable(self) -> bool:
        return self.status in (READY, UNTESTED)


def default_backend(game: Game, ctx: Context) -> str:
    options = ctx.catalog.backends_for(game.platform)
    if game.backend and game.backend in ctx.catalog.backends:
        return game.backend
    preferred = ctx.settings.get("default_backends", {}).get(game.platform)
    if preferred in options:
        return preferred
    # Prefer the first option that is installed - or that the user explicitly configured, so a broken
    # configured path is reported instead of silently switching emulators (saves live per emulator).
    configured = ctx.settings.get("programs", {})
    for bid in options:
        prog = ctx.catalog.backends[bid]["program"]
        if prog.startswith("@") or prog in configured or ctx.program(prog):
            return bid
    return options[0] if options else ""


def evaluate(game: Game, ctx: Context, backend_id: str | None = None) -> Readiness:
    plat = ctx.catalog.platforms.get(game.platform)
    upstream = plat.get("upstream", "unknown") if plat else "unknown"
    bid = backend_id or default_backend(game, ctx)
    r = Readiness(status=UNTESTED, backend=bid, upstream=upstream)

    if plat is None:
        r.status = UNSUPPORTED
        r.problems.append(Problem(f"Unknown platform '{game.platform}'.",
                                  "Add it to extra_platforms.json or re-import with --platform."))
        return r
    if not bid:
        r.status = UNSUPPORTED
        alt = plat.get("alternatives")
        r.problems.append(Problem(f"No local emulator is integrated for {plat['name']}.",
                                  alt or plat.get("note", "No supported route yet.")))
        return r
    b = ctx.catalog.backends.get(bid)
    if b is None or game.platform not in b.get("platforms", []):
        r.status = UNSUPPORTED
        r.problems.append(Problem(f"Launch method '{bid}' does not support {plat['name']}.",
                                  "Pick another launch method in the game's details."))
        return r

    # 1. The game itself.
    if b["program"] == "@browser" or b.get("tracking") == "manual":
        if not (game.path.startswith("http://") or game.path.startswith("https://")):
            r.problems.append(Problem("No streaming URL set for this entry.",
                                      "Edit the entry: ddhub add --url https://..."))
    elif bid == "steam":
        if not game.meta.get("appid"):
            r.problems.append(Problem("Steam App ID missing.", "Re-run `ddhub import-steam`."))
    elif b["kind"] in ("emulated", "native") and b.get("args") is not None:
        needs_file = any("{rom" in a for a in b.get("args", [])) or b["program"] == "@game"
        if needs_file and not Path(game.path).exists():
            r.problems.append(Problem(f"Game file not found: {game.path}",
                                      "Reconnect the drive, or re-import the folder (ddhub rescan)."))

    # 2. The program that runs it.
    prog_id = b["program"]
    if not prog_id.startswith("@"):
        rp = ctx.program(prog_id)
        spec = ctx.catalog.programs.get(prog_id, {})
        if rp is None:
            configured = ctx.settings.get("programs", {}).get(prog_id)
            if configured:
                r.problems.append(Problem(f"{spec.get('name', prog_id)} not found at configured path {configured}.",
                                          f"Fix settings.json programs.{prog_id}, or remove it to auto-detect."))
            else:
                r.problems.append(Problem(f"{spec.get('name', prog_id)} is not installed (or not found).",
                                          spec.get("install_hint", "Install it, then set its path in settings.json.")))
        else:
            # 3. RetroArch core and system files.
            if b.get("core"):
                core = find_core(rp, b["core"])
                if core is None:
                    r.problems.append(Problem(f"RetroArch core '{b['core']}' is not installed.",
                                              "RetroArch > Main Menu > Online Updater > Core Downloader "
                                              f"(Linux packages: libretro-{b['core'].replace('_', '-')})."))
                else:
                    r.core_path = str(core)
            for req in b.get("requires", []):
                if req.get("platform") and req["platform"] != game.platform:
                    continue
                if req.get("manual"):
                    r.notes.append("You must provide: " + req["note"] + " (the hub cannot check this).")
                    continue
                d = req["dir"]
                if "{retroarch_system}" in d:
                    d = d.replace("{retroarch_system}", str(retroarch_system_dir(rp)))
                found = [f for f in req["any_of"] if (Path(d) / f).is_file()]
                if not found:
                    msg = f"Missing system file: one of {', '.join(req['any_of'])} in {d}"
                    if req.get("optional"):
                        r.notes.append(msg + f" (optional - {req['note']})")
                    else:
                        r.problems.append(Problem(msg, req["note"] + ". Copy it into that folder."))

    if plat.get("note"):
        r.notes.append(plat["note"])
    if r.problems:
        r.status = SETUP
        return r

    t = game.local_test or {}
    if t.get("backend") == bid and t.get("result") == "works":
        r.status = READY
    else:
        r.status = UNTESTED
        if t.get("backend") == bid and t.get("result") == "problems":
            r.notes.append(f"Last session on this machine reported problems ({t.get('date', '')}): {t.get('notes', '')}")
        elif b.get("tracking") == "manual":
            r.notes.append("Streaming session: the hub cannot detect when you finish; confirm when done.")
    return r
