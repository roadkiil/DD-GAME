# Freely distributable games: test titles, catalog, and licenses

Research date: 2026-11-18. This is engineering research, not legal advice. Before shipping anything to the public, have someone qualified review the "attribution", "NC" and "unclear" rows.

## How this was researched (and its limits)

- **Primary sources:** every license statement below was read from the project's own files. Each repo was shallow-cloned from github.com or gitlab.com at its default-branch HEAD on 2026-11-18, and `LICENSE`, `COPYING`, `README`, `AUTHORS` and `credits` files were read with `git show`. Commit dates are given where they matter.
- **Blocked hosts:** this session's network policy blocked these hosts, so they could **not** be read directly: itch.io (including tangramgames.itch.io), tangramgames.dk, supertux.org, archive.org, codeberg.org, buildbot.libretro.com, gnu.org, the GitHub web UI and the GitHub REST API. Facts from those sites, such as itch.io file names, come only from search-engine snippets and are marked **(unverified: search snippet)**.
- **Ubuntu package versions** come from packages.ubuntu.com, which was reachable.
- **Terms used in the tables:**
  - **Code** means the license of the source code and engine.
  - **Assets** means the license of the art, music, sound, levels and story.
  - **Redistribution** values:
    - `yes`: permissive, with only a notice required.
    - `attribution`: allowed, with the credit and notice duties listed.
    - `copyleft`: allowed, but you must ship or offer the source and keep the same license.
    - `NC`: non-commercial only.
    - `no`: not allowed.
    - `unclear`: not enough information to say.

---

## Priority 1: test titles

### (a) Tobu Tobu Girl (Game Boy, Tangram Games / Simon Larsen)

| Item | Finding | Source |
|---|---|---|
| Code license | **MIT**, "Copyright (c) 2017 Tangram Games" | `LICENSE` in github.com/SimonLarsen/tobutobugirl (HEAD 048a22c, 2019-01-26) |
| Asset license | **CC BY 4.0**, from README: "All assets (images, text, sound and music) are licensed under the Creative Commons Attribution 4.0 International License." | `README.md`, same repo |
| Sound driver in the ROM | mmlgb, **MIT**, "Copyright (c) 2017 Simon Larsen" (git submodule) | github.com/SimonLarsen/mmlgb `LICENSE` |
| Compiler runtime in the ROM | GBDK 2.96a runtime libraries. The license was **not verified**. It is the same toolchain every GBDK homebrew ships, and it is low risk, but it is not documented in the repo. | n/a |
| GitHub releases | **None.** `git ls-remote` shows no tags (only `HEAD`/`master`), so the repo has no GitHub release assets. The README says: "The binaries are provided through itch.io." | `git ls-remote`, README |
| Official ROM download | Official page: **https://tangramgames.itch.io/tobutobugirl**. The game is free / pay-what-you-want, released 2017-12. itch.io downloads go through a button that generates signed, expiring CDN URLs, so **there is no stable official direct URL**. The exact itch file name could not be read because itch.io was blocked. The repo's build output is `tobu.gb` (README: "a rom file `tobu.gb` will be created"). | README; itch page **(unverified: search snippet)** |
| Stable mirror (redistributor) | Homebrew Hub (gbdev/database, GPLv3 project; each entry keeps its own license) hosts the ROM:<br>**https://raw.githubusercontent.com/gbdev/database/master/entries/tobutobugirl/tobu.gb**<br>Commit-pinned: **https://raw.githubusercontent.com/gbdev/database/37d519c998889ee2bbf8942031b56d78342d6e10/entries/tobutobugirl/tobu.gb**<br>The file is 262,144 bytes. SHA-256 `5d3871cae77db2287807e8914fd21f76203e73aa3fec20955489d45cb4571d8f`. Header title `TOBU`, CGB flag 0x00 (DMG only), cart type 0x03 (MBC1+RAM+BATTERY). The entry's `game.json` lists license "MIT", repository SimonLarsen/tobutobugirl and gameWebsite tangramgames.itch.io/tobutobugirl. | gbdev/database `entries/tobutobugirl/game.json`; downloaded and hashed in this session |
| Can we redistribute the ROM? | **Yes, with attribution.** The ROM is compiled MIT code combined with CC BY 4.0 assets, and both permit redistribution, including commercial use. | |
| Required notices | (1) Include the MIT copyright line and permission notice ("Copyright (c) 2017 Tangram Games" plus the MIT text). Also include the mmlgb MIT notice ("Copyright (c) 2017 Simon Larsen").<br>(2) Under CC BY 4.0, credit the creator (Tangram Games; credit names can come from the in-game credits), link to https://creativecommons.org/licenses/by/4.0/, say whether you modified the assets, and apply no DRM or terms that restrict recipients' CC rights.<br>Suggested credit: *"Tobu Tobu Girl © 2017 Tangram Games. Code: MIT License. Assets: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Source: https://github.com/SimonLarsen/tobutobugirl. Unmodified."* | |
| Caveats | The names and logos "Tobu Tobu Girl" and "Tangram Games" are not trademark-licensed. Use them only to identify the game, not to imply endorsement. Tangram sold a physical cartridge edition, which has no bearing on the free ROM's license. | |

