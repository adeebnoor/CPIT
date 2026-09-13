import fs from 'node:fs';
import assert from 'node:assert/strict';
const read=p=>fs.readFileSync(p,'utf8');
const chapters=[10,11,12,13,14,15,16,17,20];
const files=fs.readdirSync('lectures/iscarb');
for(const ch of chapters){
 const source=read(`lectures/iscarb/Ch${ch}-FBR-Student-Assignment.html`);
 const revealPath=source.match(/reveal:'([^']+)'/)[1];
 const reveal=JSON.parse(read('lectures/iscarb/'+revealPath));
 assert(reveal.text?.length>0,`Ch${ch} STRESS file`);
 assert(!source.includes(reveal.text),`Ch${ch} initial HTML must not expose assessed STRESS`);
 for(const marker of ['lockedPartA','readOnly=true','lockAt=now()','pagehide','Print / PDF','## FIT','## BOUND','## ACT','## EVIDENCE','## STRESS','## REFIT','assignment-learning-path','warmup-answer'])assert(source.includes(marker),`Ch${ch} missing ${marker}`);
 assert(source.includes(`keyBase:'fbr:cpit455:ch${ch}:prod:v4'`),'Preserve existing saved attempts');
 assert(!/navigator\.sendBeacon|new WebSocket|new XMLHttpRequest|gtag\(/.test(source),'No new answer telemetry');
 const lectureFile=files.find(p=>p.startsWith(`Ch${ch}-`)&&!/FBR|Faculty|Final100/.test(p)&&p.endsWith('.html'));
 const lecture=read('lectures/iscarb/'+lectureFile);
 assert(lecture.includes('data-iscarb-lesson="6"'),`Ch${ch} uses shared classroom`);
 for(const code of [...lecture.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]))new Function(code);
 for(const id of ['prev','next','mode','font','hide-answers','outline-button'])assert(lecture.includes(`id="${id}"`),`Ch${ch} ${id}`);
 console.log(`PASS Ch${ch}: committed assessment, hidden STRESS, stable storage identity, complete classroom and valid JavaScript`);
}
const gateway=read('fbr-submission.html');
for(const needle of ['id="sid"','id="ack"','id="openBtn" disabled','Evaluation rubric · 4 points'])assert(gateway.includes(needle),'Gateway: '+needle);
for(const ch of chapters)assert(read('iscarb.html').includes(`fbr-submission.html?chapter=${ch}`),`Hub assignment ${ch}`);
assert(read('.github/workflows/static.yml').includes('tools/build_public_site.py'));
console.log('FBR release readiness PASS. Assessed STRESS is public static data; the interaction test checks request ordering.');
