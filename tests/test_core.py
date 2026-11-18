import json
import sys
import time
from pathlib import Path

import pytest

from ddhub.importers import desktop, folders, steam
from ddhub.launcher import LaunchError, Session, build_plan
from ddhub.library import Game, Library, file_game_id
from ddhub import readiness
from ddhub.saves import RestoreConflict, backup, restore
from ddhub.store import load_json, save_json


def test_store_survives_corrupt_main_file(tmp_path):
    p = tmp_path / "x.json"
    save_json(p, {"a": 1})
    save_json(p, {"a": 2})  # first version now in .bak
    p.write_text("{corrupt")
    assert load_json(p, None) == {"a": 1}


def test_import_merge_keeps_user_fields(tmp_path):
    lib = Library(tmp_path / "lib.json")
    g = Game(id="x", title="T", platform="gb", kind="emulated", path="/a.gb")
    lib.upsert(g)
    lib.games["x"].favorite = True
    lib.games["x"].playtime_s = 99
    again = Game(id="x", title="T (renamed)", platform="gb", kind="emulated", path="/a.gb")
    assert lib.upsert(again) == "updated"
    assert lib.games["x"].favorite and lib.games["x"].playtime_s == 99
    assert lib.games["x"].title == "T (renamed)"
    lib.save()
    assert len(Library(tmp_path / "lib.json").games) == 1


def test_folder_scan_maps_extensions_and_skips_ambiguous(tmp_path, ctx):
    (tmp_path / "Game One (USA).gb").write_bytes(b"x")
    (tmp_path / "disc.iso").write_bytes(b"x")
    (tmp_path / "Game One (USA).png").write_bytes(b"x")
    games, warnings = folders.scan(tmp_path, ctx.catalog)
    assert [(g.title, g.platform) for g in games] == [("Game One", "gb")]
    assert games[0].cover.endswith("Game One (USA).png")
    assert any("disc.iso" in w for w in warnings)
    forced, _ = folders.scan(tmp_path, ctx.catalog, platform="ps2")
    assert [g.platform for g in forced] == ["ps2"]
    # Same files -> same ids: rescanning cannot create duplicates.
    assert folders.scan(tmp_path, ctx.catalog)[0][0].id == games[0].id


def test_desktop_entries(tmp_path):
    (tmp_path / "tux.desktop").write_text(
        "[Desktop Entry]\nType=Application\nName=Tux Game\nExec=/usr/bin/tuxgame --flag %U\nCategories=Game;ActionGame;\n")
    (tmp_path / "emu.desktop").write_text(
        "[Desktop Entry]\nType=Application\nName=Some Emu\nExec=emu\nCategories=Game;Emulator;\n")
    (tmp_path / "hidden.desktop").write_text(
        "[Desktop Entry]\nType=Application\nName=H\nExec=h\nCategories=Game;\nNoDisplay=true\n")
    games, _ = desktop.scan([tmp_path])
    assert [(g.title, g.path, g.args) for g in games] == [("Tux Game", "/usr/bin/tuxgame", ["--flag"])]


def test_steam_library_parse(tmp_path):
    root = tmp_path / "Steam"
    (root / "steamapps").mkdir(parents=True)
    lib2 = tmp_path / "SteamLib2"
    (lib2 / "steamapps").mkdir(parents=True)
    (root / "steamapps" / "libraryfolders.vdf").write_text(
        '"libraryfolders"\n{\n "0"\n {\n  "path" "%s"\n }\n "1"\n {\n  "path" "%s"\n }\n}\n' % (root, lib2))
    (root / "steamapps" / "appmanifest_620.acf").write_text(
        '"AppState"\n{\n "appid" "620"\n "name" "Portal 2"\n "installdir" "Portal 2"\n}\n')
    (lib2 / "steamapps" / "appmanifest_1493710.acf").write_text(
        '"AppState"\n{\n "appid" "1493710"\n "name" "Proton Experimental"\n}\n')
    games, _ = steam.scan([root])
    assert [(g.id, g.title, g.backend) for g in games] == [("steam-620", "Portal 2", "steam")]


def test_readiness_states(tmp_path, ctx):
    rom = tmp_path / "a.gb"
    rom.write_bytes(b"x")
    g = Game(id="g", title="A", platform="gb", kind="emulated", path=str(rom))
    r = readiness.evaluate(g, ctx)
    assert r.status in (readiness.UNTESTED, readiness.SETUP)  # depends on RetroArch/mGBA presence
    g2 = Game(id="m", title="Missing", platform="gb", kind="emulated", path=str(tmp_path / "nope.gb"))
    r2 = readiness.evaluate(g2, ctx)
    assert r2.status == readiness.SETUP and any("not found" in p.message for p in r2.problems)
    g3 = Game(id="s", title="S", platform="switch", kind="emulated", path=str(rom))
    assert readiness.evaluate(g3, ctx).status == readiness.UNSUPPORTED
    g4 = Game(id="p", title="P", platform="ps5", kind="streaming", path="", backend="ps-remote-play")
    assert readiness.evaluate(g4, ctx).status in (readiness.SETUP, readiness.UNSUPPORTED)