**Tobu Tobu Girl Deluxe** (GB/GBC/SGB remaster, 2019)

| Item | Finding |
|---|---|
| Repo | github.com/SimonLarsen/tobutobugirl-dx (HEAD 2019-11-09). No tags, so no GitHub releases. |
| Code / assets | `LICENSE` is **MIT** (Copyright (c) 2017 Tangram Games). README: assets are **CC BY 4.0**, with the same wording as the original. |
| Official download | **https://tangramgames.itch.io/tobu-tobu-girl-deluxe** (the README links `tangramgames.itch.io/tobutobugirldx`). The itch file is listed as `tobudx.gb`, 256 kB **(unverified: search snippet)**. |
| Mirror | https://raw.githubusercontent.com/gbdev/database/37d519c998889ee2bbf8942031b56d78342d6e10/entries/tobutobugirldeluxe/tobudx.gb<br>262,144 bytes, SHA-256 `0a0e8018dbbc8d7f8cd99f05e7cdc7b4cc9e358ecfe9377ebfb2291a84c6e310`. Header `TOBUDX`, CGB flag 0x80 (dual-mode), SGB flag 0x03. |
| Conflict to note | An Internet Archive upload (archive.org/details/tobudx) is reported to label the game "CC BY-ND 4.0" **(unverified: search snippet; uploader-supplied metadata)**. The authoritative statement is the developer's README, which says CC BY 4.0. If in doubt, ship it unmodified, which satisfies both. |
| Verdict | **Redistributable with attribution**, with the same notices as the original. |

Recommendation: use **Tobu Tobu Girl (DMG)** as the GB test title and **Deluxe** as the GBC/SGB test title. Pin the ROMs by SHA-256. Ship a `LICENSE-tobutobugirl.txt` containing the MIT text, the mmlgb MIT text and the CC BY 4.0 credit line.

### (b) SuperTux (native, github.com/SuperTux/supertux)

