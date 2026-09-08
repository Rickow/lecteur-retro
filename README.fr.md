<div align="center">

# 🎮 Lecteur rétro

**Un émulateur multi-système rétro dans un seul fichier HTML.**
Aucune installation, aucun serveur, aucune dépendance — il fonctionne hors ligne, même en `file://`.

*[English version](README.md) · [Crédits](CREDITS.md) · [Changelog](CHANGELOG.md)*

</div>

---

## Ce que c'est

Un **fichier HTML unique et autonome** (moteur + cores + tout inliné) qui émule 12 systèmes
rétro directement dans le navigateur. Pensé pour **iPhone (Safari)** en application web, mais
fonctionne partout — Chrome, Firefox, ou en ouvrant simplement le fichier par double-clic.

Rien n'est envoyé nulle part : **tes ROMs restent sur ton appareil.**

## Systèmes pris en charge

| Système | Extensions | Système | Extensions |
|---|---|---|---|
| NES / Famicom | `.nes` | Sega Master System | `.sms` |
| Super Nintendo | `.sfc` `.smc` | Sega Game Gear | `.gg` |
| Game Boy / Color | `.gb` `.gbc` | PC Engine / TG-16 | `.pce` |
| Game Boy Advance | `.gba` | Atari Lynx | `.lnx` |
| Sega Mega Drive / Genesis | `.md` `.gen` `.smd` | Neo Geo Pocket / Color | `.ngp` `.ngc` |
| Arcade CPS-2 | `.zip` | WonderSwan / Color | `.ws` `.wsc` |

Le système est **détecté automatiquement** d'après l'extension (avec repli sur la signature du
fichier pour Mega Drive et Lynx).

## Fonctionnalités

- **Un seul bouton** : charge une ROM depuis ton appareil, le bon émulateur démarre tout seul.
- **Historique des ROMs** (jusqu'à 12), relançables en un tap, avec ✕ pour retirer.
- **Sauvegardes d'état** (save states) : sauver / charger dans la page, exporter / importer en fichier.
- **Sauvegardes de jeu** (SRAM) : export / import.
- **Manette tactile multitouch** adaptée à chaque système :
  - croix directionnelle 8 directions,
  - façade **diamant** (SNES), **2 boutons** (NES/GB/GBA/PCE/Lynx/NGP/WS),
  - façade **Sega 6 boutons** (A/B/C · X/Y/Z · Mode),
  - façade **arcade fighting** (LP/MP/HP · LK/MK/HK · Coin).
- **Plein écran**, affichage centré au bon ratio, journal de debug intégré.
- **Hors ligne** : une fois le fichier sur l'appareil, plus besoin de réseau.

## Utilisation

1. Ouvre `lecteur-retro.html` (double-clic, ou ajoute-le à l'écran d'accueil sur iPhone via
   « Partager → Sur l'écran d'accueil »).
2. **Charger une ROM** → choisis un fichier.
3. Appuie sur **Play** (obligatoire sur iOS pour débloquer le son).

### Cas particulier : l'arcade CPS-2

L'arcade, c'est plus exigeant que les consoles :

- Le **`.zip` doit être nommé exactement comme le romset** : `sfa3.zip`, `ssf2.zip`, `mvsc.zip`,
  `vsav.zip`, `dstlk.zip`… (le core identifie le jeu par le nom du fichier).
- Le romset doit correspondre au **set FB Alpha 2012** (un set MAME/FBNeo récent aura des CRC qui
  ne correspondent pas). Pas de BIOS séparé nécessaire pour CPS-2.
- En cas d'échec, ouvre le **journal** : le core y liste les fichiers manquants ou incorrects.

## Contraintes & limites

- **Mémoire (iPhone ~1–1,5 Go/onglet)** : la ROM est chargée entièrement en mémoire. Les
  cartouches (NES→GBA, Mega Drive…) sont légères, aucun souci. Évite les fichiers énormes.
- **Décompression** : les cores sont stockés compressés (gzip) et décompressés à la volée →
  nécessite **iOS 16.4+ / un navigateur récent** (`DecompressionStream`). Message clair sinon.
- **Systèmes 3D lourds** (PSP, N64, Saturn, DS…) ne sont **pas** inclus : ils demandent des cores
  multi-thread (COOP/COEP, donc un serveur) et cassent le principe « un fichier hors ligne ».

## Reproduire / étendre

Le fichier est généré par [`build.py`](build.py), qui part de la coque de base et inline les cores
téléchargés depuis `retroarch-emscripten-build@v1.22.2`, en les compressant. Voir [`BUILD.md`](BUILD.md).

## Crédits & licence

Tout le mérite de l'émulation revient aux projets **libretro** et à **Nostalgist.js** — voir
[`CREDITS.md`](CREDITS.md). La coque est sous licence **MIT** ([`LICENSE`](LICENSE)), mais comme
elle embarque des cores **non commerciaux** (Snes9x, Genesis Plus GX, FB Alpha), le fichier
assemblé est **réservé à un usage personnel**. **Aucune ROM/BIOS n'est fournie.**
