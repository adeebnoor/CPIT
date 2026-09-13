/* Bounded functional checks for the Chapter 10 assignment. No network or browser required. */
const fs=require('fs');
const path=require('path');
const assert=require('node:assert/strict');
const {JSDOM,VirtualConsole}=require('jsdom');
const html=fs.readFileSync(process.argv[2]||path.join(__dirname,'../lectures/iscarb/Ch10-FBR-Student-Assignment.html'),'utf8');
const stress=JSON.parse(fs.readFileSync(process.argv[3]||path.join(__dirname,'../lectures/iscarb/reveal/r10-v5.json'),'utf8'));
const access='fbr:access:ch10:v4';
function token(s){let h=2166136261;for(const c of s.trim()){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return(h>>>0).toString(36);}
const sid='22001234',T=token(sid),key='fbr:cpit455:ch10:reviewed:v5:'+T,oldkey='fbr:cpit455:ch10:prod:v4:'+T;
function page(opts={}){
 const errors=[],fetches=[],downloads=[];
 const virtualConsole=new VirtualConsole();
 virtualConsole.on('jsdomError',e=>{if(!/Not implemented: navigation/.test(e.message))errors.push(e.message);});
 const dom=new JSDOM(html,{url:'https://adeebnoor.github.io/CPIT/lectures/iscarb/Ch10-FBR-Student-Assignment.html',runScripts:'dangerously',pretendToBeVisual:true,virtualConsole,beforeParse(w){
  if(opts.access!==false)w.sessionStorage.setItem(access,JSON.stringify({sid,acknowledged:true,edition:'reviewed-v5'}));
  if(opts.saved)w.localStorage.setItem(key,JSON.stringify(opts.saved));
  if(opts.legacy)w.localStorage.setItem(oldkey,JSON.stringify(opts.legacy));
  w.confirm=()=>opts.confirm!==false;w.print=()=>{};
  w.HTMLElement.prototype.scrollIntoView=()=>{};
  w.URL.createObjectURL=()=> 'blob:test';w.URL.revokeObjectURL=()=>{};
  w.HTMLAnchorElement.prototype.click=function(){downloads.push(this.download);};
  w.fetch=async(url)=>{fetches.push(url);return{ok:opts.revealFail!==true,json:async()=>opts.badStress?{text:'invalid'}:stress};};
 }});
 return{dom,w:dom.window,errors,fetches,downloads};
}
function put(w,id,value){w.document.getElementById(id).value=value;}
function partA(w){put(w,'fit','Availability governs because students need access before the deadline; independent paths require verification (lecture X01).');put(w,'bound','Continue only while confirmation integrity can be checked; reopen on unconfirmed submissions or inaccessible registration.');put(w,'act','Limit new work under the duty engineer and ask the registrar to approve an alternative route if required.');put(w,'evidence','Request peak-load failover tests for the deployed version; results remain unmeasured and an independent reviewer must check them.');}
function partB(w){w.document.querySelector('[name="boundaryState"][value="CROSSED"]').checked=true;w.document.querySelector('[name="refit"][value="REVISE"]').checked=true;put(w,'refitwhy','The sign-in outage crosses my access boundary, so new applicants need an approved alternative while confirmed work remains checkable.');put(w,'revised','Continue confirmed active sessions with integrity monitoring; ask the registrar to approve an alternative for blocked students and review before 12:00.');put(w,'aiUse','No AI used.');put(w,'signer','Student Example');w.document.getElementById('attested').checked=true;w.exportState();}
async function tick(){await new Promise(r=>setTimeout(r,0));}
(async()=>{
 const p=page();assert.deepEqual(p.errors,[]);assert.equal(p.fetches.length,0);assert(p.w.document.getElementById('lock').disabled===false);assert(p.w.valB().includes('Commit Part A'));assert(!p.w.document.getElementById('backup').disabled);assert(!p.w.document.querySelector('a[href$="#unit-10"]'));assert(!html.includes('SCENARIO_PENDING'));assert.equal(p.w.document.documentElement.dataset.iscarbStandalone,'1');
 p.w.backup();assert(p.downloads[0].includes('DRAFT_BACKUP'));assert.equal(p.fetches.length,0);assert(p.w.md().includes('DRAFT / BACKUP'));await p.w.commit();assert.equal(p.fetches.length,0);
 partA(p.w);p.w.confirm=()=>false;await p.w.commit();assert.equal(p.fetches.length,0);assert.equal(p.w.document.getElementById('fit').readOnly,false);
 p.w.confirm=()=>true;await p.w.commit();assert.equal(p.fetches.length,1);assert.equal(p.fetches[0],'reveal/r10-v5.json');assert.equal(p.w.document.getElementById('fit').readOnly,true);assert.equal(p.w.document.getElementById('save').disabled,false);assert(p.w.document.getElementById('pdf').disabled);
 partB(p.w);assert.equal(p.w.valB(),'');assert(!p.w.document.getElementById('pdf').disabled);assert(p.w.save());const saved=JSON.parse(p.w.localStorage.getItem(key));assert(saved.locked&&saved.attested);p.w.download();assert(p.downloads.some(x=>x.endsWith('_FBR.md')));assert(p.w.md(true).includes('Campus course-registration portal'));assert(p.w.md(true).includes('AI-use declaration'));p.w.printSheet(true);assert(p.w.document.getElementById('print').textContent.includes('Human review'));
 put(p.w,'revised','Changed final plan after review; this must reset the human sign-off to protect the submitted reasoning.');p.w.document.getElementById('revised').dispatchEvent(new p.w.Event('input',{bubbles:true}));assert(!p.w.document.getElementById('attested').checked);assert(p.w.document.getElementById('pdf').disabled);assert.equal(p.w.eval('S.exportedAt'),'');assert(p.w.document.getElementById('erase').disabled);p.dom.window.close();
 const reload=page({saved});await tick();assert.equal(reload.fetches.length,0);assert.equal(reload.w.document.getElementById('fit').value,saved.lockedPartA.fit);assert.equal(reload.w.document.getElementById('revised').value,saved.revised);assert.equal(reload.w.valB(),'');assert.deepEqual(reload.errors,[]);reload.dom.window.close();
 const fail=page({revealFail:true});partA(fail.w);await fail.w.commit();assert(fail.w.document.getElementById('retry'));assert.equal(fail.w.document.getElementById('fit').readOnly,true);assert(fail.w.valB());fail.w.backup();assert(fail.downloads.length===1);fail.dom.window.close();
 const invalid=page({badStress:true});partA(invalid.w);await invalid.w.commit();assert(invalid.w.document.getElementById('retry'));assert(invalid.w.valB());invalid.dom.window.close();
 const noStore=page();partA(noStore.w);assert(noStore.w.save());const initial=JSON.parse(noStore.w.localStorage.getItem(key)).lastSavedAt;const originalSet=noStore.w.Storage.prototype.setItem;noStore.w.Storage.prototype.setItem=function(k,v){if(k===key)throw new Error('Quota exceeded');return originalSet.call(this,k,v);};put(noStore.w,'fit','This changed answer cannot be saved, but it must still be recoverable in a downloadable backup.');assert.equal(noStore.w.save(),false);assert.equal(noStore.w.eval('S.lastSavedAt'),initial);assert(noStore.w.document.getElementById('saved').textContent.startsWith('Unsaved changes'));assert(noStore.w.document.getElementById('lock').disabled);noStore.w.backup();assert(noStore.downloads.length===1);assert(noStore.w.md().includes('cannot be saved'));noStore.dom.window.close();
 const commitFail=page();partA(commitFail.w);const set2=commitFail.w.Storage.prototype.setItem;commitFail.w.Storage.prototype.setItem=function(k,v){if(k===key)throw new Error('Quota exceeded');return set2.call(this,k,v);};await commitFail.w.commit();assert.equal(commitFail.fetches.length,0);assert.equal(commitFail.w.document.getElementById('fit').readOnly,false);assert.equal(commitFail.w.eval('S.locked'),false);commitFail.dom.window.close();
 const prior={sid,student:'Prior student',locked:true,lockedPartA:{fit:'Prior plant FIT',bound:'Prior plant boundary',act:'Prior plant action',evidence:'Prior plant evidence'},stress:{text:'Shared pressure transmitter in the desalination plant'},commitId:'prior-1',lockAt:'2026-09-10T12:00:00Z'};const legacy=page({legacy:prior});assert(!legacy.w.document.getElementById('legacyNotice').hidden);assert.equal(legacy.w.document.getElementById('fit').value,'');assert.equal(legacy.w.localStorage.getItem(key),null);legacy.w.document.getElementById('legacyDownload').click();assert(legacy.downloads[0].includes('PREVIOUS_v4'));assert.equal(legacy.w.localStorage.getItem(oldkey),JSON.stringify(prior));assert.equal(legacy.fetches.length,0);legacy.dom.window.close();
 const denied=page({access:false});assert.equal(denied.fetches.length,0);assert.equal(denied.w.document.getElementById('sid').value,'');denied.dom.window.close();
 console.log('PASS: entry gate; rubric/scaffold; incomplete backup; validation; cancel/commit/reveal; saved reload; final export and human review; reveal failure/invalid data; failed saves and failed commit; legacy edition isolation.');
})().catch(e=>{console.error(e);process.exitCode=1;});