| Item | Finding |
|---|---|
| Code license | **GPLv3**. `LICENSE.txt` is GPL v3. README: "`LICENSE.txt` - The GNU General Public License, under whose terms SuperTux is licensed. (Most of the data subdirectory is also licensed under CC-by-SA)". The same wording appears at tag v0.6.3. |
| Asset licensing | Mixed, and documented per file in `data/AUTHORS`.<br>The main licenses are GPLv2+ and CC BY-SA, often dual-licensed. For example: "All files in data/music created by wansti and licensed under GPLv2+CC-by-sa, unless stated otherwise". Individual files are CC BY 3.0, CC BY-SA 3.0/4.0, CC0 or GPLv3+.<br>Levels: "The license should be include in the file itself… Contrib levels are so old that they have no specific license, but they should be redistributable along with the rest of SuperTux." The contrib levels are therefore **formally unclear, but the project intends them to be redistributed**.<br>Fonts are under their own licenses in `data/fonts/*LICENSE*` (Noto Sans, Roboto, Source Code Pro, Varela Round, Dekko, Mapo Backpacking). |
| Release-specific flag | **v0.7.0** (tag dated 2026-03-15, also current master) adds two **CC BY-NC 4.0** items to `data/AUTHORS`: `images/objects/conveyor_belt/*` and `sounds/kill.wav` ("submitted by RodirodDude CC BY-NC 4.0").<br>**v0.6.3** (tag 2021-12-22) has **no NC entries**.<br>So 0.7.x contains non-commercial assets. Redistributing 0.7.x commercially (for example in a paid product or bundle) is not cleanly allowed. 0.6.3 is the cleaner choice. |
| Ubuntu packages | 22.04 jammy `0.6.3-1`; **24.04 noble `0.6.3-2build4`**; 26.04 resolute `0.6.3-5`; 26.10 `0.6.3-5build1` (universe). Ubuntu still ships **0.6.3**, so using the distro package avoids the 0.7 NC assets. |
| Redistribution | **Copyleft + attribution**. Ship or offer the GPL source, include `LICENSE.txt` and `data/AUTHORS`/`data/credits.stxt`, and keep CC BY-SA attributions. If you install the Ubuntu package, Debian's `/usr/share/doc/supertux/copyright` already covers this. |

---

## Priority 2a: native open-source PC games

