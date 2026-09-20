const fs=require('fs'),path=require('path'),assert=require('assert/strict');const {JSDOM,VirtualConsole}=require('jsdom');const root=path.resolve(__dirname,'../..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'curriculum/learning-path/lectures.json')));
let failed=false;
for(const c of catalog){
 const errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>{if(!/Not implemented: (HTMLCanvasElement|window.scrollTo)/.test(e.message))errors.push(e.message)});
 let w;try{
  const dom=new JSDOM(fs.readFileSync(path.join(root,c.path),'utf8'),{url:'https://adeebnoor.github.io/CPIT/'+c.path,runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){w.matchMedia=()=>({matches:false,addListener(){}});w.ResizeObserver=class{observe(){}disconnect(){}};w.scrollTo=()=>{};}});w=dom.window;const d=w.document;
  assert.equal(errors.length,0,errors.join('\n'));assert.equal(w.U.length,d.querySelectorAll('.slide').length);assert(w.U.length>40);
  const main=w.U.filter(u=>u.route==='core');assert.equal(main.length,c.classroom_units);assert(main.length<=20);
  const sources=[...d.querySelectorAll('[id^="source-slide-"]')];assert.equal(sources.length,c.source_slide_count);assert.equal(new Set(sources.map(x=>x.id)).size,sources.length);
  d.querySelector('[data-jump="START"]').click();assert.equal(w.U[w.cur].k,'START');
  for(let i=2;i<main.length;i++){d.getElementById('nextBtn').click();assert.equal(w.U[w.cur].k,main[i].k)}
  assert.equal(w.U[w.cur].k,'END');assert.equal(d.getElementById('nextBtn').disabled,true);assert(d.querySelector('.slide.on').textContent.includes('Before the assignment'));
  d.querySelector('.slide.on [data-jump="C01"]').click();assert.equal(w.U[w.cur].k,'C01');d.getElementById('nextBtn').click();assert.equal(w.U[w.cur].route,'study');
  const ck=w.U.findIndex(u=>u.k==='CHECK1');w.go(ck,true);let b=d.querySelector('.slide.on [data-answer-toggle]');assert(b);let box=d.querySelector('.slide.on [data-answer-box]');assert(box.hidden);b.click();assert(!box.hidden);b.click();assert(box.hidden);
  d.querySelector('[data-route-tab="toolkit"]').click();assert.equal(w.U[w.cur].k,'R07');
  d.querySelector('[data-route-tab="core"]').click();assert.equal(w.U[w.cur].k,'START');
  w.go(w.U.findIndex(u=>u.k==='APPLY'),true);let f=d.querySelector('[data-f="path_claim"]');f.value='Restrict the release until the stated operating condition has been verified.';f.dispatchEvent(new w.Event('input',{bubbles:true}));assert(w.S.f.path_claim.includes('Restrict'));assert(w.caseText().includes('Restrict'));
  w.fillOver();assert(d.getElementById('oG').textContent.includes('Required source review'));
  const unresolved=d.getElementById('deck').innerHTML.match(/\{\{[^}]+\}\}/g)||[];assert.equal(unresolved.length,0,unresolved.join(' '));
  const bad=[...d.querySelectorAll('img')].filter(i=>!i.getAttribute('src')||/undefined/.test(i.getAttribute('src')));assert.equal(bad.length,0);
  console.log('PASS CH'+c.chapter+' · navigation, source ledger, hidden answers, saved practice, export, topic links');
  dom.window.close();
 }catch(e){failed=true;console.log('FAIL CH'+c.chapter,e.stack);if(w)w.close();}
}
process.exitCode=failed?1:0;
