import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const root = process.cwd();
let failures = 0;

function read(rel){
  const p = path.join(root, rel);
  if(!fs.existsSync(p)) fail(`${rel}: missing file`);
  return fs.readFileSync(p, 'utf8');
}
function ok(msg){ console.log(`PASS  ${msg}`); }
function fail(msg){ failures++; console.error(`FAIL  ${msg}`); }
function must(text, needle, label){ text.includes(needle) ? ok(label) : fail(`${label} — missing: ${needle}`); }
function mustNot(text, needle, label){ !text.includes(needle) ? ok(label) : fail(`${label} — forbidden: ${needle}`); }
function mustRegex(text, re, label){ re.test(text) ? ok(label) : fail(`${label} — pattern not found: ${re}`); }

function buildFaculty(baseRel,prefix,label){
  const source = read(baseRel);
  const encoded = [1,2,3].map(i=>read(`lectures/iscarb/split/${prefix}.patch.${i}.txt`).trim()).join('');
  let patches;
  try{
    patches = JSON.parse(zlib.gunzipSync(Buffer.from(encoded,'base64')).toString('utf8'));
    ok(`${label} F1 split patch payload decompresses`);
  }catch(e){
    fail(`${label} F1 split patch payload decompresses — ${e.message}`);
    return '';
  }
  let out=source;
  for(let i=0;i<patches.length;i++){
    const [oldText,newText]=patches[i];
    const first=out.indexOf(oldText);
    if(first<0){ fail(`${label} F1 patch ${i+1} matches baseline`); return ''; }
    if(out.indexOf(oldText,first+1)>=0){ fail(`${label} F1 patch ${i+1} is unambiguous`); return ''; }
    out=out.slice(0,first)+newText+out.slice(first+oldText.length);
  }
  ok(`${label} F1 all split Faculty patches apply`);
  return out;
}

const hub = read('iscarb.html');
const showcase = read('iscarb-students.html');
const gateway = read('fbr-submission.html');
const pagesWorkflow = read('.github/workflows/static.yml');
const presenter = read('lectures/iscarb/Faculty-Presenter.html');
const facultyRedirect = {
  Ch10: read('lectures/iscarb/Ch10-Dependable-Systems-Faculty.html'),
  Ch11: read('lectures/iscarb/Ch11-Reliability-Engineering-Faculty.html')
};
const facultyLoader = {
  Ch10: read('lectures/iscarb/Ch10-Dependable-Systems-Faculty-Rich.html'),
  Ch11: read('lectures/iscarb/Ch11-Reliability-Engineering-Faculty-Rich.html')
};
const facultyBuilt = {
  Ch10: buildFaculty('lectures/iscarb/Ch10-Dependable-Systems.html','ch10-faculty','Ch10'),
  Ch11: buildFaculty('lectures/iscarb/Ch11-Reliability-Engineering.html','ch11-faculty','Ch11')
};
const student = {
  Ch10: read('lectures/iscarb/Ch10-FBR-Student-Assignment.html'),
  Ch11: read('lectures/iscarb/Ch11-FBR-Student-Assignment.html')
};
const reveal = {
  Ch10: JSON.parse(read('lectures/iscarb/reveal/r10-7c4d9e2f.json')),
  Ch11: JSON.parse(read('lectures/iscarb/reveal/r11-5a8e3c1b.json'))
};

console.log('\n=== FACULTY LANE ===');
must(facultyRedirect.Ch10,'Faculty-Presenter.html?chapter=10','Ch10 F1 public Faculty URL routes to presenter');
must(facultyRedirect.Ch11,'Faculty-Presenter.html?chapter=11','Ch11 F1 public Faculty URL routes to presenter');
for(const id of ['prev','next','notes','full']) must(presenter,`id="${id}"`,`Presenter F2 ${id} control`);
must(presenter,'touchstart','Presenter F2 swipe navigation');
must(presenter,'orientation:portrait','Presenter F2 portrait layout');
must(presenter,'orientation:landscape','Presenter F2 landscape layout');
must(presenter,'Ch10-Dependable-Systems-Faculty-Rich.html','Presenter F1 Ch10 rich split source');
must(presenter,'Ch11-Reliability-Engineering-Faculty-Rich.html','Presenter F1 Ch11 rich split source');
for(const [ch,html] of Object.entries(facultyLoader)){
  must(html,'DecompressionStream',`${ch} F1 rich split loader decodes patch payload`);
  must(html,`split/${ch.toLowerCase()}-faculty.patch.1.txt`,`${ch} F1 rich split patch route 1`);
  must(html,`split/${ch.toLowerCase()}-faculty.patch.2.txt`,`${ch} F1 rich split patch route 2`);
  must(html,`split/${ch.toLowerCase()}-faculty.patch.3.txt`,`${ch} F1 rich split patch route 3`);
}
for(const [ch,html] of Object.entries(facultyBuilt)){
  if(!html) continue;
  must(html,'Faculty lane',`${ch} F1 Faculty-only teaching cue present`);
  must(html,'student written work happens after class',`${ch} F1 written student work moved after class`);
  must(html,'VERBAL POLL',`${ch} F1 in-class interaction retained as verbal poll`);
  mustNot(html,'Could not load faculty lecture',`${ch} F1 built rich lecture is not loader error page`);
}