| Game | Official URL | Code license | Asset license | Redistribution | Ubuntu 24.04 (noble) | Notes |
|---|---|---|---|---|---|---|
| SuperTux | supertux.org | GPLv3 | GPLv2+/CC BY-SA mix (per-file `data/AUTHORS`); 0.7.x adds CC BY-NC items | copyleft + attribution (0.6.3); **NC caveat for 0.7.x** | 0.6.3-2build4 | See section 1(b) |
| SuperTuxKart | supertuxkart.net | GPLv3+ (`COPYING`) | "mixture of licenses including … GNU GPL, CC-BY, CC-BY-SA, Public Domain"; see the `licenses.txt` files throughout `data/` | copyleft + attribution | 1.4+dfsg-3ubuntu1 | Most track and kart data lives in a separate assets repo (stk-assets), which has its own `licenses.txt` files; those were not audited here. Debian strips some data ("+dfsg"). |
| 0 A.D. | play0ad.com | GPLv2+ (`source/`); MIT (`source/lib/`) | **CC BY-SA 3.0** (`mods/*/art`, `mods/*/audio`). Attribution must name "Wildfire Games", link wildfiregames.com and link the license. Maps have their own LICENSE. | copyleft + attribution | **not in noble** (jammy 0.0.25b-2; resolute 0.28.0-3) | `LICENSE.txt` flags `binaries/system/dbghelp.dll` as **proprietary** (Windows only); don't redistribute it. The github.com/0ad/0ad mirror's last commit is 2024-08-17, because development moved to Wildfire's Gitea. |
| OpenTTD + OpenGFX/OpenSFX/OpenMSX | openttd.org | GPLv2 (`COPYING.md`); squirrel is zlib | OpenGFX **GPLv2**; OpenSFX **CC BY-SA 3.0** (sounds), other files GPLv2+/CDDL 1.1; OpenMSX **GPLv2** | copyleft (+ BY-SA attribution for OpenSFX) | openttd 13.4-1build3; openttd-opengfx 7.1-1 | Never bundle the original TTD data files. Use the Open* sets only. |
| Mindustry | mindustrygame.github.io (Anuken/Mindustry) | GPLv3 (`LICENSE`) | No separate asset license, so the repo-wide GPLv3 applies to the sprites in the repo | copyleft | not packaged | Sold on Steam, free on itch and GitHub. The GPL allows redistributing our own builds. Trademark and name use is not licensed. |
| Xonotic | xonotic.org | GPLv3+ (game); DarkPlaces engine GPLv2+ | `COPYING`: "All source files (as defined by the respective license) in scope … are under the GPL version 3 or any later version", which covers data too. It applies only to official releases and Team-owned branches. | copyleft | **not packaged** | Automatically downloaded maps from servers are explicitly *not* covered by these terms. Disable autodownload, or treat such maps as `unclear`. |
| Battle for Wesnoth | wesnoth.org | GPLv2+ | Mostly GPLv2+. README: "new contributions are now licensed under the Creative Commons BY-SA v4.0". Per-file register in `copyrights.csv` (343 GPLv2+, 48 CC BY-SA 4.0, 5 CC0 rows). | copyleft + attribution | 1:1.16.11-1build3 | Some campaigns carry their own LICENSE (for example, Heir_To_The_Throne is GPLv3). |
| Pingus | pingus.github.io | GPLv3+ (README: "licensed under the GPLv3+") | Covered by GPLv3+; per-author credits in `AUTHORS` (music by several artists) | copyleft | 0.7.6-6build2 | A Lemmings-like game. Don't use "Lemmings" trademarks in marketing. |
| Neverball / Neverputt | neverball.org | GPLv2+ (`LICENSE.md`) | GPLv2+, with exceptions: DejaVu font, WenQuanYi font (Apache-2.0/GPLv3), **Octocat ball used "with permission from Github"**, miniz MIT | copyleft | 1.6.0+git20180603-3build2 | Remove the Octocat ball, or treat it as permission-only content. |
| Luanti (formerly Minetest) | luanti.org | **LGPL-2.1+** (`LICENSE.txt`); IrrlichtMt is zlib | Engine textures and sounds **CC BY-SA 3.0** (some CC BY-SA 4.0, Apache-2.0, CC BY 4.0) | copyleft + attribution | minetest 5.6.1 (renamed `luanti` 5.10 in resolute) | The engine ships only devtest. Pair it with Minetest Game (below). |
| Minetest Game | github.com/luanti-org/minetest_game | LGPL-2.1 | CC BY-SA 3.0 base; per-mod `license.txt` (CC BY 3.0, CC0, …) | copyleft + attribution | bundled in Debian/Ubuntu `minetest-data`/`minetest-game` | |
| Veloren | veloren.net | GPLv3 | GPLv3 by default; `assets/credits.ron` lists exceptions ("Can be omitted, but assumed to be GPL3 if not provided") | copyleft + attribution | not packaged | Heavy (Rust, about 1 GB of assets). Multiplayer-centric. |
| Frogatto & Friends | frogatto.com | Anura engine C++ `src/` is **zlib** | **Mixed, includes NC.** CC BY 3.0 by default, but `data/levels`, `images/characters`, `images/tiles`, `sounds` and `music` are **CC BY-NC-SA 4.0**, as are the story, character designs and names. | **NC**: non-commercial redistribution only, with attribution and share-alike | frogatto 1.3.1+dfsg-6build4 (Debian ships it in non-free/contrib-style packaging) | **Flag.** Don't include it in any commercial bundle. A free hub is OK if it is clearly non-commercial; get legal sign-off. |

## Priority 2b: homebrew ROMs for emulated systems

