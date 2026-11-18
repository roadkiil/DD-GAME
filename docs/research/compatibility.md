# Emulator & Execution Compatibility Map

Research date: **2026-11-18**. Scope: what a unified gaming hub (launcher) could run locally on a mid-range Windows PC, and which legal streaming/port options cover systems where local emulation is not suitable.

## Read this first

- **Nothing in this document has been tested on the user's hardware.** Every "tier" and "status" below is **upstream-reported** (from the project's own repo, site, compatibility list or official vendor page) or, where marked, **secondary** (press / wiki). Treat tiers as a planning aid, not a guarantee.
- **How the facts were gathered.**
  - *Directly observed (2026-11-18):* repository existence, latest commit date, latest tags and LICENSE/README text were read straight from the official GitHub repos (shallow `git clone` / `git ls-remote`). These rows are tagged `[repo]`.
  - *Upstream page via search index:* many official project/vendor sites (rpcs3.net, pcsx2.net, cemu.info, xemu.app, vita3k.org, playstation.com, xbox.com, nvidia.com, nintendo.com, git.eden-emu.dev, git.ryujinx.app) were **not reachable from this research sandbox**, so their content was read through search-engine snippets of those exact official pages. Tagged `[upstream-snippet]`. Re-check before relying on exact numbers.
  - *Secondary:* press or the Emulation General wiki. Tagged `[secondary]`. Several SEO "2026 guide" sites returned contradictory and probably fabricated details (version numbers, dates); they were **not used** as sources.
  - Anything that could not be confirmed is written **unverified**.
