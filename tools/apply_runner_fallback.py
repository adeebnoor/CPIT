"""Python build runner: a second download source and a clearer failure message (idempotent).

A student reported "TECHNICAL RUNNER FAILURE ... Program terminated with exit(1)" on every run, also with
simple code and in a private window. The same message appears when python_stdlib.zip cannot be downloaded
from the CDN (a blocked or unstable network), and when the code calls os._exit().

- The site keeps an unchanged copy of the Pyodide files in vendor/pyodide/0.26.4/. When Python does not load
  from the CDN, the runner loads it from the site instead.
- os._exit() in the student's code raises SystemExit, so it is reported as an error in the code.
- If Python still cannot start, the message says it could not be downloaded on this network and what to try.

Applies to the engine template (tools/apply_assignment_build.py), harness.py, builds.js, every page with the
inlined engine, and tools/build_public_site.py.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PAGES = [f'lectures/iscarb/Ch{c}-FBR-Student-Assignment.html' for c in (12, 13, 14, 15, 16, 17, 20)] + ['assignment-example.html']
HARNESS = ROOT / 'curriculum/learning-path/builds/harness.py'

H_OLD = 'import ast, json, sys, traceback\n'
H_NEW = ('import ast, json, os, sys, traceback\n\n'
         '# os._exit() would stop Python itself and look like a broken runner. In the student\'s code it raises SystemExit.\n'
         'def __exit_now(code=0):\n'
         '    raise SystemExit(code)\n\n'
         'os._exit = __exit_now\n')

ANCHOR = '\nvar HARNESS='
MIRROR = ('\n/* The same Pyodide files are copied on this site (vendor/pyodide). They are used when the CDN download fails,'
          ' for example on a blocked or unstable network. */\n'
          "var MIRROR=(function(){try{if(!/^https?:$/.test(location.protocol))return '';var p=location.pathname,"
          "i=p.indexOf('/lectures/iscarb/');return location.origin+(i>=0?p.slice(0,i+1):p.slice(0,p.lastIndexOf('/')+1))"
          "+'vendor/pyodide/0.26.4/';}catch(e){return '';}})(),src=BASE;")
JS = [
    ("w.postMessage(Object.assign({base:BASE,harness:HARNESS},msg));",
     "w.postMessage(Object.assign({base:src,harness:HARNESS},msg));"),
    ("function runOnce(ch,code){var s=SPEC[ch];return call({kind:'load'},120000).then(",
     "function load(){return call({kind:'load'},120000).catch(function(e){if(!MIRROR||src===MIRROR)throw e;"
     "if(worker){try{worker.terminate();}catch(x){}worker=null;}src=MIRROR;return call({kind:'load'},120000);});}\n"
     "function runOnce(ch,code){var s=SPEC[ch];return load().then("),
    ("if(runner)return Promise.resolve(runner(ch,code,s,'their'));return call({kind:'load'},120000).then(",
     "if(runner)return Promise.resolve(runner(ch,code,s,'their'));return load().then("),
    ("throw Error('Python build could not start after an automatic retry. Your code is preserved. '+(second.message||second));",
     "throw Error('Python build could not start after an automatic retry. Your code is preserved. '"
     "+(/Program terminated|did not load|could not start|fetch|network|importScripts/i.test(second.message||'')"
     "?'Python could not be downloaded on this network. Try another network (for example a phone hotspot) or another browser, then run again. Details: ':'')"
     "+(second.message||second));"),
]
SITE_OLD = "    shutil.copytree(ROOT/'assets/guide',DEST/'assets/guide')  # pictures for the visual assignment guide\n"
SITE_NEW = SITE_OLD + "    shutil.copytree(ROOT/'vendor/pyodide',DEST/'vendor/pyodide')  # second source for the Python build runner\n"


def once(text, old, new, where):
    if new in text and (old not in text or old in new):
        return text
    assert text.count(old) == 1, f'{where}: expected 1 occurrence of {old[:60]!r}, found {text.count(old)}'
    return text.replace(old, new)


def engine_js(text, where, harness=True):
    if harness:
        text = once(text, json.dumps(H_OLD.rstrip('\n'), ensure_ascii=False)[:-1], json.dumps(H_NEW.rstrip('\n'), ensure_ascii=False)[:-1], where)
    if MIRROR not in text:
        assert text.count(ANCHOR) == 1, where
        text = text.replace(ANCHOR, MIRROR + ANCHOR)
    for old, new in JS:
        text = once(text, old, new, where)
    return text


def main():
    assert all((ROOT / 'vendor/pyodide/0.26.4' / f).exists() for f in ('pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json'))
    t = HARNESS.read_text(encoding='utf-8')
    HARNESS.write_text(once(t, H_OLD, H_NEW, 'harness.py'), encoding='utf-8')
    p = ROOT / 'tools/apply_assignment_build.py'
    p.write_text(engine_js(p.read_text(encoding='utf-8'), p.name, harness=False), encoding='utf-8')
    for rel in ['curriculum/learning-path/builds.js'] + PAGES:
        p = ROOT / rel
        p.write_text(engine_js(p.read_text(encoding='utf-8'), rel), encoding='utf-8')
    p = ROOT / 'tools/build_public_site.py'
    p.write_text(once(p.read_text(encoding='utf-8'), SITE_OLD, SITE_NEW, p.name), encoding='utf-8')
    print('Runner fallback applied to the engine template, harness.py, builds.js and', len(PAGES), 'pages')


if __name__ == '__main__':
    main()