| Title | Platform | Official URL / ROM source | Code license | Asset license | Redistribution | Notes |
|---|---|---|---|---|---|---|
| Tobu Tobu Girl | GB | tangramgames.itch.io/tobutobugirl; mirror `gbdev/database/entries/tobutobugirl/tobu.gb` | MIT | CC BY 4.0 | **attribution** | Test title. See 1(a). |
| Tobu Tobu Girl Deluxe | GB/GBC/SGB | tangramgames.itch.io/tobu-tobu-girl-deluxe; mirror `…/tobutobugirldeluxe/tobudx.gb` | MIT | CC BY 4.0 | **attribution** | See 1(a). |
| µCity (uCity) | GBC | github.com/AntonioND/ucity (now codeberg.org/SkyLyrac/ucity); mirror `gbdev/database/entries/ucity/ucity.gbc` | GPLv3+ (only files with the GPL header); GBT Player BSD-2 | **CC BY-SA 4.0** (graphics, music) | **copyleft + attribution** | Tags v1.0–v1.3. Ship the source link (the README asks for it). |
| µCity Advance | GBA | github.com/AntonioND/ucity-advance | GPL-3.0-only | Art **CC BY-NC-SA 4.0**; music is mostly Mod Archive Distribution License (per-file txt), others CC BY-NC-SA 4.0 | **NC** | Flag NC. |
| Geometrix | GB/GBC | github.com/AntonioND/geometrix (prebuilt `geometrix.gbc` is committed in the repo); mirror in gbdev/database | GPLv3+ | No separate asset license, so GPLv3+ applies to the repo | **copyleft** | Small (32 KB). A good second GBC test ROM. |
| Libbet and the Magic Floor | GB (SGB/GBC enhanced) | github.com/pinobatch/libbet; mirror `gbdev/database/entries/libbet/libbet.gb` | **zlib** (© 2002, 2012 Martin Korth; © 2018, 2024 Damian Yerrick) | Covered by the repo's zlib grant (no separate asset license) | **yes** (zlib: don't misrepresent origin; keep the notice in source distributions) | A port of Martin Korth's Magic Floor, with permission implied by the copyright line. |
| 2048-gb | GB | github.com/Sanqui/2048-gb; mirror in gbdev/database (`2048.gb`) | zlib (© 2014 "Sanqui") | README: "Tile graphics made by beware of bgb fame"; no separate license given | **unclear** for the graphics (the code is zlib) | 2048 game design is MIT (Cirulli). Ask the author or treat it as low risk. |
| Thwaite | NES | github.com/pinobatch/thwaite-nes | GPLv3+ (some files zlib-like) | Same repo, same license | **copyleft** | A Missile Command-like game. Unlike Concentration Room, it has no binary-only exception in its README, so ship or offer the source. |
| Concentration Room | NES | github.com/pinobatch/croom-nes | GPLv3+, **plus a special exception**: "you may copy and distribute exact copies of the program, as published by Damian Yerrick, in iNES or UNIF executable form without source code" | Same | **yes** for exact copies (no source needed) | The best NES test candidate on licensing. |
| Super Tilt Bro | NES | github.com/sgadrat/super-tilt-bro; ROM at sgadrat.itch.io/super-tilt-bro | WTFPL v2 (repo-wide) | The repo claims WTFPL, but in-game credits show **third-party characters and music**: Kiki (Krita, Tyson Tan), Pepper (Pepper&Carrot, David Revoy), Sinbad (Ogre3D), music by Ozzed and others. Their original licenses are not documented in the repo. | **attribution (likely), partly unclear** | Kiki, Pepper and Ozzed's music are generally CC-licensed upstream. This was not verified here, so keep the in-game credits intact. |
| Nova the Squirrel | NES | github.com/NovaSquirrel/NovaTheSquirrel | GPLv3+ | **CC BY-NC-SA 4.0**. "Permission is not granted to use the character … of Nova in anything else." | **NC** | Also: "Do not involve this game with AI-assisted projects. I do not want it to be used to demo or promote anything that was not 100% made by humans." **Exclude** to respect the author's stated wishes. |
| Nova the Squirrel 2 | SNES | github.com/NovaSquirrel/NovaTheSquirrel2 | GPLv3 | **All rights reserved** (character designs, PNGs, levels, story) | **no** | **Exclude.** |
| snes-platformer-example | SNES | github.com/NovaSquirrel/snes-platformer-example | MIT (© 2022 NovaSquirrel) | OpenGameArt: Kenney 16x16 (CC0) and GrafxKid "Today Land" characters (OGA license not re-verified here) | **attribution** | A tech demo rather than a full game. A good SNES smoke-test ROM, but you must build it yourself. |
| Butano Fighter | GBA | github.com/GValiente/butano `games/butano-fighter`; ROM at gvaliente.itch.io/butano-fighter | zlib (Butano) plus MIT/zlib/PD libraries | Graphics CC0 / CC BY-SA 3.0. **Music includes "Attribution Non-commercial Share Alike" (5 tracks) and one "Attribution Non-commercial No Derivatives" track**, plus CC BY 4.0 and CC0. | **NC + attribution**; no-derivatives on one track (unmodified ROM only) | Flag NC. |
| Varooom 3D | GBA | github.com/GValiente/butano `games/varooom-3d`; gvaliente.itch.io/varooom-3d | zlib | Graphics, music, SFX and voices mostly **CC BY-NC-SA 4.0** (plus Apache-2.0, OFL, Unsplash) | **NC** | Flag NC. |
| Anguna: Warriors of Virtue | GBA | Bite the Chili / Nathan Tolbert; gauauu.itch.io/anguna (`anguna.zip`, 714 kB, **unverified: search snippet**) | Not open source (GameBrew lists license "Mixed") | Proprietary freeware | **free to download, redistribution unclear** | Also sold on cartridge (Piko Interactive). Link out to itch; **don't rehost**. |
| Cave Story MD | Genesis/MD | github.com/andwn/cave-story-md | MIT (engine); GPLv3 (`src/ai/`) | **Art and story: "Property of Studio Pixel … I used them without permission"**. Music covers CC BY-NC. Some fonts are "for personal product FREE". | **no / unclear** | **Exclude.** |
| Paper-io Genesis | Genesis/MD | github.com/TomAwezome/paper-io-genesis (ROM in GitHub releases) | GPLv3 | Repo-wide GPLv3 | **copyleft**, but **trademark risk** | "Paper.io" is a Voodoo trademark. Avoid it in a curated catalog, or rename it in the UI. |
| Micro Mages, Xeno Crisis, Goodboy Galaxy, etc. | NES/MD/GBA | — | proprietary | proprietary | **no (commercial)** | **Exclude.** These are commercial homebrew. |

