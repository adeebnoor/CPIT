"""Replace the JSON teaching lab in Assignments 3–9 with a Python build the student writes and tests.

Sources: curriculum/learning-path/builds/chNN_{helpers,starter,checks}.py and harness.py.
Output: curriculum/learning-path/builds.js (the engine, inlined into each assignment page).

The student writes real Python (a fault tree, an authorization rule, a reconciliation, an evidence-only
fit check, an adapter, an idempotent service, an honest display) plus at least three own tests. Python runs
locally with Pyodide in a Web Worker, with a time limit; nothing is uploaded. The build record (code
fingerprint, own tests, course checks) is frozen with Part A and exported. The build is assessed inside
the second rubric criterion; the 5-point total is unchanged and the written budget drops to 120–180 words.

Idempotent:  python3 tools/apply_assignment_build.py
"""
from __future__ import annotations
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / 'curriculum/publication.json'
SRC = ROOT / 'curriculum/learning-path/builds'
OUT = ROOT / 'curriculum/learning-path/builds.js'
PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/'
esc = lambda s: html.escape(str(s), quote=True)

CRIT = {12: 'TRACE', 13: 'TEST', 14: 'RECOVER', 15: 'COMPARE', 16: 'CONTRACT', 17: 'FAILURE', 20: 'INTEGRATE'}
TASK = {
 12: ('Build the fault tree', 'Model the hazard “the barrier closes while the zone is occupied” as two fault trees built from the case facts: current (the design as described) and revised (with your proposed control or test). Tag every event as fact, assumption or proposed. The revised tree must leave no single event that causes the hazard on its own. Use its minimal cut sets in your TRACE.'),
 13: ('Build the server-side check', 'Write can_read(user, project) so the server enforces the access rule on every request, and write tests that try to cross the boundary. At least two of your tests must be requests that are refused. Use the result in your TEST.'),
 14: ('Build the reconciliation', 'Write reconcile(central, paper_log) to bring the controlled paper log back into the central list after recovery, without losing, duplicating or overwriting changes. Use the result in your RECOVER reasoning.'),
 15: ('Build the evidence-only fit check', 'Write fit, shortlist and evidence_needed from the supplied facts only, so that nothing unknown can count as met. Use the output to test each claim in the colleague’s draft.'),
 16: ('Build the adapter', 'Write reserve_minutes(component, room_id, minutes): enforce the precondition before the call, convert minutes to seconds, and check the postcondition on the result. Your tests are the contract tests.'),
 17: ('Build the idempotent service', 'Write BookingService.reserve so that one user action creates at most one reservation, even when the reply is lost, the app retries or the service restarts. Your tests reproduce those failures.'),
 20: ('Build the honest display', 'Write display_state and headline so the dashboard shows each feed’s real state and never calls a degraded view live. Use the proposed 5-minute limit, and use the result in your review of the proposed design.'),
}
OLD_LABELS = '"labPrediction": "LAB PREDICTION", "labCases": "EXECUTABLE TEST CASES", "labEvidence": "LOCAL EXECUTION RECORD"'
NEW_LABELS = '"labPrediction": "BUILD PLAN", "labCases": "PYTHON BUILD (CODE AND TESTS)", "labEvidence": "BUILD RECORD"'
OLD_BUDGET = ('Keep the complete written response to about 180–260 focused words; use compact tables or notation. Include the source application and transfer answer in that budget. '
              'The executable log replaces prose about hypothetical test execution. No external experiment is required. ')
NEW_BUDGET = ('Keep the written response to about 120–180 focused words; use compact tables or notation. Include the source application and transfer answer in that budget. '
              'Your Python code, tests and build record are not counted in it. ')
OLD_BUDGET_78 = ('Keep the complete written response to about 180–260 focused words; use compact tables or notation. Include the source application and transfer answer in that budget. '
                 'The executable log replaces prose about hypothetical test execution. ')
OLD_CHECK = ("if(V2_CONFIG.lab){try{const r=JSON.parse($('labEvidence').value),cases=StudyLab.casesFrom($('labCases').value,V2_CONFIG.chapter);"
             "if(r.chapter!==V2_CONFIG.chapter||r.model!=='teaching-model-v2'||JSON.stringify(r.cases)!==JSON.stringify(cases)||!r.runs?.baseline||!r.runs?.corrected)throw Error('incomplete');}"
             "catch(e){return'Run both teaching-model versions with your own current test cases before commitment. Report the actual outcomes even when a test fails.';}}")
