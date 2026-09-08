# Changelog

## v2.1.0

Arcade complet + **Neo Geo**.

### ✨ Nouveautés
- Le core arcade passe de CPS-2 seul au **FB Alpha 2012 complet** : **CPS-1, CPS-2 et Neo Geo**
  (AES/MVS), tous en `.zip` auto-détectés par un seul core.
- **BIOS Neo Geo** géré de deux façons : bouton **« Charger le BIOS Neo Geo »** (stocké en IndexedDB,
  jamais dans le fichier publié), ou inliné dans une build perso via `build.py --bios neogeo.zip`.

### ⚠️ Notes
- Neo Geo **exige** son BIOS (`neogeo.zip`, set FB Alpha 2012). Non fourni.
- Le core FBA2012 complet est plus lourd → fichier ~15,8 Mo (dépôt) / ~16,4 Mo (perso avec BIOS).
- Façade arcade partagée (6 boutons) : Neo Geo utilise A/B/C/D parmi ces boutons.

## v2.0.0

De 3 à **12 systèmes**, de vraies façades de contrôle, et un fichier **plus léger** qu'avant.

### ✨ Nouveaux systèmes
- **Game Boy / Color** (`.gb` `.gbc`) — via le core mGBA déjà présent (ratio 10:9).
- **Sega Mega Drive / Master System / Game Gear** (`.md` `.gen` `.smd` `.sms` `.gg`) — Genesis Plus GX.
- **Arcade CPS-2** (`.zip`) — FB Alpha 2012.
- **PC Engine** (`.pce`), **Atari Lynx** (`.lnx`), **Neo Geo Pocket / Color** (`.ngp` `.ngc`),
  **WonderSwan / Color** (`.ws` `.wsc`).

### 🎮 Contrôles
- Façade **Sega 6 boutons** (A/B/C · X/Y/Z · Mode) avec le bon mapping RetroPad.
- Façade **arcade fighting** (LP/MP/HP · LK/MK/HK · Coin).
- Labels de la rangée basse personnalisables par système (Mode/Start, Coin/Start).

### 🪶 Poids
- Tous les cores sont désormais **compressés (gzip)** et décompressés à la volée dans le
  navigateur (`DecompressionStream`). Résultat : **~12,7 Mo** avec 12 systèmes, soit **moins**
  que la version d'origine à 3 systèmes.

### 🛡️ Robustesse
- **Arcade** : le nom du fichier romset (`.zip`) est préservé au lieu d'être renommé `game.zip`
  (le core arcade identifie le jeu par son nom) — corrige le non-chargement des CPS-2.
- Détection par **signature de fichier** en secours pour Mega Drive (`SEGA`) et Lynx (`LYNX`).
- Message d'erreur clair si le navigateur ne sait pas décompresser (trop ancien).

### ⚠️ Notes
- Nécessite **iOS 16.4+ / un navigateur récent** (décompression `DecompressionStream`).
- Les systèmes 3D lourds (PSP/N64/Saturn/DS) restent hors périmètre (cores multi-thread).

---

## v1.0.0

Version initiale : lecteur rétro monopage, hors ligne (`file://`), 3 systèmes — **NES**
(FCEUmm), **Super Nintendo** (Snes9x), **Game Boy Advance** (mGBA) — sur Nostalgist.js.
Historique des ROMs, save states, SRAM, manette tactile.
