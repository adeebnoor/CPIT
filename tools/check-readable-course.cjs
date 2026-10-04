/* End-to-end regression on an isolated origin and synthetic local drafts only. */
const {chromium}=require('playwright');
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const base=process.env.COURSE_BASE_URL||'http://127.0.0.1:8765/';
const pub=JSON.parse(fs.readFileSync('curriculum/publication.json','utf8'));
const out='test-results/readable';fs.mkdirSync(out,{recursive:true});
const results={base,slides:0,sections:0,assignments:[],errors:[],overflow:[],checks:[]};
async function run(){
 const browser=await chromium.launch();
 for(const viewport of [{width:1440,height:900},{width:1366,height:768},{width:1024,height:768},{width:390,height:844},{width:320,height:740}]){
  const context=await browser.newContext({viewport,acceptDownloads:true});const page=await context.newPage();
  await context.route('**/*.supabase.co/**',r=>r.abort());
  page.on('pageerror',e=>results.errors.push({kind:'javascript',error:e.message}));
  await page.goto(base+'iscarb.html');
  assert.equal(await page.locator('.lesson').count(),9);
  await page.locator('#chapterSearch').fill('reliability');assert.equal(await page.locator('.lesson:visible').count(),1);
  await page.locator('#chapterSearch').fill('no-match-qa');assert.equal(await page.locator('.lesson:visible').count(),0);assert.match(await page.locator('#chapterSearchStatus').innerText(),/No matching/);
  await page.locator('#chapterSearch').fill('');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));
  if(viewport.width===390){await page.locator('#navToggle').click();assert(await page.locator('#courseNav').isVisible());await page.locator('#navToggle').click();}
  if(viewport.width===1440||viewport.width===390)await page.screenshot({path:out+'/hub-'+viewport.width+'.png',fullPage:viewport.width===390});
  await page.goto(base+'nelc-alignment.html');
  assert.equal(await page.locator('html').getAttribute('lang'),'en');
  assert.equal(await page.locator('.national-chapter').count(),9);
  assert(!/[\u0600-\u06ff]/.test(await page.locator('body').innerText()),'Arabic remains in the English alignment page');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'alignment page horizontal overflow');
  if(viewport.width===1440||viewport.width===390)await page.screenshot({path:out+'/national-page-'+viewport.width+'.png',fullPage:viewport.width===390});
  for(const chapter of pub.lectures){
   try{
    await page.goto(base+chapter.path+'#TITLE');await page.waitForFunction(()=>!!window.iscarb);
    const data=await page.evaluate(()=>iscarb.data);assert.equal(data.slides.length,20);assert.equal(data.rules.length,20);assert.equal(data.objectives.length,5);
    for(let i=0;i<20;i++){
     await page.evaluate(i=>iscarb.go(i),i);await page.locator('#chapter-main img').evaluateAll(imgs=>Promise.all(imgs.map(im=>im.decode().catch(()=>{}))));
     const count=await page.locator('[data-slide-section]').count();
     for(let j=0;j<Math.max(count,1);j++){
      if(count&&viewport.width>1000)await page.locator('[data-slide-section]').nth(j).click();
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'horizontal overflow');
      assert(await page.locator('#chapter-main img').evaluateAll(a=>a.every(im=>im.complete&&im.naturalWidth>0)),'broken image');
      if(data.slides[i].figure&&!data.slides[i].figure.endsWith('.svg'))assert.equal(await page.locator('.source-vector-panel').count(),1,'original-source vector missing');
      if(viewport.width>1000){
       const problem=await page.evaluate(()=>{const root=document.querySelector('.lecture-section:not([hidden])')||document.querySelector('#chapter-main');const edge=document.querySelector('.footerbar').getBoundingClientRect().top;return root?[...root.querySelectorAll('p,li,td,th,img')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.bottom>edge-2}).map(e=>e.textContent.slice(0,60)):[];});
       const cardOverflow=await page.locator('.map-step').evaluateAll(cards=>cards.filter(c=>c.scrollHeight>c.clientHeight+3).map(c=>c.innerText.slice(0,60)));problem.push(...cardOverflow.map(x=>'Map card overflow: '+x));
       if(problem.length){results.overflow.push({chapter:chapter.chapter,slide:data.slides[i].id,section:j,viewport,problem});if(results.overflow.length<15)await page.screenshot({path:out+`/overflow-${chapter.chapter}-${i}-${j}-${viewport.width}.png`});}
      }
      results.sections++;
     }
     results.slides++;
    }
    // Both national references are full slides and must restore the same classroom position.
    const classroomCounter=await page.locator('.counter').innerText();
    for(const mode of ['READINESS','NELC']){
     await page.evaluate(k=>iscarb.open(k),mode);
     assert.equal(await page.locator('.national-canvas').count(),1);
     assert(!/[\u0600-\u06ff]/.test(await page.locator('#chapter-main').innerText()),'Arabic remains in the English reference slide');
     assert.equal(await page.locator('.national-canvas').getAttribute('dir'),'ltr');
     assert.equal(await page.locator('.national-logo img').count(),1);
     await page.locator('.national-logo img').evaluate(im=>im.decode());
     assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'national horizontal overflow');
     if(viewport.width>1000){
      const bad=await page.evaluate(()=>{const edge=document.querySelector('.footerbar').getBoundingClientRect().top;return [...document.querySelectorAll('.national-slide p,.national-slide h2,.national-slide h3,.national-slide img,.national-actions button')].filter(e=>e.getBoundingClientRect().bottom>edge+2).map(e=>e.textContent.slice(0,60));});
      assert.equal(bad.length,0,'national slide overflow: '+JSON.stringify(bad));
     }
     if(viewport.width===1440||viewport.width===390)await page.screenshot({path:out+`/ch${chapter.chapter}-${mode}-${viewport.width}.png`,fullPage:viewport.width===390});
     await page.locator('[data-national-return]').click();assert.equal(await page.locator('.counter').innerText(),classroomCounter);
    }
    results.checks.push({chapter:chapter.chapter,viewport:viewport.width,national_slides:2,return_restored:true});
    if(viewport.width===1024){for(const slide of ['MAP','END']){await page.evaluate(s=>iscarb.jump(s),slide);await page.screenshot({path:out+`/ch${chapter.chapter}-${slide}-1024.png`});}if(chapter.chapter===10){await page.evaluate(()=>iscarb.jump('X06A'));await page.screenshot({path:out+'/ch10-approaches-1024.png'});}}
    if(viewport.width===1440){
     await page.evaluate(()=>iscarb.jump('MAP'));await page.locator('[data-open="CASEMAP"]').click();assert.equal(await page.locator('.case-map-details section').count(),5);await page.locator('#modal-close').click();await page.screenshot({path:out+`/ch${chapter.chapter}-map.png`});
     await page.evaluate(()=>iscarb.go(4));await page.screenshot({path:out+`/ch${chapter.chapter}-concept.png`});
     // Next/previous walks sections; reading view exposes all authored sections.
     const before=await page.locator('.counter').innerText();await page.locator('#nextBtn').click();assert.notEqual(await page.locator('.counter').innerText(),before);
     await page.locator('#viewBtn').click();assert.equal(await page.locator('.lecture-section[hidden]').count(),0);await page.locator('#viewBtn').click();
     await page.evaluate(()=>iscarb.open('RULES'));assert.equal(await page.locator('[data-rule]').count(),20);await page.locator('#modal-close').click();
     for(const st of data.stations){await page.evaluate(no=>iscarb.startStation(no),st.no);await page.locator('#hintBtn').click();assert.match(await page.locator('#coach').innerText(),/Authored hint/);await page.locator('[data-field]').first().fill('QA-only reasoning and a proposed evidence check.');await page.locator('#timer-start').click();await page.waitForTimeout(1100);assert.notEqual(await page.locator('#timer-output').innerText(),'03:00');await page.locator('#timer-start').click();await page.locator('#station-back').click();}
     await page.evaluate(()=>iscarb.open('CARD'));await page.locator('[data-field="claim"]').fill('QA-only persistent claim.');await page.reload();await page.evaluate(()=>iscarb.open('CARD'));assert.equal(await page.locator('[data-field="claim"]').inputValue(),'QA-only persistent claim.');
     const dl=page.waitForEvent('download');await page.locator('[data-export="json"]').click();const download=await dl;await download.saveAs(out+`/qa-card-${chapter.chapter}.json`);
     await page.locator('#modal-close').click();
     await page.evaluate(()=>iscarb.open('QUIZ'));for(let q=0;q<5;q++){await page.locator(`[data-quiz="${q}"]`).first().click();await page.locator(`input[name="quiz"][value="${data.quiz[q].answer}"]`).check();await page.locator('#quiz-check').click();assert.match(await page.locator('#quiz-feedback').innerText(),/Correct for/);}await page.locator('#modal-close').click();
    }
    console.log('PASS lecture',chapter.chapter,viewport.width);
   }catch(e){console.error('FAIL lecture',chapter.chapter,viewport.width,e.message);results.errors.push({chapter:chapter.chapter,viewport,error:e.message});await page.screenshot({path:out+`/FAIL-${chapter.chapter}-${viewport.width}.png`,fullPage:true});}
  }
  await context.close();
 }
 for(const a of pub.assignments){
  const context=await browser.newContext({viewport:{width:320,height:740},acceptDownloads:true});const page=await context.newPage();const reveals=[];page.on('pageerror',e=>results.errors.push({assignment:a.chapter,kind:'javascript',error:e.message}));page.on('request',r=>{if(r.url().includes('/reveal/'))reveals.push(r.url())});page.on('dialog',d=>d.accept());
  try{
   const lms=a.stress_delivery==='lms';if(lms){assert.equal((await page.request.get(base+a.stress_path)).status(),404,'LMS-delivered STRESS must not be public');}else{const real=await (await page.request.get(base+a.stress_path)).json();assert(!real.sealed&&typeof real.text==='string'&&real.text.length>30,'published STRESS must require no code');}
   const evidence={chapter:String(a.chapter),version:a.version,text:'QA evidence for chapter '+a.chapter+': this opens automatically after commitment.',principle:'Reassess the committed claim.'};
   await page.route('**/reveal/*.json',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify(evidence)}));
   await page.goto(base+'fbr-submission.html?chapter='+a.chapter);await page.locator('#sid').fill('QA-DESIGN-ONLY');await page.locator('#ack').check();await page.locator('#openBtn').click();await page.waitForURL('**/Ch'+a.chapter+'-FBR-Student-Assignment.html');assert.equal(reveals.length,0);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'assignment horizontal overflow');
   for(const k of ['fit','measure','bound','act','evidence','technical'])if(await page.locator('#'+k).count())await page.locator('#'+k).fill('QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.');
   if(a.practical){
    // The Python build runs in Pyodide; a fixed result stands in for it here (real runs are tested separately).
    await page.locator('#labPrediction').fill('QA: the build enforces the rule; tests cover a normal, an edge and a refused case.');
    await page.evaluate(()=>StudyBuild.setRunner(()=>({error:null,tests:[['test_a',true,''],['test_b',true,''],['test_c',true,'']],checks:[['course check',true,'']]})));
    await page.locator('#labCases').fill('def test_a():\n    assert True\n');
    await page.locator('#buildRun').click();await page.waitForFunction(()=>/^BUILD RECORD/.test(document.getElementById('labEvidence').value));
   }
   await page.locator('#sourceUse').fill('Slide '+a.reading_pages[0]+': the source concept constrains the model assumptions and defines a bounded control that must be independently checked.');
   await page.locator('#section').fill('QA');await page.locator('#save').click();await page.reload();assert.match(await page.locator('#fit').inputValue(),/QA:/);
   await page.locator('#lock').click();if(lms){await page.locator('#lmsStress').waitFor();await page.evaluate(()=>{LMS_STRESS.sha='';});await page.locator('#lmsText').fill(evidence.text);await page.locator('#lmsCheck').click();await page.locator('#lmsCheck').click();}await page.locator('#refitwhy').waitFor();assert.equal(await page.locator('#stressCode').count(),0);assert.equal(reveals.length,lms?0:1);assert(await page.locator('#fit').evaluate(e=>e.readOnly));
   await page.locator('input[name="boundaryState"]').first().check();await page.locator('input[name="refit"]').first().check();
   await page.locator('#refitwhy').fill('QA: the changed evidence breaks the shared-dependency assumption, so revise the boundary and require an independent check.');
   await page.locator('#revised').fill('QA: keep the model advisory-only; a human owner checks independently. Verify version and workload, record missing tests and reopen the decision when assumptions change.');
   await page.locator('#aiUse').fill('No AI used.');await page.locator('#signer').fill('QA test');await page.locator('#attested').check();
   await page.reload();assert(await page.locator('#fit').evaluate(e=>e.readOnly));assert.equal(reveals.length,lms?0:1);
   await page.locator('#download').waitFor();assert(await page.locator('#download').isEnabled(),await page.locator('#done').innerText());
   const dl=page.waitForEvent('download');await page.locator('#download').click();const d=await dl;const file=out+`/qa-assignment-${a.chapter}.md`;await d.saveAs(file);const record=fs.readFileSync(file,'utf8');assert.match(record,new RegExp('Chapter '+a.chapter));assert.match(record,/Commit ID:/);assert.match(record,/Attested: Yes — reviewed and responsibility accepted/);
   await page.screenshot({path:out+`/assignment-${a.chapter}-mobile.png`});results.assignments.push({chapter:a.chapter,entry:true,save_reload:true,delayed_reveal:true,locked_reload:true,editable_export:true});console.log('PASS assignment',a.chapter);
  }catch(e){console.error('FAIL assignment',a.chapter,e.message);results.errors.push({assignment:a.chapter,error:e.message});await page.screenshot({path:out+`/FAIL-assignment-${a.chapter}.png`,fullPage:true});}finally{await context.close();}
 }
 await browser.close();fs.writeFileSync(out+'/results.json',JSON.stringify(results,null,2));console.log(JSON.stringify({slides:results.slides,sections:results.sections,assignments:results.assignments.length,errors:results.errors,overflow:results.overflow},null,2));if(results.errors.length||results.overflow.length)process.exitCode=1;
}
run().catch(e=>{console.error(e);fs.writeFileSync(out+'/fatal.txt',String(e.stack));process.exitCode=1});
