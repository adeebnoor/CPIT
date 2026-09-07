'use strict';
(function(){
  const job=document.body.dataset.job;
  if(!job) return;
  const sid=localStorage.getItem('iscarb.student.'+job)||'';
  if(!sid) return;
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const requested=new Set();
  const dataByUnit={};
  const pending={};
  let saveTimer=null;

  async function req(url,opt={}){
    const r=await fetch(url,{cache:'no-store',...opt,headers:{'Content-Type':'application/json',...(opt.headers||{})}});
    const t=await r.text(); let d; try{d=JSON.parse(t)}catch{d={detail:t}}
    if(!r.ok) throw Error(typeof d.detail==='string'?d.detail:'Request failed');
    return d;
  }

  function currentUnit(){
    const k=document.querySelector('#unit .unitKicker');
    if(!k) return null;
    const m=(k.textContent||'').match(/UNIT\s+(\d{1,2})\s*\/\s*20/i);
    return m?Number(m[1]):null;
  }

  async function ensureUnit(){
    const n=currentUnit(); if(!n) return;
    const unit=document.getElementById('unit');
    if(!unit || unit.querySelector('.p1VisualEvidence') || unit.querySelector('.externalVisualEvidence')) return;
    if(requested.has(n)) return;
    requested.add(n);
    try{
      const d=await req(`/api/learning/${job}/public-visual/${n}?student_id=${encodeURIComponent(sid)}`);
      dataByUnit[n]=d;
      if(d.status==='selected') renderExternal(unit,n,d);
      else if(d.status==='fallback') renderFallback(unit,n,d);
    }catch(e){ /* Search failure must never block the lecture. */ }
  }

  function renderExternal(unit,n,d){
    if(unit.querySelector('.p1VisualEvidence')||unit.querySelector('.externalVisualEvidence')) return;
    const source=unit.querySelector('.sourceFocus'), supports=unit.querySelector('.supportChannels'), drawer=unit.querySelector('.taskDrawer');
    if(!source||!drawer) return;
    const c=d.candidate||{}, brief=d.brief||{};
    const grid=document.createElement('div');grid.className='hybridVisualGrid externalHybridGrid';
    const analysis=document.createElement('div');analysis.className='hybridAnalysisPane';
    const visual=document.createElement('div');visual.className='hybridSourcePane';
    source.parentNode.insertBefore(grid,source);analysis.appendChild(source);if(supports)analysis.appendChild(supports);analysis.appendChild(drawer);
    visual.innerHTML=`<section class="externalVisualEvidence" data-public-unit="${n}">
      <div class="visualMeta externalMeta"><span>${esc((brief.image_type||'contextual').toUpperCase())}</span><b>EXTERNAL LICENSED VISUAL</b></div>
      <div class="visualCanvas publicCanvas" data-public-canvas="${n}" tabindex="0" role="img" aria-label="${esc(c.title||'Licensed contextual visual')}">
        <img src="${esc(d.image_url)}" alt="${esc(c.title||brief.cognitive_job||'Licensed contextual visual')}" loading="lazy">
        <span class="publicCircle" data-public-circle="${n}" hidden></span>
        <span class="sourceWatermark externalWatermark">${esc(c.provider||'External')}</span>
      </div>
      <div class="visualActions"><button type="button" class="btn publicZoom">Zoom to read</button><span>${esc(c.title||brief.queries?.[0]||'Contextual visual')}</span></div>
      <footer class="publicSourceFooter"><b>${esc(d.source_footer||'External licensed visual')}</b>${d.landing_url?` · <a href="${esc(d.landing_url)}" target="_blank" rel="noopener noreferrer">source</a>`:''}${d.license_url?` · <a href="${esc(d.license_url)}" target="_blank" rel="noopener noreferrer">license</a>`:''}<br><span>Contextual enrichment — not P1 evidence · rank ${esc(c.score??'—')} · ${d.clip_used?'CLIP reranked':'semantic fallback'}</span></footer>
    </section>`;
    grid.appendChild(analysis);grid.appendChild(visual);

    const body=drawer.querySelector('.taskDrawerBody');
    if(body){
      const gate=document.createElement('section');gate.className='visualAnnotationGate publicAnnotationGate';
      gate.innerHTML=`<div class="unitKicker">EXTERNAL VISUAL → DECISION EVIDENCE</div><h3>Use the image; do not merely view it.</h3><p>${esc(d.interaction_prompt||brief.cognitive_job||'Mark the region that changes your judgment and explain why.')}</p><div class="publicAnnotControls"><label>Circle size <input type="range" min="3" max="24" value="8" data-public-radius="${n}"></label><span>Click the image to place the circle.</span></div><div class="field"><label>Why does this selected region change your engineering decision?</label><textarea rows="3" data-public-note="${n}" placeholder="Connect the visual observation to a source-backed claim…"></textarea></div><div class="visualGateStatus" data-public-status="${n}">Place a circle and add an engineering note. Autosave: 5s.</div>`;
      body.insertBefore(gate,body.firstChild);
    }
    bindExternal(n,d,visual);
  }

  function bindExternal(n,d,visual){
    const canvas=visual.querySelector(`[data-public-canvas="${n}"]`), circle=visual.querySelector(`[data-public-circle="${n}"]`);
    const note=document.querySelector(`[data-public-note="${n}"]`), radius=document.querySelector(`[data-public-radius="${n}"]`);
    const zoom=visual.querySelector('.publicZoom');
    if(zoom)zoom.onclick=()=>openLightbox(d);
    function place(clientX,clientY){
      if(!canvas||!circle)return;const r=canvas.getBoundingClientRect();
      const x=Math.max(0,Math.min(1,(clientX-r.left)/Math.max(1,r.width))),y=Math.max(0,Math.min(1,(clientY-r.top)/Math.max(1,r.height)));
      const rad=Math.max(.03,Math.min(.24,Number(radius?.value||8)/100));
      pending[n]={...(pending[n]||{}),x,y,radius:rad,note:note?.value||''};
      circle.hidden=false;circle.style.left=(x*100)+'%';circle.style.top=(y*100)+'%';circle.style.width=(rad*200)+'%';circle.style.height=(rad*200)+'%';
      const s=document.querySelector(`[data-public-status="${n}"]`);if(s)s.textContent='Region selected. Explain why it changes the decision.';scheduleSave();
    }
    if(canvas){canvas.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();place(e.clientX,e.clientY)},true);canvas.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();const r=canvas.getBoundingClientRect();place(r.left+r.width/2,r.top+r.height/2)}})}
    if(note)note.oninput=()=>{pending[n]={...(pending[n]||{}),note:note.value};scheduleSave()};
    if(radius)radius.oninput=()=>{if(!pending[n])pending[n]={x:.5,y:.5,note:note?.value||''};pending[n].radius=Number(radius.value)/100;if(circle&&!circle.hidden){circle.style.width=(pending[n].radius*200)+'%';circle.style.height=(pending[n].radius*200)+'%'}scheduleSave()};
  }

  function renderFallback(unit,n,d){
    const drawer=unit.querySelector('.taskDrawerBody');if(!drawer||drawer.querySelector('.publicVisualFallback'))return;
    const f=d.fallback||{};const x=document.createElement('div');x.className='publicVisualFallback';
    x.innerHTML=`<span class="materialFallback" aria-hidden="true">▧</span><div><b>No defensible public visual cleared the gate.</b><p>${esc(f.note||'ISCARB kept the Unit text-first instead of inserting a weak or ambiguous image.')}</p></div>`;
    drawer.appendChild(x);
  }

  function scheduleSave(){if(saveTimer)return;saveTimer=setTimeout(()=>{saveTimer=null;flush()},5000)}
  async function flush(){
    const entries=Object.entries(pending);pending={};
    for(const [n,v] of entries){
      const note=String(v.note||document.querySelector(`[data-public-note="${n}"]`)?.value||'').trim();
      if(note.length<8||!Number.isFinite(v.x)||!Number.isFinite(v.y)){pending[n]=v;continue}
      try{
        await req(`/api/learning/${job}/public-visual-annotation`,{method:'POST',body:JSON.stringify({student_id:sid,unit_no:Number(n),x:v.x,y:v.y,radius:v.radius||.08,note})});
        const s=document.querySelector(`[data-public-status="${n}"]`);if(s)s.textContent='Visual annotation saved as learner evidence.';
      }catch(e){pending[n]=v;const s=document.querySelector(`[data-public-status="${n}"]`);if(s)s.textContent='Local annotation kept; autosave will retry.'}
    }
    if(Object.keys(pending).length)scheduleSave();
  }

  function openLightbox(d){
    const c=d.candidate||{},box=document.createElement('div');box.className='visualLightbox publicLightbox';
    box.innerHTML=`<div class="visualLightboxCard"><button type="button" class="visualLightboxClose" aria-label="Close">×</button><img src="${esc(d.image_url)}" alt="${esc(c.title||'Licensed contextual visual')}"><div class="visualLightboxCaption"><b>${esc(d.source_footer||'External licensed visual')}</b><br>Contextual enrichment — not P1 evidence.</div></div>`;
    document.body.appendChild(box);box.querySelector('.visualLightboxClose').onclick=()=>box.remove();box.onclick=e=>{if(e.target===box)box.remove()};
  }

  const observer=new MutationObserver(()=>setTimeout(ensureUnit,180));observer.observe(document.body,{childList:true,subtree:true});
  setInterval(()=>{if(Object.keys(pending).length)flush()},5000);
  setInterval(ensureUnit,1200);
  setTimeout(ensureUnit,400);
})();