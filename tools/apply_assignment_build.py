"""Replace the JSON teaching lab in Assignments 3–9 with a Python build the student writes and tests.

Sources: curriculum/learning-path/builds/chNN_{helpers,starter,checks}.py and harness.py.
Output: curriculum/learning-path/builds.js (the engine, inlined into each assignment page).

The student writes real Python (a fault tree, an authorization rule, a reconciliation, an evidence-only
fit check, an adapter, an idempotent service, an honest display) plus at least three own tests. Python runs
locally with Pyodide in a Web Worker, with a time limit; nothing is uploaded. The build record (code
fingerprint, own tests, course checks) is frozen with Part A and exported. The build is assessed inside
the second rubric criterion; the 5-point total is unchanged and the written budget drops to 120–180 words.

v2 adds: mutation testing (the student's own tests run against known buggy versions in chNN_mutants.py and
must catch each one), a micro-viva change request chosen from the Student ID, and one primary source per task.

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

CRIT = {0: 'PRACTICE', 12: 'TRACE', 13: 'TEST', 14: 'RECOVER', 15: 'COMPARE', 16: 'CONTRACT', 17: 'FAILURE', 20: 'INTEGRATE'}
# Course learning outcome each build practises (syllabus numbering); every build also practises CLO 11 through its tests.
CLO = {
 12: (4, 'Design safety in safety-critical systems', 'the fault tree'),
 13: (5, 'Design and test secure systems', 'the server-side access rule'),
 14: (6, 'Design systems to support resilience', 'the reconciliation'),
 15: (7, 'Identify reuse elements and approaches', 'the evidence-only fit check'),
 16: (8, 'Compose standardized reusable components', 'the adapter'),
 17: (9, 'Explain distributed systems and architectures', 'the idempotent service'),
 20: (10, 'Explain systems of systems and their engineering challenges', 'the honest display'),
}
CLO11 = 'Design and implement test cases across testing strategies'
COVERAGE_MARK = '<div class="coverage-step" id="coverageStep">'
# Run 3 · their change: a part the student did not write changes (Chapters 15, 16, 17, 20 only)
THEIR_CH = (15, 16, 17, 20)
THEIR_MARK = '/* THEIR-CHANGE: run 3 */'

TASK = {
 0: ('Practice build: the loan rule', 'Write can_borrow(student, item) for the lab-equipment desk, and tests that try to break the rule. Not assessed: use it to learn the build before your first assignment.'),
 12: ('Build the fault tree', 'Model the hazard “the barrier closes while the zone is occupied” as two fault trees built from the case facts: current (the design as described) and revised (with your proposed control or test). Tag every event as fact, assumption or proposed. The revised tree must leave no single event that causes the hazard on its own. Use its minimal cut sets in your TRACE.'),
 13: ('Build the server-side check', 'Write can_read(user, project) so the server enforces the access rule on every request, and write tests that try to cross the boundary. At least two of your tests must be requests that are refused. Use the result in your TEST.'),
 14: ('Build the reconciliation', 'Write reconcile(central, paper_log) to bring the controlled paper log back into the central list after recovery, without losing, duplicating or overwriting changes. Use the result in your RECOVER reasoning.'),
 15: ('Build the evidence-only fit check', 'Write fit, shortlist and evidence_needed from the supplied facts only, so that nothing unknown can count as met. Use the output to test each claim in the colleague’s draft.'),
 16: ('Build the adapter', 'Write reserve_minutes(component, room_id, minutes): enforce the precondition before the call, convert minutes to seconds, and check the postcondition on the result. Your tests are the contract tests.'),
 17: ('Build the idempotent service', 'Write BookingService.reserve so that one user action creates at most one reservation, even when the reply is lost, the app retries or the service restarts. Your tests reproduce those failures.'),
 20: ('Build the honest display', 'Write display_state and headline so the dashboard shows each feed’s real state and never calls a degraded view live. Use the proposed 5-minute limit, and use the result in your review of the proposed design.'),
}
READING = {
 0: ('J. H. Saltzer and M. D. Schroeder, “The Protection of Information in Computer Systems,” <i>Proceedings of the IEEE</i> 63(9), 1975',
      'the principle “fail-safe defaults”. Which line of can_borrow refuses when it cannot read the input?'),
 12: ('W. E. Vesely, F. F. Goldberg, N. H. Roberts and D. F. Haasl, <i>Fault Tree Handbook</i> (NUREG-0492), U.S. Nuclear Regulatory Commission, 1981',
      'the AND and OR gates and minimal cut sets. Which cut set of one event does your revised tree remove?'),
 13: ('J. H. Saltzer and M. D. Schroeder, “The Protection of Information in Computer Systems,” <i>Proceedings of the IEEE</i> 63(9), 1975',
      'the design principles “complete mediation” and “fail-safe defaults”. Which line of can_read applies each one?'),
 14: ('P. Helland and D. Campbell, “Building on Quicksand,” <i>CIDR</i>, 2009',
      'why work done while disconnected must be reconciled later, and why each change needs a unique identity. Where does your code use that identity?'),
 15: ('D. Garlan, R. Allen and J. Ockerbloom, “Architectural Mismatch: Why Reuse Is So Hard,” <i>IEEE Software</i> 12(6), 1995',
      'the assumptions a reused component makes that its description does not state. Which of your “unknown” results is such an assumption?'),
 16: ('B. Meyer, “Applying ‘Design by Contract’,” <i>IEEE Computer</i> 25(10), 1992',
      'preconditions, postconditions and who is to blame when each is broken. Which side does your ValueError protect, and which side does your ContractError blame?'),
 17: ('P. Helland, “Idempotence Is Not a Medical Condition,” <i>ACM Queue</i> 10(4), 2012',
      'why messages are retried and how a unique request identity makes a retry safe. Which of your tests reproduces the retry the article describes?'),
 20: ('M. W. Maier, “Architecting Principles for Systems-of-Systems,” <i>Systems Engineering</i> 1(4), 1998',
      'operational and managerial independence of the component systems. Which line of your code exists because no feed owner answers to the dashboard?'),
}
VIVA = {
 0: ['The lab now lends three items. Change one thing and say which test changes.',
     'Delete your overdue test and run again. Which known bug is no longer caught?',
     'A student record arrives with loans as the text "1". What does your code do, and why is that safe?',
     'Students with a lab permit may borrow one extra item. Add the rule and one refusal test.'],
 12: ['The night tests now exist and the camera passed them. Change your trees: which event changes its source tag, and does any cut set change?',
      'Remove your proposed control from revised and run again. Which check fails, and what does it say about the barrier?',
      'An auditor says the stop button is enough. Show with cut_sets why it is or is not.',
      'Add rain as a new fact under the camera. Where does it belong in current, and does revised still pass?'],
 13: ['A new role “ta” is added and must read only its assigned groups. Change can_read and add one test that must be refused.',
      'A project may now have two owners (owner is a list). Change can_read; which of your tests changes?',
      'Remove your malformed-input handling and run again. Which known bug is no longer caught, and why?',
      'Staff may now read a project only while it is not archived. Add the rule and one refusal test.'],
 14: ['Two paper changes to the same pickup were written from the same base version. Show what your code does and defend it.',
      'Delete your repeated-change test and run again. Which known bug survives, and what would it cost the transport desk?',
      'The paper log arrives out of order (c2 before c1). Show what happens and whether it is safe.',
      'Return conflicts with the pickup id as well as the change id. Change the code and one test.'],
 15: ['The vendor sends a measured peak-load report for Option A that passes. Change one fact and show the new shortlist.',
      'Add a sixth requirement, “arabic-ui”, that nobody has checked. Which outputs change, and why do no facts change?',
      'Remove your test for an unchecked option and run again. Which known bug survives?',
      'Option B gets a written three-year support commitment. Change one fact: is B shortlisted now? Why not?'],
 16: ['The component now takes milliseconds (1 to 7,200,000). Change the adapter and say which tests change.',
      'The maximum becomes 90 minutes. Change one thing and show the test that proves it.',
      'The component may return an end time one second late. Keep or relax the postcondition? Defend it with a test.',
      'Remove the type check and run again. Which known bug is no longer caught?'],
 17: ['The store is wiped every night. Is your service still idempotent across midnight? Show it with a test.',
      'Two different users send the same request id. What does your service do, and should it?',
      'Remove the persistence of request ids and run again. Which test fails first, and which real failure is it?',
      'A retry arrives with a different event for the same request id. Change the code to refuse it, with a test.'],
 20: ['The owners agree a 3-minute limit. Change one thing and show which of your tests changes.',
      'Add a fourth feed, parking, that is unavailable. What does the headline say? Show it with a test.',
      'The transport clock runs 2 minutes ahead. Which feed state changes, and is it honest?',
      'Change > to >= in the freshness rule and run again. Which known bug did you reintroduce?'],
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
FULL = ' <b>Build:</b> every course check passes, your own tests catch every known bug (mutation test), and you can make your micro-viva change and explain which tests change; the text uses what the build showed.'
OLD_FULL = ' <b>Build:</b> every course check passes, and your own tests (at least three) include a case that must be refused or must fail safely; the text uses what the build showed.'
COV_A = ('"labEvidence"],M=', '"labEvidence", "coverageNote"],M=')
COV_LABEL = ('"labEvidence": "BUILD RECORD"}', '"labEvidence": "BUILD RECORD", "coverageNote": "COVERAGE SENTENCE (COURSE OUTCOME 11)"}')
THEIR_A = ('"labEvidence", "coverageNote"],M=', '"labEvidence", "coverageNote", "theirGreen", "theirCorrect", "theirNote", "theirFacts"],M=')
THEIR_LABEL = ('"coverageNote": "COVERAGE SENTENCE (COURSE OUTCOME 11)"}',
               '"coverageNote": "COVERAGE SENTENCE (COURSE OUTCOME 11)", "theirGreen": "THEIR CHANGE · YOUR TESTS", "theirCorrect": "THEIR CHANGE · THE RESULT", '
               '"theirNote": "THEIR CHANGE · YOUR SENTENCE", "theirFacts": "THEIR CHANGE · RUN 3 RECORD (verified after commitment)"}')
THEIR_SCRIPT = (THEIR_MARK + "(function(){if(!document.getElementById('theirFacts'))return;"
 "function dec(v){try{return String(v||'').indexOf('their-v1:')===0?JSON.parse(atob(String(v).slice(9))):null}catch(e){return null}}"
 "var bV=valA;valA=function(){var i=bV();if(i)return i;var ev=$('labEvidence').value;if(/TECHNICAL RUNNER FAILURE/.test(ev))return'';"
 "var f=dec($('theirFacts').value),h=((ev.match(/Code fingerprint: ([0-9a-f]{16})/)||[])[1]||'');"
 "if(!f||f.h!==h||!/THEIR CHANGE · run 3/.test(ev))return'Run 3 · their change: when your tests pass, run their change without editing your code or tests, then answer the two questions.';return''};"
 "var bM=md;md=function(final=false){var t=bM(final),d=data(),a=d.partA||{},f=dec(a.theirFacts),line;"
 "if(!d.locked)line='The run 3 verdict is added to this record when Part A is committed.';else if(!f)line='Run 3 was not recorded.';"
 "else{var g=/^Yes/.test(a.theirGreen||''),c=/^Yes/.test(a.theirCorrect||''),met=g===f.green&&c===f.correct;"
 "line='The run showed: your tests '+(f.green?'stayed green':'turned red')+'; the result '+(f.correct?'was still correct':'was no longer correct')+'.\\n'"
 "+'Your answer: tests '+(g?'green':'red')+'; result '+(c?'correct':'not correct')+'.\\n'"
 "+'THEIR CHANGE row: '+(met?'met':'NOT MET (your answer does not match the run)')+'. This row adds no points.';}"
 "return t+'\\n\\n## THEIR CHANGE · run 3 verdict\\n'+line+'\\n';};"
 "var bL=lockedView;lockedView=function(){bL();if(S.locked)['theirGreen','theirCorrect'].forEach(function(x){var e=$(x);if(e)e.disabled=true;});};"
 "if(S.locked)lockedView();})();\n")
COV_CHECK = (r"if(V2_CONFIG.lab&&!/TECHNICAL RUNNER FAILURE/.test($('labEvidence').value)&&+((($('labEvidence').value.match(/^Run (\d+) on this device/m))||[])[1]||0)<2)"
             "return'Coverage step: after your three tests pass, change one input in one of your tests and run again. The build record must show Run 2 or later.';")
HALF = ' Or the build fails course checks that the written record does not explain.'

ENGINE = r'''/* Python build tasks for Assignments 3–9 (generated by tools/apply_assignment_build.py).
   The student's code runs locally with Pyodide in a Web Worker, with a time limit. Nothing is uploaded. */
var StudyBuild=(function(){
'use strict';
var BASE=(typeof window!=='undefined'&&window.ISCARB_PYODIDE_BASE)||__BASE__;
/* The same Pyodide files are copied on this site (vendor/pyodide). They are used when the CDN download fails, for example on a blocked or unstable network. */
var MIRROR=(function(){try{if(!/^https?:$/.test(location.protocol))return '';var p=location.pathname,i=p.indexOf('/lectures/iscarb/');return location.origin+(i>=0?p.slice(0,i+1):p.slice(0,p.lastIndexOf('/')+1))+'vendor/pyodide/0.26.4/';}catch(e){return '';}})(),src=BASE;
var HARNESS=__HARNESS__;
var SPEC=__SPEC__;
var worker=null,runner=null;
function workerSource(){return "self.onmessage=async function(e){var m=e.data;try{if(!self.py){importScripts(m.base+'pyodide.js');self.py=await loadPyodide({indexURL:m.base});self.py.runPython(m.harness);}if(m.kind==='load'){postMessage({ok:true});return;}var their=m.kind==='their',f=self.py.globals.get(their?'__their':'__run');var r=their?f(m.helpers,m.student,m.their):f(m.helpers,m.student,m.checks,m.mutants||'');if(f.destroy)f.destroy();postMessage({ok:true,result:String(r)});}catch(err){postMessage({ok:false,error:String(err&&err.message||err)});}};";}
function call(msg,ms){return new Promise(function(resolve,reject){
 if(!worker){try{worker=new Worker(URL.createObjectURL(new Blob([workerSource()],{type:'text/javascript'})));}catch(e){reject(Error('This browser cannot start Python here. Use a current Chrome, Edge, Firefox or Safari.'));return;}}
 var w=worker,t=setTimeout(function(){w.terminate();if(worker===w)worker=null;reject(Error(msg.kind==='load'?'Python did not load in time. Check your internet connection and try again.':'Stopped after '+ms/1000+' seconds. Look for an endless loop, then run again.'));},ms);
 w.onmessage=function(e){clearTimeout(t);if(e.data.ok){resolve(e.data.result);}else{w.terminate();if(worker===w)worker=null;reject(Error(e.data.error));}};
 w.onerror=function(e){clearTimeout(t);w.terminate();if(worker===w)worker=null;reject(Error('Python could not start: '+(e.message||'check your internet connection')));};
 w.postMessage(Object.assign({base:src,harness:HARNESS},msg));});}
function load(){return call({kind:'load'},120000).catch(function(e){if(!MIRROR||src===MIRROR)throw e;if(worker){try{worker.terminate();}catch(x){}worker=null;}src=MIRROR;return call({kind:'load'},120000);});}
function runOnce(ch,code){var s=SPEC[ch];return load().then(function(){return call({kind:'run',helpers:s.helpers,student:code,checks:s.checks,mutants:s.mutants||''},20000);}).then(JSON.parse);}
function runChecks(ch,code){var s=SPEC[ch];if(runner)return Promise.resolve(runner(ch,code,s));return runOnce(ch,code).catch(function(first){if(/^Stopped after /.test(first.message||''))throw first;if(worker){try{worker.terminate();}catch(e){}worker=null;}return runOnce(ch,code).catch(function(second){throw Error('Python build could not start after an automatic retry. Your code is preserved. '+(/Program terminated|did not load|could not start|fetch|network|importScripts/i.test(second.message||'')?'Python could not be downloaded on this network. Try another network (for example a phone hotspot) or another browser, then run again. Details: ':'')+(second.message||second));});});}
function runTheir(ch,code){var s=SPEC[ch];if(runner)return Promise.resolve(runner(ch,code,s,'their'));return load().then(function(){return call({kind:'their',helpers:s.helpers,student:code,their:s.their},20000);}).then(JSON.parse);}
function encodeFacts(f){try{return 'their-v1:'+btoa(JSON.stringify(f));}catch(e){return '';}}
function fingerprint(text){try{if(typeof crypto!=='undefined'&&crypto.subtle&&typeof TextEncoder!=='undefined')return crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)).then(function(b){return Array.from(new Uint8Array(b)).map(function(x){return x.toString(16).padStart(2,'0');}).join('');});}catch(e){}var h=2166136261;for(var i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return Promise.resolve('fnv1a-'+h.toString(16));}
function lines(list){return list.map(function(r){return '  '+(r[1]?'✓ ':'✗ ')+r[0]+(r[1]||!r[2]?'':' · '+r[2]);}).join('\n');}
function runKey(ch,sid){return 'fbr:build-runs:ch'+ch+':'+String(sid||'').trim();}
/* A run counts as new when the code differs from the previous run: the coverage step needs a second run after one input changes. */
function nextRun(ch,sid,hash){var k=runKey(ch,sid),p=null;try{p=JSON.parse(localStorage.getItem(k)||'null');}catch(e){}var n=p&&p.n||0,prev=p&&p.hash||'',same=prev===hash;if(!same)n+=1;try{localStorage.setItem(k,JSON.stringify({n:n,hash:hash}));}catch(e){}return {n:n,prev:same?(p&&p.prev||''):prev,same:same};}
function runLine(run){return 'Run '+run.n+' on this device'+(run.same?' (same code as the previous run)':'')+(run.prev?' · previous code fingerprint: '+run.prev.slice(0,16):'')+'\n';}
function coverageText(r){var c=r.coverage;if(!c)return 'Coverage of your code by your own tests: not measured by this runner.\n';var gates=c.unit==='gates',miss=c.rows.filter(function(x){return !x[3]||!x[5];});return 'Coverage of your code by your own tests (course checks not counted): '+(gates?'gates evaluated '+c.lines[0]+' of '+c.lines[1]+' · gate outcomes ':'lines '+c.lines[0]+' of '+c.lines[1]+' · branches ')+c.branches[0]+' of '+c.branches[1]+'\n'+(gates&&!c.lines[0]&&c.lines[1]?'  Your tests never evaluated a gate: call occurs(revised, {"event name", ...}) in a test.\n':'')+(miss.length?miss.map(function(x){var not=[];if(!x[3])not.push(x[2]);if(!x[5])not.push(x[4]);return '  '+(gates?'Outcome not seen':'Branch not taken')+': '+(typeof x[0]==='number'?'line '+x[0]:x[0])+' · '+x[1]+' · '+not.join(' and ');}).join('\n'):'  Every branch was taken by your tests.')+(c.missed.length?'\n  Lines never run by your tests: '+c.missed.join(', '):'')+'\n';}
function summary(r){if(r.error)return r.error;var t=r.tests.filter(function(x){return x[1];}).length,c=r.checks.filter(function(x){return x[1];}).length;return 'Your tests: '+t+' of '+r.tests.length+' pass · Course checks: '+c+' of '+r.checks.length+' pass';}
function vivaFor(ch,sid){var v=SPEC[ch].viva||[],h=2166136261,i;sid=String(sid||'').trim();if(!v.length||!sid)return '';for(i=0;i<sid.length;i++){h^=sid.charCodeAt(i);h=Math.imul(h,16777619)>>>0;}return v[(h+ch)%v.length];}
function report(ch,r,hash,sid,run){var q=vivaFor(ch,sid),head='BUILD RECORD · '+(SPEC[ch].assignment?'Assignment '+SPEC[ch].assignment+' (Chapter '+ch+')':'Practice (not assessed)')+' · '+new Date().toISOString()+'\nCode fingerprint: '+hash.slice(0,16)+' (the code above, exactly as run)\n'+(run?runLine(run):'')+(q?'Micro-viva change request (from Student ID '+String(sid).trim()+'): '+q+'\n':'');
 if(r.error)return head+'Result: '+r.error+'\n';
 return head+summary(r)+'\nYour tests:\n'+(r.tests.length?lines(r.tests):'  (none found: name them test_…)')+'\nCourse checks:\n'+lines(r.checks)+'\n'+(r.mutants?'Known bugs your tests catch (mutation test):\n'+lines(r.mutants.map(function(m){return [m[0],m[1],m[1]?'':'not caught'];}))+'\n':'')+coverageText(r);}
function mount(ch){
 var el=function(id){return document.getElementById(id);},code=el('labCases'),s=SPEC[ch];if(!code||!s)return;
 var ev=el('labEvidence'),plan=el('labPrediction'),out=el('buildOutput'),run=el('buildRun'),reset=el('buildReset'),status=el('labStatus'),armed=false;
 function changed(){ev.dispatchEvent(new Event('input',{bubbles:true}));}
 var tf=el('theirFacts');function clearTheir(){if(tf&&tf.value!=='their-v0:run-3-not-recorded'){tf.value='their-v0:run-3-not-recorded';tf.dispatchEvent(new Event('input',{bubbles:true}));}}
 if(!code.value.trim()&&!code.readOnly){code.value=s.starter;code.dispatchEvent(new Event('input',{bubbles:true}));}
 out.textContent=ev.value?'Last recorded run:\n\n'+ev.value:'Write your plan, then run your tests and the course checks.';
 if(ev.value)plan.readOnly=true;
 code.addEventListener('keydown',function(e){if(e.key==='Tab'&&!e.shiftKey&&!code.readOnly){e.preventDefault();var a=code.selectionStart,b=code.selectionEnd;code.value=code.value.slice(0,a)+'    '+code.value.slice(b);code.selectionStart=code.selectionEnd=a+4;code.dispatchEvent(new Event('input',{bubbles:true}));}});
 code.addEventListener('input',function(){if(code.readOnly)return;if(plan.readOnly)plan.readOnly=false;clearTheir();if(ev.value){ev.value='';changed();out.textContent='Code changed: run again to record the new result.';}});
 run.disabled=code.readOnly;if(reset)reset.disabled=code.readOnly;
 run.addEventListener('click',function(){if(code.readOnly)return;
  if(plan.value.trim().length<30){status.textContent='Write your build plan first (at least 30 characters): what your code will do and which cases your tests cover.';return;}
  run.disabled=true;status.textContent=runner?'Running…':'Starting Python… the first run downloads it once (about 10 MB).';
  var src=code.value;
  runChecks(ch,src).then(function(r){return fingerprint(src).then(function(h){var sidEl=el('sid'),sid=sidEl?sidEl.value:'';if(code.value!==src)return;var rec=report(ch,r,h,sid,nextRun(ch,sid,h));clearTheir();ev.value=rec;changed();plan.readOnly=true;out.textContent=rec;status.textContent=summary(r)+'. Explain in your '+s.criterion+' what the build shows.';});})
  .catch(function(e){if(/^Stopped after /.test(e&&e.message||'')){if(code.value===src){if(ev.value){ev.value='';changed();}out.textContent=e.message;status.textContent=e.message;}return;}/* an endless loop is a bug in the code, not a runner failure: no record */return fingerprint(src).then(function(h){var sidEl=el('sid'),r={error:'TECHNICAL RUNNER FAILURE: '+(e.message||e)},rec=report(ch,r,h,sidEl?sidEl.value:'');if(code.value!==src)return;ev.value=rec;changed();plan.readOnly=true;out.textContent=rec;status.textContent='Python runner failed after automatic recovery attempts. A technical-failure Build Record was created so Part A is not blocked; your instructor can review it.';});}).then(function(){run.disabled=code.readOnly;});});
 var tr=el('theirRun'),ts=el('theirStatus');
 if(tr&&s.their){tr.disabled=code.readOnly;tr.addEventListener('click',function(){if(code.readOnly)return;var rec=ev.value,m=rec.match(/Your tests: (\d+) of (\d+) pass/),n=+((rec.match(/^Run (\d+) on this device/m)||[])[1]||0);
  if(!/^BUILD RECORD/.test(rec)||!m){ts.textContent='Run your tests first.';return;}
  if(m[1]!==m[2]||+m[2]<3){ts.textContent='Make your own tests pass first (at least three). Then run their change without editing them.';return;}
  if(n<2){ts.textContent='Do the coverage step first (Run 2). Then run their change.';return;}
  var src=code.value;tr.disabled=true;ts.textContent='Running their change… your code and tests are not edited.';
  runTheir(ch,src).then(function(r){return fingerprint(src).then(function(h){if(code.value!==src)return;if(r.error){ts.textContent=r.error;return;}
   var pass=r.tests.filter(function(x){return x[1];}).length,green=r.tests.length>=3&&pass===r.tests.length,base=ev.value.split('\n\nTHEIR CHANGE · run 3')[0];
   ev.value=base+'\n\nTHEIR CHANGE · run 3 · your code and tests unchanged (fingerprint '+h.slice(0,16)+')\nWhat changed (you did not write it): '+s.theirChange+'\n  - '+s.theirBefore+'\n  + '+s.theirAfter+'\nYour tests after their change: '+pass+' of '+r.tests.length+' pass\n'+lines(r.tests)+'\nWhat the shared case shows:\n'+(r.evidence||[]).map(function(x){return '  '+x;}).join('\n')+'\n';changed();
   if(tf){tf.value=encodeFacts({h:h.slice(0,16),green:green,correct:r.correct===true});tf.dispatchEvent(new Event('input',{bubbles:true}));}
   out.textContent=ev.value;ts.textContent='Their change is recorded. Now answer: did your tests stay green, and is the result still correct?';});})
  .catch(function(e){ts.textContent=(e&&e.message)||String(e);}).then(function(){tr.disabled=code.readOnly;});});}
 if(reset)reset.addEventListener('click',function(){if(code.readOnly)return;if(!armed){armed=true;reset.textContent='Click again to replace your code';setTimeout(function(){armed=false;reset.textContent='Reset to starter code';},4000);return;}armed=false;reset.textContent='Reset to starter code';plan.readOnly=false;code.value=s.starter;code.dispatchEvent(new Event('input',{bubbles:true}));});
}
return{SPEC:SPEC,mount:mount,runChecks:runChecks,vivaFor:vivaFor,coverageText:coverageText,nextRun:nextRun,setRunner:function(f){runner=f;}};
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
        mut = SRC / f'ch{ch}_mutants.py'
        if mut.exists(): part['mutants'] = mut.read_text(encoding='utf-8')
        if ch in THEIR_CH:
            part['their'] = (SRC / f'ch{ch}_their.py').read_text(encoding='utf-8')
            t: dict = {}
            exec(part['their'], t)
            part.update(theirChange=t['CHANGE'], theirBefore=t['BEFORE'], theirAfter=t['AFTER'])
        labels = check_labels(part['checks']) + (['your tests catch every known bug (mutation test)'] if 'mutants' in part else [])
        out[ch] = dict(part, title=TASK[ch][0], criterion=CRIT[ch] if ch else 'written answers', assignment=number.get(ch), checkLabels=labels, viva=VIVA[ch])
    return out


def engine(sp: dict) -> str:
    return (ENGINE.replace('__BASE__', json.dumps(PYODIDE))
            .replace('__HARNESS__', json.dumps((SRC / 'harness.py').read_text(encoding='utf-8'), ensure_ascii=False))
            .replace('__SPEC__', json.dumps({str(k): v for k, v in sp.items()}, ensure_ascii=False)))


def markup(ch: int, sp: dict) -> str:
    title, task = TASK[ch]
    checks = ''.join(f'<li>{esc(c)}</li>' for c in sp['checkLabels'])
    mono = 'font:15px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;tab-size:4'
    eyebrow = 'PYTHON BUILD · PRACTICE, NOT ASSESSED' if ch == 0 else f'PYTHON BUILD · ASSESSED IN {CRIT[ch]}'
    return (f'<section class="card" id="practical" data-build="v2"><p class="ey">{eyebrow}</p><h2>{esc(title)}</h2><p>{esc(task)}</p>'
            + ('' if ch == 0 else '<p class="hint">First time? Try the not-assessed practice build and a complete worked example on <a href="../../assignment-example.html">How to do an assignment</a>.</p>')
            + '<p>Budget about 30 minutes. Python runs in your browser: nothing to install, and nothing is uploaded. The first run downloads Python once (about 10 MB, internet needed). '
            'Passing every check is necessary, not sufficient: your written record must use what the build shows.</p>'
            + (f'<p>Your own tests are tested too: the course runs them against known buggy versions of this code, and each bug must make one of your tests fail. ' if 'mutants' in sp else '<p>')
            + 'Your build record names a <b>micro-viva change request</b> chosen from your Student ID. Be ready to make that change in front of your instructor and explain which tests change and why.</p>'
            f'<p class="hint"><b>Primary source · about 15 minutes:</b> {READING[ch][0]}. Read it for {esc(READING[ch][1])} Use the answer in your build plan.</p>'
            f'<details><summary>The course checks your build must pass</summary><ul>{checks}</ul></details>'
            '<label for="labPrediction" class="field-label">Build plan: what will your code do, and which cases will your tests cover?</label>'
            '<textarea id="labPrediction" placeholder="My approach, the edge cases I will test, and the case that must be refused or fail safely…"></textarea>'
            '<label for="labCases" class="field-label">Your Python code and tests</label>'
            '<p class="hint">Keep the given names. Write at least three functions whose names start with test_. Tab inserts four spaces.</p>'
            f'<textarea id="labCases" spellcheck="false" autocapitalize="off" autocomplete="off" style="{mono};min-height:380px;white-space:pre;overflow-wrap:normal;overflow-x:auto"></textarea>'
            '<div class="buttons"><button type="button" id="buildRun" data-lab-mode="build">Run my tests and the course checks</button><button type="button" id="buildReset" data-lab-mode="reset">Reset to starter code</button></div>'
            '<p id="labStatus" role="status" aria-live="polite">Write your plan, then run.</p>'
            f'<pre id="buildOutput" style="white-space:pre-wrap;overflow-wrap:anywhere;{mono}"></pre>'
            '<label for="labEvidence" class="field-label">Build record' + ('' if ch == 0 else ' · included in your submission') + '</label>'
            '<textarea id="labEvidence" readonly style="min-height:160px" placeholder="Created when you run. Changing the code clears it until you run again."></textarea>'
            + coverage_markup(ch) + (their_markup(ch, sp) if ch in THEIR_CH else '') + '</section>')


def their_markup(ch: int, sp: dict) -> str:
    """Run 3 · their change: the student's tests stay as they are while a part they did not write changes."""
    yes_g, no_g = 'Yes: my tests stayed green after their change', 'No: at least one of my tests turned red'
    yes_c, no_c = 'Yes: the result is still correct after their change', 'No: the result is no longer correct after their change'
    sel = lambda i, a, b: (f'<select id="{i}" style="display:block;width:100%;max-width:100%;white-space:normal"><option value="">Choose…</option><option value="{esc(a)}">{esc(a)}</option>'
                           f'<option value="{esc(b)}">{esc(b)}</option></select>')
    return ('<div class="their-step" id="theirStep"><p class="ey">RUN 3 · THEIR CHANGE · A PART YOU DID NOT WRITE CHANGES</p>'
            f'<p>{esc(sp["theirChange"])}</p>'
            f'<pre style="white-space:pre-wrap;overflow-wrap:anywhere">- {esc(sp["theirBefore"])}\n+ {esc(sp["theirAfter"])}</pre>'
            '<p>After your tests pass (Run 2), run their change. Do not edit your code or your tests first.</p>'
            '<div class="buttons"><button type="button" id="theirRun" data-lab-mode="their">Run their change</button></div>'
            '<p id="theirStatus" role="status" aria-live="polite"></p>'
            '<label for="theirGreen" class="field-label">Did your tests stay green?</label>' + sel('theirGreen', yes_g, no_g)
            + '<label for="theirCorrect" class="field-label">Is the result still correct?</label>' + sel('theirCorrect', yes_c, no_c)
            + '<label for="theirNote" class="field-label">One sentence · included in your submission: what in the run shows it?</label>'
            '<textarea id="theirNote" rows="2" maxlength="600" placeholder="My tests … after their change, and the result is … because the run shows …"></textarea>'
            '<input type="hidden" id="theirFacts" value="their-v0:run-3-not-recorded"></div>')


