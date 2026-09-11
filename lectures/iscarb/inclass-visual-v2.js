/* ISCARB In-Class Visual Layer v2 */
(function(){
  const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  function addCss(d){
    if(d.getElementById('iscarb-v2-css')) return;
    const l=d.createElement('link');l.id='iscarb-v2-css';l.rel='stylesheet';l.href='inclass-visual-v2.css?v=20260912-visual2';d.head.appendChild(l);
  }
  function colorOf(card){for(const c of ['mag','teal','sand','violet','green']) if(card.classList.contains('c-'+c)) return c;return 'sand'}
  function flowFromCards(d,slide,compact){
    if(slide.dataset.vflow==='1') return;
    const grids=[...slide.querySelectorAll('.area > .grid')];
    const grid=grids.find(g=>g.querySelectorAll(':scope > .card').length===5);
    if(!grid) return;
    const cards=[...grid.querySelectorAll(':scope > .card')];
    const wrap=d.createElement('div');wrap.className='vflow'+(compact?' compact':'');wrap.style.setProperty('--vn',cards.length);
    cards.forEach((card,i)=>{
      let lab=(card.querySelector('.lab')?.textContent||'').trim();
      lab=lab.replace(/^\d+\s*/,'').trim();
      const txt=(card.querySelector('.txt,.lead')?.textContent||'').trim();
      const c=colorOf(card);
      const node=d.createElement('div');node.className='vstep';node.dataset.c=c;
      node.innerHTML='<div class="vnode"><span>'+String(i+1).padStart(2,'0')+'</span></div><div class="vlab">'+esc(lab)+'</div><div class="vtxt">'+esc(txt)+'</div>';
      wrap.appendChild(node);
    });
    grid.replaceWith(wrap);slide.dataset.vflow='1';
  }
  function practiceHtml(){
    const items=[
      ['Limit visibility','Give a component only the state it needs; private representation prevents accidental corruption.','s.56'],
      ['Validate every input','Check range, size, representation and reasonableness before processing.','s.57–58'],
      ['Handle every exception','Signal, recover with an alternative path, or hand control to runtime support.','s.59–61'],
      ['Avoid error-prone constructs','Reduce hidden state, imprecise comparison, unsafe pointers, timing traps and other constructs that magnify human error.','s.62–65'],
      ['Provide restart capability','Preserve forms or checkpoint state so a failure does not force the user to start again.','s.66'],
      ['Check array bounds','Out-of-range access can corrupt memory and create buffer-overflow vulnerabilities.','s.67'],
      ['Time out external calls','A silent remote failure must become an explicit failure state after a defined wait.','s.68'],
      ['Name real-world constants','Use one named value instead of duplicated magic numbers so change happens in one controlled place.','s.69']
    ];
    let h='<div class="practice-map"><div class="practice-core"><div class="pc-k">DEPENDABLE PROGRAMMING · s.53–69</div><div class="pc-big">Eight guardrails.<br>One purpose.</div><div class="pc-sub">Reduce the chance that an unchecked assumption survives long enough to become a service failure.</div></div><div class="practice-grid">';
    items.forEach((x,i)=>{h+='<div class="practice-item"><div class="pn">'+String(i+1).padStart(2,'0')+'</div><div><div class="pt">'+x[0]+'</div><div class="px">'+x[1]+'</div><div class="ps">PRIMARY SOURCE · '+x[2]+'</div></div></div>'});
    h+='<div class="practice-transfer">TRANSFER · Which one of these eight could fail silently in your own project, and what artifact would prove you fixed it?</div></div></div>';
    return h;
  }
  function patchCh11(w,d){
    if(!Array.isArray(w.U)||w.__ch11ProgrammingPatch) return;
    const idx=w.U.findIndex(u=>u&&u.k==='R11');
    if(idx<0) return;
    const u=w.U[idx];
    u.phase='SOURCE EXPANSION / DEPENDABLE PROGRAMMING';
    u.rule='SOURCE EXPANSION - eight guardrails for dependable code';
    u.accent='sand';
    u.learn='Explain how eight coding practices reduce fault introduction, expose abnormal states, and support recovery.';
    u.title='Dependable code is eight small refusals';
    u.sub='The chapter moves from architecture to code: reliability is also built by refusing unchecked state, unchecked input, silent exceptions and silent dependencies.';
    u.timebox='3 min';
    u.task='Pick one guardrail your project needs most. Name the failure it prevents and the artifact that would prove the guardrail exists.';
    u.say='These are not style rules. Each one removes a path by which a local programming mistake can become a system failure.';
    u.notes='Three minutes. This restores the Chapter 11 dependable-programming section to the in-class spine. Do not teach the eight as a checklist to memorise: group them by engineering intent. Visibility and safer constructs reduce fault introduction; input checks and bounds expose invalid state before it spreads; exception handling, timeouts and restart turn abnormal states into controlled behaviour; named real-world constants reduce inconsistent change. Then transfer one rule to the student project.';
    u.blocks=[{t:'raw',src:'P1 · s.53-69',html:practiceHtml()},{t:'principle',txt:'Dependable programming is fault containment at code scale: constrain what can go wrong, detect what still goes wrong, and recover without pretending nothing happened.'}];
    const slide=d.querySelector('.slide[data-i="'+idx+'"]');
    if(slide){
      const eye=slide.querySelector('.eyebrow');if(eye){eye.innerHTML=u.phase;eye.style.color='var(--sand)'}
      const pill=slide.querySelector('.pill');if(pill){pill.innerHTML=u.rule;pill.style.borderColor='var(--sand)';pill.style.color='var(--sand)'}
      const h1=slide.querySelector('h1');if(h1)h1.innerHTML=u.title;
      const sub=slide.querySelector('.sub');if(sub)sub.innerHTML=u.sub;
      const area=slide.querySelector('.area');if(area)area.innerHTML=w.T(w.rBlocks(u.blocks));
      slide.dataset.vprogramming='1';
    }
    const bi=w.U.findIndex(x=>x&&x.k==='B01');
    if(bi>=0){
      const bu=w.U[bi];
      if(bu.blocks&&bu.blocks[1]) bu.blocks[1].src='P1 · s.62-65';
      const bs=d.querySelector('.slide[data-i="'+bi+'"]');
      const bc=bs?.querySelector('[data-f="bridge_own"]')?.closest('.card')||bs?.querySelector('.area .card:last-of-type');
      if(bc&&!bc.querySelector('.src')){const s=d.createElement('div');s.className='src';s.textContent='P1 · s.62–65';bc.appendChild(s)}
    }
    if(w.LECTURE?.coverage?.sections?.[4]) delete w.LECTURE.coverage.sections[4].why;
    if(typeof w.renderCoverage==='function') w.renderCoverage();
    w.__ch11ProgrammingPatch=true;
  }
  function markDensity(d){
    d.querySelectorAll('.slide .area').forEach(a=>{
      if(a.querySelector('.practice-map,.vflow,.splitfig,.cov,.pm,.jah,.qz,.bridge')) return;
      const major=[...a.children].filter(x=>!x.classList.contains('src'));
      if(major.length<=2)a.dataset.vdensity='sparse';
    });
  }
  function closeFlow(d,w){
    const end=d.querySelector('.slide[data-i="'+(w.U.length-1)+'"]');if(!end)return;
    end.dataset.vend='1';
    const area=end.querySelector('.area');if(!area||area.querySelector('.vflow'))return;
    const grid=area.querySelector('.grid.g5');if(!grid)return;
    const cards=[...grid.querySelectorAll('.card')];
    const clone=d.createElement('div');clone.className='vflow compact';clone.style.setProperty('--vn','5');
    cards.forEach((card,i)=>{const c=colorOf(card),lab=(card.querySelector('.lab')?.textContent||'').trim();const n=d.createElement('div');n.className='vstep';n.dataset.c=c;n.innerHTML='<div class="vnode"><span>'+String(i+1).padStart(2,'0')+'</span></div><div class="vlab">'+esc(lab)+'</div>';clone.appendChild(n)});
    grid.insertAdjacentElement('afterend',clone);
  }
  function apply(frame,ch){
    const w=frame?.contentWindow,d=w?.document;if(!w||!d||!d.getElementById('stage')||!Array.isArray(w.U))return false;
    if(d.documentElement.dataset.iscarbVisualV2==='1') return true;
    addCss(d);
    if(ch==='11') patchCh11(w,d);
    w.U.forEach((u,i)=>{
      const slide=d.querySelector('.slide[data-i="'+i+'"]');if(!slide)return;
      if(/five-step engineering flow/i.test(u.title||''))flowFromCards(d,slide,false);
      if((u.k==='END')||i===w.U.length-1)slide.dataset.vend='1';
    });
    closeFlow(d,w);
    markDensity(d);
    d.documentElement.dataset.iscarbVisualV2='1';
    if(typeof w.renderCoverage==='function')w.renderCoverage();
    if(typeof w.renderPath==='function')w.renderPath();
    return true;
  }
  window.ISCARBVisualV2={apply};
})();
