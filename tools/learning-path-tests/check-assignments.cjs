const fs=require('fs'),path=require('path'),assert=require('assert/strict');const {JSDOM,VirtualConsole}=require('jsdom');const root=path.resolve(__dirname,'../..');
const specs=JSON.parse(fs.readFileSync(path.join(root,'curriculum/publication.json'))).assignments.filter(x=>x.points===5);
const flush=()=>new Promise(r=>setTimeout(r,30));
(async()=>{for(const c of specs){let calls=0;const errors=[];const vc=new VirtualConsole();vc.on('jsdomError',e=>{if(!/navigation|print/.test(e.message))errors.push(e.message)});const stress=JSON.parse(fs.readFileSync(path.join(root,c.stress_path)));const dom=new JSDOM(fs.readFileSync(path.join(root,c.path),'utf8'),{url:'https://adeebnoor.github.io/CPIT/'+c.path,runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){w.sessionStorage.setItem(c.access_key,JSON.stringify({sid:'TEST2026',acknowledged:true,edition:c.edition}));w.confirm=()=>true;w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=function(){};w.fetch=async(url)=>{calls++;assert.equal(url,c.stress_path.replace('lectures/iscarb/',''));return{ok:true,json:async()=>stress}};w.URL.createObjectURL=()=> 'blob:test';w.URL.revokeObjectURL=()=>{};}});const w=dom.window,d=w.document;
try{
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(calls,0,'Reveal must not be fetched before commit');assert(!d.body.textContent.includes(stress.text));
 for(const id of ['fit','measure','bound','act','evidence']){const f=d.getElementById(id);f.value='A specific test response identifying the supplied condition and relevant evidence for '+id+'.';f.dispatchEvent(new w.Event('input',{bubbles:true}))}
 d.getElementById('save').click();await flush();d.getElementById('lock').click();await flush();
 assert.equal(calls,1,'Fetch only after commit');assert(d.getElementById('fit').readOnly);assert(d.getElementById('partB').textContent.includes(stress.text));assert(d.querySelector('[name="refit"]'));
 const before=d.getElementById('fit').value;assert(d.getElementById('lock').disabled);d.getElementById('lock').click();assert.equal(calls,1);assert.equal(d.getElementById('fit').value,before);
 for(const name of ['boundaryState','refit']){const r=d.querySelector('input[name="'+name+'"]');r.checked=true;r.dispatchEvent(new w.Event('change',{bubbles:true}))}
 for(const id of ['refitwhy','revised','aiUse','signer']){d.getElementById(id).value=id==='signer'?'QA reviewer':'This is a specific final response explaining the revised condition and the evidence still required.';d.getElementById(id).dispatchEvent(new w.Event('input',{bubbles:true}))}
 const attest=d.getElementById('attested');attest.checked=true;attest.dispatchEvent(new w.Event('change',{bubbles:true}));await flush();
 assert.equal(w.eval('valB()'),'');assert.equal(d.getElementById('download').disabled,false);assert(w.eval('md(true)').includes(stress.text));assert(w.eval('md(true)').includes('Chapter '+c.chapter));
 const stored=Array.from({length:w.localStorage.length},(_,i)=>w.localStorage.key(i)).filter(k=>k.startsWith(c.storage_key));assert(stored.length);assert.equal(errors.length,0,errors.join('\n'));
 console.log('PASS CH'+c.chapter+' · unique draft, no early reveal, commit lock, STRESS, REFIT, disclosure, final export');
}catch(e){console.error('FAIL CH'+c.chapter,e.stack);process.exitCode=1}finally{dom.window.close()}}
})();