def coverage_markup(ch: int) -> str:
    """CLO 11 · the coverage step: after the three tests pass, change one input, run again, name the branch still untested."""
    return (COVERAGE_MARK + '<p class="ey">COVERAGE STEP · COURSE OUTCOME 11 · ' + esc(CLO11.upper()) + ('' if ch else ' · PRACTICE') + '</p>'
            '<p>The build record measures which lines and branches of your code your own tests run. The course checks are not counted.</p>'
            '<ol><li>Make your three tests pass and read the coverage lines in the build record.</li>'
            '<li>Change one input in one of your tests' + (' (in this build, the set of events you pass to <code>occurs</code>)' if ch == 12 else '') + '. Run again: the record shows <i>Run 2</i>.</li>'
            '<li>Write one sentence: which ' + ('gate outcome' if ch == 12 else 'branch') + ' is still not tested, and which input would test it.</li></ol>'
            '<label for="coverageNote" class="field-label">Coverage sentence' + ('' if ch == 0 else ' · included in your submission') + '</label>'
            '<textarea id="coverageNote" rows="2" maxlength="600" placeholder="After run 2, the branch on line … (if … is false) is still not tested; the input … would test it."></textarea></div>')


LAB_INLINE = re.compile(r"<script>/\* Deterministic teaching models\..*?module\.exports=StudyLab;\n?</script>", re.S)
BUILD_INLINE = re.compile(r"<script>/\* Python build tasks for Assignments.*?module\.exports=StudyBuild;\n?</script>", re.S)


