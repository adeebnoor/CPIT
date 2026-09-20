/* DOM interaction checks. JSDOM has no layout engine: these checks intentionally
 * do not claim to verify visual fit, CSS fragmentation or real-device rendering. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {JSDOM,VirtualConsole}=require('jsdom');
const root=path.resolve(__dirname,'../..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'curriculum/learning-path/lectures.json')));
function boot(html,pathname){
 const errors=[],files=[],vc=new VirtualConsole();
 vc.on('jsdomError',e=>{if(!/Not implemented: (HTMLCanvasElement|window.scrollTo)/.test(e.message))errors.push(e.message)});
 const dom=new JSDOM(html,{url:'https://adeebnoor.github.io/CPIT/'+pathname,runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){
  w.matchMedia=()=>({matches:false,addListener(){}});w.ResizeObserver=class{observe(){}disconnect(){}};w.scrollTo=()=>{};
  w.Blob=class{constructor(parts,options){this.parts=parts;this.type=options.type}};
  w.URL.createObjectURL=b=>{files.push(b);return 'blob:test'};w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=function(){};
 }});return {dom,w:dom.window,d:dom.window.document,errors,files};
}
for(const c of catalog){
 const html=fs.readFileSync(path.join(root,c.path),'utf8');
 const x=boot(html,c.path),{w,d}=x;const L=w.eval('LECTURE'),api=w.ISCARB_PAGES;
 assert(api);assert.equal(x.errors.length,0,x.errors.join('\n'));
 const baselineHtml=html.replace(/\/\* Paginated visual presentation[\s\S]*?<\/script>/,'</script>');
 const baseline=boot(baselineHtml,c.path);
 // Every original field and source text survives moving the existing DOM nodes.
 const fields=doc=>[...doc.querySelectorAll('#deck [data-f]')].map(f=>f.dataset.f).sort();
 assert.deepEqual(fields(d),fields(baseline.d));
 for(const source of baseline.d.querySelectorAll('.lp-source-section')){
  assert.equal(d.getElementById(source.id).querySelector('.lp-source-text').textContent,source.querySelector('.lp-source-text').textContent);
 }
 const images=doc=>new Set([...doc.querySelectorAll('#deck img')].map(i=>i.getAttribute('src')));
 for(const src of images(baseline.d))assert(images(d).has(src),'Lost source image');
 for(const [key,spec] of Object.entries(L.visualStory.units)){
  const index=w.U.findIndex(u=>u.k===key);assert(index>=0);w.go(index,true);
  assert.equal(api.current().mode,'overview');
  const summary=d.querySelector('.slide.on [data-view=overview]');
  assert(summary.querySelector('img,svg,.v3-diagram'),'Missing meaningful visual '+key);
  assert(summary.textContent.includes(spec.takeaway));assert(spec.takeaway.split(/\s+/).length<=28,'Overlong takeaway '+key);
  d.querySelector('.slide.on .v3-mode').click();assert.equal(api.current().mode,'details');
  assert(!d.querySelector('.slide.on [data-view=explanation]').hidden);
 }
 // Controlled dimensions test navigation semantics, not CSS layout.
 const first=w.U.findIndex(u=>u.k==='X01');w.go(first,true);api.explain();
 const win=d.querySelector('.slide.on .v3-window'),flow=win.querySelector('[data-view=explanation]');
 Object.defineProperty(win,'clientWidth',{value:800,configurable:true});
 Object.defineProperty(flow,'scrollWidth',{value:2480,configurable:true});api.refresh();
 assert.equal(api.current().pages,3);
 d.getElementById('nextBtn').click();assert.equal(w.cur,first);assert.equal(api.current().page,1);
 d.dispatchEvent(new w.KeyboardEvent('keydown',{key:'PageDown',bubbles:true}));assert.equal(api.current().page,2);
 d.getElementById('nextBtn').click();assert.notEqual(w.cur,first);
 d.getElementById('prevBtn').click();assert.equal(w.cur,first);assert.equal(api.current().page,2);
 api.goPage(99);assert.equal(api.current().page,2);api.goPage(-2);assert.equal(api.current().page,0);
 // Opening and rebuilding a dialog must keep its real export controls.
 w.openOv('case');assert(d.querySelector('.lp-top').inert);assert(d.querySelector('#case #cDown'));
 w.closeOv('case');w.openOv('case');assert.equal(d.querySelectorAll('#case #cDown').length,1);w.closeOv('case');
 assert.equal(d.querySelector('.lp-top').inert,false);
 w.go(w.U.findIndex(u=>u.k==='APPLY'),true);
 const field=d.querySelector('[data-f=path_claim]');field.value='Retain the decision only while its tested assumption holds.';field.dispatchEvent(new w.Event('input',{bubbles:true}));
 w.downloadLecture();const downloaded=x.files.find(b=>b.type.startsWith('text/html'));assert(downloaded);
 const reopened=boot(downloaded.parts.join(''),c.path);
 assert.equal(reopened.errors.length,0,reopened.errors.join('\n'));
 assert.equal(reopened.d.querySelectorAll('.lp-top').length,1,'Duplicated navigation in offline export');
 assert.equal(reopened.d.querySelectorAll('#cDown').length,1);
 assert(reopened.w.S.f.path_claim.includes('tested assumption'));
 assert.equal(reopened.d.querySelectorAll('.slide').length,w.U.length);
 reopened.dom.window.close();baseline.dom.window.close();x.dom.window.close();
 console.log('PASS CH'+c.chapter+' · concise visual summaries, retained sources/fields, page navigation, dialogs and offline re-open');
}
console.log('DOM checks only; real browser layout and device checks remain separate.');
