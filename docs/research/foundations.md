# Foundations research: unified gaming hub

Research date: 2026-11-18. Goal: pick a foundation for a console-like hub (open hub, pick a game, play, return to the hub) across Windows, Linux/SteamOS and macOS.

## How this was verified (read first)

- **Verified directly** means fetched from the upstream source in this session: GitHub release/commit Atom feeds, raw `LICENSE`/`README` files on raw.githubusercontent.com, the ES-DE GitLab API and raw docs, and the NuGet API for PlayniteSDK.
- Several official sites could not be reached from the research sandbox: playnite.link, api.playnite.link (Playnite docs), retroarch.com, manual.emudeck.com, es-de.org, pegasus-frontend.org, retrobat.org, launchbox-app.com, lutris.net, heroicgameslauncher.com and gamingonlinux.com. Anything taken from those sites came through search-engine snippets, and is marked *(via search index)*. Re-check those items before relying on them.
- "unverified" means I could not confirm the item from an upstream source.

---

## 1. Comparison table

| Candidate | Role | OS | License (read from LICENSE) | Latest release (date) | Recent commits | Controller / fullscreen | Extension model | Fit for "hub" |
|---|---|---|---|---|---|---|---|---|
| **Playnite** | PC library manager and launcher, with emulation | Windows 10/11 only | MIT | 10.64 (2026-11-09) | Yes. `master` has 20 commits between 2026-10-18 and 2026-11-08; P11 is developed privately | Fullscreen mode (`Playnite.FullscreenApp`) with full gamepad navigation | .NET plugins (generic, library, metadata), PowerShell scripts, Desktop and Fullscreen themes (XAML), YAML emulator profiles | **Best on Windows** |
| **ES-DE** | Emulation and app frontend | Windows, Linux (x64 and AArch64 AppImage), macOS, Haiku, Android (paid) | MIT | 3.5.0 (2026-09-30); 4.0.0 in development | Yes. Last commit 2026-11-07; project activity 2026-11-15 | Controller-first, fullscreen | `es_systems.xml`, `es_find_rules.xml`, `es_import_rules.xml` under `custom_systems/`, themes, custom event scripts | **Best on Linux/SteamOS and macOS** |
| **Pegasus Frontend** | Emulation frontend | Windows, Linux, macOS, Android, Raspberry Pi | GPL-3.0-or-later **plus Section 7 trademark terms** | No tagged stable release. "Continuous build" (2026-11-11); last weekly release 2024-10-05 | Light. 20 commits between 2026-03-31 and 2026-11-11 | Controller-first, fullscreen | QML themes; `metadata.pegasus.txt`; reads ES2 gamelists | Viable, but releases are slow |
| **RetroArch** | libretro multi-system emulator, not a library hub | Windows, Linux, macOS, Android, iOS, consoles | GPL-3.0 (frontend). **Each core has its own license**, and some cores are non-commercial | v1.22.2 (2025-11-20) | Very active. 20 commits on 2026-11-18 alone | Controller-first menus (XMB, Ozone, RGUI) | Cores, `.lpl` playlists, shaders, overlays | Emulation backend, not the hub |
| **EmuDeck** | Installer and configurator (emulators, SRM, ES-DE, Pegasus) | SteamOS/Linux (bash), Windows (`emudeck-we`), Android beta; macOS unverified | Scripts: GPL-3.0 (`dragoonDorise/EmuDeck`, `EmuDeck/emudeck-we`). Electron GUI: MIT | Scripts repo 2.7 (2026-08-27) and 2.7 EA (2026-09-14). GUI v2.7.2 beta/unstable (2026-11-04) | Active. Org repos updated 2026-11-18 | Not applicable; it configures other tools | Reference for a "setup companion", not a runtime | Setup layer |
| **Steam ROM Manager** | Adds ROMs and other launchers' games to Steam as non-Steam shortcuts, with artwork | Windows, macOS, Linux (also CLI builds for x64 and arm64) | GPL-3.0 | 2.6.3 (2026-11-11) | Active (2.6.0 to 2.6.3 in November 2026) | Uses Steam Big Picture or Gaming Mode as the hub | Parsers, presets, CLI | Lets Steam itself be the hub on SteamOS |
| **RetroBat** | Windows bundle: an EmulationStation fork, RetroArch and standalone emulators, `emulatorLauncher` | Windows 8.1/10/11 | Code LGPL-3.0, except where upstream licenses apply. Written and graphic content CC BY-NC-SA 4.0. **Selling it on preinstalled machines or storage is not allowed** (from the README; no LICENSE file at the repo root) | v8.3.1.1 (2026-10-17); beta 8.4.0 (2026-11-07) | Active | Controller-first, fullscreen | ES themes, emulatorLauncher config | Windows emulation appliance; redistribution limits |
| **LaunchBox / Big Box** | Windows library manager. Big Box is its HTPC fullscreen UI | Windows (plus a separate Android app). No macOS. Linux "in development", 2027 target *(via search index)* | **Proprietary.** Free tier; Big Box needs a paid Premium license *(via search index)* | 14.0 (2026-08-15) *(via search index)*; 14.0.1 or 14.1 reported by third parties, unverified | unverified (closed source) | Big Box is fully controller driven | .NET plugin API, Big Box themes (closed product) | Proprietary; cannot be redistributed or forked |
| **Lutris** | Linux game manager (runners: Wine, emulators, native) | Linux only | GPL-3.0 | v0.5.22 (2026-02-26) | Active. 20 commits 2026-11-08 to 2026-11-18 | No dedicated fullscreen or gamepad mode found in the README | Runner YAML, install scripts; `lutris:rungame/<slug>` URIs and `lutris -l` | Backend for Linux PC games |
| **Heroic Games Launcher** | Epic (Legendary), GOG (gogdl), Amazon (Nile) and sideloaded games | Windows 10/11, macOS 14+, Linux, SteamOS (via Discover) | GPL-3.0 | 2.22.4 "Hotfix 4" (2026-10-15) | Very active. Commits to 2026-11-17 | Has gamepad navigation (not confirmed in the README) | No plugin API; Electron app | Store backend for Epic/GOG/Amazon |
| *RetroDECK* (added) | All-in-one Flatpak: ES-DE plus emulators | Linux/SteamOS | unverified | 0.10.10b (2026-10-03) | Active | Inherits ES-DE | Inherits ES-DE | Easiest SteamOS bundle; ships ES-DE as its UI |

