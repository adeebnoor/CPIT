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
  await page.waitForURL(/InClass-Presenter\.html/,{timeout:15000});
  await page.waitForSelector('#lecture');
  const rich=page.frameLocator('#lecture');
  await rich.locator('#stage .slide.on').waitFor({timeout:30000});
  await page.waitForFunction(()=>window.__facultyFocus?.indexes?.length>1,null,{timeout:30000});

  assert(page.url().includes('InClass-Presenter.html'),`${label} F1 direct In-Class presenter opens`);
  assert(!((await page.locator('#status').innerText()).toLowerCase().includes('loading')),`${label} F1 presenter shows no visible Loading state`);
  for(const id of ['#prev','#notes','#next','#present']) assert(await page.locator(id).isVisible(),`${label} F2 ${id.slice(1)} mobile control visible`);
  const taskHref=await page.locator('#studentTask').getAttribute('href');
  assert(taskHref===`../../fbr-submission.html?chapter=${chapter}`,`${label} presenter routes through official After-Class gateway`);

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

async function facultyDesktopSmoke(path,label){
  const context=await browser.newContext({viewport:{width:1536,height:864}});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(BASE+path,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#lecture');
  const rich=page.frameLocator('#lecture');
  await rich.locator('#stage .slide.on').waitFor({timeout:30000});
  await page.waitForFunction(()=>window.__facultyFocus?.indexes?.length>1,null,{timeout:30000});
  assert(!((await page.locator('#status').innerText()).toLowerCase().includes('loading')),`${label} desktop presenter shows no visible Loading state`);
  const box=await page.locator('#lecture').boundingBox();
  assert(Boolean(box&&box.width>=1450&&box.height>=700),`${label} desktop classroom viewport uses large projection surface`);
  const before=await rich.locator('body').evaluate(()=>window.cur);
  await page.click('#next'); await page.waitForTimeout(140);
  const after=await rich.locator('body').evaluate(()=>window.cur);
  assert(after!==before,`${label} desktop Next navigation works`);
  await page.click('#prev'); await page.waitForTimeout(100);
  await page.click('#present'); await page.waitForTimeout(120);
  assert(errors.length===0,`${label} Present control invokes without JavaScript error in desktop Chromium`);
  if(await page.evaluate(()=>Boolean(document.fullscreenElement))) await page.keyboard.press('Escape').catch(()=>{});
  await context.close();
}

async function enterAssignment(page,chapter){
  await page.goto(BASE+`/fbr-submission.html?chapter=${chapter}`,{waitUntil:'domcontentloaded'});
  const expectedWeek=chapter==='11'?'11':'10';
  assert(await page.locator('#openBtn').isDisabled(),`Ch${chapter} gateway disabled without Student ID / acknowledgment`);
  assert((await page.locator('#pdfFilenameRule').innerText()).includes(`W${expectedWeek}`),`Ch${chapter} gateway PDF filename uses W${expectedWeek}`);
  assert((await page.locator('#filenameRule').innerText()).includes(`W${expectedWeek}`),`Ch${chapter} gateway evidence filename uses W${expectedWeek}`);
  await page.fill('#sid','TEST-001');
  assert(await page.locator('#openBtn').isDisabled(),`Ch${chapter} gateway remains disabled until acknowledgment`);
  await page.check('#ack');
  assert(!(await page.locator('#openBtn').isDisabled()),`Ch${chapter} gateway enables only after Student ID + acknowledgment`);
  await page.click('#openBtn');
  await page.waitForURL(new RegExp(`Ch${chapter}-FBR-Student-Assignment\\.html`),{timeout:15000});
  await page.waitForSelector('#fit');
}

async function studentSmoke(chapter,label,reveal){
  const context=await browser.newContext({viewport:{width:390,height:844}});
  let page=await context.newPage();
  const requested=[]; const errors=[];
  page.on('request',r=>requested.push(r.url()));
  page.on('pageerror',e=>errors.push(String(e)));
  await enterAssignment(page,chapter);
  assert((await page.inputValue('#sid'))==='TEST-001',`${label} gateway passes Student ID into assignment`);
  const storageKey=await page.evaluate(()=>KEY);
  const keyBase=await page.evaluate(()=>C.keyBase);
  assert(storageKey.startsWith(keyBase+':')&&storageKey!==keyBase,`${label} local storage is isolated by Chapter + Student ID token`);
  assert(!(await page.locator('body').innerText()).includes(reveal.text),`${label} S3 STRESS absent before lock`);
  assert(!requested.some(u=>u.includes('/reveal/')),`${label} S3 no reveal network request before lock`);

  await page.fill('#student','Release Test Student');
  await page.fill('#section','CI');
  await page.fill('#fit','This engineering mechanism is fit because the decision and stated operating context require this specific evidence-based choice.');
  await page.fill('#bound','This decision remains fit only while the stated operating conditions and evidence assumptions remain observable and unchanged.');
  await page.fill('#act','Issue a measurable professional engineering artifact with an explicit owner, trigger, and acceptance condition for this use.');
  await page.fill('#evidence','Use signed logs, representative measurements, an observation window, and an accountable evidence owner to defend the action.');
  await page.click('#save'); await page.waitForTimeout(120);
  const savedFit=await page.inputValue('#fit');
  await page.close();

  page=await context.newPage();
  const reopenedRequests=[]; const reopenedErrors=[];
  page.on('request',r=>reopenedRequests.push(r.url()));
  page.on('pageerror',e=>reopenedErrors.push(String(e)));
  await enterAssignment(page,chapter);
  assert((await page.inputValue('#fit'))===savedFit,`${label} S1 local data survives tab close/re-entry`);
  assert(!reopenedRequests.some(u=>u.includes('/reveal/')),`${label} S3 re-entered unlocked page still does not request STRESS`);

  await page.click('#lock');
  await page.waitForSelector('.card.stress');
  assert(await page.locator('#fit').getAttribute('readonly')!==null,`${label} S2 FIT is read-only after lock`);
  assert(await page.locator('#bound').getAttribute('readonly')!==null,`${label} S2 BOUND is read-only after lock`);
  assert(await page.locator('#act').getAttribute('readonly')!==null,`${label} S2 ACT is read-only after lock`);
  assert(await page.locator('#evidence').getAttribute('readonly')!==null,`${label} S2 EVIDENCE is read-only after lock`);
  assert((await page.locator('#lockBanner').innerText()).includes('PART A COMMITTED'),`${label} S2 visible committed state`);
  assert((await page.locator('.card.stress').innerText()).includes(reveal.text),`${label} S3 STRESS appears after lock`);
  assert(reopenedRequests.some(u=>u.includes('/reveal/')),`${label} S3 reveal asset requested only after lock`);
  assert(await page.getByRole('button',{name:/reset/i}).count()===0,`${label} S7 no reset path exists after Commit`);

  const stored=await page.evaluate(()=>JSON.parse(localStorage.getItem(KEY)));
  assert(Boolean(stored?.lockedPartA?.fit),`${label} S2 locked Part A snapshot persisted`);
  assert(Boolean(stored?.lockAt),`${label} S5 lock timestamp persisted`);

  assert(await page.locator('#pdf').isDisabled(),`${label} S4 PDF export disabled before REFIT is complete`);
  await page.check('input[name=boundaryState][value="CROSSED"]');
  await page.check('input[name=refit][value="REVISE"]');
  await page.fill('#refitwhy','The changed condition crosses the applicability boundary, so the original action must be revised rather than merely restated.');
  await page.fill('#revised','Revise the professional artifact so that its metric, evidence, trigger, and accountable owner match the changed condition.');
  await page.waitForTimeout(100);
  assert(!(await page.locator('#pdf').isDisabled()),`${label} S4 PDF export enabled only after complete REFIT`);
  assert(!(await page.locator('#download').isDisabled()),`${label} editable evidence export enabled only after complete REFIT`);

  const markdown=await page.evaluate(()=>md());
  for(const section of ['## FIT','## BOUND','## ACT','## EVIDENCE','## STRESS','## Boundary status','## REFIT']) assert(markdown.includes(section),`${label} S4 export contains ${section.replace('## ','')}`);
  assert(markdown.includes('TEST-001'),`${label} S6 export contains Student ID`);
  await page.evaluate(()=>printSheet());
  const printText=await page.locator('#print').innerText();
  assert(printText.includes('TEST-001')&&printText.includes('FIT')&&printText.includes('REFIT'),`${label} S8 print/PDF surface is complete`);
  assert([...errors,...reopenedErrors].length===0,`${label} no page JavaScript errors in Chromium`);
  await context.close();
}

async function hubSmoke(){
  const context=await browser.newContext({viewport:{width:390,height:844}}); const page=await context.newPage();
  await page.goto(BASE+'/iscarb.html',{waitUntil:'domcontentloaded'});
  assert(await page.locator('a.faculty').count()===2,'Hub H1 has two In-Class lane links');
  assert(await page.locator('a.student').count()===2,'Hub H1 has two After-Class FBR links');
  assert(await page.locator('.ready').count()===2,'Hub H2 only Ch10/Ch11 marked READY');
  assert(await page.getByText('Coming soon · not active').count()>=1,'Hub H3 inactive chapters are not links');
  const facultyHrefs=await page.locator('a.faculty').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')));
  assert(facultyHrefs.some(x=>x?.includes('InClass-Presenter.html?chapter=10')),'Hub In-Class Ch10 routes directly to final presenter');
  assert(facultyHrefs.some(x=>x?.includes('InClass-Presenter.html?chapter=11')),'Hub In-Class Ch11 routes directly to final presenter');
  const studentHrefs=await page.locator('a.student').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')));
  assert(studentHrefs.some(x=>x?.includes('fbr-submission.html?chapter=10')),'Hub After-Class Ch10 routes to official gateway');
  assert(studentHrefs.some(x=>x?.includes('fbr-submission.html?chapter=11')),'Hub After-Class Ch11 routes to official gateway');
  await context.close();
}

try{
  await facultySmoke('/lectures/iscarb/InClass-Presenter.html?chapter=10&v=release1','Ch10 Faculty','10');
  await facultySmoke('/lectures/iscarb/InClass-Presenter.html?chapter=11&v=release1','Ch11 Faculty','11');
  await facultyDesktopSmoke('/lectures/iscarb/InClass-Presenter.html?chapter=10&v=release1','Ch10 classroom');
  await facultyDesktopSmoke('/lectures/iscarb/InClass-Presenter.html?chapter=11&v=release1','Ch11 classroom');
  await studentSmoke('10','Ch10 Student',reveals.Ch10);
  await studentSmoke('11','Ch11 Student',reveals.Ch11);
  await hubSmoke();
} finally { await browser.close(); }
if(failures.length){console.error(`\nFBR BROWSER SMOKE: FAIL (${failures.length})`);failures.forEach(x=>console.error(' - '+x));process.exit(1)}
console.log('\nFBR BROWSER SMOKE: PASS');