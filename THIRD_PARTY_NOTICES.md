# Third-party notices

DD Hub does **not** bundle or redistribute any emulator, emulator core, BIOS, firmware or
commercial game. It finds and starts copies **you** install. The only third-party content in this
repository is listed below.

## Bundled content

### Libbet and the Magic Floor (`content/homebrew/libbet/`)

- Game Boy homebrew by Damian Yerrick. Upstream: https://github.com/pinobatch/libbet
- Built unmodified from source: commit `1232e71dc1ac852786ad9825316e19d2b341bc4a` (2026-07-30) with RGBDS
  v0.9.4 (`d1829ed`). ROM SHA-256: `71fb43fa90bf2dfa4110e851a3368b5de74ed08e09055c8ebb25f3029a4fbf71`.
- License: zlib (code and assets; repository has a single license). Full text: `content/homebrew/libbet/LICENSE`.
  - Copyright 2002, 2012 Martin Korth; Copyright 2018, 2024 Damian Yerrick.
- `libbet.png` is a screenshot of the game itself, taken during DD Hub's verification run.
- `UPSTREAM_README.md` is the upstream README, copied verbatim.

## Runtime dependencies (installed by pip, not vendored)

| Component | License | Notes |
|---|---|---|
| pygame-ce | LGPL-2.1-or-later | Used as an unmodified, dynamically installed library. If you ever ship a frozen build (PyInstaller etc.), include the LGPL text and the notices of the libraries inside the pygame-ce wheel (SDL2 zlib, FreeType, libpng, etc.) and allow relinking. |
| SDL2 (inside pygame-ce) | zlib | |
| psutil | BSD-3-Clause | |

## Programs DD Hub can launch (user-installed; never bundled)

See `docs/compatibility-matrix.md` for each program's license. Note in particular:

- **Non-commercial / no-derivatives licenses:** DuckStation (CC BY-NC-ND 4.0), FinalBurn Neo and Genesis Plus GX cores
  (non-commercial). Fine to launch your own copy; do not bundle them in anything distributed or sold.
- **RetroArch** is GPL-3.0. Bundling it would require shipping its source offer; DD Hub only launches your installation.

Detailed research with sources (accessed 2026-11-18): `docs/research/games-and-licenses.md`.
