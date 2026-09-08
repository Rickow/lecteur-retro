# Crédits

Le **Lecteur rétro** n'est qu'une coque : tout le travail d'émulation est celui des projets
ci-dessous. Merci à leurs auteurs et mainteneurs. Chaque core embarqué **conserve sa licence
d'origine** (voir la colonne Licence).

## Moteur & build

| Composant | Rôle | Dépôt | Licence |
|---|---|---|---|
| **Nostalgist.js** | Moteur qui charge et pilote les cores libretro dans le navigateur | https://github.com/arianrhodsandlot/nostalgist | MIT |
| **retroarch-emscripten-build** | Builds WebAssembly des cores (source exacte, tag `v1.22.2`) | https://github.com/arianrhodsandlot/retroarch-emscripten-build | GPL-3.0 (scripts) |
| **RetroArch / libretro** | API libretro sur laquelle reposent les cores | https://github.com/libretro/RetroArch | GPL-3.0 |

## Cores d'émulation embarqués

| Système | Core | Dépôt | Licence |
|---|---|---|---|
| NES / Famicom | **FCEUmm** | https://github.com/libretro/libretro-fceumm | GPL-2.0 |
| Super Nintendo | **Snes9x** | https://github.com/libretro/snes9x | Snes9x (non-commercial) |
| Game Boy / Color / Advance | **mGBA** | https://github.com/libretro/mgba | MPL-2.0 |
| Sega Mega Drive / Master System / Game Gear | **Genesis Plus GX** | https://github.com/libretro/Genesis-Plus-GX | Genesis Plus GX (non-commercial) |
| Arcade CPS-2 | **FB Alpha 2012** | https://github.com/libretro/fbalpha2012 | FB Alpha (non-commercial) |
| PC Engine / TurboGrafx-16 | **Beetle PCE FAST** (mednafen_pce_fast) | https://github.com/libretro/beetle-pce-fast-libretro | GPL-2.0 |
| Atari Lynx | **Handy** | https://github.com/libretro/libretro-handy | zlib |
| Neo Geo Pocket / Color | **Beetle NeoPop** (mednafen_ngp) | https://github.com/libretro/beetle-ngp-libretro | GPL-2.0 |
| WonderSwan / Color | **Beetle Cygne** (mednafen_wswan) | https://github.com/libretro/beetle-wswan-libretro | GPL-2.0 |

## Note de licence importante

Parce que **Snes9x**, **Genesis Plus GX** et **FB Alpha** sont distribués sous des licences
**non commerciales**, le fichier assemblé `lecteur-retro.html` — qui inclut ces cores — est
**réservé à un usage personnel / non commercial**. Le code de la coque (interface, chargement,
sauvegardes) est fourni sous licence MIT (voir [`LICENSE`](LICENSE)), mais cela ne lève pas les
restrictions des cores embarqués.

Aucune ROM, BIOS ou jeu n'est distribué avec ce projet. Vous devez fournir vos propres fichiers,
dont vous possédez les droits.
