<div align="center">

# 🎮 Lecteur rétro

**A multi-system retro emulator in a single HTML file.**
No install, no server, no dependencies — it runs offline, even from `file://`.

*[Version française](README.fr.md) · [Credits](CREDITS.md) · [Changelog](CHANGELOG.md)*

</div>

---

## What it is

A **single, self-contained HTML file** (engine + cores + everything inlined) that emulates 12
retro systems right in the browser. Built for **iPhone (Safari)** as a web app, but it works
anywhere — Chrome, Firefox, or just by double-clicking the file.

Nothing is uploaded anywhere: **your ROMs stay on your device.**

## Supported systems

| System | Extensions | System | Extensions |
|---|---|---|---|
| NES / Famicom | `.nes` | Sega Master System | `.sms` |
| Super Nintendo | `.sfc` `.smc` | Sega Game Gear | `.gg` |
| Game Boy / Color | `.gb` `.gbc` | PC Engine / TG-16 | `.pce` |
| Game Boy Advance | `.gba` | Atari Lynx | `.lnx` |
| Sega Mega Drive / Genesis | `.md` `.gen` `.smd` | Neo Geo Pocket / Color | `.ngp` `.ngc` |
| Arcade CPS-2 | `.zip` | WonderSwan / Color | `.ws` `.wsc` |

The system is **auto-detected** from the file extension (with a magic-byte fallback for Mega
Drive and Lynx).

## Features

- **One button**: load a ROM from your device, the right emulator starts by itself.
- **ROM history** (up to 12), one-tap relaunch, ✕ to remove.
- **Save states**: save/load in-page, export/import to a file.
- **Game saves** (SRAM): export/import.
- **Multitouch on-screen gamepad**, tailored per system:
  - 8-direction D-pad,
  - **diamond** face (SNES), **2-button** face (NES/GB/GBA/PCE/Lynx/NGP/WS),
  - **Sega 6-button** face (A/B/C · X/Y/Z · Mode),
  - **arcade fighting** face (LP/MP/HP · LK/MK/HK · Coin).
- **Fullscreen**, aspect-correct centered display, built-in debug log.
- **Offline**: once the file is on the device, no network needed.

## Usage

1. Open `lecteur-retro.html` (double-click, or on iPhone add it to the Home Screen via
   *Share → Add to Home Screen*).
2. **Load a ROM** → pick a file.
3. Tap **Play** (required on iOS to unlock audio).

### Special case: CPS-2 arcade

Arcade is stricter than consoles:

- The **`.zip` must be named exactly as its romset**: `sfa3.zip`, `ssf2.zip`, `mvsc.zip`,
  `vsav.zip`, `dstlk.zip`… (the core identifies the game by the filename).
- The romset must match the **FB Alpha 2012 set** (a recent MAME/FBNeo set will have mismatched
  CRCs). No separate BIOS is needed for CPS-2.
- If it fails, open the **log**: the core lists the missing/incorrect files.

## Constraints & limits

- **Memory (iPhone ~1–1.5 GB/tab)**: the ROM is loaded fully into memory. Cartridges
  (NES→GBA, Mega Drive…) are light, no problem.
- **Decompression**: cores are stored gzip-compressed and inflated at runtime →
  requires **iOS 16.4+ / a modern browser** (`DecompressionStream`). Clear message otherwise.
- **Heavy 3D systems** (PSP, N64, Saturn, DS…) are **not** included: they need multi-threaded
  cores (COOP/COEP, i.e. a server), which breaks the "single offline file" design.

## Reproduce / extend

The file is produced by [`build.py`](build.py), which starts from the base shell and inlines the
cores downloaded from `retroarch-emscripten-build@v1.22.2`, compressing them. See [`BUILD.md`](BUILD.md).

## Credits & license

All emulation credit goes to the **libretro** cores and **Nostalgist.js** — see
[`CREDITS.md`](CREDITS.md). The shell is **MIT** ([`LICENSE`](LICENSE)), but because it bundles
**non-commercial** cores (Snes9x, Genesis Plus GX, FB Alpha), the assembled file is for
**personal use only**. **No ROMs/BIOS are provided.**
