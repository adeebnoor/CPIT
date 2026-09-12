import fs from 'node:fs';
import { chromium } from 'playwright';

const BASE = process.env.FBR_BASE_URL || 'http://127.0.0.1:8080';
const CHAPTERS = ['10','11','12','13','14','15','16','17','20'];
const revealFiles = {
 '10':'r10-7c4d9e2f.json','11':'r11-5a8e3c1b.json','12':'r12-9f3a7c2d.json','13':'r13-b61e4a90.json',
 '14':'r14-2d7c5e81.json','15':'r15-7ab41d63.json','16':'r16-4ce98b17.json','17':'r17-d85f2a46.json','20':'r20-f31c8d72.json'
};
const failures=[];
const pass=m=>console.log('PASS  '+m);
const fail=m=>{failures.push(m);console.error('FAIL  '+m)};
const assert=(c,m)=>c?pass(m):fail(m);
const reveals=Object.fromEntries(CHAPTERS.map(ch=>[ch,JSON.parse(fs.readFileSync(`lectures/iscarb/reveal/${revealFiles[ch]}`,'utf8'))]));
const browser=await chromium.launch({headless:true});

async function facultySmoke(ch){
  const context=await browser.newContext({viewport:{width:1536,height:864}}); const page=await context.newPage(); const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(`${BASE}/lectures/iscarb/InClass-Presenter.html?chapter=${ch}&v=smoke`,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('#lecture');
  const frame=page.frameLocator('#lecture');
  await frame.locator('body').waitFor({timeout:30000});
  await page.waitForTimeout(500);
  assert(!((await page.locator('#status').innerText()).toLowerCase().includes('loading')),`Ch${ch} In-Class has no visible Loading state`);
  for(const id of ['#prev','#notes','#next','#present']) assert(await page.locator(id).isVisible(),`Ch${ch} ${id.slice(1)} control visible`);
  const href=await page.locator('#studentTask').getAttribute('href');
  assert(href===`../../fbr-submission.html?chapter=${ch}`,`Ch${ch} presenter routes to official After-Class gateway`);
  const before=await frame.locator('body').evaluate(()=>typeof window.cur==='number'?window.cur:null).catch(()=>null);
  await page.click('#next'); await page.waitForTimeout(120);
  const after=await frame.locator('body').evaluate(()=>typeof window.cur==='number'?window.cur:null).catch(()=>null);
  if(before!==null&&after!==null) assert(after!==before,`Ch${ch} Next navigation works`);
  assert(errors.length===0,`Ch${ch} In-Class has no JavaScript errors`);
  await context.close();
}

async function enterAssignment(page,ch,sid='TEST-001'){
  await page.goto(`${BASE}/fbr-submission.html?chapter=${ch}`,{waitUntil:'domcontentloaded'});
  assert(await page.locator('#openBtn').isDisabled(),`Ch${ch} gateway disabled before ID + acknowledgment`);
  assert((await page.locator('#pdfFilenameRule').innerText()).includes(`W${ch}`),`Ch${ch} PDF filename uses W${ch}`);
  assert((await page.locator('#filenameRule').innerText()).includes(`W${ch}`),`Ch${ch} evidence filename uses W${ch}`);
  await page.fill('#sid',sid); assert(await page.locator('#openBtn').isDisabled(),`Ch${ch} still disabled before acknowledgment`);
  await page.check('#ack'); assert(!(await page.locator('#openBtn').isDisabled()),`Ch${ch} gateway enables after ID + acknowledgment`);
  await page.click('#openBtn');
  await page.waitForURL(new RegExp(`Ch${ch}-FBR-Student-Assignment\\.html`),{timeout:15000});
  await page.waitForSelector('#fit');
}

async function studentSmoke(ch){
  const reveal=reveals[ch], context=await browser.newContext({viewport:{width:390,height:844},acceptDownloads:true});
  let page=await context.newPage(); const req=[]; const errors=[];
  page.on('request',r=>req.push(r.url())); page.on('pageerror',e=>errors.push(String(e)));
  await enterAssignment(page,ch,`TEST-${ch}`);
  assert((await page.inputValue('#sid'))===`TEST-${ch}`,`Ch${ch} Student ID passes into assignment`);
  const storageKey=await page.evaluate(()=>KEY), keyBase=await page.evaluate(()=>C.keyBase);
  assert(storageKey.startsWith(keyBase+':')&&storageKey!==keyBase,`Ch${ch} storage isolated by Chapter + Student ID token`);
  assert(!(await page.locator('body').innerText()).includes(reveal.text),`Ch${ch} STRESS absent before Commit`);
  assert(!req.some(u=>u.includes('/reveal/')),`Ch${ch} no reveal request before Commit`);

  const txt='This professional judgment states an observable condition, an explicit engineering action, and inspectable evidence that another engineer can defend.';
  await page.fill('#student','Smoke Student'); await page.fill('#section','CI');
  for(const id of ['fit','bound','act','evidence']) await page.fill('#'+id,txt);
  await page.click('#save'); await page.waitForTimeout(120); const saved=await page.inputValue('#fit');
  await page.close();

  page=await context.newPage(); const req2=[]; const errors2=[];
  page.on('request',r=>req2.push(r.url())); page.on('pageerror',e=>errors2.push(String(e)));
  await enterAssignment(page,ch,`TEST-${ch}`);
  assert((await page.inputValue('#fit'))===saved,`Ch${ch} draft survives tab close/re-entry`);
  assert(!req2.some(u=>u.includes('/reveal/')),`Ch${ch} re-entered draft still does not request STRESS`);
  await page.click('#lock'); await page.waitForSelector('.card.stress',{timeout:15000});
  for(const id of ['fit','bound','act','evidence']) assert(await page.locator('#'+id).getAttribute('readonly')!==null,`Ch${ch} ${id.toUpperCase()} read-only after Commit`);
  assert((await page.locator('.card.stress').innerText()).includes(reveal.text),`Ch${ch} STRESS appears after Commit`);
  assert(req2.some(u=>u.includes('/reveal/')),`Ch${ch} reveal requested only after Commit`);
  assert(await page.getByRole('button',{name:/reset/i}).count()===0,`Ch${ch} no reset after Commit`);
  assert(await page.locator('#pdf').isDisabled(),`Ch${ch} export disabled before REFIT completion`);
  await page.check('input[name=boundaryState][value="CROSSED"]'); await page.check('input[name=refit][value="REVISE"]');
  await page.fill('#refitwhy',txt); await page.fill('#revised',txt); await page.waitForTimeout(100);
  assert(!(await page.locator('#pdf').isDisabled()),`Ch${ch} PDF enabled after complete REFIT`);
  assert(!(await page.locator('#download').isDisabled()),`Ch${ch} evidence export enabled after complete REFIT`);
  const md=await page.evaluate(()=>md());
  for(const sec of ['## FIT','## BOUND','## ACT','## EVIDENCE','## STRESS','## Boundary status','## REFIT']) assert(md.includes(sec),`Ch${ch} export contains ${sec.slice(3)}`);
  {
    const dp=page.waitForEvent('download'); await page.click('#download'); const d=await dp;
    assert(d.suggestedFilename()===`CPIT455_W${ch}_TEST-${ch}_FBR.md`,`Ch${ch} download filename correct`);
  }
  assert([...errors,...errors2].length===0,`Ch${ch} no JavaScript errors`);
  await context.close();
}

async function hubSmoke(){
  const context=await browser.newContext({viewport:{width:390,height:844}}), page=await context.newPage();
  await page.goto(`${BASE}/iscarb.html`,{waitUntil:'domcontentloaded'});
  assert(await page.locator('a.in').count()===9,'Hub has nine In-Class links');
  assert(await page.locator('a.after').count()===9,'Hub has nine After-Class links');
  for(const ch of CHAPTERS){
    assert(await page.locator(`a.in[href*="chapter=${ch}"]`).count()===1,`Hub Ch${ch} In-Class link present`);
    assert(await page.locator(`a.after[href="fbr-submission.html?chapter=${ch}"]`).count()===1,`Hub Ch${ch} After-Class link present`);
  }
  assert((await page.locator('body').innerText()).includes('professional judgment'),'Hub preserves split-delivery message');
  await context.close();
}

try{
  await facultySmoke('10'); await facultySmoke('11');
  for(const ch of CHAPTERS) await studentSmoke(ch);
  await hubSmoke();
} finally { await browser.close(); }
if(failures.length){console.error(`\nFBR BROWSER SMOKE: FAIL (${failures.length})`); failures.forEach(x=>console.error(' - '+x)); process.exit(1)}
console.log('\nFBR BROWSER SMOKE: PASS');
