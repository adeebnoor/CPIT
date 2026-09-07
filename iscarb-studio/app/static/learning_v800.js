'use strict';
(function(){
  const job=document.body.dataset.job;
  if(!job) return;
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const studentKey='iscarb.student.'+job;
  const sid=localStorage.getItem(studentKey)||'';
  if(!sid) return;

  let visualData=null;
  let pending={};
  let saveTimer=null;

  async function req(url,opt={}){
    const r=await fetch(url,{cache:'no-store',...opt,headers:{'Content-Type':'application/json',...(opt.headers||{})}});
    const t=await r.text(); let d; try{d=JSON.parse(t)}catch{d={detail:t}}
    if(!r.ok) throw Error(typeof d.detail==='string'?d.detail:'Request failed');
    return d;
  }

  async function load(){
    visualData=await req(`/api/learning/${job}/hybrid-visuals?student_id=${encodeURIComponent(sid)}`);
    observe(); enhanceAll();
  }

  function observe(){
    const observer=new MutationObserver(()=>enhanceAll());
    observer.observe(document.body,{childList:true,subtree:true});
  }

  function currentUnitNumber(){
    const k=document.querySelector('#unit .unitKicker');
    if(!k) return null;
    const m=(k.textContent||'').match(/UNIT\s+(\d{1,2})\s*\/\s*20/i);
    return m?Number(m[1]):null;
  }

  function annotationFor(key){return (visualData?.visual_annotations||{})[String(key)]||null}

  function imageCard(v,key,interactive=true){
    const ann=annotationFor(key);
    const marker=ann?`<span class="visualPin" style="left:${ann.x*100}%;top:${ann.y*100}%" aria-label="Saved annotation point"></span>`:'';
    return `<section class="p1VisualEvidence" data-visual-key="${esc(key)}">
      <div class="visualMeta"><span>${esc((v.category||'source visual').toUpperCase())}</span><b>${esc(v.source_anchor||'P1')}</b></div>
      <div class="visualCanvas ${interactive?'annotatable':''}" data-canvas="${esc(key)}" tabindex="0" role="img" aria-label="${esc(v.alt_text||'Primary source visual')}">
        <img src="${esc(v.image_url)}" alt="${esc(v.alt_text||'Primary source visual')}" loading="eager">${marker}
        <span class="sourceWatermark">P1 · Page ${esc(v.page)}</span>
      </div>
      <div class="visualActions"><button type="button" class="btn visualZoom" data-zoom="${esc(key)}">Zoom to read</button><span>${esc(v.title||'')}</span></div>
      ${tableCards(v)}
    </section>`;
  }

  function tableCards(v){
    const cards=Array.isArray(v.table_cards)?v.table_cards:[];
    if(!cards.length) return '';
    return `<div class="sourceTableCards"><div class="unitKicker">P1 TABLE → INTERACTIVE ROWS</div>${cards.map((c,i)=>`<details><summary>${esc(c.label)}</summary><p>${esc(c.description)}</p></details>`).join('')}</div>`;
  }

  function enhanceU00(){
    const card=document.querySelector('.knowledgeModal .knowledgeCard');
    const v=visualData?.u00;
    if(!card||!v||card.dataset.v800==='1') return;
    card.dataset.v800='1';
    const flip=card.querySelector('.flipGrid');
    if(!flip) return;
    const grid=document.createElement('div'); grid.className='u00HybridGrid';
    const left=document.createElement('div'); left.className='u00CardsPane';
    flip.parentNode.insertBefore(grid,flip);
    left.appendChild(flip); grid.appendChild(left);
    const right=document.createElement('div'); right.className='u00VisualPane'; right.innerHTML=imageCard(v,'u00',false);
    grid.appendChild(right);
    bindVisualUI(right,v,'u00',false);
  }

  function enhanceUnit(){
    const n=currentUnitNumber();
    if(!n) return;
    const unit=document.getElementById('unit');
    const v=visualData?.units?.[String(n)];
    if(!unit||!v||unit.dataset.v800===String(n)) return;
    unit.dataset.v800=String(n);

    const source=unit.querySelector('.sourceFocus');
    const supports=unit.querySelector('.supportChannels');
    const drawer=unit.querySelector('.taskDrawer');
    if(!source||!drawer) return;

    const grid=document.createElement('div'); grid.className='hybridVisualGrid';
    const analysis=document.createElement('div'); analysis.className='hybridAnalysisPane';
    const visual=document.createElement('div'); visual.className='hybridSourcePane';
    source.parentNode.insertBefore(grid,source);
    analysis.appendChild(source); if(supports) analysis.appendChild(supports); analysis.appendChild(drawer);
    visual.innerHTML=imageCard(v,String(n),true);
    grid.appendChild(analysis); grid.appendChild(visual);

    const body=drawer.querySelector('.taskDrawerBody');
    if(body){
      const ann=annotationFor(String(n));
      const gate=document.createElement('section'); gate.className='visualAnnotationGate';
      gate.innerHTML=`<div class="unitKicker">VISUAL EVIDENCE · REQUIRED</div><h3>The figure must change the decision, not decorate it.</h3><p>${esc(v.interaction_prompt||'Mark the visual element that changes your decision and explain why.')}</p><div class="field"><label>Why does the marked element change your decision?</label><textarea rows="3" data-visual-note="${n}" placeholder="Explain the engineering significance…">${esc(ann?.note||'')}</textarea></div><div class="visualGateStatus" data-visual-status="${n}">${ann?'Visual evidence saved.':'Click the P1 visual to place a marker, then explain it.'}</div>`;
      body.insertBefore(gate,body.firstChild);
    }

    const next=unit.querySelector('#next');
    if(next){
      next.dataset.v800BaseDisabled=next.disabled?'1':'0';
      if(!annotationFor(String(n)) && next.dataset.v800BaseDisabled==='0'){
        next.disabled=true; next.classList.remove('primary');
      }
    }
    bindVisualUI(visual,v,String(n),true);
    bindNote(n);
  }

  function bindVisualUI(scope,v,key,interactive){
    scope.querySelectorAll('[data-zoom]').forEach(btn=>btn.onclick=()=>openLightbox(v));
    if(!interactive) return;
    const canvas=scope.querySelector('[data-canvas]');
    if(!canvas) return;
    const mark=(clientX,clientY)=>{
      const r=canvas.getBoundingClientRect();
      const x=Math.max(0,Math.min(1,(clientX-r.left)/Math.max(1,r.width)));
      const y=Math.max(0,Math.min(1,(clientY-r.top)/Math.max(1,r.height)));
      pending[key]=pending[key]||{}; pending[key].x=x; pending[key].y=y;
      let pin=canvas.querySelector('.visualPin');
      if(!pin){pin=document.createElement('span');pin.className='visualPin';canvas.appendChild(pin)}
      pin.style.left=(x*100)+'%'; pin.style.top=(y*100)+'%';
      const status=document.querySelector(`[data-visual-status="${key}"]`); if(status) status.textContent='Marker placed. Explain why this point changes your decision.';
      scheduleSave();
    };
    canvas.addEventListener('click',e=>{if(e.target.closest('.sourceWatermark'))return;mark(e.clientX,e.clientY)});
    canvas.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();const r=canvas.getBoundingClientRect();mark(r.left+r.width/2,r.top+r.height/2)}});
  }

  function bindNote(n){
    const note=document.querySelector(`[data-visual-note="${n}"]`); if(!note)return;
    note.oninput=()=>{pending[String(n)]=pending[String(n)]||{};pending[String(n)].note=note.value;scheduleSave()};
  }

  function scheduleSave(){
    if(saveTimer) return;
    saveTimer=setTimeout(()=>{saveTimer=null;flushPending()},5000);
  }

  async function flushPending(){
    const entries=Object.entries(pending); pending={};
    for(const [key,delta] of entries){
      const old=annotationFor(key)||{};
      const note=(delta.note??document.querySelector(`[data-visual-note="${key}"]`)?.value??old.note??'').trim();
      const x=Number(delta.x??old.x??.5), y=Number(delta.y??old.y??.5);
      if(note.length<8){pending[key]={...delta,note};continue}
      try{
        const out=await req(`/api/learning/${job}/visual-annotation`,{method:'POST',body:JSON.stringify({student_id:sid,unit_key:key,x,y,note})});
        visualData.visual_annotations=visualData.visual_annotations||{};visualData.visual_annotations[key]=out.annotation;
        const status=document.querySelector(`[data-visual-status="${key}"]`);if(status)status.textContent='Visual evidence saved automatically.';
        const next=document.querySelector('#unit #next');
        if(next&&next.dataset.v800BaseDisabled==='0'){next.disabled=false;next.classList.add('primary')}
      }catch(e){
        pending[key]={x,y,note};
        const status=document.querySelector(`[data-visual-status="${key}"]`);if(status)status.textContent='Local note kept; server save will retry: '+e.message;
      }
    }
    if(Object.keys(pending).length) scheduleSave();
  }

  function openLightbox(v){
    const box=document.createElement('div');box.className='visualLightbox';
    box.innerHTML=`<div class="visualLightboxCard"><button type="button" class="visualLightboxClose" aria-label="Close">×</button><img src="${esc(v.image_url)}" alt="${esc(v.alt_text||'Primary source visual')}"><div class="visualLightboxCaption"><b>${esc(v.source_anchor||'P1')}</b> · ${esc(v.title||'')}</div></div>`;
    document.body.appendChild(box);box.querySelector('.visualLightboxClose').onclick=()=>box.remove();box.onclick=e=>{if(e.target===box)box.remove()};
  }

  function enhanceAll(){if(!visualData)return;enhanceU00();enhanceUnit()}
  setInterval(()=>{if(Object.keys(pending).length)flushPending()},5000);
  load().catch(()=>{});
})();