def _native_game(tmp_path, code: str) -> Game:
    script = tmp_path / "game.py"
    script.write_text(code)
    return Game(id="n", title="N", platform="pc", kind="native", path=sys.executable,
                args=[str(script)], backend="native-exe")


def test_ready_requires_local_confirmation(tmp_path, ctx):
    g = _native_game(tmp_path, "pass")
    assert readiness.evaluate(g, ctx).status == readiness.UNTESTED
    g.local_test = {"result": "works", "backend": "native-exe"}
    assert readiness.evaluate(g, ctx).status == readiness.READY
    g.local_test = {"result": "works", "backend": "steam"}  # different backend: not evidence
    assert readiness.evaluate(g, ctx).status == readiness.UNTESTED


def test_argv_is_a_list_and_never_shell_interpreted(tmp_path, ctx):
    evil = tmp_path / "x; rm -rf ~ $(whoami).gb"
    evil.write_bytes(b"x")
    g = Game(id="e", title="E", platform="gb", kind="emulated", path=str(evil), backend="mgba-standalone")
    try:
        plan, _ = build_plan(g, ctx)
    except LaunchError:
        pytest.skip("mGBA not installed")
    assert plan.argv[-1] == str(evil)  # one argv element, passed verbatim


def test_session_tracks_child_processes(tmp_path, ctx):
    # The launcher exits at once but leaves a child running (like many game launchers).
    code = ("import subprocess, sys, time\n"
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(2.5)'])\n")
    g = _native_game(tmp_path, code)
    plan, _ = build_plan(g, ctx)
    s = Session(g, plan, ctx)
    s.start()
    t0 = time.time()
    while not s.poll():
        time.sleep(0.1)
        assert time.time() - t0 < 15
    assert time.time() - t0 >= 2.0, "session ended before the child process exited"
    assert s.result.error == ""


def test_quick_crash_is_reported_with_log(tmp_path, ctx):
    g = _native_game(tmp_path, "import sys; print('missing data file'); sys.exit(3)")
    plan, _ = build_plan(g, ctx)
    s = Session(g, plan, ctx)
    s.start()
    while not s.poll():
        time.sleep(0.05)
    assert s.result.exit_code == 3 and "exited immediately" in s.result.error
    assert "missing data file" in s.result.error


def test_stop_terminates_tree(tmp_path, ctx):
    g = _native_game(tmp_path, "import time; time.sleep(60)")
    plan, _ = build_plan(g, ctx)
    s = Session(g, plan, ctx)
    s.start()
    time.sleep(0.5)
    s.stop(grace=2)
    t0 = time.time()
    while not s.poll():
        time.sleep(0.05)
        assert time.time() - t0 < 5
    assert s.result.stopped_by_hub and s.result.error == ""


def test_save_backup_restore_guards_newer(tmp_path, ctx):
    savedir = tmp_path / "saves"
    savedir.mkdir()
    f = savedir / "profile.dat"
    f.write_text("v1")
    g = _native_game(tmp_path, "pass")
    g.save_paths = [str(savedir)]
    info = backup(g, ctx)
    assert info and info.files == 1
    time.sleep(1.1)
    f.write_text("v2-newer")
    with pytest.raises(RestoreConflict):
        restore(g, ctx, info.path)
    assert f.read_text() == "v2-newer"
    restore(g, ctx, info.path, force=True)
    assert f.read_text() == "v1"
    labels = sorted(p.name.split("-")[-1] for p in info.path.parent.glob("*.zip"))
    assert "restore.zip" in labels  # pre-restore safety copy


def test_backup_refuses_other_game(tmp_path, ctx):
    savedir = tmp_path / "s"
    savedir.mkdir()
    (savedir / "a").write_text("x")
    g = _native_game(tmp_path, "pass")
    g.save_paths = [str(savedir)]
    info = backup(g, ctx)
    other = Game(id="other", title="O", platform="pc", kind="native", path=g.path)
    with pytest.raises(ValueError):
        restore(other, ctx, info.path)


def test_data_files_are_consistent(ctx):
    for pid, p in ctx.catalog.platforms.items():
        for b in p.get("backends", []):
            assert b in ctx.catalog.backends, f"{pid} lists unknown backend {b}"
            assert pid in ctx.catalog.backends[b]["platforms"], f"{b} does not declare {pid}"
    for bid, b in ctx.catalog.backends.items():
        assert b["program"].startswith("@") or b["program"] in ctx.catalog.programs, bid
        assert isinstance(b["args"], list)
        assert b.get("tracking") in ("process", "steam", "manual"), bid


def test_install_bundled_copies_out_of_repo(hub_home):
    from ddhub import actions, paths
    lib = Library()
    assert actions.install_bundled(lib) == ["Libbet and the Magic Floor"]
    g = lib.sorted()[0]
    assert Path(g.path).is_file() and str(paths.REPO_DIR) not in g.path  # saves must not land in the repo
    assert Path(g.cover).is_file()
    actions.install_bundled(lib)
    assert len(lib.games) == 1
