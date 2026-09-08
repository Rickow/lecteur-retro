# Reconstruire le fichier

Le fichier livrable `lecteur-retro.html` est **généré** par [`build.py`](build.py) à partir de la
coque de base `base/lecteur-retro.base.html`.

## Prérequis
- **Python 3** (bibliothèque standard uniquement — pas de pip).
- Un **accès réseau** au premier build (pour télécharger les cores). Ensuite ils sont mis en cache
  dans `cores/` (dossier ignoré par git).

## Lancer
```bash
python3 build.py
```
Le script :
1. télécharge les cores manquants depuis `retroarch-emscripten-build@v1.22.2` ;
2. compresse tous les cores (gzip) et les inline en base64 ;
3. écrit `lecteur-retro.html` (~12–13 Mo), décompressé au runtime dans le navigateur.

## Ajouter un système
Cores légers **mono-thread** uniquement (le multi-thread casse le `file://` hors ligne).

1. Trouve le core dans [retroarch-emscripten-build (tag v1.22.2)](https://github.com/arianrhodsandlot/retroarch-emscripten-build/tree/v1.22.2/retroarch).
2. Ajoute-le au dictionnaire `DL` en haut de `build.py` (`'nom_du_core': 'core-<clé>'`).
3. Ajoute une entrée dans la map `CORES` (section E) : `jsId`, `wasmId`, `aspect`, `exts`, `label`,
   `face`, et si besoin `noSh` / `se` / `ngCore` / `keepName` (arcade).
4. Complète `accept` et le hint (section J).
5. `python3 build.py`, puis teste sur l'appareil réel.

## Validation (sans navigateur)
- **Syntaxe** : extraire le dernier `<script>` applicatif et lancer `node --check`.
- **Intégrité** : décoder un blob (base64 → gunzip) et comparer son sha1 au fichier source dans `cores/`.

## Détails techniques utiles
- **Nostalgist mappe le nom `core` → global `libretro_<core>`.** Pour réutiliser un blob sous un
  autre nom (ex. GB/GBC via mGBA), utiliser le champ `ngCore`.
- **Arcade** : le core identifie le jeu par le **nom du fichier** → `keepName:true` conserve le nom
  du romset (`sfa3.zip`) au lieu de le renommer en `game.zip`.
- **Compression** : chaque blob commence par la signature gzip `1f 8b` ; `gunzip()` la détecte,
  sinon laisse passer les données brutes (rétro-compatible).
