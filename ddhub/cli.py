"""Command-line interface. `ddhub` with no arguments opens the fullscreen hub."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import actions, paths
from .backends import Context
from .diagnostics import report
from .launcher import LaunchError, run_blocking
from .library import KIND_LABELS, Game, Library, file_game_id
from .readiness import evaluate
from .saves import RestoreConflict, backup, find_files, list_backups, restore
from .settings import Settings


def _ctx() -> tuple[Library, Context]:
    return Library(), Context(Settings())


def _print_stats(stats, warnings):
    print(f"Added {stats['added']}, updated {stats['updated']} (existing entries keep favorites/playtime).")
    for w in warnings:
        print("  warning:", w)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ddhub", description="DD Hub - unified game launcher")
    sp = ap.add_subparsers(dest="cmd")

    u = sp.add_parser("ui", help="open the hub (default)")
    u.add_argument("--windowed", action="store_true")

    f = sp.add_parser("import-folder", help="import a folder of game files")
    f.add_argument("folder")
    f.add_argument("--platform", help="force a platform id (needed for .iso/.chd/.zip folders)")
    sp.add_parser("rescan", help="re-scan every remembered folder")
    sp.add_parser("import-desktop", help="Linux: import installed games from desktop entries")
    sp.add_parser("import-steam", help="import installed Steam games")
    sp.add_parser("install-bundled", help="add the freely distributable games shipped with the hub")

    a = sp.add_parser("add", help="add a single entry manually")
    a.add_argument("--title", required=True)
    a.add_argument("--platform", required=True)
    a.add_argument("--path", help="game file or executable")
    a.add_argument("--url", help="streaming URL (cloud gaming)")
    a.add_argument("--backend")
    a.add_argument("--arg", action="append", default=[], help="argument for native programs (repeatable)")

    ls = sp.add_parser("list", help="list the library")
    ls.add_argument("--platform")
    ls.add_argument("--search", default="")

    la = sp.add_parser("launch", help="launch a game and wait for it to exit")
    la.add_argument("game")
    la.add_argument("--backend")

    m = sp.add_parser("mark", help="record whether a game actually played correctly on this machine")
    m.add_argument("game")
    m.add_argument("result", choices=["works", "problems", "clear"])
    m.add_argument("--notes", default="")
    m.add_argument("--backend")

    sp.add_parser("doctor", help="diagnose programs, cores, BIOS files and library readiness")

    b = sp.add_parser("backup", help="back up a game's saves and states")
    b.add_argument("game")
    bl = sp.add_parser("backups", help="list backups for a game")
    bl.add_argument("game")
    r = sp.add_parser("restore", help="restore a backup (saves only unless --states)")
    r.add_argument("game")
    r.add_argument("backup", help="backup file name or path ('latest' for the newest)")
    r.add_argument("--states", action="store_true", help="also restore emulator save states")
    r.add_argument("--force", action="store_true", help="overwrite newer files / cross-backend")

    s = sp.add_parser("set-program", help="set an explicit executable path for a program id")
    s.add_argument("program")
    s.add_argument("path")

    o = sp.add_parser("set-options", help="per-game launch options, e.g. graphics flags "
                      "(ddhub set-options SuperTux -- --renderer sdl)")
    o.add_argument("game")
    o.add_argument("options", nargs=argparse.REMAINDER)

    sp.add_parser("catalog", help="show the curated freely distributable catalog")

    args = ap.parse_args(argv)
    cmd = args.cmd or "ui"

    if cmd == "ui":
        from .ui.app import run
        return run(windowed=getattr(args, "windowed", False))

    lib, ctx = _ctx()

    if cmd == "import-folder":
        _print_stats(*actions.import_folder(lib, ctx, args.folder, args.platform))
    elif cmd == "rescan":
        _print_stats(*actions.rescan(lib, ctx))
    elif cmd == "import-desktop":
        _print_stats(*actions.import_desktop(lib))
    elif cmd == "import-steam":
        stats, w = actions.import_steam(lib)
        _print_stats(stats, w)
        if not stats["added"] and not stats["updated"]:
            print("No Steam libraries found (looked in: standard Steam locations).")
    elif cmd == "install-bundled":
        print("Added:", ", ".join(actions.install_bundled(lib)) or "nothing")
    elif cmd == "add":
        if args.platform not in ctx.catalog.platforms:
            print(f"Unknown platform '{args.platform}'. Known: {', '.join(sorted(ctx.catalog.platforms))}")
            return 2
        target = args.url or args.path
        if not target:
            print("Give --path or --url.")
            return 2
        if args.url:
            kind, gid = "streaming", "u-" + file_game_id(args.platform, args.url)[2:]
        else:
            target = str(Path(target).expanduser().resolve())
            kind = "native" if args.platform == "pc" else "emulated"
            gid = file_game_id(args.platform, target)
        g = Game(id=gid, title=args.title, platform=args.platform, kind=kind, path=target,
                 backend=args.backend or ("browser-url" if args.url else ("native-exe" if kind == "native" else "")),
                 args=args.arg, source="manual")
        print(lib.upsert(g), g.id)
        lib.save()
    elif cmd == "list":
        base = lib.sorted()
        for g in lib.search(args.search, args.platform, base):
            rd = evaluate(g, ctx)
            fav = "*" if g.favorite else " "
            print(f"{fav} {rd.status:<15} {g.title[:40]:<40} {ctx.catalog.platform_name(g.platform):<22} "
                  f"{KIND_LABELS.get(g.kind, g.kind):<17} {g.id}")
    elif cmd == "launch":
        g = actions.find_game(lib, args.game)
        bid = args.backend or evaluate(g, ctx).backend
        try:
            res = run_blocking(g, ctx, bid)
        except LaunchError as e:
            print(f"Cannot launch {g.title}: {e.message}\nNext step: {e.action}")
            g.last_error = e.message
            lib.save()
            return 1
        if not g.backend:
            g.backend = bid  # pin the method actually used
        print(f"Session ended after {res.duration:.0f}s (exit code {res.exit_code}).")
        if res.error:
            print("Problem:", res.error, "\nNext step:", res.action)
        msg = actions.after_session(lib, ctx, g, res.started, res.ended, bid)
        if msg:
            print(msg)
        if sys.stdin.isatty() and not res.error:
            ans = input("Did it play correctly? [y]es / [n]o / Enter to skip: ").strip().lower()
            if ans in ("y", "yes", "n", "no"):
                actions.record_test(g, ctx, bid, "works" if ans.startswith("y") else "problems")
                lib.save()
        return 1 if res.error else 0
    elif cmd == "mark":
        g = actions.find_game(lib, args.game)
        bid = args.backend or evaluate(g, ctx).backend
        if args.result == "clear":
            g.local_test = {}
        else:
            actions.record_test(g, ctx, bid, args.result, args.notes)
        lib.save()
        print(f"{g.title}: now {evaluate(g, ctx).status}")
    elif cmd == "doctor":
        print(report(ctx, lib))
    elif cmd == "backup":
        g = actions.find_game(lib, args.game)
        files = find_files(g, ctx)
        info = backup(g, ctx)
        print(f"Backed up {info.files} file(s) to {info.path}" if info else
              f"No save files found for {g.title}. Searched for saves/states named '{Path(g.path).stem}.*'.")
        for kind, p in files:
            print(f"  [{kind}] {p}")
    elif cmd == "backups":
        g = actions.find_game(lib, args.game)
        for bi in list_backups(g):
            print(f"{bi.path.name:<40} {time.ctime(bi.created)}  {bi.files} file(s)  {bi.label}")
    elif cmd == "restore":
        g = actions.find_game(lib, args.game)
        backups = list_backups(g)
        if args.backup == "latest":
            if not backups:
                print("No backups.")
                return 1
            path = backups[0].path
        else:
            path = Path(args.backup)
            if not path.is_file():
                path = paths.hub_home() / "backups" / g.id / args.backup
        try:
            done = restore(g, ctx, path, include_states=args.states, force=args.force)
        except RestoreConflict as e:
            print(str(e) + "\nNothing was changed. Re-run with --force to overwrite.")
            return 1
        except ValueError as e:
            print(f"Not restored: {e}")
            return 1
        print(f"Restored {len(done)} file(s):", *done, sep="\n  ")
    elif cmd == "set-program":
        ctx.settings["programs"][args.program] = args.path
        ctx.settings.save()
        ctx.invalidate()
        print("found" if ctx.program(args.program) else "WARNING: not found at that path", "-", args.path)
    elif cmd == "set-options":
        g = actions.find_game(lib, args.game)
        g.extra_args = [a for a in args.options if a != "--"]
        lib.save()
        print(f"{g.title}: launch options = {g.extra_args or '(none)'}")
    elif cmd == "catalog":
        from .store import load_json
        for k, c in load_json(paths.DATA_DIR / "catalog.json", {}).items():
            if k.startswith("_"):
                continue
            print(f"{c['title']:<34} {c['platform']:<6} code: {c['code_license']:<20} assets: {c['asset_license']}\n"
                  f"{'':<34} {c['url']}{'  (bundled)' if c.get('bundled') else ''}")
    return 0