NEW_CHECK = ("if(V2_CONFIG.lab&&!/^BUILD RECORD · Assignment /.test($('labEvidence').value))"
             "return'Run your Python build (your own tests and the course checks) with your current code before commitment. Keep the actual result even when a check fails, and explain it.';")
FULL = ' <b>Build:</b> every course check passes, and your own tests (at least three) include a case that must be refused or must fail safely; the text uses what the build showed.'
HALF = ' Or the build fails course checks that the written record does not explain.'

ENGINE = r'''/* Python build tasks for Assignments 3–9 (generated by tools/apply_assignment_build.py).
   The student's code runs locally with Pyodide in a Web Worker, with a time limit. Nothing is uploaded. */
var StudyBuild=(function(){
'use strict';
var BASE=(typeof window!=='undefined'&&window.ISCARB_PYODIDE_BASE)||__BASE__;
var HARNESS=__HARNESS__;
var SPEC=__SPEC__;
var worker=null,runner=null;
function workerSource(){return "self.onmessage=async function(e){var m=e.data;try{if(!self.py){importScripts(m.base+'pyodide.js');self.py=await loadPyodide({indexURL:m.base});self.py.runPython(m.harness);}if(m.kind==='load'){postMessage({ok:true});return;}var f=self.py.globals.get('__run');var r=f(m.helpers,m.student,m.checks);if(f.destroy)f.destroy();postMessage({ok:true,result:String(r)});}catch(err){postMessage({ok:false,error:String(err&&err.message||err)});}};";}
function call(msg,ms){return new Promise(function(resolve,reject){
 if(!worker){try{worker=new Worker(URL.createObjectURL(new Blob([workerSource()],{type:'text/javascript'})));}catch(e){reject(Error('This browser cannot start Python here. Use a current Chrome, Edge, Firefox or Safari.'));return;}}
 var w=worker,t=setTimeout(function(){w.terminate();if(worker===w)worker=null;reject(Error(msg.kind==='load'?'Python did not load in time. Check your internet connection and try again.':'Stopped after '+ms/1000+' seconds. Look for an endless loop, then run again.'));},ms);
 w.onmessage=function(e){clearTimeout(t);e.data.ok?resolve(e.data.result):reject(Error(e.data.error));};
 w.onerror=function(e){clearTimeout(t);w.terminate();if(worker===w)worker=null;reject(Error('Python could not start: '+(e.message||'check your internet connection')));};
 w.postMessage(Object.assign({base:BASE,harness:HARNESS},msg));});}
function runChecks(ch,code){var s=SPEC[ch];if(runner)return Promise.resolve(runner(ch,code,s));return call({kind:'load'},120000).then(function(){return call({kind:'run',helpers:s.helpers,student:code,checks:s.checks},10000);}).then(JSON.parse);}
function fingerprint(text){try{if(typeof crypto!=='undefined'&&crypto.subtle&&typeof TextEncoder!=='undefined')return crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)).then(function(b){return Array.from(new Uint8Array(b)).map(function(x){return x.toString(16).padStart(2,'0');}).join('');});}catch(e){}var h=2166136261;for(var i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return Promise.resolve('fnv1a-'+h.toString(16));}
function lines(list){return list.map(function(r){return '  '+(r[1]?'✓ ':'✗ ')+r[0]+(r[1]||!r[2]?'':' · '+r[2]);}).join('\n');}
function summary(r){if(r.error)return r.error;var t=r.tests.filter(function(x){return x[1];}).length,c=r.checks.filter(function(x){return x[1];}).length;return 'Your tests: '+t+' of '+r.tests.length+' pass · Course checks: '+c+' of '+r.checks.length+' pass';}
function report(ch,r,hash){var head='BUILD RECORD · Assignment '+SPEC[ch].assignment+' (Chapter '+ch+') · '+new Date().toISOString()+'\nCode fingerprint: '+hash.slice(0,16)+' (the code above, exactly as run)\n';
 if(r.error)return head+'Result: '+r.error+'\n';
 return head+summary(r)+'\nYour tests:\n'+(r.tests.length?lines(r.tests):'  (none found: name them test_…)')+'\nCourse checks:\n'+lines(r.checks)+'\n';}
function mount(ch){
 var el=function(id){return document.getElementById(id);},code=el('labCases'),s=SPEC[ch];if(!code||!s)return;
 var ev=el('labEvidence'),plan=el('labPrediction'),out=el('buildOutput'),run=el('buildRun'),reset=el('buildReset'),status=el('labStatus'),armed=false;
 function changed(){ev.dispatchEvent(new Event('input',{bubbles:true}));}
 if(!code.value.trim()&&!code.readOnly){code.value=s.starter;code.dispatchEvent(new Event('input',{bubbles:true}));}
 out.textContent=ev.value?'Last recorded run:\n\n'+ev.value:'Write your plan, then run your tests and the course checks.';
 if(ev.value)plan.readOnly=true;
 code.addEventListener('keydown',function(e){if(e.key==='Tab'&&!e.shiftKey&&!code.readOnly){e.preventDefault();var a=code.selectionStart,b=code.selectionEnd;code.value=code.value.slice(0,a)+'    '+code.value.slice(b);code.selectionStart=code.selectionEnd=a+4;code.dispatchEvent(new Event('input',{bubbles:true}));}});
 code.addEventListener('input',function(){if(code.readOnly)return;if(ev.value){ev.value='';changed();out.textContent='Code changed: run again to record the new result.';}});
 run.disabled=code.readOnly;if(reset)reset.disabled=code.readOnly;
 run.addEventListener('click',function(){if(code.readOnly)return;
  if(plan.value.trim().length<30){status.textContent='Write your build plan first (at least 30 characters): what your code will do and which cases your tests cover.';return;}
  run.disabled=true;status.textContent=runner?'Running…':'Starting Python… the first run downloads it once (about 10 MB).';
  var src=code.value;
  runChecks(ch,src).then(function(r){return fingerprint(src).then(function(h){var rec=report(ch,r,h);if(code.value!==src)return;ev.value=rec;changed();plan.readOnly=true;out.textContent=rec;status.textContent=summary(r)+'. Explain in your '+s.criterion+' what the build shows.';});})
  .catch(function(e){status.textContent=e.message;}).then(function(){run.disabled=code.readOnly;});});
 if(reset)reset.addEventListener('click',function(){if(code.readOnly)return;if(!armed){armed=true;reset.textContent='Click again to replace your code';setTimeout(function(){armed=false;reset.textContent='Reset to starter code';},4000);return;}armed=false;reset.textContent='Reset to starter code';code.value=s.starter;code.dispatchEvent(new Event('input',{bubbles:true}));});
}
return{SPEC:SPEC,mount:mount,runChecks:runChecks,setRunner:function(f){runner=f;}};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=StudyBuild;
'''