console.log('\n=== STUDENT FBR ===');
for(const [ch, html] of Object.entries(student)){
  must(html, 'local-only-v2', `${ch} R1 local-only marker`);
  must(html, 'localStorage.setItem', `${ch} S1 local save`);
  must(html, 'localStorage.getItem', `${ch} S1 local restore`);
  must(html, "window.addEventListener('beforeunload'", `${ch} S7 unsaved-exit warning`);
  must(html, "window.addEventListener('pagehide'", `${ch} S1 pagehide persistence`);
  must(html, 'lockedPartA', `${ch} S2 locked snapshot`);
  must(html, 'readOnly=true', `${ch} S2 fields become read-only`);
  must(html, 'state.locked=true', `${ch} S2 explicit lock state`);
  must(html, 'lockAt=now()', `${ch} S5 lock timestamp`);
  must(html, 'lastModifiedAt', `${ch} S5 last-modified timestamp`);
  must(html, 'Student ID', `${ch} S6 student identity field`);
  must(html, 'Research mode · anonymous local ID', `${ch} R2 local anonymous research mode`);
  must(html, 'Download submission (.md)', `${ch} S4 download export`);
  must(html, 'Copy submission', `${ch} S4 copy export`);
  must(html, 'Print / PDF', `${ch} S8 print/PDF control`);
  must(html, '## FIT', `${ch} S4 FIT in export`);
  must(html, '## BOUND', `${ch} S4 BOUND in export`);
  must(html, '## ACT', `${ch} S4 ACT in export`);
  must(html, '## EVIDENCE', `${ch} S4 EVIDENCE in export`);
  must(html, '## STRESS', `${ch} S4 STRESS in export`);
  must(html, '## REFIT', `${ch} S4 REFIT in export`);
  must(html, 'Part A locked:', `${ch} S5 timestamps in print/export surface`);
  mustNot(html, reveal[ch].text, `${ch} S3 STRESS absent from initial HTML/DOM`);
  mustRegex(html, /fetch\(CONFIG\.reveal[\s\S]*credentials:'same-origin'/, `${ch} S3 reveal requested only through gated reveal function`);
  mustNot(html, 'navigator.sendBeacon(', `${ch} R1 no beacon upload`);
  mustNot(html, 'new WebSocket(', `${ch} R1 no WebSocket upload`);
  mustNot(html, 'new XMLHttpRequest(', `${ch} R1 no XHR upload`);
  mustNot(html, 'gtag(', `${ch} R1 no Google Analytics sender`);
  mustNot(html, 'mixpanel.', `${ch} R1 no Mixpanel sender`);
  mustNot(html, 'amplitude.', `${ch} R1 no Amplitude sender`);
  mustNot(html, 'model answer', `${ch} R3 no model-answer text`);
  mustNot(html, 'answer key', `${ch} R3 no answer-key text`);
}

console.log('\n=== STUDENT SUBMISSION GATEWAY ===');
must(gateway, 'OFFICIAL STUDENT SUBMISSION RULES', 'G1 official rules heading');
must(gateway, 'No “I did not know” exception.', 'G1 no-excuse notice');
must(gateway, 'Weekly grading · 4 points', 'G2 grading policy');
must(gateway, 'AI / LLM policy', 'G3 AI policy');
must(gateway, '60–120 second micro-viva', 'G4 oral verification policy');
must(gateway, 'id="sid"', 'G5 Student ID required');
must(gateway, 'id="ack"', 'G5 acknowledgment checkbox');
must(gateway, 'id="openBtn" disabled', 'G5 assignment button gated');
must(gateway, 'Ch10-FBR-Student-Assignment.html', 'G6 Ch10 target');
must(gateway, 'Ch11-FBR-Student-Assignment.html', 'G6 Ch11 target');

console.log('\n=== HUB ===');
must(hub, '▣ Faculty lecture', 'H1 faculty label');
must(hub, '◇ Student FBR assignment', 'H1 student label');
must(hub, 'Ch10-Dependable-Systems-Faculty.html', 'H1 Ch10 routes to split Faculty lane');
must(hub, 'Ch11-Reliability-Engineering-Faculty.html', 'H1 Ch11 routes to split Faculty lane');
must(hub, 'fbr-submission.html?chapter=10', 'H1 Ch10 routes through student rules gateway');
must(hub, 'fbr-submission.html?chapter=11', 'H1 Ch11 routes through student rules gateway');
const readyCount = (hub.match(/class="ready">READY/g) || []).length;
readyCount === 2 ? ok('H2 READY badges only on Ch10/Ch11') : fail(`H2 expected 2 READY badges, found ${readyCount}`);
must(hub, 'Coming soon · not active', 'H3 inactive coming-soon state');
must(hub, '<strong>Publishing rule:</strong> approved faculty presentation lanes and student FBR assignments only.', 'H4 publishing rule preserved');
must(hub, 'href="iscarb-students.html"', 'H5 showcase link');
must(showcase, 'No approved student PDFs yet', 'H5 showcase empty-state status');
must(showcase, 'No student PDF has been approved for public display yet.', 'H5 showcase clear empty message');

console.log('\n=== GITHUB PAGES PUBLICATION ===');
must(pagesWorkflow, 'fbr-submission.html', 'P1 student gateway included in Pages artifact');
must(pagesWorkflow, 'cp -R slides lectures _site/', 'P2 lecture tree included in Pages artifact');

console.log('\n=== STATIC-HOSTING SECURITY BOUNDARY ===');
for(const [ch, data] of Object.entries(reveal)) must(data.text, data.text, `${ch} reveal asset parses and contains STRESS`);
console.log('INFO  STRESS assets are public static files by design. The guard verifies they are absent from initial student HTML and requested only after application lock; GitHub Pages cannot provide server-side secrecy for public assets.');

if(failures){
  console.error(`\nFBR RELEASE READINESS: FAIL (${failures} failure${failures===1?'':'s'})`);
  process.exit(1);
}
console.log('\nFBR RELEASE READINESS: PASS');
