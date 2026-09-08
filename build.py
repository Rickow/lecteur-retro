#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — génère lecteur-retro.html (12 systèmes) à partir de la coque de base.

Ce que fait le script :
  1. télécharge les cores libretro manquants depuis retroarch-emscripten-build@v1.22.2 (dans cores/) ;
  2. part de base/lecteur-retro.base.html (la coque 3 systèmes NES/SNES/GBA) ;
  3. compresse TOUS les cores (gzip) + inline en base64, décompressés au runtime (DecompressionStream) ;
  4. ajoute la map CORES, les façades de contrôle, la détection d'extensions.

Usage :  python3 build.py     (depuis la racine du dépôt)
Prérequis : python3, accès réseau pour le 1er build (ensuite cores/ est en cache).
Aucune ROM/BIOS n'est téléchargée : seulement les cores d'émulation (voir CREDITS.md).
"""
import base64, gzip, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC  = ROOT / 'base' / 'lecteur-retro.base.html'
WS   = ROOT / 'lecteur-retro.html'
CD   = ROOT / 'cores'
CORE_BASE = "https://cdn.jsdelivr.net/gh/arianrhodsandlot/retroarch-emscripten-build@v1.22.2/retroarch"

# cores à télécharger + inliner (ceux de la base NES/SNES/GBA sont déjà dans base/, compressés in-place)
DL = {
  'genesis_plus_gx':  'core-md',
  'fbalpha2012_cps2': 'core-cps2',
  'mednafen_pce_fast':'core-pce',
  'handy':            'core-lynx',
  'mednafen_ngp':     'core-ngp',
  'mednafen_wswan':   'core-wswan',
}

def fetch_cores():
    CD.mkdir(exist_ok=True)
    import zipfile, io
    for core in DL:
        js, wasm = CD/f'{core}_libretro.js', CD/f'{core}_libretro.wasm'
        if js.exists() and wasm.exists():
            continue
        url = f'{CORE_BASE}/{core}_libretro.zip'
        print(f'  téléchargement {core}…')
        data = urllib.request.urlopen(url, timeout=120).read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(CD)

def enc_gz(raw: bytes) -> str:
    return base64.b64encode(gzip.compress(raw, 9)).decode('ascii')
def rep(h, old, new, what, n=1):
    c = h.count(old)
    if c != n: sys.exit(f"[ÉCHEC] '{what}': attendu {n}, trouvé {c}")
    return h.replace(old, new)

def main():
    if not SRC.exists():
        sys.exit(f"Coque de base introuvable : {SRC}")
    fetch_cores()
    h = SRC.read_text()

    # A) compresser les 6 blobs EXISTANTS in-place (nes/snes/gba × js+wasm)
    for cid in ['core-nes-js','core-nes-wasm','core-snes-js','core-snes-wasm','core-gba-js','core-gba-wasm']:
        m = re.search(r'(id="'+cid+r'">)([A-Za-z0-9+/=]+)(</script>)', h)
        if not m: sys.exit(f"[ÉCHEC] blob existant introuvable: {cid}")
        h = h[:m.start(2)] + enc_gz(base64.b64decode(m.group(2))) + h[m.end(2):]

    # B) inliner les 6 NOUVEAUX cores (gzippés)
    ids = {}
    for core, pfx in DL.items():
        ids[pfx+'-js']   = CD/f'{core}_libretro.js'
        ids[pfx+'-wasm'] = CD/f'{core}_libretro.wasm'
    inserts = "".join(f'  <script type="text/plain" id="{cid}">{enc_gz(fp.read_bytes())}</script>\n'
                      for cid, fp in ids.items())
    h = rep(h, '\n  <script>(function(global, factory)',
            '\n' + inserts + '\n  <script>(function(global, factory)', "ancre lib")

    # C) décompression runtime : coreBlobs async + gunzip
    old_cb = "    function coreBlobs(name){ var c=CORES[name]; return { js:new Blob([b64ToU8(c.jsId)],{type:'application/javascript'}), wasm:new Blob([b64ToU8(c.wasmId)],{type:'application/wasm'}) }; }"
    new_cb = ("    async function gunzip(u8){ if(u8.length>2&&u8[0]===0x1f&&u8[1]===0x8b){"
              " if(typeof DecompressionStream!=='function') throw new Error('D\\u00e9compression gzip non support\\u00e9e par ce navigateur (iOS 16.4+ / r\\u00e9cent requis).');"
              " var s=new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'));"
              " return new Uint8Array(await new Response(s).arrayBuffer()); } return u8; }\n"
              "    async function coreBlobs(name){ var c=CORES[name]; var js=await gunzip(b64ToU8(c.jsId)), wasm=await gunzip(b64ToU8(c.wasmId));"
              " return { js:new Blob([js],{type:'application/javascript'}), wasm:new Blob([wasm],{type:'application/wasm'}) }; }")
    h = rep(h, old_cb, new_cb, "coreBlobs async")
    h = rep(h, "blobs=coreBlobs(curCore)", "blobs=await coreBlobs(curCore)", "await coreBlobs", n=2)

    # D) façades boutons
    face_anchor = "var FACE_DUO='<div class=\"face duo\"><button class=\"b\" data-btn=\"b\">B</button><button class=\"a\" data-btn=\"a\">A</button></div>';"
    face_add = face_anchor + "\n" \
      + "    var FACE_SEGA6='<div class=\"face six\"><button data-btn=\"l\">X</button><button data-btn=\"x\">Y</button><button data-btn=\"r\">Z</button><button data-btn=\"y\">A</button><button data-btn=\"b\">B</button><button data-btn=\"a\">C</button></div>';\n" \
      + "    var FACE_FIGHT='<div class=\"face six\"><button data-btn=\"y\">LP</button><button data-btn=\"x\">MP</button><button data-btn=\"l\">HP</button><button data-btn=\"b\">LK</button><button data-btn=\"a\">MK</button><button data-btn=\"r\">HK</button></div>';"
    h = rep(h, face_anchor, face_add, "constantes FACE")

    # E) map CORES
    old_cores = """    var CORES={
      fceumm:{jsId:'core-nes-js',wasmId:'core-nes-wasm',aspect:4/3,exts:['nes'],label:'NES',face:FACE_DUO,noSh:true},
      snes9x:{jsId:'core-snes-js',wasmId:'core-snes-wasm',aspect:4/3,exts:['sfc','smc'],label:'Super Nintendo',face:FACE_DIAMOND},
      mgba:{jsId:'core-gba-js',wasmId:'core-gba-wasm',aspect:3/2,exts:['gba'],label:'Game Boy Advance',face:FACE_DUO}
    };"""
    new_cores = """    var CORES={
      fceumm:{jsId:'core-nes-js',wasmId:'core-nes-wasm',aspect:4/3,exts:['nes'],label:'NES',face:FACE_DUO,noSh:true},
      snes9x:{jsId:'core-snes-js',wasmId:'core-snes-wasm',aspect:4/3,exts:['sfc','smc'],label:'Super Nintendo',face:FACE_DIAMOND},
      mgba:{jsId:'core-gba-js',wasmId:'core-gba-wasm',aspect:3/2,exts:['gba'],label:'Game Boy Advance',face:FACE_DUO},
      gb:{ngCore:'mgba',jsId:'core-gba-js',wasmId:'core-gba-wasm',aspect:10/9,exts:['gb','gbc'],label:'Game Boy / Color',face:FACE_DUO,noSh:true},
      genesis_plus_gx:{jsId:'core-md-js',wasmId:'core-md-wasm',aspect:4/3,exts:['md','gen','smd','sms','gg'],label:'Sega Mega Drive / MS / GG',face:FACE_SEGA6,noSh:true,se:['Mode','Start']},
      fbalpha2012_cps2:{jsId:'core-cps2-js',wasmId:'core-cps2-wasm',aspect:4/3,exts:['zip'],label:'Arcade CPS-2',face:FACE_FIGHT,noSh:true,se:['Coin','Start'],keepName:true},
      mednafen_pce_fast:{jsId:'core-pce-js',wasmId:'core-pce-wasm',aspect:4/3,exts:['pce'],label:'PC Engine',face:FACE_DUO,noSh:true},
      handy:{jsId:'core-lynx-js',wasmId:'core-lynx-wasm',aspect:80/51,exts:['lnx'],label:'Atari Lynx',face:FACE_DUO,noSh:true},
      mednafen_ngp:{jsId:'core-ngp-js',wasmId:'core-ngp-wasm',aspect:160/152,exts:['ngp','ngc'],label:'Neo Geo Pocket',face:FACE_DUO,noSh:true},
      mednafen_wswan:{jsId:'core-wswan-js',wasmId:'core-wswan-wasm',aspect:14/9,exts:['ws','wsc'],label:'WonderSwan',face:FACE_DUO,noSh:true}
    };"""
    h = rep(h, old_cores, new_cores, "map CORES")

    # F) ngCore + arcade keepName (nom du romset préservé)
    h = rep(h, "core:curCore,", "core:(CORES[curCore].ngCore||curCore),", "core:curCore", n=2)
    h = rep(h, "rom:{ fileName:'game.'+det.ext, fileContent:romBlob },",
            "rom:{ fileName:(CORES[curCore].keepName?curName+'.'+curExt:'game.'+det.ext), fileContent:romBlob },", "fileName launchRom")
    h = rep(h, "rom:{fileName:'game.'+curExt,fileContent:new Blob([curBytes])}, sram:sram,",
            "rom:{fileName:(CORES[curCore].keepName?curName+'.'+curExt:'game.'+curExt),fileContent:new Blob([curBytes])}, sram:sram,", "fileName SRAM")

    # G) buildPad : labels Mode/Coin
    h = rep(h,
      "+'<div class=\"se\"><button data-btn=\"select\">Select</button><button data-btn=\"start\">Start</button></div>';",
      "+'<div class=\"se\"><button data-btn=\"select\">'+((C.se&&C.se[0])||'Select')+'</button><button data-btn=\"start\">'+((C.se&&C.se[1])||'Start')+'</button></div>';",
      "labels se")

    # H) robustesse detect() : magic-bytes Genesis + Lynx (fallback additif)
    old_det = "      if(u8.length>8 && u8[4]===0x24&&u8[5]===0xFF&&u8[6]===0xAE&&u8[7]===0x51) return {core:'mgba',ext:'gba'};\n      return {core:'snes9x',ext:'sfc'}; }"
    new_det = ("      if(u8.length>8 && u8[4]===0x24&&u8[5]===0xFF&&u8[6]===0xAE&&u8[7]===0x51) return {core:'mgba',ext:'gba'};\n"
               "      if(u8.length>0x104 && u8[0x100]===0x53&&u8[0x101]===0x45&&u8[0x102]===0x47&&u8[0x103]===0x41) return {core:'genesis_plus_gx',ext:'md'};\n"
               "      if(u8.length>4 && u8[0]===0x4C&&u8[1]===0x59&&u8[2]===0x4E&&u8[3]===0x58) return {core:'handy',ext:'lnx'};\n"
               "      return {core:'snes9x',ext:'sfc'}; }")
    h = rep(h, old_det, new_det, "detect magic-bytes")

    # I) CSS façade 6 boutons
    h = rep(h,
      "  #pad .face.duo button{width:var(--k);height:var(--k)} #pad .face.duo .a{margin-bottom:1.4rem}",
      "  #pad .face.duo button{width:var(--k);height:var(--k)} #pad .face.duo .a{margin-bottom:1.4rem}\n"
      "  #pad .face.six{display:grid;grid-template-columns:repeat(3,var(--k));grid-template-rows:repeat(2,var(--k));gap:3px}\n"
      "  #pad .face.six button{border-radius:50%;font-size:.6rem;font-weight:700}",
      "CSS face.six")

    # J) accept + hint + titre + crest
    h = rep(h, 'accept=".nes,.sfc,.smc,.gba,application/octet-stream"',
            'accept=".nes,.sfc,.smc,.gba,.gb,.gbc,.md,.gen,.smd,.sms,.gg,.pce,.lnx,.ngp,.ngc,.ws,.wsc,.zip,application/octet-stream"', "accept")
    h = rep(h, '.nes (NES) · .sfc/.smc (SNES) · .gba (GBA)',
            '.nes · .sfc/.smc · .gba · .gb/.gbc · .md (Mega Drive) · .sms/.gg · .pce · .lnx · .ngp · .ws · .zip (arcade CPS-2)', "hint")
    h = rep(h, '<title>Lecteur rétro — NES / SNES / GBA</title>', '<title>Lecteur rétro — 12 systèmes</title>', "title")
    h = rep(h, 'Émulateur · NES / SNES / GBA', 'Émulateur · 12 systèmes rétro', "crest")

    WS.write_text(h)
    print(f"OK — {WS.name} ({WS.stat().st_size/1048576:.1f} Mo)")

if __name__ == '__main__':
    main()
