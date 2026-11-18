# Test results

**Where these tests ran:** a Linux build container. This is **not your gaming computer.** It has no GPU (software
OpenGL, llvmpipe), no audio device and no physical controller, and the display was virtual (Xvfb 1280×720).

| Item | Version |
|---|---|
| OS | Ubuntu 24.04.5 LTS, kernel 6.18.44 (x86_64), 4 CPU threads, 15.7 GiB RAM |
| Python / pygame-ce / SDL | 3.13.18 / 2.5.8 / 2.32.10 |
| RetroArch | 1.18.0 (Ubuntu package `1.18.0+dfsg-1`, Git b2ceb50) |
| mGBA libretro core | 0.10.2 (Ubuntu `libretro-mgba 0.10.2+dfsg-1.1build3`) |
| SuperTux | 0.6.3 (Ubuntu `supertux 0.6.3-2build4`) |
| Libbet ROM | built from source, commit `1232e71`, RGBDS 0.9.4, SHA-256 `71fb43fa…bf71` |

## End-to-end run: 2026-11-18 15:15 UTC, 10/10 passed

The harness is `tools/verify_e2e.py`. It drives the **real hub UI** with real X key events (xdotool) and reads
the hub's state file. Games run from a throwaway HOME and hub directory. Raw output is in
`e2e-results.json`, and the evidence is in `screenshots/`.

| # | Test | Result | Evidence |
|---|---|---|---|
| 1 | Fresh setup, then importing twice (bundled + desktop) | PASS. Two entries and no duplicates | — |
| 2 | Hub navigation by keyboard: grid, tabs, on-screen search, clear | PASS | `01-library`, `02-search` |
| 3 | **Emulated homebrew:** Libbet via RetroArch + mGBA. Launch, play, exit, return | PASS. Window appeared. Idle-vs-input pixel change: Start 0 → 562,500 px, D-pad 0 → 150 px. After the in-game quit the hub took focus back and showed the post-session prompt | `04-*`, `05-*`, `07-libbet-returned` |
| 4 | Confirming "plays correctly" changes Untested → Ready | PASS | `08-libbet-ready` |
| 5 | **Native game:** SuperTux. Launch and in-game input | PASS, with a caveat (below). Title → Story Mode → world map; Tux moved down the map path when Down was pressed. Idle 432,423 px vs input 713,801 px | `09-*`, `10-*` |
| 6 | SuperTux quit through its own menu, hub detects exit and returns | PASS | `12-*`, `13-*` |
| 7 | Persistence after restarting the hub: recent order, playtime, test result | PASS | `14-after-restart` |
| 8 | Game file missing → *Setup required*, UI dialog and CLI message with next step | PASS | `15-missing-file` |
| 9 | Configured emulator path broken → clear error. The hub does **not** silently switch to another emulator | PASS | — |
| 10 | Save backup and restore: emulator save state written via `--appendconfig`, automatic post-session backup, restore refuses to overwrite a newer file, forced restore matches the original bytes, pre-restore safety copy | PASS | — |

Unit tests (`python3 -m pytest`): 19 passed. They cover JSON crash safety, import merging, extension mapping,
desktop and Steam parsing (with fixture files), readiness rules, argv safety with a hostile file name, tracking
a child process whose launcher already exited, quick-crash reporting with log tail, process-tree stop,
save-conflict guards, bundled content copied out of the install directory, data-file consistency, and controller mapping using **synthetic** SDL controller events.

## What these results do *not* show

- **Nothing was tested on your hardware.** Readiness on your PC starts as *Untested* until you play and confirm.
- **SuperTux in-level gameplay is unverified.** Entering a level stalled on the level-intro screen in this
  container under software rendering (CPU pegged by llvmpipe; `--renderer sdl` did not change it). The world map,
  menus, input and exit were verified, but the platforming itself was not. For that reason the run left SuperTux
  *Untested*. The world-map metric is also weaker than Libbet's, because the water is animated even when idle;
  I reviewed those frames visually.
- **No physical controller.** `/dev/uinput` doesn't exist here, so no virtual device could be created either.
  Controller mapping, stick deadzone and repeat, remapping and hot-unplug were tested with synthetic events only.
  The hold-Select+Start quit combo is implemented but untested.
- **Audio** was not tested (no device).
- **Windows and macOS** were not run. Windows-specific code paths (registry `RunningAppID`, `%APPDATA%` paths,
  process groups) are untested.
- **Steam** launching and exit tracking are untested (no Steam client). Only manifest parsing is tested, with fixtures.
- **Streaming** entries (browser / Remote Play / Moonlight) are untested.
- Every emulator other than RetroArch + mGBA: the hub has definitions, but nothing was run.

Re-run on your own machine (Linux/X11): `python3 tools/verify_e2e.py --out docs/test-results`.
On Windows, follow the manual checklist in the main README.