---

## 2. Per-candidate notes

### 2.1 Playnite (Windows)

- **Repository:** https://github.com/JosefNemec/Playnite (branches: `master` for releases, `devel` for work in progress). Downloads (installer or portable): https://playnite.link/download.html. Playnite notifies users of updates itself.
- **OS:** Windows 10 or 11 (README).
- **License:** MIT (`LICENSE.md`, "Copyright (c) 2020 Josef Nemec"). You can redistribute and fork it; you must keep the notice. Builds are code-signed through SignPath Foundation, so a fork would need its own signing.
- **Latest release:** 10.64 (2026-11-09). Earlier: 10.63 (2026-10-19), 10.62 (2026-09-29), 10.57 to 10.61 (September 2026). 10.64 fixes the update process, updates emulator profiles, fixes fullscreen misalignment when the taskbar is on the left or right, and updates framework dependencies. 10.63 adds `.lnk` import options, JPEG XL support and new emulator profiles. The `Playnite.csproj` contains `<Version>10.64</Version>` and `<TargetFramework>net462</TargetFramework>`, with `x86` / `win-x86` as the only platform. About 4,092 commits.
- **Build stack (P10):** WPF and WinForms on **.NET Framework 4.6.2**, 32-bit x86, C# `LangVersion 12`, solution file `source/Playnite.slnx`. The projects are `Playnite`, `Playnite.DesktopApp`, `Playnite.FullscreenApp`, `PlayniteSDK`, `Playnite.BrowserProcess` (CEF), and `Tools/Playnite.Toolbox` and `Tools/PlayniteInstaller`.
- **SDK:** NuGet `PlayniteSDK` **6.18.0** (published 2026-09-29, MIT, targets `.NETFramework4.6.2`). Earlier versions: 6.17.0 (2026-09-10) and 6.16.0 (2026-04-10).

#### Extension types (P10)

From `Playnite.Toolbox/Program.cs` and `PlayniteSDK/Plugins/*.cs`:

| Type | Base class / manifest `Type` | Purpose |
|---|---|---|
| Generic plugin | `GenericPlugin` / `GenericPlugin` | Any behaviour: game lifecycle events, menus, sidebar and top-panel items, custom play, install and uninstall controllers, settings views, custom theme elements |
| Library plugin | `LibraryPlugin` / `GameLibrary` | Imports games from a source (Steam, Epic and so on) |
| Metadata plugin | `MetadataPlugin` / `MetadataProvider` | Provides metadata and artwork |
| PowerShell script | / `Script` | Script extension with event functions and menu items |
| Desktop theme | / theme manifest | XAML theme for desktop mode |
| Fullscreen theme | / theme manifest | XAML theme for the controller UI |

