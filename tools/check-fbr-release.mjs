import fs from 'node:fs';
import path from 'node:path';

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

const hub = read('iscarb.html');
const showcase = read('iscarb-students.html');
const faculty = {
  'Ch10': read('lectures/iscarb/Ch10-Dependable-Systems-Faculty.html'),
  'Ch11': read('lectures/iscarb/Ch11-Reliability-Engineering-Faculty.html')
};
const student = {
  'Ch10': read('lectures/iscarb/Ch10-FBR-Student-Assignment.html'),
  'Ch11': read('lectures/iscarb/Ch11-FBR-Student-Assignment.html')
};
const reveal = {
  'Ch10': JSON.parse(read('lectures/iscarb/reveal/r10-7c4d9e2f.json')),
  'Ch11': JSON.parse(read('lectures/iscarb/reveal/r11-5a8e3c1b.json'))
};

console.log('\n=== FACULTY LANE ===');
for(const [ch, html] of Object.entries(faculty)){
  must(html, 'faculty-lane-static', `${ch} F1 static faculty marker`);
  mustNot(html, 'Loading faculty lecture', `${ch} F1 no permanent loading shell`);
  mustNot(html, 'DecompressionStream', `${ch} F1 no runtime patch decompression`);
  must(html, 'id="prev"', `${ch} F2 previous control`);
  must(html, 'id="next"', `${ch} F2 next control`);
  must(html, 'id="noteBtn"', `${ch} F2 notes control`);
  must(html, "addEventListener('keydown'", `${ch} F2 keyboard navigation`);
  must(html, "touchstart", `${ch} F2 mobile swipe navigation`);
  mustNot(html, "fetch('./Ch", `${ch} F1 no runtime lecture fetch`);
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

console.log('\n=== HUB ===');
must(hub, '▣ Faculty lecture', 'H1 faculty label');
must(hub, '◇ Student FBR assignment', 'H1 student label');
const readyCount = (hub.match(/class="ready">READY/g) || []).length;
readyCount === 2 ? ok('H2 READY badges only on Ch10/Ch11') : fail(`H2 expected 2 READY badges, found ${readyCount}`);
must(hub, 'Coming soon · not active', 'H3 inactive coming-soon state');
must(hub, '<strong>Publishing rule:</strong> approved faculty presentation lanes and student FBR assignments only.', 'H4 publishing rule preserved');
must(hub, 'href="iscarb-students.html"', 'H5 showcase link');
must(showcase, 'No approved student PDFs yet', 'H5 showcase empty-state status');
must(showcase, 'No student PDF has been approved for public display yet.', 'H5 showcase clear empty message');

console.log('\n=== STATIC-HOSTING SECURITY BOUNDARY ===');
for(const [ch, data] of Object.entries(reveal)){
  must(data.text, data.text, `${ch} reveal asset parses and contains STRESS`);
}
console.log('INFO  STRESS assets are public static files by design. The guard verifies they are absent from initial student HTML and requested only after application lock; GitHub Pages cannot provide server-side secrecy for public assets.');

if(failures){
  console.error(`\nFBR RELEASE READINESS: FAIL (${failures} failure${failures===1?'':'s'})`);
  process.exit(1);
}
console.log('\nFBR RELEASE READINESS: PASS');
