"""Python build runner: a third source for the standard library that does not look like a ZIP download (idempotent).

A student still got "TECHNICAL RUNNER FAILURE ... Program terminated with exit(1)" after the second source was
added, in Chrome and Edge and on a phone hotspot. In a browser test this exact message appears when
python_stdlib.zip is blocked or replaced on both sources (CDN and this site), which a device-level filter such as
antivirus web protection or a browser extension can do for every site.

- vendor/pyodide/0.26.4/python_stdlib.dat holds the same bytes as python_stdlib.zip, each XOR 90, so it is not
  recognized as an archive. When Python does not start from the CDN or from the site copy, the worker downloads
  the .dat file, restores the original bytes and passes them to Pyodide as its standard library.
- The final message names the likely device-level causes and what to try.

Applies to the engine template (tools/apply_assignment_build.py), builds.js and every page with the inlined engine.
"""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
PAGES = [f'lectures/iscarb/Ch{c}-FBR-Student-Assignment.html' for c in (12, 13, 14, 15, 16, 17, 20)] + ['assignment-example.html']
VENDOR = ROOT / 'vendor/pyodide/0.26.4'
KEY = 90

JS = [
    ("self.py=await loadPyodide({indexURL:m.base});",
     "var o={indexURL:m.base};if(m.std){var q=await fetch(m.base+m.std);if(!q.ok)throw Error('Python could not start: the standard library returned '+q.status);"
     f"var a=new Uint8Array(await q.arrayBuffer());for(var i=0;i<a.length;i++)a[i]^={KEY};o.stdLibURL=URL.createObjectURL(new Blob([a],{{type:'application/zip'}}));}}"
     "self.py=await loadPyodide(o);"),
    ("'vendor/pyodide/0.26.4/';}catch(e){return '';}})(),src=BASE;",
     "'vendor/pyodide/0.26.4/';}catch(e){return '';}})(),src=BASE,std='';"),
    ("w.postMessage(Object.assign({base:src,harness:HARNESS},msg));",
     "w.postMessage(Object.assign({base:src,std:std,harness:HARNESS},msg));"),
    ("function load(){return call({kind:'load'},120000).catch(function(e){if(!MIRROR||src===MIRROR)throw e;"
     "if(worker){try{worker.terminate();}catch(x){}worker=null;}src=MIRROR;return call({kind:'load'},120000);});}",
     "function load(){return call({kind:'load'},120000).catch(function(e){if(!MIRROR||(src===MIRROR&&std))throw e;"
     "if(worker){try{worker.terminate();}catch(x){}worker=null;}if(src!==MIRROR)src=MIRROR;else std='python_stdlib.dat';return load();});}"),
    ("?'Python could not be downloaded on this network. Try another network (for example a phone hotspot) or another browser, then run again. Details: ':'')",
     "?'Python could not be downloaded or started on this device. Antivirus web protection, a network filter or a browser extension can block its files. "
     "Try another device (for example a lab computer), or another network, then run again. Details: ':'')"),
]


def once(text, old, new, where):
    if new in text and (old not in text or old in new):
        return text
    assert text.count(old) == 1, f'{where}: expected 1 occurrence of {old[:60]!r}, found {text.count(old)}'
    return text.replace(old, new)


def encoded_stdlib():
    raw = (VENDOR / 'python_stdlib.zip').read_bytes()
    enc = bytes(b ^ KEY for b in raw)
    out = VENDOR / 'python_stdlib.dat'
    if not out.exists() or out.read_bytes() != enc:
        out.write_bytes(enc)
    assert hashlib.sha256(bytes(b ^ KEY for b in out.read_bytes())).digest() == hashlib.sha256(raw).digest()


def main():
    encoded_stdlib()
    for rel in ['tools/apply_assignment_build.py', 'curriculum/learning-path/builds.js'] + PAGES:
        p = ROOT / rel
        t = p.read_text(encoding='utf-8')
        for old, new in JS:
            t = once(t, old, new, rel)
        p.write_text(t, encoding='utf-8')
    readme = VENDOR / 'README.txt'
    t = readme.read_text(encoding='utf-8')
    note = ('\npython_stdlib.dat: the bytes of python_stdlib.zip, each XOR 90. The runner uses it as a third source when '
            'python_stdlib.zip is blocked on the device (tools/apply_runner_stdlib.py).\n')
    if 'python_stdlib.dat' not in t:
        readme.write_text(t.rstrip('\n') + '\n' + note, encoding='utf-8')
    print('Runner standard-library source applied to the engine template, builds.js and', len(PAGES), 'pages')


if __name__ == '__main__':
    main()