- **Plugin hooks:** `OnGameStarting`, `OnGameStarted`, `OnGameStopped`, `OnGameStartupCancelled`, `OnGameInstalled`, `OnGameUninstalled`, `OnGameSelected`, `OnApplicationStarted`, `OnApplicationStopped`, `OnLibraryUpdated`, `OnControllerButtonStateChanged`, `OnDesktopControllerButtonStateChanged`, `OnControllerConnected`, `OnControllerDisconnected`, `OnFullscreenViewChanged`, `GetPlayActions`, `GetInstallActions`, `GetUninstallActions`, `GetGameMenuItems`, `GetMainMenuItems`, `GetSidebarItems`, `GetTopPanelItems`, `GetGameViewControl`, and `GetSettings` / `GetSettingsView(firstRunView)`. The `firstRunView` flag is the built-in first-run wizard hook.
- **Toolbox:** `Toolbox.exe` has the verbs `new` (scaffold: DesktopTheme, FullscreenTheme, PowerShellScript, GenericPlugin, LibraryPlugin, MetadataPlugin), `pack` (build the `.pext` or `.pthm` package), `update` and `verify` (manifest check).
- **Distribution:** packages are `.pext` (extensions) and `.pthm` (themes). Add-ons can be published to the Add-on browser through the community add-on database (details *via search index*).

#### Emulation

- Emulator definitions ship as YAML in `source/Playnite/Emulation/Emulators/<Name>/emulator.yaml`, alongside `Platforms.yaml` and `Regions.yaml`. Example (RetroArch):
  ```yaml
  - Name: 4DO
    StartupArguments: '-L ".\cores\4do_libretro.dll" "{ImagePath}"'
    Platforms: [3do]
    ImageExtensions: [7z, bin, chd, cue, iso, zip]
    ProfileFiles: ['cores\4do_libretro.dll']
    StartupExecutable: ^retroarch\.exe$
  ```
- The user (or a companion) points Playnite at an emulator folder. Playnite auto-detects it from `StartupExecutable` and `ProfileFiles` and creates **built-in profiles**. **Custom profiles** (any executable, with arguments and `{ImagePath}` variables) are also possible. Games are imported with the emulated-game scanner. Fixes to built-in profiles ship in regular releases (10.63 and 10.64 both updated them).

#### Process tracking (how Playnite knows a game has ended)

From the `TrackingMode` enum in `PlayniteSDK/Models/GameAction.cs`:

| Mode | Behaviour |
|---|---|
| `Default` (0) | Playnite picks the best method automatically |
| `Process` (1) | Tracks the original process and all child processes it starts |
| `Directory` (2), labelled "Folder" in the UI | The game counts as running while any process from `TrackingPath` runs |
| `OriginalProcess` (3) | Tracks only the process that was started; child processes are ignored |
| `ProcessName` (4) | Tracks any process with a given name |

- Related fields: `TrackingPath`, `InitialTrackingDelay` (default 0 ms) and `TrackingFrequency` (default 2000 ms polling).
- Plugins can supply their own `PlayController`, for example an `AutomaticPlayController` or a custom controller. The plugin then raises the started and stopped events itself, which is how store integrations like Steam handle launcher stubs.
- **Return to hub:** the `AfterLaunch` setting (None / **Minimize** (default) / Close) and the `AfterGameClose` setting (None / Restore / **RestoreOnlyFromUI** (default) / Exit) control what Playnite does. For a console feel, set `AfterGameClose = Restore` so the window comes back even when the game was launched by URI or CLI.
- **Known gotchas:**
  - Launcher stubs make the default tracking end early. Examples are games that start a launcher and exit, or UWP/Store games. Use Folder or ProcessName tracking for these.
  - Emulators that fork a process need Folder or Process tracking.
- **CLI and URI:** `--start <gameId>`, `playnite://playnite/start/<gameId>`, `--nolibupdate`, `--userdatadir`, `--hidesplashscreen` *(via search index)*. The fullscreen executable is `Playnite.FullscreenApp.exe`. A `--startfullscreen` flag is unverified.

#### How to build a "setup companion" for Playnite (P10)

