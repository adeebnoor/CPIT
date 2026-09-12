import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
let failures = 0;

function read(rel){
  const p=path.join(root,rel);
  if(!fs.existsSync(p)){ fail(`${rel}: missing file`); return ''; }
  return fs.readFileSync(p,'utf8');
}
function ok(msg){console.log(`PASS  ${msg}`)}
function fail(msg){failures++;console.error(`FAIL  ${msg}`)}
function must(text,needle,label){text.includes(needle)?ok(label):fail(`${label} — missing: ${needle}`)}
function mustNot(text,needle,label){!text.includes(needle)?ok(label):fail(`${label} — forbidden: ${needle}`)}
function count(text,re){return (text.match(re)||[]).length}

const hub=read('iscarb.html');
const showcase=read('iscarb-students.html');
const gateway=read('fbr-submission.html');
const pagesWorkflow=read('.github/workflows/static.yml');
const presenter=read('lectures/iscarb/InClass-Presenter.html');
const presenterAlias=read('lectures/iscarb/Faculty-Presenter.html');
const visual2=read('lectures/iscarb/inclass-visual-v2.js');
const visual5=read('lectures/iscarb/inclass-visual-v4.js');
const visual5css=read('lectures/iscarb/inclass-visual-v4.css');
const lecture={
  Ch10:read('lectures/iscarb/Ch10-Dependable-Systems.html'),
  Ch11:read('lectures/iscarb/Ch11-Reliability-Engineering.html')
};
const facultyAlias={
  Ch10:read('lectures/iscarb/Ch10-Dependable-Systems-Faculty.html'),
  Ch11:read('lectures/iscarb/Ch11-Reliability-Engineering-Faculty.html')
};
const student={
  Ch10:read('lectures/iscarb/Ch10-FBR-Student-Assignment.html'),
  Ch11:read('lectures/iscarb/Ch11-FBR-Student-Assignment.html')
};
const reveal={
  Ch10:JSON.parse(read('lectures/iscarb/reveal/r10-7c4d9e2f.json')),
  Ch11:JSON.parse(read('lectures/iscarb/reveal/r11-5a8e3c1b.json'))
};

console.log('\n=== IN-CLASS PRESENTER ===');
must(presenterAlias,"location.replace('InClass-Presenter.html'+location.search+location.hash)",'F1 compatibility alias routes to current In-Class presenter');
for(const id of ['prev','notes','next','present']) must(presenter,`id=\"${id}\"`,`F2 ${id} control present`);
must(presenter,'touchstart','F2 swipe navigation present');
must(presenter,'orientation:portrait','F2 portrait layout present');
must(presenter,'orientation:landscape','F2 landscape layout present');
must(presenter,'inclass-visual-v4.js?v=20260912-visual5','F3 visual5 layer loaded');
must(presenter,"Ch10-Dependable-Systems.html?v=20260912-visual5",'F3 Ch10 visual5 source');
must(presenter,"Ch11-Reliability-Engineering.html?v=20260912-visual5",'F3 Ch11 visual5 source');
must(presenter,"../../fbr-submission.html?chapter=10",'F4 Ch10 After-Class routes through official gateway');
must(presenter,"../../fbr-submission.html?chapter=11",'F4 Ch11 After-Class routes through official gateway');
must(presenter,"u?.k==='R15'||u?.k==='R20'",'F5 AI and ETEC readiness moments forced into Faculty sequence');
must(facultyAlias.Ch10,'Faculty-Presenter.html?chapter=10&v=20260912-visual5','F6 Ch10 public In-Class alias uses visual5');
must(facultyAlias.Ch11,'Faculty-Presenter.html?chapter=11&v=20260912-visual5','F6 Ch11 public In-Class alias uses visual5');

console.log('\n=== 20-UNIT GRAMMAR ===');
for(const [ch,html] of Object.entries(lecture)){
  let missing=[];
  for(let i=1;i<=20;i++){
    const key=`R${String(i).padStart(2,'0')}`;
    if(!html.includes(`k:'${key}'`)) missing.push(key);
  }
  missing.length?fail(`${ch} 20-unit grammar missing: ${missing.join(', ')}`):ok(`${ch} preserves R01–R20 20-unit grammar`);
}

console.log('\n=== VISUAL5 CLASSROOM QA GUARDS ===');
try{new Function(visual2);ok('V1 visual-v2 JavaScript parses')}catch(e){fail(`V1 visual-v2 JavaScript syntax — ${e.message}`)}
try{new Function(visual5);ok('V1 visual5 JavaScript parses')}catch(e){fail(`V1 visual5 JavaScript syntax — ${e.message}`)}
must(visual5,'AI Literacy','V2 explicit AI visual identity');
must(visual5,'ETEC Readiness','V2 explicit ETEC readiness visual identity');
must(visual5,'COURSE-BUILT PRACTICE · NOT AN OFFICIAL ETEC ITEM','V2 ETEC non-official disclaimer');
must(visual5,'ETEC Readiness Check: What did you take from Dependable Systems?','V3 Ch10 ETEC readiness is English');
must(visual5,'ETEC Readiness Check: What did you take from Reliability Engineering?','V3 Ch11 ETEC readiness is English');
must(visual5,"if(ch!=='10')return",'V4 Agile patch is Chapter 10 only');
must(visual5,"const is11=ch==='11'",'V4 stress mutation is chapter-specific');
must(visual5css,'.slide.v4-roomy h1{font-size:58px','V5 sparse-slide projection title enlarged');
must(visual5css,'.slide.v4-roomy .area{justify-content:center','V5 sparse-slide content vertically centered');
must(visual5css,'.slide.v4-normal h1{font-size:46px','V5 normal projection typography enlarged');
must(visual5css,'.v4-badge.ai','V6 AI badge styling present');
must(visual5css,'.v4-badge.etec','V6 ETEC badge styling present');