### Catalog sources and indexes (for finding more titles)

- **Homebrew Hub / gbdev database** (github.com/gbdev/database, project GPLv3). Holds 1,371 GB/GBC entries as of 2026-11-17, each with `game.json` (a `license` or `gameLicense` field) and the ROM file in git. This makes it the most practical stable mirror: ROMs are fetched over raw.githubusercontent.com and can be pinned by commit. Its README says: "Each game, homebrew, demo and their related asset … is released under different license terms … Please refer to the single entries for details." **Verify each entry against its upstream repo, as done above**, because the `license` field often names only the code license (it says "MIT" for Tobu Tobu Girl and leaves out CC BY 4.0).
- **RetroArch "Content Downloader"**: this fetches from `buildbot.libretro.com/assets/cores/<system>/` (per the `core_updater_buildbot_assets_url` setting). The server was blocked, so its contents and per-item licenses could **not** be verified. Treat each item as **unclear** until its own readme is read. Don't mirror the whole set.
- **PDRoms (pdroms.de)**: blocked in this session. "PD" on that site is a historical label, not a legal guarantee; many entries are freeware without a redistribution grant. Treat entries as **unclear** unless the entry carries an explicit license.
- **itch.io homebrew**: being free to download does **not** imply the right to redistribute. Rehost only titles whose page or repo states an open license; otherwise link to the itch page.

---

