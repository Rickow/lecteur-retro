#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — génère lecteur-retro.html (12 systèmes) à partir de la coque de base.

  python3 build.py                         → lecteur-retro.html (SANS BIOS, publiable)
  python3 build.py --bios chemin/neogeo.zip → lecteur-retro-neogeo.html (BIOS Neo Geo inliné, PERSO)

Étapes : télécharge les cores (retroarch-emscripten-build@v1.22.2), compresse tout en gzip+base64
(décompressé au runtime via DecompressionStream), ajoute la map CORES, les façades, la détection.
Le BIOS Neo Geo peut être chargé au runtime (stocké en IndexedDB) OU inliné (--bios).
Aucune ROM/BIOS n'est téléchargée par le script (voir CREDITS.md).
"""
import base64, gzip, re, sys, zipfile, io, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC  = ROOT / 'base' / 'lecteur-retro.base.html'
CD   = ROOT / 'cores'
CORE_BASE = "https://cdn.jsdelivr.net/gh/arianrhodsandlot/retroarch-emscripten-build@v1.22.2/retroarch"

DL = {   # core libretro -> préfixe d'id de blob
  'genesis_plus_gx':  'core-md',
  'fbalpha2012':      'core-arcade',   # CPS-1 / CPS-2 / Neo Geo
  'mednafen_pce_fast':'core-pce',
  'handy':            'core-lynx',
  'mednafen_ngp':     'core-ngp',
  'mednafen_wswan':   'core-wswan',
}

def fetch_cores():
    CD.mkdir(exist_ok=True)
    for core in DL:
        js, wasm = CD/f'{core}_libretro.js', CD/f'{core}_libretro.wasm'
        if js.exists() and wasm.exists(): continue
        print(f'  téléchargement {core}…')
        data = urllib.request.urlopen(f'{CORE_BASE}/{core}_libretro.zip', timeout=180).read()
        with zipfile.ZipFile(io.BytesIO(data)) as z: z.extractall(CD)

def enc_gz(raw: bytes) -> str:
    return base64.b64encode(gzip.compress(raw, 9)).decode('ascii')
def rep(h, old, new, what, n=1):
    c = h.count(old)
    if c != n: sys.exit(f"[ÉCHEC] '{what}': attendu {n}, trouvé {c}")
    return h.replace(old, new)

def main():
    bios_path = None
    if '--bios' in sys.argv:
        bios_path = Path(sys.argv[sys.argv.index('--bios') + 1])
        if not bios_path.is_file(): sys.exit(f"BIOS introuvable : {bios_path}")
    out = ROOT / ('lecteur-retro-neogeo.html' if bios_path else 'lecteur-retro.html')

    if not SRC.exists(): sys.exit(f"Coque de base introuvable : {SRC}")
    fetch_cores()
    h = SRC.read_text()

    # A) compresser les 6 blobs EXISTANTS in-place (nes/snes/gba × js+wasm)
    for cid in ['core-nes-js','core-nes-wasm','core-snes-js','core-snes-wasm','core-gba-js','core-gba-wasm']:
        m = re.search(r'(id="'+cid+r'">)([A-Za-z0-9+/=]+)(</script>)', h)
        if not m: sys.exit(f"[ÉCHEC] blob existant introuvable: {cid}")
        h = h[:m.start(2)] + enc_gz(base64.b64decode(m.group(2))) + h[m.end(2):]

    # B) inliner les nouveaux cores (gzippés) + éventuellement le BIOS Neo Geo
    ids = {}
    for core, pfx in DL.items():
        ids[pfx+'-js']   = CD/f'{core}_libretro.js'
        ids[pfx+'-wasm'] = CD/f'{core}_libretro.wasm'
    inserts = "".join(f'  <script type="text/plain" id="{cid}">{enc_gz(fp.read_bytes())}</script>\n'
                      for cid, fp in ids.items())
    if bios_path:
        inserts += f'  <script type="text/plain" id="bios-neogeo">{enc_gz(bios_path.read_bytes())}</script>\n'
    h = rep(h, '\n  <script>(function(global, factory)',
            '\n' + inserts + '\n  <script>(function(global, factory)', "ancre lib")

    # C) décompression runtime + résolution BIOS Neo Geo
    old_cb = "    function coreBlobs(name){ var c=CORES[name]; return { js:new Blob([b64ToU8(c.jsId)],{type:'application/javascript'}), wasm:new Blob([b64ToU8(c.wasmId)],{type:'application/wasm'}) }; }"
    new_cb = ("    async function gunzip(u8){ if(u8.length>2&&u8[0]===0x1f&&u8[1]===0x8b){"
              " if(typeof DecompressionStream!=='function') throw new Error('D\\u00e9compression gzip non support\\u00e9e par ce navigateur (iOS 16.4+ / r\\u00e9cent requis).');"
              " var s=new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'));"
              " return new Uint8Array(await new Response(s).arrayBuffer()); } return u8; }\n"
              "    async function coreBlobs(name){ var c=CORES[name]; var js=await gunzip(b64ToU8(c.jsId)), wasm=await gunzip(b64ToU8(c.wasmId));"
              " return { js:new Blob([js],{type:'application/javascript'}), wasm:new Blob([wasm],{type:'application/wasm'}) }; }\n"
              "    async function resolveNeoBios(){"
              " try{ var el=document.getElementById('bios-neogeo'); if(el&&el.textContent.trim().length>10) return await gunzip(b64ToU8('bios-neogeo')); }catch(e){}"
              " try{ var st=await idbGet('bios:neogeo'); if(st) return new Uint8Array(st.buf?st.buf:st); }catch(e){}"
              " return null; }")
    h = rep(h, old_cb, new_cb, "coreBlobs+bios")
    h = rep(h, "blobs=coreBlobs(curCore)", "blobs=await coreBlobs(curCore)", "await coreBlobs", n=2)

    # câblage BIOS dans launchRom : résoudre + passer à Nostalgist
    h = rep(h, "        var blobs=await coreBlobs(curCore), romBlob=new Blob([u8],{type:'application/octet-stream'});",
            "        var blobs=await coreBlobs(curCore), romBlob=new Blob([u8],{type:'application/octet-stream'});\n"
            "        var _bios=CORES[curCore].neobios?await resolveNeoBios():null;", "resolve bios launchRom")

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
      fbalpha2012:{jsId:'core-arcade-js',wasmId:'core-arcade-wasm',aspect:4/3,exts:['zip'],label:'Arcade (CPS / Neo Geo)',face:FACE_FIGHT,noSh:true,se:['Coin','Start'],keepName:true,neobios:true},
      mednafen_pce_fast:{jsId:'core-pce-js',wasmId:'core-pce-wasm',aspect:4/3,exts:['pce'],label:'PC Engine',face:FACE_DUO,noSh:true},
      handy:{jsId:'core-lynx-js',wasmId:'core-lynx-wasm',aspect:80/51,exts:['lnx'],label:'Atari Lynx',face:FACE_DUO,noSh:true},
      mednafen_ngp:{jsId:'core-ngp-js',wasmId:'core-ngp-wasm',aspect:160/152,exts:['ngp','ngc'],label:'Neo Geo Pocket',face:FACE_DUO,noSh:true},
      mednafen_wswan:{jsId:'core-wswan-js',wasmId:'core-wswan-wasm',aspect:14/9,exts:['ws','wsc'],label:'WonderSwan',face:FACE_DUO,noSh:true}
    };"""
    h = rep(h, old_cores, new_cores, "map CORES")

    # F) ngCore + arcade keepName (nom du romset) + bios dans les options de lancement
    h = rep(h, "core:curCore,", "core:(CORES[curCore].ngCore||curCore),", "core:curCore", n=2)
    # BIOS arcade = écrit À CÔTÉ du jeu (2e fichier rom -> contentDirectory), car FBA le cherche là.
    # RetroArch charge rom[0] (le jeu) ; rom[1] (neogeo.zip) est juste posé dans le même dossier.
    h = rep(h, "rom:{ fileName:'game.'+det.ext, fileContent:romBlob },",
            "rom:(_bios?[{fileName:(CORES[curCore].keepName?curName+'.'+curExt:'game.'+det.ext),fileContent:romBlob},{fileName:'neogeo.zip',fileContent:new Blob([_bios])}]"
            ":{fileName:(CORES[curCore].keepName?curName+'.'+curExt:'game.'+det.ext),fileContent:romBlob}),", "rom(+bios) launchRom")
    h = rep(h, "rom:{fileName:'game.'+curExt,fileContent:new Blob([curBytes])}, sram:sram,",
            "rom:{fileName:(CORES[curCore].keepName?curName+'.'+curExt:'game.'+curExt),fileContent:new Blob([curBytes])}, sram:sram,", "fileName SRAM")

    # G) buildPad : labels Mode/Coin
    h = rep(h,
      "+'<div class=\"se\"><button data-btn=\"select\">Select</button><button data-btn=\"start\">Start</button></div>';",
      "+'<div class=\"se\"><button data-btn=\"select\">'+((C.se&&C.se[0])||'Select')+'</button><button data-btn=\"start\">'+((C.se&&C.se[1])||'Start')+'</button></div>';",
      "labels se")

    # H) robustesse detect() : magic-bytes Genesis + Lynx
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

    # J) BIOS Neo Geo : input + bouton d'accueil + handlers
    h = rep(h, '  <input type="file" id="file-sram"  accept=".srm,.sav,application/octet-stream">',
            '  <input type="file" id="file-sram"  accept=".srm,.sav,application/octet-stream">\n'
            '  <input type="file" id="file-bios"  accept=".zip,application/octet-stream">', "input bios")
    h = rep(h, '<div class="hint">.nes (NES) · .sfc/.smc (SNES) · .gba (GBA)<br>Rien n\'est envoyé : tout reste sur l\'appareil.</div>',
            '<div class="hint">.nes · .sfc/.smc · .gba · .gb/.gbc · .md (Mega Drive) · .sms/.gg · .pce · .lnx · .ngp · .ws · .zip (arcade CPS / Neo Geo)<br>Rien n\'est envoyé : tout reste sur l\'appareil.</div>\n'
            '      <button id="load-bios" style="margin-top:.6rem;font:inherit;font-size:.62rem;padding:5px 10px;border-radius:8px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.05);color:#9aa;cursor:pointer">⚙ Charger le BIOS Neo Geo (.zip)</button>', "bouton bios")
    h = rep(h, "    (async function init(){",
            "    document.getElementById('load-bios').addEventListener('click',function(){document.getElementById('file-bios').click();});\n"
            "    document.getElementById('file-bios').addEventListener('change',async function(e){ var f=e.target.files[0]; e.target.value=''; if(!f) return;\n"
            "      try{ var u8=new Uint8Array(await f.arrayBuffer()); await idbSet('bios:neogeo',{buf:u8.buffer}); log('BIOS Neo Geo enregistré ('+f.name+', '+((u8.length/1024)|0)+' Ko).','ok'); }catch(err){ showLog(); log('BIOS : '+(err&&(err.message||err)),'err'); } });\n"
            "    (async function init(){", "handlers bios")

    # L) diagnostic : log détaillé RetroArch + capture console -> journal de la page
    h = rep(h, "Object.assign({video_smooth:false},BINDS)",
            "Object.assign({video_smooth:false,log_verbosity:true,frontend_log_level:0},BINDS)",
            "log_verbosity", n=2)
    h = rep(h, "    window.addEventListener('error', function(e){ showLog(); log('Erreur : '+(e.message||e),'err'); });",
            "    (function(){ var _l=console.log.bind(console),_w=console.warn.bind(console),_e=console.error.bind(console);\n"
            "      function s(a){ try{ return Array.prototype.map.call(a,function(x){return (x&&typeof x==='object')?JSON.stringify(x):String(x);}).join(' ').slice(0,300); }catch(e){ return ''; } }\n"
            "      console.log=function(){ _l.apply(null,arguments); try{ log(s(arguments),'muted'); }catch(e){} };\n"
            "      console.warn=function(){ _w.apply(null,arguments); try{ log('\\u26a0 '+s(arguments),'muted'); }catch(e){} };\n"
            "      console.error=function(){ _e.apply(null,arguments); try{ showLog(); log('\\u2716 '+s(arguments),'err'); }catch(e){} }; })();\n"
            "    window.addEventListener('error', function(e){ showLog(); log('Erreur : '+(e.message||e),'err'); });",
            "capture console")

    # K) accept + titre + crest
    h = rep(h, 'accept=".nes,.sfc,.smc,.gba,application/octet-stream"',
            'accept=".nes,.sfc,.smc,.gba,.gb,.gbc,.md,.gen,.smd,.sms,.gg,.pce,.lnx,.ngp,.ngc,.ws,.wsc,.zip,application/octet-stream"', "accept")
    h = rep(h, '<title>Lecteur rétro — NES / SNES / GBA</title>', '<title>Lecteur rétro — 13 systèmes</title>', "title")
    h = rep(h, 'Émulateur · NES / SNES / GBA', 'Émulateur · 13 systèmes rétro', "crest")

    out.write_text(h)
    tag = " (BIOS Neo Geo inliné)" if bios_path else " (sans BIOS)"
    print(f"OK — {out.name} ({out.stat().st_size/1048576:.1f} Mo){tag}")

if __name__ == '__main__':
    main()