console.log('\n=== STUDENT FBR ===');
for(const [ch,html] of Object.entries(student)){
  must(html,'localStorage.setItem',`${ch} S1 local save`);
  must(html,'localStorage.getItem',`${ch} S1 local restore`);
  must(html,"window.addEventListener('pagehide'",`${ch} S1 pagehide persistence`);
  must(html,'lockedPartA',`${ch} S2 locked Part A snapshot`);
  must(html,'readOnly=true',`${ch} S2 Part A becomes read-only`);
  must(html,'lockAt=now()',`${ch} S2 lock timestamp`);
  must(html,'Student ID',`${ch} S3 Student ID present`);
  must(html,'Print / PDF',`${ch} S4 PDF export present`);
  for(const sec of ['## FIT','## BOUND','## ACT','## EVIDENCE','## STRESS','## REFIT']) must(html,sec,`${ch} S4 export contains ${sec.slice(3)}`);
  mustNot(html,reveal[ch].text,`${ch} S5 STRESS absent from initial HTML`);
  mustNot(html,'navigator.sendBeacon(',`${ch} S6 no beacon upload`);
  mustNot(html,'new WebSocket(',`${ch} S6 no WebSocket upload`);
  mustNot(html,'new XMLHttpRequest(',`${ch} S6 no XHR upload`);
  mustNot(html,'gtag(',`${ch} S6 no Google Analytics sender`);
  mustNot(html,'model answer',`${ch} S7 no model-answer text`);
  mustNot(html,'answer key',`${ch} S7 no answer-key text`);
}

console.log('\n=== AFTER-CLASS ENTRY ===');
must(gateway,'CPIT-455 · OFFICIAL AFTER-CLASS FBR ENTRY','G1 official After-Class entry heading');
must(gateway,'Quick start · 4 steps','G1 four-step quick start');
must(gateway,'Official submission:</b> the course LMS only','G2 LMS-only submission statement');
must(gateway,'Evaluation rubric · 4 points','G3 4-point grading rubric');
must(gateway,'AI / LLM policy','G4 AI policy');
must(gateway,'60–120 second micro-viva','G5 micro-viva policy');
must(gateway,'id="sid"','G6 Student ID required');
must(gateway,'id="ack"','G6 acknowledgment required');
must(gateway,'id="openBtn" disabled','G6 assignment button initially gated');
must(gateway,'Ch10-FBR-Student-Assignment.html','G7 Ch10 assignment target');
must(gateway,'Ch11-FBR-Student-Assignment.html','G7 Ch11 assignment target');
must(gateway,'Recommended PDF filename','G8 PDF filename guidance');
must(gateway,'Expected time:</b> 25–40 minutes','G8 expected task time');

console.log('\n=== HUB ===');
must(hub,'▣ In-Class','H1 In-Class label');
must(hub,'◇ After-Class','H1 After-Class label');
must(hub,'Ch10-Dependable-Systems-Faculty.html','H1 Ch10 In-Class route');
must(hub,'Ch11-Reliability-Engineering-Faculty.html','H1 Ch11 In-Class route');
must(hub,'fbr-submission.html?chapter=10','H1 Ch10 After-Class gateway route');
must(hub,'fbr-submission.html?chapter=11','H1 Ch11 After-Class gateway route');
const readyCount=count(hub,/class="ready">READY/g);
readyCount===2?ok('H2 READY badges only on Ch10/Ch11'):fail(`H2 expected 2 READY badges, found ${readyCount}`);
must(hub,'Coming soon · not active','H3 inactive chapters remain unavailable');
must(hub,'Publishing rule:</strong> approved In-Class presentations and After-Class FBR assignments only.','H4 publishing rule matches split delivery');
must(hub,'href="iscarb-students.html"','H5 student showcase link');
must(showcase,'No approved student PDFs yet','H5 showcase empty state');

console.log('\n=== GITHUB PAGES / SECURITY BOUNDARY ===');
must(pagesWorkflow,'fbr-submission.html','P1 After-Class gateway included in Pages artifact');
must(pagesWorkflow,'cp -R slides lectures _site/','P2 lecture tree included in Pages artifact');
for(const [ch,data] of Object.entries(reveal)){
  data?.text?ok(`${ch} reveal asset parses and contains STRESS`):fail(`${ch} reveal asset missing STRESS text`);
}
console.log('INFO  STRESS assets remain public static files by design. The browser smoke test verifies that they are not requested before Part A is locked.');

if(failures){
  console.error(`\nFBR RELEASE READINESS: FAIL (${failures} failure${failures===1?'':'s'})`);
  process.exit(1);
}
console.log('\nFBR RELEASE READINESS: PASS');