## Emulator and tooling licenses (what to ship if we bundle)

| Component | License (verified file) | If we redistribute binaries |
|---|---|---|
| RetroArch | **GPLv3** (`COPYING`); the libretro API header is MIT | Provide the corresponding source, or a written offer, for the exact version shipped. Include GPLv3 text. Our launcher must not link GPL code into a proprietary binary; running it as a separate process is fine. **Flag:** `media/icons/LICENSE/LICENSE.txt` says the Android Material icon-generator icons are **CC BY-NC 3.0**. Those are Android-port assets; don't ship them in a commercial product. The separate `retroarch-assets` repo (themes) was not audited. |
| mGBA (standalone) | **MPL-2.0** (`LICENSE`). Bundled third-party code: inih (BSD-3), LZMA SDK (PD), MurmurHash3 (PD), getopt-MSVC (PD), SQLite3 (PD) | MPL is file-level copyleft: if you modify any MPL file, make that file's source available. Include the MPL text and the inih BSD-3 notice. The README offers separate commercial licensing ("licensing@mgba.io"); we don't need it. |
| libretro mgba core (github.com/libretro/mgba) | **MPL-2.0** (same `LICENSE`; HEAD 2026-09-16) | Same as mGBA. Ubuntu packages it as `libretro-mgba` 0.10.2 (noble). |
| pygame-ce | **LGPL-2.1-or-later** (README "License Identifier: LGPL-2.1-or-later"; text in `docs/LGPL.txt`) | Ship pygame-ce as a replaceable dynamic library or package (normal pip/wheel layout satisfies this). Include the LGPL text and the bundled-library licenses from `docs/licenses/`: SDL2, SDL2_image, SDL2_mixer, freetype, harfbuzz, libpng, libjpeg, zlib, ogg/vorbis, opus, FLAC, mpg123, portmidi, libtiff, webp, wavpack, xmp, fluidsynth, and others. Wheels bundle these, so their notices must go out with the wheel. |
| SDL2 | **zlib** (`LICENSE.txt`, © 1997-2026 Sam Lantinga; the master branch is SDL3, also zlib; latest SDL2 tag seen is `release-2.32.8`) | No notice is required in binary distributions; acknowledgment is "appreciated but not required". Keep the notice in any source distribution and mark altered sources. Ubuntu noble ships `libsdl2-2.0-0` 2.30.0. |

**Suggested bundle hygiene:**
- Ship a `THIRD_PARTY_NOTICES/` directory with one file per game and per tool: license text, copyright line, source URL and the exact version or SHA-256.
- Show game credits in the hub's "About this game" panel. This also satisfies CC BY "reasonable manner" attribution.
- Keep NC titles (Frogatto, µCity Advance, Butano Fighter, Varooom 3D, SuperTux 0.7.x NC items) behind a `non_commercial: true` flag so they can be dropped from any commercial build.

---

## Sources (accessed 2026-11-18)

Primary files read from cloned repositories (default branch HEAD unless a tag is named):