- **Legal baseline (applies to every row).** BIOS/firmware/keys/game images must be **dumped by the user from hardware and media they own**. The launcher must never bundle, download or link to BIOS, firmware, keys or ROMs. Where a vendor publishes firmware itself (PS3, PS Vita system software from Sony's servers), the launcher may point the user to the official vendor download page. Laws on circumvention differ by country (e.g. US DMCA §1201); this is not legal advice.
- **Assumed "mid-range Windows PC"** for the priority column: Windows 10/11 x64, 6-core/12-thread CPU with AVX2 (e.g. Ryzen 5 5600 / Core i5-10400 class, which is exactly RPCS3's "recommended" tier), 16 GB RAM, GPU with Vulkan 1.3 and D3D12 (RTX 2060 / RX 5600 XT class or newer), SSD.

### Tier legend (synthesised from upstream-reported status)

| Tier | Meaning |
|---|---|
| **mature** | Upstream reports near-complete library compatibility; long-stable project. |
| **good** | Most of the library playable per upstream; some titles need per-game settings. |
| **partial** | A meaningful subset playable; many titles in-game with issues. |
| **experimental** | Few titles playable; project itself says expect crashes/low compatibility. |
| **unsupported** | No usable emulator; use official/legal alternatives. |

### Priority legend (for a mid-range Windows PC)

| Priority | Meaning |
|---|---|
| **P1** | Integrate first: mature, low-friction, permissive enough to launch as an external app. |
| **P2** | Integrate next: good results but heavier setup (firmware, keys, per-game config) or heavier hardware. |
| **P3** | Optional / advanced users only: partial, experimental, legally contentious, or niche. |
| **Stream** | Prefer official ports or streaming (see streaming table). |

### Licensing notes that affect a launcher

- Launching an emulator as a separate, user-installed executable is the lowest-risk integration (no redistribution).
- **DuckStation is CC BY-NC-ND 4.0** `[repo]`: non-commercial, no derivatives. Do not bundle or ship modified builds; launch a user-installed copy only.
- **FinalBurn Neo** and **Genesis Plus GX** carry **non-commercial** licenses `[repo]`. Same advice.
- GPL emulators can be bundled only with full GPL compliance (source offer etc.). MPL-2.0 (Cemu, mGBA) and ISC (ares) are more permissive.

---

## Nintendo

| Platform | Candidate emulator(s) (standalone / libretro core) | Official project & compatibility list | License | Hardware notes | User-provided files | Important limitations | Tier (upstream-reported) | Priority | Source |
|---|---|---|---|---|---|---|---|---|---|
| NES / Famicom | **Mesen2** (standalone); libretro: Mesen, FCEUmm, Nestopia UE | github.com/SourMesen/Mesen2 (no formal list; accuracy-focused) | GPL-3.0 `[repo]` | Any modern PC | None (FDS needs `disksys.rom` BIOS) | Mesen2 last commit 2026-06-04, tag 2.1.1 `[repo]`; still the reference accuracy emulator but update cadence slowed | mature | P1 | [Mesen2](https://github.com/SourMesen/Mesen2) |
| SNES / Super Famicom | **bsnes** (standalone), **ares** (multi-system), **Mesen2**; libretro: bsnes, Snes9x | github.com/bsnes-emu/bsnes; github.com/ares-emulator/ares | bsnes GPL-3.0; ares ISC `[repo]` | Any modern PC; bsnes/ares accuracy cores want a faster CPU | None (some enhancement-chip games need DSP/coprocessor firmware dumps for ares/bsnes) | bsnes tag v115, last commit 2026-10-07; ares v148, active 2026-11-18 `[repo]` | mature | P1 | [bsnes](https://github.com/bsnes-emu/bsnes), [ares](https://github.com/ares-emulator/ares) |
| Nintendo 64 | **gopher64** (standalone), **RMG** (Rosalie's Mupen GUI, mupen64plus-based), **ares**; libretro: Mupen64Plus-Next, ParaLLEl-N64 | github.com/gopher64/gopher64; github.com/Rosalie241/RMG | GPL-3.0 (both) `[repo]` | Vulkan GPU recommended for ParaLLEl-RDP-style accurate rendering (unverified per-project) | None | gopher64 v1.2.1, active 2026-11-18; RMG v0.9.1, 2026-11-04 `[repo]`. simple64 repo no longer publicly reachable on GitHub (clone failed) — treat as discontinued/unverified | good | P1 | [gopher64](https://github.com/gopher64/gopher64), [RMG](https://github.com/Rosalie241/RMG) |
| GameCube | **Dolphin** (standalone); libretro: Dolphin core (lags upstream) | dolphin-emu.org; wiki.dolphin-emu.org per-game pages | GPL-2.0-or-later `[repo]` | x86-64 or ARMv8; D3D11.1/OpenGL 3.3 min, D3D11.1/OpenGL 4.4 recommended; D3D/D3D12/OGL/Vulkan backends `[repo]` | None required (IPL/BIOS optional) | Latest tags 2609 / 2609a / 2609b (Sept 2026 release line), active 2026-11-18 `[repo]` | mature | P1 | [Dolphin README](https://github.com/dolphin-emu/dolphin) |
| Wii | **Dolphin** | as above | GPL-2.0-or-later | as above; Wii Remote needs Bluetooth passthrough or emulated input | None for most games; NAND/system menu dump optional | Online services gone (third-party revivals out of scope) | mature | P1 | [Dolphin](https://github.com/dolphin-emu/dolphin) |
| Wii U | **Cemu** (standalone) | cemu.info; compat list wiki.cemu.info | MPL-2.0 `[repo]` | 64-bit Win/Linux/macOS; GPU OpenGL 4.5 or Vulkan 1.1/1.2 (sources differ), 4 GB RAM min, 8 GB rec. `[upstream-snippet]`; macOS build "purely experimental" `[repo]` | Encrypted WUD/WUX need per-game keys in `keys.txt` from the user's own dump; online play needs files dumped from own console `[upstream-snippet]` | v2.6 latest tag; active 2026-11-13 `[repo]` | good | P2 | [Cemu README](https://github.com/cemu-project/Cemu), [Cemu wiki](https://wiki.cemu.info/wiki/Main_Page) |
| Switch (1) | **Ryubing** (Ryujinx fork, C#), **Eden** (yuzu-lineage, C++), Kenji-NX, Citron (yuzu fork) | Ryubing: git.ryujinx.app (self-hosted Forgejo); Eden: git.eden-emu.dev | Ryujinx/Ryubing MIT (inherited, unverified for fork); Eden GPL-3.0-or-later (per SPDX headers seen in derived Lichii repo) | Vulkan GPU; Eden publishes a "Zen 4 or newer" optimised build plus generic builds `[upstream-snippet]` | `prod.keys` + firmware dumped from own Switch (required) | **Legal risk is the defining factor.** yuzu & Citra shut down (2024, Tropic Haze settlement); Ryujinx ceased Oct 2024; yuzu/citra GitHub repos are gone (clone fails `[repo]`). Nintendo DMCA notices to GitHub on 2026-02-12 named Citron, Eden, Kenji-NX, MeloNX, Pine, Pomelo, **Ryubing**, Ryujinx, Skyline, Sudachi, Sumi, Suyu, yuzu; further notices 2026-03-27 (Citron/Eden/forks), 2026-09-30 (Ryujinx-linking repos), 2026-11-06 (Citron Neo, 71 repos disabled). Ryubing moved off GitHub to self-hosted Forgejo; canary builds listed into late Aug 2026, stable 1.3.x `[upstream-snippet]` — current release **unverified** (host blocked). Eden: stable v0.2.0 dated 2026-05-13 on its releases page, commits to 2026-11-16 `[upstream-snippet]`; later version numbers seen only on unreliable sites → **unverified**. Citron (citron-neo) GitHub org disabled after the Nov 2026 notice | partial→good per upstream claims (Eden says "most commercial games at full speed"); **legally contested** | P3 (user-installed only; do not bundle, link to downloads, or help obtain keys) | [GitHub DMCA 2026-02-12](https://github.com/github/dmca/blob/master/2026/02/2026-02-12-nintendo.md), [2026-11-06](https://github.com/github/dmca/blob/master/2026/11/2026-11-06-nintendo-4.md), [2026-09-30](https://github.com/github/dmca/blob/master/2026/09/2026-09-30-nintendo.md), [Ryubing Forgejo](https://git.ryujinx.app/projects/Ryubing), [Eden releases](https://git.eden-emu.dev/eden-emu/eden/releases), [VGC](https://www.videogameschronicle.com/news/nintendo-issues-dmca-takedown-on-more-switch-emulators-but-at-least-one-is-fighting-back/) |
| Switch 2 | **Lichii** (Eden/yuzu-derived fork, "VERY experimental"); Eden-NX2/NS2 (reported discontinued); pound (research project) | github.com/zortos293/Lichii; compat site lichii.zortos.me | GPL-3.0-or-later (SPDX) `[repo]` | Windows builds; high-end GPU implied (unverified) | Switch 2 keys/firmware + game dumps from own console; requires a console exploit to dump (legally fraught) | Lichii: tags nx2-build-15…34, commit 2026-11-18 `[repo]`; README: "experimental … rendering errors, stutters and crashes remain possible", no frame-rate guarantees. Press reports a commercial title (Zelda: OoT remake) booting at 20–60 fps with visual errors `[secondary]`. Extremely high DMCA exposure (Eden lineage) | experimental | **Stream/none**: no official cloud or remote play; use console. Do not integrate | [Lichii](https://github.com/zortos293/Lichii), [Notebookcheck](https://www.notebookcheck.net/Zelda-Ocarina-of-Time-remake-runs-on-PC-with-Switch-2-emulator-before-release-date.1442531.0.html), [Tom's Hardware](https://www.tomshardware.com/video-games/nintendo/nintendos-latest-zelda-remake-already-circulating-online-as-a-switch-2-rom-openai-assisted-software-jailbreak-new-game-dumper-let-pirates-share-game-for-free-immediately-following-release) |
| Game Boy / GBC / GBA | **mGBA** (standalone); libretro: mGBA, Gambatte, SameBoy | github.com/mgba-emu/mgba | MPL-2.0 `[repo]` | Any PC | None (HLE BIOS built in; real BIOS optional) | mGBA 0.10.5 latest stable tag, active 2026-11-18 `[repo]` | mature | P1 | [mGBA](https://github.com/mgba-emu/mgba) |
| DS / DSi | **melonDS** (standalone); libretro: melonDS DS, DeSmuME | github.com/melonDS-emu/melonDS | GPL-3.0 `[repo]` | Any modern PC; OpenGL for upscaling | DS: none required (FreeBIOS) — real BIOS/firmware improve compatibility; DSi mode needs BIOS + NAND dump (unverified detail) | v1.1 latest tag, active 2026-11-04 `[repo]` | mature (DS) / partial (DSi) | P1 | [melonDS](https://github.com/melonDS-emu/melonDS) |
| 3DS | **Azahar** (Citra successor, merged Lime3DS/PabloMK7 forks); Panda3DS (alt, earlier stage) | github.com/azahar-emu/azahar; list github.com/azahar-emu/compatibility-list | Azahar GPL-3.0; Panda3DS GPL-3.0 `[repo]` | Win10 x64 / macOS 13.4 / Linux; **x86-64 with SSE4.2**; GPU OpenGL 4.3 or Vulkan 1.1; 2 GB RAM (4 rec.); Windows-on-ARM not supported `[repo]` | **Decrypted** dumps from the user's own 3DS; encrypted ROM support dropped in 2120 and "will not change" `[upstream-snippet]` | Tags up to 2127.0-rc4, active 2026-11-18 `[repo]`; Citra repos gone | good | P2 | [Azahar README](https://github.com/azahar-emu/azahar), [Dumping wiki](https://github.com/azahar-emu/azahar/wiki/Dumping-Games), [Panda3DS](https://github.com/wheremyfoodat/Panda3DS) |
| Virtual Boy | libretro **Beetle VB** (Mednafen); Mednafen standalone | docs.libretro.com (unverified this session) | GPL-2.0 (Mednafen) — unverified this session | Any PC; stereoscopic output modes (anaglyph/side-by-side) | None | Tiny library; 3D presentation is the only real issue | good (unverified) | P3 | unverified |

**Legal Nintendo alternatives:** Nintendo Switch Online / Expansion Pack classic libraries on Switch/Switch 2 (on-console only). Nintendo has **no remote play** to PC. "Cloud Version" games on Switch/Switch 2 stream from servers for a small set of third-party titles (needs Nintendo Account + Access Pass; NSO not required except for online features; regional availability historically US/Canada for some titles — check eShop) — not usable from a PC launcher. See [Nintendo Cloud Versions FAQ](https://en-americas-support.nintendo.com/app/answers/detail/a_id/53518/~/cloud-versions-of-games---faq).

---

## Sony

| Platform | Candidate emulator(s) | Official project & compatibility list | License | Hardware notes | User-provided files | Important limitations | Tier (upstream-reported) | Priority | Source |
|---|---|---|---|---|---|---|---|---|---|
| PS1 | **DuckStation** (standalone); libretro: Beetle PSX (HW), SwanStation | github.com/stenzek/duckstation | **CC BY-NC-ND 4.0** `[repo]` | x86-64 with SSE4.1 (SSE2 legacy build exists), ARM64, RISC-V; GPU OpenGL 3.1 / D3D11 FL10 / Vulkan 1.0; Windows 10 1809+ only `[repo]` | PS1 (or PS2) BIOS dump **required** `[repo]` | Non-commercial/no-derivatives license: launch only, never bundle/modify | mature | P1 | [DuckStation README](https://github.com/stenzek/duckstation) |
| PS2 | **PCSX2** (standalone); libretro: LRPS2 (PCSX2-based, lags) | pcsx2.net; compat pcsx2.net/compat | GPL-3.0 `[repo]` | Minimum: SSE4.1, PassMark ST ≥1500, Vulkan 1.1/D3D11. Moderate: **AVX2**, ST ≥2000, Vulkan 1.3/D3D12, 4 GB VRAM. Heavy: AVX2, ST ≥2600, 6 cores+SMT, 8 GB VRAM `[upstream-snippet]` | PS2 BIOS dump from own console **required** `[repo]` | Tags v2.9.18x (nightly line), active 2026-11-18 `[repo]` | mature | P1 | [PCSX2 README](https://github.com/PCSX2/pcsx2), [requirements](https://pcsx2.net/docs/setup/requirements/) |
| PS3 | **RPCS3** (standalone only) | rpcs3.net; rpcs3.net/compatibility | GPL-2.0-only `[repo]` | CPU without AVX2 or with ≤4 threads "should perform badly"; recommended Ryzen 5 5600 / i5-10400; GPU Vulkan 1.2, RX 5600 XT / RTX 2060 rec.; Intel GPUs not recommended; 16 GB RAM + SSD rec. `[upstream-snippet]` | Official PS3 system software (PUP) — Sony distributes it publicly; disc games dumped by user; PSN titles need the user's license files (RAP/act.dat) | Official list: **2,859 of 3,558 (~80%) Playable**, ~19% Ingame (snapshot dated Nov 2026) `[upstream-snippet]`; >80% milestone reported late Oct 2026 `[secondary]` | good | P2 | [RPCS3 README](https://github.com/RPCS3/rpcs3), [compatibility](https://rpcs3.net/compatibility), [requirements](https://rpcs3.net/requirements) |
| PS4 | **shadPS4** (standalone) | github.com/shadps4-emu/shadPS4; list github.com/shadps4-compatibility/shadps4-game-compatibility (statuses: playable / ingame / menus / boots / nothing) | GPL-2.0 `[repo]` | Vulkan **1.3** hard requirement (VK_KHR_swapchain, VK_KHR_push_descriptor); GPU ≥2 GB VRAM; 8 GB RAM; Win10 / Ubuntu 22.04 / macOS 15.4 (README now says macOS 26, no Intel Macs); older quickstart also required **AVX2** `[upstream-snippet]`/`[repo]` | Some PS4 system modules (`sys_modules/*.sprx`, 34 listed) "must be dumped from your legally owned PlayStation 4" `[repo]`; games dumped from own (jailbroken) PS4 | Rapid releases: tags v0.19.0 → **v0.21.0**, active 2026-11-17 `[repo]`. List shows ~2.4k reports but no official aggregate %; most titles not yet Playable (per-game check needed) | partial | P3 (plus **Stream** via PS Remote Play / official PC ports) | [shadPS4](https://github.com/shadps4-emu/shadPS4), [compat list](https://github.com/shadps4-compatibility/shadps4-game-compatibility), [quickstart](https://shadps4.net/quickstart/) |
| PS5 | None usable | — | — | — | — | No credible public PS5 emulator. "PS5 emulator" downloads are typically scams | unsupported | **Stream** (PS Remote Play, PS Portal, PS Plus Premium cloud on console/Portal) / official PC ports | — |
| PSP | **PPSSPP** (standalone); libretro: PPSSPP | github.com/hrydgard/ppsspp; report.ppsspp.org/games | GPL-2.0-or-later (per README) `[repo]` | Very light; Vulkan/D3D11/OpenGL; D3D9 being dropped `[repo]` | **None** (HLE, no BIOS) `[repo]` | v1.20.4 latest tag, active 2026-11-18 `[repo]` | mature | P1 | [PPSSPP](https://github.com/hrydgard/ppsspp) |
| PS Vita | **Vita3K** (standalone) | vita3k.org; commercial list vita3k.org/compatibility.html; homebrew list on GitHub | GPL-2.0 `[repo]` | OpenGL or Vulkan; see vita3k.org/quickstart `[repo]` | Official Vita firmware **and** separate font firmware package, both downloadable from PlayStation servers; games dumped from own Vita (NoNpDrm/FAGDec) `[upstream-snippet]`/`[repo]` | README: "early stage … Expect crashes, glitches, low compatibility and poor performance", though it now "runs most homebrew programs and commercial games" `[repo]`; continuous builds only | partial | P3 | [Vita3K](https://github.com/Vita3K/Vita3K), [quickstart](https://vita3k.org/quickstart) |

---

## Microsoft

| Platform | Candidate emulator(s) | Official project & compatibility list | License | Hardware notes | User-provided files | Important limitations | Tier (upstream-reported) | Priority | Source |
|---|---|---|---|---|---|---|---|---|---|
| Xbox (original) | **xemu** (standalone) | xemu.app; compat list xemu.app/titles (unverified URL this session) | GPL-2.0 `[repo]` | Modern GPU (OpenGL/Vulkan; unverified detail) | **MCPX boot ROM** (1.0 Xbox), **flash BIOS** — a stock retail BIOS will not boot games (debug or modified BIOS needed), and an **HDD image** (dump own drive or xemu's copyright-free prebuilt image) `[upstream-snippet]` | The BIOS requirement adds legal friction (modified BIOS); v0.8.139 latest tag, active 2026-11-16 `[repo]` | good | P2 | [xemu repo](https://github.com/xemu-project/xemu), [required files](https://xemu.app/docs/required-files/) |
| Xbox 360 | **Xenia Canary** (fork; upstream xenia-project last commit 2026-02-18) | github.com/xenia-canary/xenia-canary; list github.com/xenia-canary/game-compatibility/issues | BSD-3-Clause `[repo]` | Windows 10 x64+; **x86-64 with AVX or AVX2**; GPU **D3D12 or Vulkan** (no OpenGL/D3D11); AMD GPUs discouraged (driver crashes), iGPUs too slow; 4 GB RAM min; Linux via Proton/AppImage `[repo wiki]` | **None** (no dashboard/keys needed); games from own console | Canary is the de facto maintained build (rolling tags, commit 2026-11-17 `[repo]`); per-game status very uneven | partial | P3 | [Xenia Canary](https://github.com/xenia-canary/xenia-canary), [Quickstart wiki](https://github.com/xenia-canary/xenia-canary/wiki/Quickstart) |
| Xbox One / Series X/S | None usable | — | — | — | — | No public emulator | unsupported | **Stream** (Xbox Cloud Gaming, Xbox Remote Play) / Xbox Play Anywhere & PC Game Pass native Windows versions | see streaming table |

---

## Sega

| Platform | Candidate emulator(s) | Official project & compatibility list | License | Hardware notes | User-provided files | Important limitations | Tier (upstream-reported) | Priority | Source |
|---|---|---|---|---|---|---|---|---|---|
| SG-1000 / Master System | libretro **Genesis Plus GX**, Gearsystem; standalone **ares** | github.com/ekeeke/Genesis-Plus-GX | GPGX: **non-commercial** license `[repo]`; ares ISC | Any PC | None (SMS BIOS optional) | — | mature | P1 | [Genesis Plus GX](https://github.com/ekeeke/Genesis-Plus-GX) |
| Genesis / Mega Drive | **Genesis Plus GX** (libretro), **ares**, BlastEm (unverified this session) | as above | as above | Any PC | None | — | mature | P1 | [Genesis Plus GX](https://github.com/ekeeke/Genesis-Plus-GX), [ares](https://github.com/ares-emulator/ares) |
| Sega CD / Mega-CD | **Genesis Plus GX**, **ares** | as above | as above | Any PC | **Sega CD BIOS required** (region-matched) | — | mature | P1 | [Genesis Plus GX](https://github.com/ekeeke/Genesis-Plus-GX) |
| 32X | libretro **PicoDrive**; **ares** | PicoDrive repo (unverified this session) | PicoDrive: non-standard/MAME-like license (unverified) | Any PC | 32X BIOS optional/required depending on core (unverified) | Smaller library; accuracy of 32X in ares vs PicoDrive unverified | good (unverified) | P2 | [ares](https://github.com/ares-emulator/ares) |
| Saturn | libretro **Beetle Saturn** (Mednafen); Kronos (GitHub repo no longer reachable — status unverified); standalone Mednafen | github.com/libretro/beetle-saturn-libretro | GPL-2.0 `[repo]` | Beetle Saturn is CPU-heavy (accuracy-first); faster CPU needed | **Saturn BIOS required** | Beetle Saturn active 2026-11-17 `[repo]`; ST-V arcade support varies by core | good | P2 | [Beetle Saturn](https://github.com/libretro/beetle-saturn-libretro) |
| Dreamcast | **Flycast** (standalone + libretro) | github.com/flyinghead/flycast | GPL-2.0 `[repo]` | Vulkan or OpenGL (D3D11 on Windows, unverified) `[repo]` | Dreamcast BIOS recommended (HLE BIOS exists for many games — unverified detail) | v2.7 latest tag, active 2026-11-13 `[repo]` | mature | P1 | [Flycast](https://github.com/flyinghead/flycast) |
| Game Gear | **Genesis Plus GX**, Gearsystem, ares | as SMS | as SMS | Any PC | None | — | mature | P1 | [Genesis Plus GX](https://github.com/ekeeke/Genesis-Plus-GX) |

---

## Arcade

| Platform | Candidate emulator(s) | Official project & compatibility list | License | Hardware notes | User-provided files | Important limitations | Tier (upstream-reported) | Priority | Source |
|---|---|---|---|---|---|---|---|---|---|
| Multi-arcade | **MAME** (standalone); libretro: MAME (current), MAME 2003-Plus (old sets) | mamedev.org; per-driver status in MAME itself / arcadedb | GPL-2.0-or-later as a whole (some files BSD-3) `[repo]` | Varies hugely by driver (3D-era boards are demanding) | **Version-matched ROM sets** (incl. BIOS sets like `neogeo.zip`) from boards the user owns/has rights to | Sets change every monthly release — launcher must record the MAME version per set; latest tag **mame0289**, active 2026-11-18 `[repo]` | mature | P1 | [MAME](https://github.com/mamedev/mame) |
| CPS/Neo Geo/etc. | **FinalBurn Neo** (standalone + libretro) | github.com/finalburnneo/FBNeo | **Non-commercial** custom license `[repo]` | Light | FBNeo-specific ROM sets | Do not bundle (non-commercial) | mature | P1 | [FBNeo](https://github.com/finalburnneo/FBNeo) |
| Naomi / Naomi 2 / Atomiswave | **Flycast** | github.com/flyinghead/flycast | GPL-2.0 `[repo]` | As Dreamcast | Naomi/Atomiswave BIOS zips + game sets (Flycast-compatible) | MAME also has these drivers but Flycast is the playable option (secondary knowledge; unverified this session) | good | P2 | [Flycast](https://github.com/flyinghead/flycast) |

---

## PC

| Platform | Candidate runner(s) | Official project | License | Hardware notes | User-provided files | Important limitations | Tier (upstream-reported) | Priority | Source |
|---|---|---|---|---|---|---|---|---|---|
| Native Windows | Direct launch / store clients (Steam, GOG Galaxy, Epic, Xbox app) | — | — | — | Store accounts | Integration via store URIs: `steam://rungameid/<appid>` (widely used; not found in official Steamworks docs this session → partially unverified); Epic `com.epicgames.launcher://apps/<id>?action=launch` (unverified); GOG `goggalaxy://` (unverified) | mature | P1 | — |
| Native Linux / Windows games on Linux | **Proton** (Steam), **Wine** | github.com/ValveSoftware/Proton; winehq.org | Proton: mixed (BSD-3 scripts + LGPL Wine) `[repo]`; Wine LGPL-2.1 | Vulkan GPU (DXVK/VKD3D) | — | Proton latest tag proton-11.0-2e (commit 2026-11-10); Wine dev series at 11.22 `[repo]`. Kernel anti-cheat titles often blocked. Only relevant if the hub also targets Linux | good | P3 (Windows hub) | [Proton](https://github.com/ValveSoftware/Proton), [Wine mirror](https://github.com/wine-mirror/wine) |
| DOS | **DOSBox Staging**, **DOSBox-X**; libretro: DOSBox-Pure | github.com/dosbox-staging/dosbox-staging; github.com/joncampbell123/dosbox-x | Staging GPL-2.0-or-later; DOSBox-X GPL-2.0 `[repo]` | Any PC | Game files the user owns (GOG releases often ship DOSBox configs) | Staging: v0.83.1 latest tag; DOSBox-X: 2026.10.01 `[repo]`. X is better for Win9x/PC-98/edge cases | mature | P1 | [DOSBox Staging](https://github.com/dosbox-staging/dosbox-staging), [DOSBox-X](https://github.com/joncampbell123/dosbox-x) |
| Point-and-click adventures | **ScummVM** | github.com/scummvm/scummvm; scummvm.org/compatibility | GPL-3.0 `[repo]` | Any PC | Original game data files | Latest tag v2026.4.0 (new calendar versioning), active 2026-11-18 `[repo]` | mature | P1 | [ScummVM](https://github.com/scummvm/scummvm) |

---

## Other systems (brief)

| Platform | Candidate(s) | License | User files | Tier | Priority | Source |
|---|---|---|---|---|---|---|
| Atari 2600 | Stella (standalone + libretro) | GPL-2.0 (unverified this session) | None | mature (unverified) | P1 | unverified |
| Atari 7800 | ProSystem / A7800 (MAME-derived) cores | unverified | BIOS optional | good (unverified) | P2 | unverified |
| Atari Lynx | libretro Handy / Beetle Lynx | unverified | `lynxboot.img` BIOS needed by most cores | good (unverified) | P2 | unverified |
| TurboGrafx-16 / PC Engine (+CD) | libretro Beetle PCE / PCE Fast; **ares** | Mednafen GPL-2.0; ares ISC `[repo]` | CD: System Card BIOS required | mature | P1 | [ares](https://github.com/ares-emulator/ares) |
| Neo Geo (MVS/AES) | FBNeo, MAME | see Arcade | `neogeo.zip` BIOS set | mature | P1 | [FBNeo](https://github.com/finalburnneo/FBNeo) |
| Neo Geo CD / Pocket | FBNeo (NGCD), Beetle NeoPop (NGP) | see Arcade | NGCD BIOS | good (unverified) | P3 | unverified |
| Frontend option | **RetroArch** (libretro) — hosts most cores above | GPL-3.0 `[repo]` | per core | mature | P1 as an optional backend | [RetroArch](https://github.com/libretro/RetroArch) (v1.22.2 latest tag `[repo]`) |

---

## Streaming & official alternatives (newer systems)

Use these where local emulation is unsupported (PS5, Xbox One/Series, Switch 2) or partial (many PS4 / Xbox 360 titles).

| Service | Covers | Hardware / client | Subscription & limits | Region / account | Launcher integration | Status notes (2026) | Source |
|---|---|---|---|---|---|---|---|
| **Official PC ports** (Steam/Epic/GOG; Sony PC titles; Xbox Play Anywhere / PC Game Pass) | Many PS4/PS5 first-party and Xbox titles | The PC itself | Per-game purchase or PC Game Pass | Store account; some Sony PC games link a PSN account | Store URIs (see PC table) | Best-quality legal option where a port exists | [PlayStation gaming on PC](https://www.playstation.com/en-us/support/playstation-gaming-on-pc/), [Xbox PC app](https://www.xbox.com/en-US/apps/xbox-app-on-pc) |
| **PS Remote Play** (Windows app) | PS5/PS4 games the user owns, streamed from their own console | Windows 10/11 64-bit, 7th-gen Intel Core or later, 2 GB RAM, 100 MB, DualSense/DS4 over USB; PS5 on latest firmware `[upstream-snippet]` | Free; ≥5 Mbps up/down, 15 Mbps recommended; UDP 8572 must not be blocked `[upstream-snippet]` | Same PSN account as the console | Launch the official PS Remote Play app (no documented URI scheme → unverified) | Unaffected by PC app retirement below | [PS Remote Play on PC](https://www.playstation.com/en-us/support/games/playstation-remote-play-on-pc-and-mac/), [Windows guide](https://remoteplay.dl.playstation.net/remoteplay/lang/en/1100001.html) |
| **PlayStation Portal** | Remote play from own PS5; **cloud streaming** (since 2025-11-05) of PS Plus Game/Classics Catalog and select owned digital PS5 games | Portal device | **PS Plus Premium** required for cloud | Availability varies by region | Not launchable from a PC hub (separate device) | Live | [PS Blog 2025-11-05](https://blog.playstation.com/2025/11/05/cloud-streaming-officially-arrives-on-playstation-portal-today-with-new-support-for-digital-ps5-games-in-your-library/), [Portal cloud support](https://www.playstation.com/en-us/support/subscriptions/psportal-cloud-game-streaming/) |
| **PS Plus Premium cloud on PC** | PS Plus streaming catalogue on Windows | PlayStation Plus PC app | PS Plus Premium | — | **Do not build on it** | **Being retired: PS Plus PC app ends 10 Dec 2026 (blog) / 11 Dec 2026 (support notice).** Console and Portal cloud streaming continue `[upstream-snippet]` | [Sony important notice](https://www.playstation.com/en-us/support/important-notice/), [PS Blog 2026-11-10](https://blog.playstation.com/2026/11/10/playstation-plus-game-catalog-for-november-death-stranding-2-on-the-beach-like-a-dragon-pirate-yakuza-in-hawaii-atomfall-dragon-quest-iii-hd-2d-remake-and-more/) |
| **Xbox Cloud Gaming** | Game Pass cloud catalogue + eligible owned games | Browser (xbox.com/play), Xbox PC app, phones, TVs | **Changed Nov 2026: monthly hour allowance** — Ultimate 15 h, Premium 10 h, Essential 5 h; extra hours purchasable via Xbox Store; unused hours don't roll over, multiple subs don't stack; free ad-supported tier has session limits `[upstream-snippet]`. Prices: Essential $9.99, Premium $14.99, Ultimate reported $22.99 after Apr 2026 change `[secondary]` (verify) | Microsoft account; hours/purchase options vary by market | Open `https://www.xbox.com/play/...` in browser or launch Xbox app; per-game deep-link format unverified | Recent and material change — hub should surface remaining hours if an API exists (unverified) | [Xbox Wire 2026-09-03](https://news.xbox.com/en-us/2026/09/03/xbox-cloud-gaming-changes/), [Cloud playtime support](https://support.xbox.com/en-US/help/games-apps/cloud-gaming/cloud-gaming-playtime) |
| **Xbox Remote Play** | Games installed on the user's own Xbox One / Series | Xbox PC app (Win10/11 22H2+), or browser xbox.com/play/consoles | **No subscription**; ≥10 Mbps; console on/in sleep with remote features enabled `[upstream-snippet]`. 1440p streaming in Insider preview only | Microsoft account | Xbox app / `https://www.xbox.com/en-us/play/consoles` | — | [Xbox Remote Play](https://www.xbox.com/en-US/consoles/remote-play), [xbox.com/play/consoles](https://www.xbox.com/en-us/play/consoles) |
| **GeForce NOW** | PC games the user owns on Steam/Epic/Ubisoft/Xbox etc. (supported titles only) | Windows app, browser (play.geforcenow.com) | Free (limited), Performance, Ultimate; **100 h/month cap** for paid tiers since Jan 2026 (≤15 h rollover); extra hours purchasable; legacy unlimited plans ended after 15 Jan 2026; Founders keep unlimited `[upstream-snippet]` | NVIDIA account + linked store accounts; catalogue varies by region | **Official deep link:** `https://play.geforcenow.com/games?game-id=<uuid>&utm_source=<src>&utm_campaign=<camp>` (unavailable-in-region → homepage) | — | [GFN FAQ](https://www.nvidia.com/en-us/geforce-now/faq/), [GFN SDK deep-linking](https://github.com/NVIDIAGameWorks/GeForceNOW-SDK/blob/master/doc/GfnSdk-Deep-Linking.md) |
| **Steam Remote Play / Steam Link** | Streaming the user's own Steam PC to another device | Steam client on host + client | Free | Steam account | `steam://` URIs (see PC table; partly unverified) | Not fetched this session → details unverified | unverified |
| **Moonlight + Sunshine** (open source) | Streaming the user's own PC (incl. emulators) to other devices | Sunshine host: hardware encode via NVENC / AMF / QuickSync (Windows), VAAPI/NVENC (Linux); Moonlight clients on PC/mobile/TV `[repo]` | Free | None (local pairing) | Sunshine "apps" list can expose the hub itself; Moonlight-qt has a CLI (`moonlight stream <host> <app>`) for scripting (CLI syntax unverified) | Sunshine tags v2026.1118.x (built today), Moonlight-qt v6.2.0 `[repo]` | [Sunshine](https://github.com/LizardByte/Sunshine), [moonlight-qt](https://github.com/moonlight-stream/moonlight-qt) |
| **Nintendo** | Switch / Switch 2 | Console only | NSO for online/classics; Cloud Versions need an Access Pass per game | Nintendo Account; Cloud Versions limited region availability | **None from PC** — no remote play, no PC cloud | Recommend "play on console" entry in hub | [Cloud Versions FAQ](https://en-americas-support.nintendo.com/app/answers/detail/a_id/53518/~/cloud-versions-of-games---faq) |

---

## Recently changed (as of 2026-11-18)

1. **Xbox Cloud Gaming moved to monthly hour caps in Nov 2026** (15/10/5 h by tier).
2. **Sony is retiring the PS Plus PC app (cloud streaming on Windows) on 10/11 Dec 2026**; Portal/console cloud and PS Remote Play stay.
3. **GeForce NOW** paid tiers have a 100 h/month cap since Jan 2026.
4. **Switch emulation:** Nintendo sent further GitHub DMCA rounds in 2026 (Feb, Mar, Sep, Nov). Ryubing and Eden distribute from self-hosted Forgejo; Citron Neo's GitHub network was disabled on 2026-11-06. The current Ryubing/Eden release numbers are **unverified** (hosts unreachable from the research sandbox).
5. **Switch 2:** experimental public emulators exist (Lichii, active today); a commercial game reportedly boots with errors. Not suitable for a hub.
6. **RPCS3** passed ~80% Playable. **shadPS4** is at v0.21.0 and improving quickly, but is still partial.
7. **Azahar** is the maintained 3DS emulator; it needs decrypted dumps.

## Open items / unverified

- Exact current Ryubing and Eden versions (git.ryujinx.app / git.eden-emu.dev not reachable here).
- Steam, Epic and GOG URI formats, plus any PS Remote Play or Xbox app protocol handlers: verify against vendor docs before implementing.
- Xbox Game Pass US prices after the April 2026 change (only secondary sources found).
- Atari, Virtual Boy, 32X and Neo Geo Pocket core licenses and states, which were not checked this session.
- Per-title compatibility for PS4, Xbox 360, Switch and Vita must be checked per game against the upstream lists. Nothing here is a test result.

## Sources (accessed 2026-11-18)

Official repositories (read directly via git):
- https://github.com/SourMesen/Mesen2
- https://github.com/bsnes-emu/bsnes
- https://github.com/ares-emulator/ares
- https://github.com/gopher64/gopher64
- https://github.com/Rosalie241/RMG
- https://github.com/dolphin-emu/dolphin
- https://github.com/cemu-project/Cemu
- https://github.com/mgba-emu/mgba
- https://github.com/melonDS-emu/melonDS
- https://github.com/azahar-emu/azahar
- https://github.com/azahar-emu/compatibility-list
- https://github.com/wheremyfoodat/Panda3DS
- https://github.com/zortos293/Lichii
- https://github.com/stenzek/duckstation
- https://github.com/PCSX2/pcsx2
- https://github.com/RPCS3/rpcs3
- https://github.com/shadps4-emu/shadPS4
- https://github.com/shadps4-compatibility/shadps4-game-compatibility
- https://github.com/hrydgard/ppsspp
- https://github.com/Vita3K/Vita3K
- https://github.com/xemu-project/xemu
- https://github.com/xenia-canary/xenia-canary
- https://github.com/xenia-canary/xenia-canary/wiki/Quickstart
- https://github.com/xenia-project/xenia
- https://github.com/ekeeke/Genesis-Plus-GX
- https://github.com/libretro/beetle-saturn-libretro
- https://github.com/flyinghead/flycast
- https://github.com/mamedev/mame
- https://github.com/finalburnneo/FBNeo
- https://github.com/dosbox-staging/dosbox-staging
- https://github.com/joncampbell123/dosbox-x
- https://github.com/scummvm/scummvm
- https://github.com/libretro/RetroArch
- https://github.com/ValveSoftware/Proton
- https://github.com/wine-mirror/wine
- https://github.com/LizardByte/Sunshine
- https://github.com/moonlight-stream/moonlight-qt
- https://github.com/NVIDIAGameWorks/GeForceNOW-SDK/blob/master/doc/GfnSdk-Deep-Linking.md

Legal / DMCA:
- https://github.com/github/dmca/blob/master/2026/02/2026-02-12-nintendo.md
- https://github.com/github/dmca/blob/master/2026/03/2026-03-27-nintendo.md
- https://github.com/github/dmca/blob/master/2026/09/2026-09-30-nintendo.md
- https://github.com/github/dmca/blob/master/2026/11/2026-11-06-nintendo-4.md

Official sites (content read through search-index snippets; direct fetch was blocked from the sandbox):
- https://git.ryujinx.app/projects/Ryubing
- https://git.ryujinx.app/Ryubing/Canary/releases
- https://git.eden-emu.dev/eden-emu/eden/releases
- https://github.com/azahar-emu/azahar/wiki/Dumping-Games
- https://rpcs3.net/compatibility
- https://rpcs3.net/requirements
- https://rpcs3.net/faq
- https://pcsx2.net/docs/setup/requirements/
- https://shadps4.net/quickstart/
- https://vita3k.org/quickstart
- https://xemu.app/docs/required-files/
- https://cemu.info/
- https://wiki.cemu.info/wiki/Main_Page
- https://www.playstation.com/en-us/support/games/playstation-remote-play-on-pc-and-mac/
- https://remoteplay.dl.playstation.net/remoteplay/lang/en/1100001.html
- https://www.playstation.com/en-us/support/important-notice/
- https://www.playstation.com/en-us/support/subscriptions/psportal-cloud-game-streaming/
- https://www.playstation.com/en-us/support/playstation-gaming-on-pc/
- https://blog.playstation.com/2025/11/05/cloud-streaming-officially-arrives-on-playstation-portal-today-with-new-support-for-digital-ps5-games-in-your-library/
- https://blog.playstation.com/2026/11/10/playstation-plus-game-catalog-for-november-death-stranding-2-on-the-beach-like-a-dragon-pirate-yakuza-in-hawaii-atomfall-dragon-quest-iii-hd-2d-remake-and-more/
- https://news.xbox.com/en-us/2026/09/03/xbox-cloud-gaming-changes/
- https://support.xbox.com/en-US/help/games-apps/cloud-gaming/cloud-gaming-playtime
- https://www.xbox.com/en-US/consoles/remote-play
- https://www.xbox.com/en-us/play/consoles
- https://www.xbox.com/en-US/apps/xbox-app-on-pc
- https://www.nvidia.com/en-us/geforce-now/faq/
- https://en-americas-support.nintendo.com/app/answers/detail/a_id/53518/~/cloud-versions-of-games---faq

Secondary (press):
- https://www.videogameschronicle.com/news/nintendo-issues-dmca-takedown-on-more-switch-emulators-but-at-least-one-is-fighting-back/
- https://www.pcgamer.com/games/they-can-never-kill-emulation-players-vexed-as-nintendo-continues-its-siege-on-switch-emulation-handing-dmcas-to-various-emulators-on-github/
- https://www.notebookcheck.net/Zelda-Ocarina-of-Time-remake-runs-on-PC-with-Switch-2-emulator-before-release-date.1442531.0.html
- https://www.tomshardware.com/video-games/nintendo/nintendos-latest-zelda-remake-already-circulating-online-as-a-switch-2-rom-openai-assisted-software-jailbreak-new-game-dumper-let-pirates-share-game-for-free-immediately-following-release
- https://www.purexbox.com/news/2026/04/heres-a-breakdown-of-the-new-prices-for-xbox-game-pass-as-of-april-2026
