import fs from 'node:fs';
import { chromium } from 'playwright';

const BASE = process.env.FBR_BASE_URL || 'http://127.0.0.1:8080';
const failures = [];
function pass(msg){ console.log(`PASS  ${msg}`); }
function fail(msg){ failures.push(msg); console.error(`FAIL  ${msg}`); }
function assert(cond,msg){ cond ? pass(msg) : fail(msg); }

const reveals = {
  Ch10: JSON.parse(fs.readFileSync('lectures/iscarb/reveal/r10-7c4d9e2f.json','utf8')),
  Ch11: JSON.parse(fs.readFileSync('lectures/iscarb/reveal/r11-5a8e3c1b.json','utf8'))
};

const browser = await chromium.launch({headless:true});

async function facultySmoke(path,label,chapter){
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(BASE+path,{waitUntil:'domcontentloaded'});
  await page.waitForURL(/Faculty-Presenter\.html/,{timeout:15000});
  await page.waitForSelector('#lecture');
  const rich=page.frameLocator('#lecture');
  await rich.locator('#stage .slide.on').waitFor({timeout:30000});
  await page.waitForFunction(()=>window.__facultyFocus?.indexes?.length>1,null,{timeout:30000});

  assert(page.url().includes('Faculty-Presenter.html'),`${label} F1 alias opens Faculty Focus presenter`);
  for(const id of ['#prev','#notes','#next','#present']) assert(await page.locator(id).isVisible(),`${label} F2 ${id.slice(1)} mobile control visible`);
  const taskHref=await page.locator('#studentTask').getAttribute('href');
  assert(taskHref===`Ch${chapter}-FBR-Student-Assignment.html`,`${label} Faculty header links directly to Student FBR assignment`);

  const firstText=(await rich.locator('#stage .slide.on').innerText()).trim().slice(0,700);
  assert(firstText.length>20,`${label} rich original slide renders substantive content`);
  assert(await rich.locator('#stars').count()===1,`${label} original rich ISCARB visual engine preserved`);

  const info=await page.evaluate(()=>window.__facultyFocus);
  assert(info.rawCount>0,`${label} Faculty Focus sees original deck (${info.rawCount} raw slides)`);
  assert(info.indexes.length>1,`${label} Faculty Focus has usable teaching sequence`);
  assert(info.indexes.length<info.rawCount,`${label} heavy written/activity slides are filtered from Faculty sequence`);
  assert(Object.values(info.special).includes('fit'),`${label} FIT moment remains in Faculty sequence`);
  assert(Object.values(info.special).includes('stress'),`${label} STRESS/REFIT remains as spoken demonstration`);

  const barDisplay=await rich.locator('#bar').evaluate(el=>getComputedStyle(el).display);
  assert(barDisplay==='none',`${label} old in-class task/timer bar hidden in Faculty Focus`);
  const visibleWriting=await rich.locator('#stage .slide.on textarea,#stage .slide.on select,#stage .slide.on [contenteditable="true"],#stage .slide.on input[type="text"],#stage .slide.on input[type="search"],#stage .slide.on input[type="email"],#stage .slide.on input[type="number"],#stage .slide.on input[type="url"],#stage .slide.on input[type="tel"],#stage .slide.on input[type="date"],#stage .slide.on input[type="time"],#stage .slide.on input:not([type])').evaluateAll(xs=>xs.filter(x=>getComputedStyle(x).display!=='none'&&getComputedStyle(x).visibility!=='hidden').length);
  assert(visibleWriting===0,`${label} no visible student-writing controls in current Faculty slide`);

  const frameBox=await page.locator('#lecture').boundingBox();
  assert(Boolean(frameBox&&frameBox.width>=380&&frameBox.height>=210),`${label} portrait lecture uses full mobile width`);
  const firstRaw=await rich.locator('body').evaluate(()=>window.cur);
  await page.click('#next'); await page.waitForTimeout(150);
  const secondRaw=await rich.locator('body').evaluate(()=>window.cur);
  assert(secondRaw!==firstRaw,`${label} mobile Next changes slide`);
  assert(info.indexes.includes(secondRaw),`${label} mobile Next lands only on Faculty Focus slide`);
  await page.click('#prev'); await page.waitForTimeout(150);
  const backRaw=await rich.locator('body').evaluate(()=>window.cur);
  assert(backRaw===firstRaw,`${label} mobile Previous returns to first focus slide`);

  await page.click('#notes'); await page.waitForTimeout(120);
  assert(await rich.locator('#notes.on').count()===1,`${label} mobile Notes opens instructor overlay`);
  await page.click('#notes');
  assert(errors.length===0,`${label} no page JavaScript errors in Chromium mobile`);
  await context.close();
}