def check_labels(src: str) -> list[str]:
    return re.findall(r'\(\s*"([^"]+)",\s*\w+\s*\)', src.split('CHECKS', 1)[1]) + ['your own tests: at least three, all passing']


def spec() -> dict:
    pub = json.loads(PUB.read_text(encoding='utf-8'))
    number = {a['chapter']: a.get('assignment') or i + 1 for i, a in enumerate(pub['assignments'])}
    out = {}
    for ch in CRIT:
        part = {k: (SRC / f'ch{ch}_{k}.py').read_text(encoding='utf-8') for k in ('helpers', 'starter', 'checks')}
        out[ch] = dict(part, title=TASK[ch][0], criterion=CRIT[ch], assignment=number.get(ch), checkLabels=check_labels(part['checks']))
    return out


def engine(sp: dict) -> str:
    return (ENGINE.replace('__BASE__', json.dumps(PYODIDE))
            .replace('__HARNESS__', json.dumps((SRC / 'harness.py').read_text(encoding='utf-8'), ensure_ascii=False))
            .replace('__SPEC__', json.dumps({str(k): v for k, v in sp.items()}, ensure_ascii=False)))


def markup(ch: int, sp: dict) -> str:
    title, task = TASK[ch]
    checks = ''.join(f'<li>{esc(c)}</li>' for c in sp['checkLabels'])
    mono = 'font:15px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;tab-size:4'
    return (f'<section class="card" id="practical" data-build="v1"><p class="ey">PYTHON BUILD · ASSESSED IN {CRIT[ch]}</p><h2>{esc(title)}</h2><p>{esc(task)}</p>'
            '<p>Budget about 30 minutes. Python runs in your browser: nothing to install, and nothing is uploaded. The first run downloads Python once (about 10 MB, internet needed). '
            'Passing every check is necessary, not sufficient: your written record must use what the build shows.</p>'
            f'<details><summary>The course checks your build must pass</summary><ul>{checks}</ul></details>'
            '<label for="labPrediction" class="field-label">Build plan: what will your code do, and which cases will your tests cover?</label>'
            '<textarea id="labPrediction" placeholder="My approach, the edge cases I will test, and the case that must be refused or fail safely…"></textarea>'
            '<label for="labCases" class="field-label">Your Python code and tests</label>'
            '<p class="hint">Keep the given names. Write at least three functions whose names start with test_. Tab inserts four spaces.</p>'
            f'<textarea id="labCases" spellcheck="false" autocapitalize="off" autocomplete="off" style="{mono};min-height:380px;white-space:pre;overflow-wrap:normal;overflow-x:auto"></textarea>'
            '<div class="buttons"><button type="button" id="buildRun" data-lab-mode="build">Run my tests and the course checks</button><button type="button" id="buildReset" data-lab-mode="reset">Reset to starter code</button></div>'
            '<p id="labStatus" role="status" aria-live="polite">Write your plan, then run.</p>'
            f'<pre id="buildOutput" style="white-space:pre-wrap;overflow-wrap:anywhere;{mono}"></pre>'
            '<label for="labEvidence" class="field-label">Build record · included in your submission</label>'
            '<textarea id="labEvidence" readonly style="min-height:160px" placeholder="Created when you run. Changing the code clears it until you run again."></textarea></section>')