- https://github.com/SimonLarsen/tobutobugirl: `LICENSE`, `README.md` (HEAD 048a22c2, 2019-01-26); `git ls-remote` showed no tags
- https://github.com/SimonLarsen/tobutobugirl-dx: `LICENSE`, `README.md` (HEAD 4985d4d2); no tags
- https://github.com/SimonLarsen/mmlgb: `LICENSE`
- https://github.com/gbdev/database: `README.md`, `LICENSE`, `entries/{tobutobugirl,tobutobugirldeluxe,ucity,libbet,geometrix,2048gb}/game.json` (HEAD 37d519c9, 2026-11-17); ROMs downloaded via raw.githubusercontent.com and hashed
- https://github.com/SuperTux/supertux: `LICENSE.txt`, `README.md`, `data/AUTHORS` at HEAD, `v0.6.3` and `v0.7.0`
- https://github.com/supertuxkart/stk-code: `COPYING`, `README.md`, `data/CREDITS`
- https://github.com/0ad/0ad: `LICENSE.txt`, `binaries/data/mods/public/{art,audio}/LICENSE.txt`
- https://github.com/OpenTTD/OpenTTD (`COPYING.md`, `README.md`), https://github.com/OpenTTD/OpenGFX, https://github.com/OpenTTD/OpenSFX, https://github.com/OpenTTD/OpenMSX (`LICENSE`, `README.md`)
- https://github.com/Anuken/Mindustry: `LICENSE`, `README.md`
- https://gitlab.com/xonotic/xonotic: `COPYING`
- https://github.com/wesnoth/wesnoth: `copyright`, `COPYING`, `data/COPYING.txt`, `copyrights.csv`, `README.md`
- https://github.com/Pingus/pingus: `LICENSE.txt`, `README.md`, `AUTHORS`
- https://github.com/Neverball/neverball: `LICENSE.md`
- https://github.com/frogatto/frogatto: `LICENSE`
- https://gitlab.com/veloren/veloren: `LICENSE`, `README.md`, `assets/credits.ron`
- https://github.com/luanti-org/luanti (`LICENSE.txt`), https://github.com/luanti-org/minetest_game (`LICENSE.txt`, `mods/default/license.txt`)
- https://github.com/AntonioND/ucity (`readme.rst`, tags), https://github.com/AntonioND/ucity-advance (`readme.rst`, `licenses/`), https://github.com/AntonioND/geometrix (`readme.rst`)
- https://github.com/pinobatch/libbet (`LICENSE`, `README.md`), https://github.com/pinobatch/thwaite-nes (`LICENSE.txt`, `README.md`), https://github.com/pinobatch/croom-nes (`LICENSE.txt`, `README.md`)
- https://github.com/Sanqui/2048-gb: `LICENSE`, `README.md`
- https://github.com/sgadrat/super-tilt-bro: `LICENSE`, `README.md`, `game/data/menu_credits/credits.asm`
- https://github.com/NovaSquirrel/NovaTheSquirrel, https://github.com/NovaSquirrel/NovaTheSquirrel2, https://github.com/NovaSquirrel/snes-platformer-example: `LICENSE.txt`, `README.md`
- https://github.com/GValiente/butano: `LICENSE`, `README.md`, `games/*/credits/*.txt`
- https://github.com/andwn/cave-story-md: `README.md`, `doc/LICENSE.md`
- https://github.com/TomAwezome/paper-io-genesis: `LICENSE`, `README.md`
- https://github.com/libretro/RetroArch: `COPYING`, `media/icons/LICENSE/LICENSE.txt`
- https://github.com/mgba-emu/mgba and https://github.com/libretro/mgba: `LICENSE`, `README.md`
- https://github.com/pygame-community/pygame-ce: `README.rst`, `docs/licenses/`
- https://github.com/libsdl-org/SDL: `LICENSE.txt`, tags

Package data:
- https://packages.ubuntu.com/search?keywords=supertux&searchon=names&exact=1&suite=all&section=all (and the same query for supertuxkart, 0ad, openttd, openttd-opengfx, wesnoth, pingus, neverball, frogatto, minetest, luanti, retroarch, mgba-qt, libretro-mgba, libsdl2-2.0-0, python3-pygame)

Search-engine snippets only (pages blocked in this session; treat as unverified):
- https://tangramgames.itch.io/tobutobugirl
- https://tangramgames.itch.io/tobu-tobu-girl-deluxe
- https://tangramgames.dk/tobutobugirl/ and https://tangramgames.dk/tobutobugirldx/
- https://archive.org/details/tobudx
- https://gauauu.itch.io/anguna and https://gamebrew.org/wiki/Anguna_Warriors_of_Virtue_GBA
- https://github.com/NickHeap2/retroarch-asset-server (describes the Content Downloader protocol)