1. Write a **GenericPlugin** (C#, .NET Framework 4.6.2, NuGet `PlayniteSDK` 6.18.0). Scaffold it with `Toolbox.exe new GenericPlugin` and package it with `Toolbox.exe pack`.
2. Use `GetSettingsView(firstRunView: true)` or `OnApplicationStarted` to run a first-run wizard. The wizard can:
   - download or locate emulators;
   - register emulators through `PlayniteApi.Database.Emulators`, using the built-in definitions via `PlayniteApi.Emulation`;
   - create platforms;
   - trigger the game scanner, and set fullscreen as the startup mode. This API is not verified; the alternative is to write the settings file before first launch.
3. Use `OnGameStopped` for post-game actions, such as save sync or restoring the display, and `OnControllerButtonStateChanged` for global hotkeys while in Fullscreen.
4. Alternative without a plugin: an external installer (MSI or Inno Setup) that bundles **portable Playnite** (MIT allows this), preseeds its config and extensions folder, and launches `Playnite.FullscreenApp.exe`. Keep the MIT notice. Do not use the Playnite name or logo for a modified fork without checking with the author (there is no trademark clause in the LICENSE, but courtesy and confusion risk apply).

#### Playnite 11 (P11) status: what changed

- The README says P11 is "being rewritten from scratch". Development happens in a **private repository until beta**, and the code will then be published "under the same license as current version 10" (MIT). Pull requests to P10 are "generally on pause", and there is no public feature list.
- **P11 alpha docs exist** at `api.playnite.link/docs/wpfdevel11/` *(via search index)*:
  - Alpha **11.0.2.0** is the latest listed. It brought a revised plugin template. Its date is unverified.
  - The alpha targets extension developers and is not feature complete. The roadmap puts achievements, an **emulation plugin** and a finished Steam plugin in Alpha 2, followed by Beta 1.
  - **The runtime moves from .NET Framework 4.6.2 to .NET 10**, with nullable reference types in the template.
  - **Generic, library and metadata plugin types merge into a single plugin type**, configured through `LibrarySettings` and `MetadataSettings`, with initialisation in `InitializeAsync`.
  - **PowerShell extensions are being removed.**
  - Theming is not implemented yet in the alpha.
  - Emulation moves into a plugin.
  - Neither the alpha nor P11 final supports Linux. Linux is planned after P11; the developer said he was "planning to move to Linux in 2026 after P11 is done" *(via search index)*.
- **What this means for us:**
  - P10 (10.64, SDK 6.18) is still what ships and is still actively released. Fourteen 10.x releases came out in 2026.
  - P10 plugins will **not** be binary compatible with P11, and PowerShell-based logic has no future. Keep companion logic in a thin C# layer, and keep the core (downloads, config writing) in a separate executable or library that both P10 and P11 plugins can call.
  - No P11 beta date is published. Do not plan around it.

### 2.2 ES-DE (EmulationStation Desktop Edition)

- **Repository:** https://gitlab.com/es-de/emulationstation-de. Downloads come from https://es-de.org. As of 2026-11-01 the download and updater URLs moved to `updates.es-de.org` (commits "Changed the download URLs..." and "Changed the application updater to use updates.es-de.org instead of gitlab.com").
- **OS:** Android, Linux, macOS, Windows and Haiku are official; FreeBSD has an unofficial port. Builds: Linux x64 AppImage plus a Steam Deck AppImage (needs `libfuse2`), AArch64 AppImage, Windows (installer and portable), and macOS (ARM and x86 packages; the changelog mentions both).
- **License:** MIT ("Copyright (c) 2024-2026 Northwestern Software AB; 2020-2024 Leon Styhre; 2014 Alec Lofquist"). The desktop builds are free and redistributable. **The Android port is a paid app** (Patreon, Samsung, Huawei stores).
- **Latest release:** v3.5.0 (2026-09-30). Earlier: v3.4.1 (2026-04-10) and v3.4.0 (2025-11-07). 4.0.0 is in development.
- **Emulator integration:**
  - The bundled `resources/systems/<os>/es_systems.xml` defines systems and commands. Users override it with `~/ES-DE/custom_systems/es_systems.xml`.
  - `es_find_rules.xml` locates emulators and cores. Rule types are `winregistrypath`, `winregistryvalue`, `systempath` and `staticpath`, with `%ESPATH%`-relative entries for portable installs.
  - Commands use variables such as `%EMULATOR_RETROARCH%`, `%CORE_RETROARCH%`, `%ROM%`, `%BASENAME%`, `%ROMPATH%`, `%STARTDIR%`, `%PRECOMMAND_WINE%`, `%HIDEWINDOW%`, `%ESCAPESPECIALS%` and `%RUNINBACKGROUND%`.
  - Several `<command label=...>` entries give alternative emulators.
  - `es_import_rules.xml` is a game importer for Steam, Android apps and desktop apps.
- **Return-to-hub behaviour:**
  - By default ES-DE **suspends while the game runs and resumes when the launched process exits**.
  - `%RUNINBACKGROUND%` (needed for Steam games, which hand off to a running Steam client) keeps ES-DE running instead. In that case the `game-end` event fires "on application wakeup" rather than on real exit.
  - Play time is tracked.
  - **Custom event scripts** in `~/ES-DE/scripts/<event>/` include `game-start` and `game-end` (arguments: ROM path, game name, system, full system name) and screensaver events. These are the integration points for a companion.
- **Themes:** the built-in theme downloader and the theme engine documented in `THEMES.md`. Controller config is per GUID in `es_input.xml`.
- **Known issues** (from the user guide):
  - Windows: Intel iGPU flicker and unresponsiveness after the KB5048685 update (the workaround is MSAA 2X); Intel Iris Xe crashes; DS4Windows breaks input.
  - macOS: weak controller support, and no Vulkan, which limits the emulators available.
  - Steam Deck: an immutable filesystem, and Flatpak emulators need permissions for external storage.
  - Some games misbehave with "Run in background" enabled.
  - EmuDeck installs a non-standard ES-DE layout.
- **Packaging:** the AppImage updates itself. Windows and macOS packages are downloaded in-app but installed manually.

### 2.3 Pegasus Frontend

- **Repository:** https://github.com/mmatyas/pegasus-frontend. Downloads: GitHub releases and https://pegasus-frontend.org.
- **OS:** Windows, Linux, macOS, Android, Raspberry Pi and Odroid.
- **License:** GPL-3.0-or-later, **with Section 7 additional terms**:
  - Use of the names and logos "Pegasus Frontend / Pegasus Launcher / Pegasus" is limited to unmodified copies.
  - A significantly modified fork must not use them without written consent.
  - There is an indemnification clause.
- **Releases:** only a rolling "Continuous build" (2026-11-11). The last named weekly release was 2024-10-05 (Alpha 16 was 2022). Commits are sparse (20 commits span 2026-03-31 to 2026-11-11). A recent commit added "a setting to delay or skip hiding Pegasus after launching a game".
- **Integration:**
  - `metadata.pegasus.txt` (UTF-8, LF) defines `collection:` with `extensions:` and `files:`, plus a `launch:` command using `{file.path}`.
  - It also reads EmulationStation gamelists and other sources.
  - Themes are QML, so they are fully programmable.
  - Build: Qt 5.15 and SDL2.
- **Assessment:** the most flexible UI, but release cadence and the trademark terms make it a weaker base to fork or ship.

### 2.4 RetroArch

- **Repository:** https://github.com/libretro/RetroArch. Downloads: https://www.retroarch.com (also Steam, Flathub and app stores).
- **License:** GPL-3.0 (`COPYING`). **Core licenses vary.** Several popular cores carry **non-commercial** licenses (snes9x and Genesis Plus GX are commonly cited; check each core's license before bundling). Bundling cores in a commercial or "sold preinstalled" product needs a per-core license review.
- **Latest release:** v1.22.2 (2025-11-20), after v1.22.0 (2025-11-14). **No stable release in the 12 months since.** `master` is very active (20 commits on 2026-11-18 alone), and nightlies are on the buildbot.
- **Role:** the multi-system emulation backend that Playnite, ES-DE, RetroBat, EmuDeck and Pegasus all launch (`retroarch -L <core> <rom>`). Its own menus are controller-first, and `.lpl` playlists can act as a minimal hub, but it does not manage PC or store games.

### 2.5 EmuDeck

- **Repositories:** https://github.com/dragoonDorise/EmuDeck (Linux/SteamOS bash scripts, GPL-3.0), https://github.com/EmuDeck/emudeck-we (Windows, PowerShell, GPL-3.0), and https://github.com/EmuDeck/emudeck-electron (Electron GUI, MIT; the GUI components submodule is GPL-3.0). Downloads: https://www.emudeck.com. Manual: https://manual.emudeck.com (not reachable here).
- **Releases:** scripts repo 2.7 (2026-08-27) and "2.7 EA" (2026-09-14). The Electron app has v2.7.2-beta.425 and unstable.138, plus Flatpak early-unstable builds (2026-11-04).
- **What it does:**
  - creates the ROM folder layout;
  - downloads emulators (there is an `emulators-mirror` repo);
  - writes emulator configs and controller layouts;
  - installs and configures **Steam ROM Manager**, **ES-DE** (Steam Deck AppImage) and Pegasus, plus compressor tools.
- **OS:** SteamOS/Linux and Windows are confirmed. The Android beta is from secondary sources, and **macOS is unverified** because third-party sources contradict each other.
- **Relevance:** this is the model for our "setup companion". GPL-3.0 means copying its scripts makes our companion GPL. Instead, reuse its approach, or invoke it as a separate program.

### 2.6 Steam ROM Manager (SRM)

- **Repository:** https://github.com/SteamGridDB/steam-rom-manager. GPL-3.0. Windows (exe, msi, Chocolatey), macOS (dmg), Linux (AppImage, deb, Flathub), and CLI builds for x64 and arm64.
- **Latest release:** 2.6.3 (2026-11-11). Releases 2.6.0 to 2.6.3 all came out in November 2026.
- **What it does:**
  - Adds ROMs (Glob, Glob-regex and Manual parsers) and games from Epic, GOG Galaxy, EA, Amazon, Ubisoft, Xbox/UWP, Battle.net, itch.io and Legendary to Steam as non-Steam shortcuts.
  - Adds artwork (SteamGridDB) and controller templates.
- **Hub angle:** on SteamOS, **Steam Gaming Mode is already the console hub**. SRM populates it, and Steam handles launch and return. Steam generally needs to be closed while SRM writes shortcuts; this is from community knowledge, not the README (unverified).

### 2.7 RetroBat

- **Repository:** https://github.com/RetroBat-Official/retrobat (plus its EmulationStation fork and `emulatorLauncher` repos). Downloads: https://www.retrobat.org.
- **OS:** Windows 8.1, 10 and 11. Needs the VC++ runtimes and DirectX; XInput pads are recommended.
- **License:** code LGPL-3.0, except where upstream licenses apply. Text and graphic content CC BY-NC-SA 4.0. **"Selling RetroBat on preinstalled machines or storage devices is not allowed."** This is a real redistribution constraint for any commercial hub.
- **Latest release:** v8.3.1.1 (2026-10-17); beta 8.4.0 (2026-11-07). About monthly cadence in 2026.
- **Role:** a Windows emulation appliance with automatic emulator download and configuration, and a portable mode. It is not a PC/store game library.

### 2.8 LaunchBox / Big Box (proprietary)

- **Source:** closed source, from Unbroken Software. Downloads: https://www.launchbox-app.com.
- **License:** proprietary freeware. Big Box (the controller-driven fullscreen UI) and other features need a paid Premium license. Pricing in third-party sources conflicts, so it is unverified. **It cannot be redistributed, forked or bundled.**
- **Latest release:** LaunchBox for Windows 14.0 (2026-08-15). 13.28 grew into 14.0, which added a controller-first Filter/Sort in Big Box and "Shutdown Applications". Before that, 13.27 (2026-05-13). Versions 14.0.1 and 14.1 are reported by third parties and are unverified. *(All via search index; the changelog is at feedback.launchbox-app.com.)*
- **OS:** Windows; there is also a separate LaunchBox for Android. There is no macOS version. A Linux version was announced as in development, targeting 2027 *(via search index)*.
- **Assessment:** a strong user product, but a non-starter as a foundation because we cannot ship or modify it.

### 2.9 Lutris

- **Repository:** https://github.com/lutris/lutris. GPL-3.0. Linux only. Distributed through distro packages, the repo's `debian/` and `packaging/` folders, and Flathub (`net.lutris.Lutris`; the README does not mention Flatpak). Python and GTK.
- **Latest release:** v0.5.22 (2026-02-26); before that, v0.5.21 and v0.5.20 (February 2026) and v0.5.19 (2025-02-23). Active commits to 2026-11-18 (mypy and typing work).
- **Integration:**
  - Runners (Wine/Proton, emulators, native) are configured in `runners/*.yml`, with settings that cascade from system to runner to game.
  - YAML installers.
  - CLI: `lutris -l` (list games), `-i` (install from YAML), `-e` (execute with the Lutris runtime), and `lutris:rungame/<slug>` URIs. These make it easy for a hub to drive Lutris.
- No dedicated controller fullscreen mode was found. It is a backend, not a hub UI.

### 2.10 Heroic Games Launcher

- **Repository:** https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher. GPL-3.0. Electron.
- **OS:** Windows 10/11, macOS 14+, Linux (Ubuntu LTS, Fedora, Arch), and SteamOS through Discover (Flatpak).
- **Packaging:** Flathub, AppImage, tar.xz, deb, rpm, AUR, nixpkgs, WinGet, setup or portable exe, Homebrew cask, and dmg.
- **Latest release:** 2.22.4 "Hotfix 4" (2026-10-15); the 2.22 "Hajrudin" line started 2026-05-16. Very active (for example, "Heroic Backup System and Wizard" was merged 2026-11-17).
- **Role:** the open-source way to reach **Epic, GOG and Amazon** libraries on all three desktop OSes. Playnite, ES-DE and SRM can all launch Heroic games: Playnite has community library plugins, ES-DE has import rules, and SRM has a Legendary parser. A `heroic://launch/...` protocol exists, but this was not verified in the README.

### 2.11 Other credible options (brief)

- **RetroDECK:** https://github.com/RetroDECK/RetroDECK. A Flatpak that bundles ES-DE with emulators. 0.10.10b (2026-10-03). The ES-DE user guide recommends it as the easiest SteamOS install. License unverified.
- **Steam Big Picture / Gaming Mode:** not open source, but on SteamOS it is the system shell. Pair it with SRM rather than replacing it.

---

## 3. Recommendation

### Windows: **Playnite 10.x in Fullscreen mode**, with a C# setup-companion plugin

- It is the only open-source (MIT) candidate that covers **both PC store libraries and emulation**. It has library plugins for Steam, Epic, GOG, EA, Battle.net and others, plus YAML emulator profiles with auto-detection.
- It has a controller-first Fullscreen mode with themes, and a large plugin SDK, including first-run settings views and game lifecycle events.
- **Return-to-hub is solved:** five tracking modes (Process, OriginalProcess, Directory/Folder, ProcessName, Default) handle launcher stubs and forking emulators, and `AfterGameClose = Restore` brings the hub back.
- The MIT license allows bundling a portable Playnite with our companion.
- **Risks:**
  - The P10 stack (.NET Framework 4.6.2, 32-bit, SDK 6.18) is a dead end. P11 moves to .NET 10, uses a single plugin type and drops PowerShell, and its date is unknown.
  - Keep the companion's core logic outside the plugin, and avoid PowerShell extensions.
  - For emulation-only Windows setups, ES-DE (MIT) is a fine alternative. RetroBat's no-sale clause and CC BY-NC-SA content rule it out for any commercial or preinstalled distribution.

### Linux / SteamOS: **ES-DE**, launched as a non-Steam game from Steam Gaming Mode, with SRM, Heroic and Lutris as backends

- ES-DE is MIT, cross-platform and actively released (3.5.0, September 2026), and runs on Steam Deck as a self-updating AppImage.
- `custom_systems/es_systems.xml` and `es_find_rules.xml` give a clean, documented emulator integration point, and `game-start` / `game-end` scripts give hooks for a companion.
- By default it suspends and resumes on process exit, so returning to the hub is handled. For Steam games use `%RUNINBACKGROUND%`, and accept that the return is detected on wakeup.
- On SteamOS, Steam Gaming Mode remains the outer shell. Use SRM to put ES-DE itself, or individual games, into Steam.
- Use Heroic (Flatpak) for Epic, GOG and Amazon, and Lutris (`lutris:rungame/…`) for other PC games. Both are reachable from ES-DE commands.
- Use EmuDeck or RetroDECK as references, or as optional installers, for emulator provisioning. Do not fork them because of GPL-3.0.
- Playnite has no Linux build: P11 will not support Linux, and Linux comes "after P11".

### macOS: **ES-DE** (plus Heroic for store games)

- It is one of only a few candidates with official macOS builds (ARM and x86), along with Pegasus, RetroArch, SRM and Heroic. It is MIT and released regularly, and uses the same config model as Linux, so one integration layer covers both.
- Pegasus is the fallback if we need fully custom QML UIs. Its release cadence and trademark terms make it the riskier base.
- **Caveats** (from the ES-DE user guide): weak controller support on macOS, and no Vulkan, which means fewer emulators.
- Playnite and LaunchBox do not exist on macOS. Heroic (macOS 14+) covers Epic, GOG and Amazon, and RetroArch (GPL-3.0) is the main emulator backend.

### Cross-platform architecture implication

- Use **two frontends behind one companion**: Playnite on Windows and ES-DE on Linux, SteamOS and macOS.
- The companion owns emulator download and configuration, and writes either Playnite emulator records or ES-DE `custom_systems` XML.
- Keep RetroArch cores out of any bundled, sold distribution until each core's license has been checked.

---

## 4. Surprising findings

1. **Playnite 11 changes the extension model.** It moves to .NET 10, merges the three plugin types into one, and **removes PowerShell extensions** *(alpha docs, via search index)*. P10 is still shipping releases often (10.57 to 10.64 between September and November 2026).
2. **RetroArch has not shipped a stable release in a year.** v1.22.2 (2025-11-20) is still the latest, even though commits land daily.
3. **ES-DE moved its download and updater infrastructure** from GitLab to `updates.es-de.org` (2026-11-01). Its Android build is paid; the desktop builds are free and MIT.
4. **RetroBat forbids selling it preinstalled,** and its non-code content is CC BY-NC-SA.
5. **Pegasus's GPL has Section 7 trademark terms,** and it has had no tagged release since 2024 (rolling builds only).
6. **LaunchBox went from 13.27 straight to 14.0** (August 2026) and plans a Linux version for 2027. It is still proprietary.

---

## Sources (accessed 2026-11-18)

Directly fetched:

- Playnite repo and README: https://github.com/JosefNemec/Playnite, https://raw.githubusercontent.com/JosefNemec/Playnite/master/README.md
- Playnite LICENSE: https://raw.githubusercontent.com/JosefNemec/Playnite/master/LICENSE.md
- Playnite releases: https://github.com/JosefNemec/Playnite/releases.atom, https://github.com/JosefNemec/Playnite/releases
- Playnite commits: https://github.com/JosefNemec/Playnite/commits/master.atom
- Playnite source files:
  - https://raw.githubusercontent.com/JosefNemec/Playnite/master/source/PlayniteSDK/Models/GameAction.cs
  - https://raw.githubusercontent.com/JosefNemec/Playnite/master/source/PlayniteSDK/Plugins/Plugin.cs
  - https://raw.githubusercontent.com/JosefNemec/Playnite/master/source/Playnite/Playnite.csproj
  - https://raw.githubusercontent.com/JosefNemec/Playnite/master/source/Playnite/Settings/PlayniteSettings.cs
  - https://raw.githubusercontent.com/JosefNemec/Playnite/master/source/Tools/Playnite.Toolbox/Program.cs
  - https://raw.githubusercontent.com/JosefNemec/Playnite/master/source/Playnite/Emulation/Emulators/RetroArch/emulator.yaml
- PlayniteSDK on NuGet: https://api.nuget.org/v3-flatcontainer/playnitesdk/index.json, https://api.nuget.org/v3-flatcontainer/playnitesdk/6.18.0/playnitesdk.nuspec
- ES-DE repo and releases API: https://gitlab.com/es-de/emulationstation-de, https://gitlab.com/api/v4/projects/es-de%2Femulationstation-de/releases
- ES-DE raw docs:
  - https://gitlab.com/es-de/emulationstation-de/-/raw/master/LICENSE
  - https://gitlab.com/es-de/emulationstation-de/-/raw/master/README.md
  - https://gitlab.com/es-de/emulationstation-de/-/raw/master/CHANGELOG.md
  - https://gitlab.com/es-de/emulationstation-de/-/raw/master/USERGUIDE.md
  - https://gitlab.com/es-de/emulationstation-de/-/raw/master/INSTALL.md
- RetroArch: https://github.com/libretro/RetroArch/releases.atom, https://github.com/libretro/RetroArch/tags.atom, https://github.com/libretro/RetroArch/commits/master.atom, https://raw.githubusercontent.com/libretro/RetroArch/master/COPYING
- EmuDeck:
  - https://github.com/dragoonDorise/EmuDeck/releases.atom
  - https://raw.githubusercontent.com/dragoonDorise/EmuDeck/main/LICENSE
  - https://github.com/EmuDeck
  - https://github.com/EmuDeck/emudeck-electron
  - https://github.com/EmuDeck/emudeck-electron/releases.atom
  - https://raw.githubusercontent.com/EmuDeck/emudeck-electron/main/LICENSE
  - https://raw.githubusercontent.com/EmuDeck/emudeck-we/main/LICENSE
- Pegasus:
  - https://github.com/mmatyas/pegasus-frontend/releases.atom
  - https://github.com/mmatyas/pegasus-frontend/commits/master.atom
  - https://raw.githubusercontent.com/mmatyas/pegasus-frontend/master/LICENSE.md
  - https://raw.githubusercontent.com/mmatyas/pegasus-frontend/master/README.md
- Steam ROM Manager: https://github.com/SteamGridDB/steam-rom-manager, https://github.com/SteamGridDB/steam-rom-manager/releases.atom, https://raw.githubusercontent.com/SteamGridDB/steam-rom-manager/master/LICENSE
- RetroBat: https://github.com/RetroBat-Official/retrobat, https://github.com/RetroBat-Official/retrobat/releases.atom
- Lutris: https://github.com/lutris/lutris, https://github.com/lutris/lutris/releases.atom, https://github.com/lutris/lutris/commits/master.atom, https://raw.githubusercontent.com/lutris/lutris/master/LICENSE
- Heroic:
  - https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher
  - https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases.atom
  - https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/commits/main.atom
  - https://raw.githubusercontent.com/Heroic-Games-Launcher/HeroicGamesLauncher/main/COPYING
- RetroDECK: https://github.com/RetroDECK/RetroDECK/releases.atom

Via search index only (site not reachable from the research sandbox; re-verify):

- Playnite site and docs: https://playnite.link/, https://playnite.link/download.html, https://api.playnite.link/docs/
- Playnite pages:
  - https://api.playnite.link/docs/manual/library/games/gameActions.html
  - https://api.playnite.link/docs/manual/advanced/cmdlineArguments.html
  - https://api.playnite.link/docs/manual/features/emulationSupport/addingNewEmulators.html
- Playnite 11 alpha docs:
  - https://api.playnite.link/docs/wpfdevel11/manual/intro.html
  - https://api.playnite.link/docs/wpfdevel11/manual/changelog.html
  - https://api.playnite.link/docs/wpfdevel11/manual/plugins.html
- Playnite Linux plans:
  - https://www.gamingonlinux.com/2025/11/playnite-may-get-a-linux-version-during-2026-as-the-creator-plans-a-move-to-linux/
  - https://gamingonlinux.com/2025/02/popular-game-launcher-playnite-will-get-linux-support-but-its-still-a-while-away
- RetroArch: https://www.retroarch.com/, https://forums.libretro.com/t/version-1-22-0-to-1-22-2-stable-release-but-no-announcements/49150
- EmuDeck: https://manual.emudeck.com/, https://emudeck.github.io/frequently-asked-questions/windows
- ES-DE site: https://es-de.org
- Pegasus docs: https://pegasus-frontend.org/docs/user-guide/meta-files/, https://pegasus-frontend.org/docs/dev/meta-syntax/
- LaunchBox:
  - https://feedback.launchbox-app.com/changelog/launchbox-for-windows-140
  - https://feedback.launchbox-app.com/changelog/launchbox-for-windows-1327
  - https://emulation.gametechwiki.com/index.php/BigBox
  - https://gamingonlinux.com/2026/08/game-launcher-launchbox-should-get-a-linux-version-in-2027
- RetroBat site: https://www.retrobat.org