async function studentSmoke(path,label,reveal){
  const context=await browser.newContext({viewport:{width:390,height:844}});
  let page=await context.newPage();
  const requested=[]; const errors=[];
  page.on('request',r=>requested.push(r.url()));
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(BASE+path,{waitUntil:'domcontentloaded'});
  assert(!(await page.locator('body').innerText()).includes(reveal.text),`${label} S3 STRESS absent before lock`);
  assert(!requested.some(u=>u.includes('/reveal/')),`${label} S3 no reveal network request before lock`);

  await page.fill('#student','Release Test Student');
  await page.fill('#sid','TEST-001');
  await page.fill('#section','CI');
  await page.fill('#fit','This engineering mechanism is fit because the decision and stated operating context require this specific evidence-based choice.');
  await page.fill('#bound','This decision remains fit only while the stated operating conditions and evidence assumptions remain observable and unchanged.');
  await page.fill('#act','Issue a measurable professional engineering artifact with an explicit owner, trigger, and acceptance condition for this use.');
  await page.fill('#evidence','Use signed logs, representative measurements, an observation window, and an accountable evidence owner to defend the action.');
  await page.click('#save'); await page.waitForTimeout(100);
  const savedFit=await page.inputValue('#fit');
  await page.close();

  page=await context.newPage();
  const reopenedRequests=[]; const reopenedErrors=[];
  page.on('request',r=>reopenedRequests.push(r.url()));
  page.on('pageerror',e=>reopenedErrors.push(String(e)));
  await page.goto(BASE+path,{waitUntil:'domcontentloaded'});
  assert((await page.inputValue('#fit'))===savedFit,`${label} S1 local data survives tab close/reopen`);
  assert(!reopenedRequests.some(u=>u.includes('/reveal/')),`${label} S3 reopened unlocked page still does not request STRESS`);

  await page.click('#lock');
  await page.waitForSelector('.card.stress');
  assert(await page.locator('#fit').getAttribute('readonly')!==null,`${label} S2 FIT is read-only after lock`);
  assert(await page.locator('#bound').getAttribute('readonly')!==null,`${label} S2 BOUND is read-only after lock`);
  assert((await page.locator('#lockBanner').innerText()).includes('PART A LOCKED'),`${label} S2 visible locked state`);
  assert((await page.locator('.card.stress').innerText()).includes(reveal.text),`${label} S3 STRESS appears after lock`);
  assert(reopenedRequests.some(u=>u.includes('/reveal/')),`${label} S3 reveal asset requested only after lock`);

  const stored=await page.evaluate(()=>JSON.parse(localStorage.getItem(CONFIG.key)));
  assert(Boolean(stored?.lockedPartA?.fit),`${label} S2 locked Part A snapshot persisted`);
  assert(Boolean(stored?.lockAt),`${label} S5 lock timestamp persisted`);
  assert(Boolean(stored?.lastModifiedAt),`${label} S5 last-modified timestamp persisted`);

  await page.check('input[name=refit][value="REVISE"]');
  await page.fill('#refitwhy','The changed condition crosses the applicability boundary, so the original action must be revised rather than merely restated.');
  await page.fill('#revised','Revise the professional artifact so that its metric, evidence, trigger, and accountable owner match the changed condition.');
  await page.click('#save');
  const markdown=await page.evaluate(()=>md());
  for(const section of ['## FIT','## BOUND','## ACT','## EVIDENCE','## STRESS','## REFIT']) assert(markdown.includes(section),`${label} S4 export contains ${section.replace('## ','')}`);
  assert(markdown.includes('TEST-001'),`${label} S6 export contains Student ID`);
  assert(markdown.includes('Part A locked:'),`${label} S5 export contains lock timestamp`);
  assert(markdown.includes('Last modified:'),`${label} S5 export contains last-modified timestamp`);
  await page.evaluate(()=>buildPrintSheet());
  const printText=await page.locator('#printSheet').innerText();
  assert(printText.includes('TEST-001')&&printText.includes('FIT')&&printText.includes('REFIT'),`${label} S8 print/PDF surface is complete`);
  assert([...errors,...reopenedErrors].length===0,`${label} no page JavaScript errors in Chromium`);
  await context.close();
}

async function hubSmoke(){
  const context=await browser.newContext({viewport:{width:390,height:844}}); const page=await context.newPage();
  await page.goto(BASE+'/iscarb.html',{waitUntil:'domcontentloaded'});
  assert(await page.getByText('▣ Faculty lecture').count()===2,'Hub H1 has two Faculty lane links');
  assert(await page.getByText('◇ Student FBR assignment').count()===2,'Hub H1 has two Student FBR links');
  assert(await page.locator('.ready').count()===2,'Hub H2 only Ch10/Ch11 marked READY');
  assert(await page.getByText('Coming soon · not active').count()>=1,'Hub H3 inactive chapters are not links');
  assert((await page.locator('.strip').innerText()).includes('Publishing rule:'),'Hub H4 publishing rule visible');
  const facultyHrefs=await page.locator('a.faculty').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')));
  assert(facultyHrefs.some(x=>x?.includes('Ch10-Dependable-Systems-Faculty.html')),'Hub Faculty Ch10 routes to Faculty Focus alias');
  assert(facultyHrefs.some(x=>x?.includes('Ch11-Reliability-Engineering-Faculty.html')),'Hub Faculty Ch11 routes to Faculty Focus alias');
  await context.close();
}

try{
  await facultySmoke('/lectures/iscarb/Ch10-Dependable-Systems-Faculty.html','Ch10 Faculty','10');
  await facultySmoke('/lectures/iscarb/Ch11-Reliability-Engineering-Faculty.html','Ch11 Faculty','11');
  await studentSmoke('/lectures/iscarb/Ch10-FBR-Student-Assignment.html','Ch10 Student',reveals.Ch10);
  await studentSmoke('/lectures/iscarb/Ch11-FBR-Student-Assignment.html','Ch11 Student',reveals.Ch11);
  await hubSmoke();
} finally { await browser.close(); }
if(failures.length){console.error(`\nFBR BROWSER SMOKE: FAIL (${failures.length})`);failures.forEach(x=>console.error(' - '+x));process.exit(1)}
console.log('\nFBR BROWSER SMOKE: PASS');