def patch(path: Path, ch: int, sp: dict, eng: str) -> bool:
    s0 = s = path.read_text(encoding='utf-8')
    def one(old, new, count=1):
        nonlocal s
        if s.count(old) != count:
            raise SystemExit(f'{path.name}: expected {count}× {old[:70]!r}, found {s.count(old)}')
        s = s.replace(old, new)
    m = re.search(r'<section(?=[^>]*\bid="practical")[^>]*>.*?</section>', s, re.S)
    if not m: raise SystemExit(f'{path.name}: practical section not found')
    s = s[:m.start()] + markup(ch, sp) + s[m.end():]
    if OLD_LABELS in s: one(OLD_LABELS, NEW_LABELS, count=3)
    if OLD_BUDGET in s: one(OLD_BUDGET, NEW_BUDGET)
    if OLD_BUDGET_78 in s: one(OLD_BUDGET_78, NEW_BUDGET)
    if OLD_CHECK in s: one(OLD_CHECK, NEW_CHECK)
    # CLO 11 coverage step: the sentence is a Part A field, labelled in the export, and a second run is required
    if '"labEvidence", "coverageNote"' not in s:
        one(*COV_A)
    if '"coverageNote": "COVERAGE SENTENCE' not in s:
        one(*COV_LABEL, count=3)
    if COV_CHECK not in s:
        one(NEW_CHECK, NEW_CHECK + COV_CHECK)
    if ch in THEIR_CH:
        if THEIR_A[1] not in s:
            one(*THEIR_A)
        if THEIR_LABEL[1] not in s:
            one(*THEIR_LABEL, count=3)
        if THEIR_MARK in s:
            s = re.sub(re.escape(THEIR_MARK) + r'.*?\}\)\(\);\n', lambda _: THEIR_SCRIPT, s, count=1, flags=re.S)
        else:
            one(f'\nStudyBuild.mount({ch});\n', f'\nStudyBuild.mount({ch});\n' + THEIR_SCRIPT)
    if 'StudyLab.mount(' in s: one(f'\nStudyLab.mount({ch});\n', f'\nStudyBuild.mount({ch});\n')
    if LAB_INLINE.search(s): s = LAB_INLINE.sub(lambda _: '<script>' + eng + '</script>', s, count=1)
    else: s, n = BUILD_INLINE.subn(lambda _: '<script>' + eng + '</script>', s, count=1); assert n == 1, path.name
    # rubric: the second criterion assesses the build
    i = s.index('<table class="rubric">'); j = s.index('</table>', i); table = s[i:j]
    row = re.search(rf'<tr><th scope="row">{CRIT[ch]} · 1 point</th>.*?</tr>', table, re.S)
    if not row: raise SystemExit(f'{path.name}: rubric row {CRIT[ch]} not found')
    r = row.group(0)
    if OLD_FULL in r:
        r = r.replace(OLD_FULL, FULL); table = table.replace(row.group(0), r); s = s[:i] + table + s[j:]
    elif '<b>Build:</b>' not in r:
        r = r.replace('<details class="levels">', FULL + '<details class="levels">', 1)
        r = re.sub(r'(<b>0\.5:</b>.*?)(<br/>)', lambda m: m.group(1).rstrip() + HALF + m.group(2), r, count=1, flags=re.S)
        table = table.replace(row.group(0), r); s = s[:i] + table + s[j:]
    if s != s0: path.write_text(s, encoding='utf-8')
    return s != s0


def main() -> int:
    sp = spec(); eng = engine(sp)
    OUT.write_text(eng, encoding='utf-8')
    ex = ROOT / 'assignment-example.html'
    if ex.exists():
        t = ex.read_text(encoding='utf-8'); t2, n = BUILD_INLINE.subn(lambda _: '<script>' + eng + '</script>', t, count=1)
        t2, m = re.subn(r'<!--practice-build-->.*?<!--/practice-build-->', lambda _: '<!--practice-build-->' + markup(0, sp[0]) + '<!--/practice-build-->', t2, count=1, flags=re.S)
        if m != 1: raise SystemExit('assignment-example.html: practice-build markers not found')
        if n != 1: raise SystemExit('assignment-example.html: build engine block not found')
        if t2 != t: ex.write_text(t2, encoding='utf-8')
    pub = json.loads(PUB.read_text(encoding='utf-8')); done = []
    for a in pub['assignments']:
        if a['chapter'] in CRIT:
            if patch(ROOT / a['path'], a['chapter'], sp[a['chapter']], eng): done.append(a['chapter'])
            a['build'] = 'python-v2'
    PUB.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Python build applied or refreshed in chapters', done or 'none (already current)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