LAB_INLINE = re.compile(r"<script>/\* Deterministic teaching models\..*?module\.exports=StudyLab;\n?</script>", re.S)
BUILD_INLINE = re.compile(r"<script>/\* Python build tasks for Assignments.*?module\.exports=StudyBuild;\n?</script>", re.S)


def patch(path: Path, ch: int, sp: dict, eng: str) -> bool:
    s0 = s = path.read_text(encoding='utf-8')
    def one(old, new, count=1):
        nonlocal s
        if s.count(old) != count:
            raise SystemExit(f'{path.name}: expected {count}× {old[:70]!r}, found {s.count(old)}')
        s = s.replace(old, new)
    m = re.search(r'<section class="card" id="practical"[^>]*>.*?</section>', s, re.S)
    if not m: raise SystemExit(f'{path.name}: practical section not found')
    s = s[:m.start()] + markup(ch, sp) + s[m.end():]
    if OLD_LABELS in s: one(OLD_LABELS, NEW_LABELS, count=3)
    if OLD_BUDGET in s: one(OLD_BUDGET, NEW_BUDGET)
    if OLD_BUDGET_78 in s: one(OLD_BUDGET_78, NEW_BUDGET)
    if OLD_CHECK in s: one(OLD_CHECK, NEW_CHECK)
    if 'StudyLab.mount(' in s: one(f'\nStudyLab.mount({ch});\n', f'\nStudyBuild.mount({ch});\n')
    if LAB_INLINE.search(s): s = LAB_INLINE.sub(lambda _: '<script>' + eng + '</script>', s, count=1)
    else: s, n = BUILD_INLINE.subn(lambda _: '<script>' + eng + '</script>', s, count=1); assert n == 1, path.name
    # rubric: the second criterion assesses the build
    i = s.index('<table class="rubric">'); j = s.index('</table>', i); table = s[i:j]
    row = re.search(rf'<tr><th scope="row">{CRIT[ch]} · 1 point</th>.*?</tr>', table, re.S)
    if not row: raise SystemExit(f'{path.name}: rubric row {CRIT[ch]} not found')
    r = row.group(0)
    if '<b>Build:</b>' not in r:
        r = r.replace('<details class="levels">', FULL + '<details class="levels">', 1)
        r = re.sub(r'(<b>0\.5:</b>.*?)(<br/>)', lambda m: m.group(1).rstrip() + HALF + m.group(2), r, count=1, flags=re.S)
        table = table.replace(row.group(0), r); s = s[:i] + table + s[j:]
    if s != s0: path.write_text(s, encoding='utf-8')
    return s != s0


def main() -> int:
    sp = spec(); eng = engine(sp)
    OUT.write_text(eng, encoding='utf-8')
    pub = json.loads(PUB.read_text(encoding='utf-8')); done = []
    for a in pub['assignments']:
        if a['chapter'] in CRIT:
            if patch(ROOT / a['path'], a['chapter'], sp[a['chapter']], eng): done.append(a['chapter'])
            a['build'] = 'python-v1'
    PUB.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Python build applied or refreshed in chapters', done or 'none (already current)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
