# Adding games and platforms

All of this works from a terminal; the hub's Start menu can re-run the imports afterwards.

## Games

| Source | Command | Notes |
|---|---|---|
| Bundled free games | `ddhub install-bundled` | Currently Libbet (Game Boy homebrew, zlib). |
| A folder of game files | `ddhub import-folder D:\Games\GBA` | Platform is detected from unambiguous extensions (`.gba`, `.sfc`, `.nds`...). The folder is remembered. |
| Folders of `.iso/.chd/.cue/.zip` | `ddhub import-folder D:\Games\PS2 --platform ps2` | These formats are used by many systems, so the hub never guesses. |
| Re-scan remembered folders | `ddhub rescan` | Re-imports never create duplicates and never reset favorites, playtime or test results. |
| Steam (installed games) | `ddhub import-steam` | Reads Steam's own manifest files (read-only); launches through the Steam client. |
| Linux installed games | `ddhub import-desktop` | Uses `.desktop` entries in the *Game* category (emulators/launchers excluded). |
| One program or URL | `ddhub add --title "Game" --platform pc --path C:\Games\game.exe` | Add `--arg X` for each argument. |
| Cloud streaming entry | `ddhub add --title "Some Game (Cloud)" --platform cloud --url https://...` | The hub cannot see when a browser session ends; you confirm when done. |

Cover art: put `<same name as the game file>.png/.jpg` next to the file or in a `covers/` folder. No online
scraping is done (metadata services need accounts and their artwork licenses vary).

## After adding: make it Ready

1. `ddhub doctor` lists what each game still needs (emulator, RetroArch core, BIOS file) and the next step.
2. Launch it. After you exit, the hub asks **"Did it play correctly on this machine?"**
   Only a *yes* turns *Untested* into *Ready*. Launching is not playing.
3. Changed something? `ddhub mark <game> works|problems|clear`.

## Per-game options

- Choose the launch method in the game's details (Left/Right on *Launch method*), or set a system-wide default in
  `settings.json` -> `default_backends`, e.g. `{"psx": "duckstation"}`.
- Graphics or other flags: `ddhub set-options "SuperTux" -- --renderer sdl`. They are passed as separate arguments;
  nothing goes through a shell.
- A program in a non-standard place: `ddhub set-program retroarch "D:\Emu\RetroArch\retroarch.exe"`.

## Saves

- After every session the hub zips the game's saves/states into `<hub dir>/backups/<game id>/` (last 10 kept).
- `ddhub backup <game>`, `ddhub backups <game>`, `ddhub restore <game> latest` (add `--states` for emulator save states).
- Restore refuses to overwrite a file newer than the backup unless you pass `--force`, and always makes a
  *pre-restore* backup first. It also refuses a backup made with a different emulator unless forced. Save formats
  are not portable between emulators.
- `settings.json` -> `"retroarch_managed_dirs": true` makes RetroArch keep saves/states/screenshots in the hub's
  folders (via `--appendconfig`; your `retroarch.cfg` is never edited). It is **off by default** so existing saves keep
  loading from where RetroArch already keeps them.
- Native games: add their save folder to the entry's `save_paths` (the catalog does this for SuperTux).

## Platforms and emulators (no code changes)

Definitions live in `ddhub/data/`. To extend without editing them, create files in the hub directory
(`%APPDATA%\DDHub`, `~/.local/share/ddhub`, or `~/Library/Application Support/DDHub`):

`extra_programs.json` - where to find an executable:

```json
{ "vita3k": { "name": "Vita3K", "homepage": "https://vita3k.org/", "license": "GPL-2.0",
              "find": { "windows": ["C:\\Vita3K\\Vita3K.exe"], "linux": ["Vita3K"] },
              "install_hint": "Download Vita3K and install the PS Vita firmware from Sony." } }
```

`extra_backends.json` - how to launch it (argv tokens, never a shell string):

```json
{ "vita3k": { "name": "Vita3K", "kind": "emulated", "program": "vita3k", "platforms": ["vita"],
              "args": ["-r", "{rom}"], "fullscreen_args": ["-F"], "tracking": "process",
              "requires": [{"manual": true, "note": "PS Vita firmware installed in Vita3K"}],
              "features": {} } }
```

`extra_platforms.json` - a new system, or an override of an existing one (the whole entry is replaced).

Placeholders: `{rom}` `{rom_dir}` `{rom_stem}` `{core_path}` `{appid}` `{url}`. Tracking: `process` (waits for the
whole process tree, including children whose launcher exits early), `steam` (watches Steam's running game id),
`manual` (you confirm). Only list a feature (save states, rewind, netplay...) if the backend really has it; the
hub displays exactly what you declare.

Then run `python3 tools/gen_matrix.py` to refresh `docs/compatibility-matrix.md`, and `python3 -m pytest` - one
test checks that every platform, backend and program definition is consistent.
