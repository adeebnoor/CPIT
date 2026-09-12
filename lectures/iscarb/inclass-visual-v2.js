/* ISCARB In-Class Visual Layer v3 */
(function(){
  const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const COLORS=['mag','teal','sand','violet','green'];

  function addCss(d){
    if(d.getElementById('iscarb-v2-css')) return;
    const l=d.createElement('link');
    l.id='iscarb-v2-css';l.rel='stylesheet';l.href='inclass-visual-v2.css?v=20260912-visual3';
    d.head.appendChild(l);
  }
  function colorOf(card){for(const c of COLORS) if(card.classList.contains('c-'+c)) return c;return 'sand'}
  function getSlide(w,d,key){const idx=w.U.findIndex(u=>u&&u.k===key);return {idx,u:idx>=0?w.U[idx]:null,slide:idx>=0?d.querySelector('.slide[data-i="'+idx+'"]'):null}}
  function heading(slide,title,sub,rule,accent){
    if(!slide)return;
    const h1=slide.querySelector('h1');if(h1&&title)h1.textContent=title;
    const s=slide.querySelector('.sub');if(s&&sub!=null)s.textContent=sub;
    const p=slide.querySelector('.pill');if(p&&rule){p.textContent=rule;if(accent){p.style.borderColor='var(--'+accent+')';p.style.color='var(--'+accent+')'}}
  }
  function cardLead(card){return (card.querySelector('.lead')?.textContent||card.querySelector('.txt')?.textContent||'').trim()}
  function cardLab(card){return (card.querySelector('.lab')?.textContent||'').trim().replace(/^\d+\s*/,'')}

  function flowFromCards(d,slide,compact){
    if(!slide||slide.dataset.vflow==='1') return;
    const grids=[...slide.querySelectorAll('.area > .grid')];
    const grid=grids.find(g=>g.querySelectorAll(':scope > .card').length===5);
    if(!grid) return;
    const cards=[...grid.querySelectorAll(':scope > .card')];
    const wrap=d.createElement('div');wrap.className='vflow'+(compact?' compact':'');wrap.style.setProperty('--vn',cards.length);
    cards.forEach((card,i)=>{
      const lab=cardLab(card),txt=cardLead(card),c=colorOf(card);
      const node=d.createElement('div');node.className='vstep';node.dataset.c=c;
      node.innerHTML='<div class="vnode"><span>'+String(i+1).padStart(2,'0')+'</span></div><div class="vlab">'+esc(lab)+'</div>'+(compact?'':'<div class="vtxt">'+esc(txt)+'</div>');
      wrap.appendChild(node);
    });
    grid.replaceWith(wrap);slide.dataset.vflow='1';
  }

  function patchCrisis(w,d){
    const {u,slide}=getSlide(w,d,'R01');if(!u||!slide||slide.dataset.vduo==='1')return;
    const area=slide.querySelector('.area');if(!area)return;
    const cards=[...area.querySelectorAll('.card')].filter(c=>!c.querySelector('textarea,.picker,button'));
    if(cards.length<2)return;
    const chosen=cards.slice(0,2);
    const wrap=d.createElement('div');wrap.className='vduo';
    chosen.forEach((card,i)=>{
      const c=colorOf(card),lab=cardLab(card)||['DECISION','UNKNOWN'][i],txt=cardLead(card);
      const el=d.createElement('div');el.className='vduo-item';el.dataset.c=c;
      el.innerHTML='<div class="vduo-num">0'+(i+1)+'</div><div class="vduo-lab">'+esc(lab)+'</div><div class="vduo-text">'+esc(txt)+'</div>';
      wrap.appendChild(el);
    });
    area.innerHTML='';area.appendChild(wrap);
    const p=d.createElement('div');p.className='principle mag';
    p.textContent='Decide with what you know now — and make the boundary of that decision explicit.';
    area.appendChild(p);slide.dataset.vduo='1';
    u.sub=(u.sub||'').split('.').slice(0,1).join('.')||u.sub;
  }

  function patchQuestions(w,d){
    const {u,slide}=getSlide(w,d,'H01');if(!u||!slide||slide.dataset.vquestions==='1')return;
    const area=slide.querySelector('.area');if(!area)return;
    const cards=[...area.querySelectorAll('.card')].filter(c=>!c.querySelector('textarea,.picker,button')).slice(0,3);
    if(cards.length!==3)return;
    const wrap=d.createElement('div');wrap.className='vquestions';
    cards.forEach((card,i)=>{
      const c=["teal","sand","mag"][i],lab=cardLab(card),txt=cardLead(card);
      const el=d.createElement('div');el.className='vq';el.dataset.c=c;
      el.innerHTML='<div class="vq-n">'+(i+1)+'</div><div class="vq-l">'+esc(lab)+'</div><div class="vq-t">'+esc(txt)+'</div>';
      wrap.appendChild(el);
    });
    area.innerHTML='';area.appendChild(wrap);
    const p=d.createElement('div');p.className='principle mag';p.textContent='Commit the reasoning before the reveal; the answer comes later.';area.appendChild(p);
    heading(slide,'Three questions before the answer','Use the questions to make your assumptions visible before you see the source.',u.rule,'violet');
    slide.dataset.vquestions='1';
  }

  function compactFigureCards(d,slide){
    if(!slide||slide.dataset.vconcepts==='1')return;
    const split=slide.querySelector('.splitfig');if(!split)return;
    const grids=[...split.querySelectorAll('.grid')];
    const grid=grids.find(g=>{
      const cards=[...g.querySelectorAll(':scope > .card')];
      return cards.length>=4&&cards.every(c=>!c.querySelector('textarea,.picker,button'));
    });
    if(!grid)return;
    const cards=[...grid.querySelectorAll(':scope > .card')];
    const wrap=d.createElement('div');wrap.className='vconcepts';
    cards.forEach(card=>{
      const e=d.createElement('div');e.className='vconcept';e.dataset.c=colorOf(card);
      e.innerHTML='<div class="vc-lab">'+esc(cardLab(card))+'</div><div class="vc-lead">'+esc(cardLead(card))+'</div>';
      wrap.appendChild(e);
    });
    grid.replaceWith(wrap);slide.dataset.vconcepts='1';
  }

  function patchAI(w,d,ch){
    const {u,slide}=getSlide(w,d,'R15');if(!u||!slide||slide.dataset.vai==='1')return;
    const area=slide.querySelector('.area');if(!area)return;
    u.title='AI may accelerate the work; it cannot own the judgment';
    u.sub='Used well, AI frees time for comparison and evidence. Used badly, it hides whether you learned the judgment.';
    u.rule='RULE 15 - AI assist + human ownership';
    u.learn='Distinguish AI-supported production from student-owned professional judgment, verification, and sign-off.';
    u.task='Explain one AI-assisted decision without the AI: what did it accelerate, what did you verify, and what judgment remained yours?';
    u.notes='Keep this to two minutes. The point is learning, not policy compliance. AI can accelerate drafting, summarising and evidence organisation. It can also conceal weak understanding and create false confidence. The student still owns FIT, BOUND, verification, adaptation and final sign-off. Ask one student to explain an AI-assisted decision without looking at the model output.';
    heading(slide,u.title,u.sub,u.rule,'sand');
    const chapterLine=ch==='11'?'the metric, its boundary, and the evidence behind the number':'the fit, its boundary, and the evidence behind the decision';
    area.innerHTML=
      '<div class="ai-learning">'+
        '<div class="ai-lane" data-c="teal"><div class="ai-k">AI CAN ACCELERATE</div><div class="ai-big">Draft. Compare. Organise.</div><div class="ai-small">Summaries, candidate options, test ideas, log triage, and evidence structure can become faster.</div></div>'+
        '<div class="ai-lane" data-c="sand"><div class="ai-k">AI CAN HIDE</div><div class="ai-big">Weak understanding behind fluent text.</div><div class="ai-small">A polished answer can still contain unverified assumptions, false confidence, or a boundary the student cannot explain.</div></div>'+
        '<div class="ai-lane" data-c="mag"><div class="ai-k">YOU MUST OWN</div><div class="ai-big">Judge. Verify. Sign.</div><div class="ai-small">You must be able to defend '+esc(chapterLine)+' without asking the model to think for you.</div></div>'+
        '<div class="ai-check"><div class="ai-tag">LEARNING CHECK</div><div class="ai-line">Can you <b>explain it</b>, <b>verify one claim independently</b>, and <b>name what would change your mind</b>?</div></div>'+
      '</div>';
    slide.dataset.vai='1';
  }

  function patchReadiness(w,d,ch){
    const {u,slide}=getSlide(w,d,'R20');if(!u||!slide||slide.dataset.vready==='1')return;
    const area=slide.querySelector('.area');if(!area)return;
    const gates=ch==='11' ? [
      ['FIT','Can you choose the right reliability or availability measure?','Name why this measure fits the failure mode and service use.'],
      ['BOUND','Can you state what makes the number valid?','Define the observation window, failure meaning, degraded mode, and reopen trigger.'],
      ['EVIDENCE','Can you show how the number will be measured?','Name the logs, incidents, service data, or test evidence another engineer can inspect.'],
      ['ADAPT','Can you revise the requirement when conditions change?','Explain whether new evidence means retain, revise, or replace — and why.']
    ] : [
      ['FIT','Can you select the dependability mechanism that fits this case?','Choose a property or mechanism for this use — not just a definition.'],
      ['BOUND','Can you state when your decision stops being fit?','Name an observable condition that would force the decision to be reopened.'],
      ['EVIDENCE','Can you show what would prove you wrong?','Name a test, log, measurement, record, or inspection another engineer can examine.'],
      ['ADAPT','Can you change proportionately under stress?','Explain whether the original action should be retained, revised, or replaced.']
    ];
    u.title=ch==='11'?'Readiness check: can you defend the number?':'Readiness check: can you defend the decision?';
    u.sub='This is the end-of-class readiness test. Click a gate only if you can demonstrate it without being given the answer.';
    u.rule='FINAL READINESS CHECK - four gates';
    u.learn='Self-assess whether the learner can select, bound, evidence, and adapt a professional judgment.';
    u.task='Pass only the gates you can actually demonstrate. Any unchecked gate is the next thing to revisit before After-Class.';
    u.notes='Do not skip this slide. It is the readiness test. Give the class 45 seconds. Students click only gates they can defend from their own work. Four of four means ready for After-Class; anything less gives a precise feed-forward target. This is self-check, not a grade.';
    heading(slide,u.title,u.sub,u.rule,'teal');
    area.innerHTML='<div class="ready-shell"><div class="ready-score"><div class="rs-k">READINESS</div><div class="rs-n"><span>0</span>/4</div><div class="rs-state">Not ready yet</div><div class="rs-help">Click only what you can demonstrate from your own reasoning. This is a self-check, not a grade.</div></div><div class="ready-gates">'+
      gates.map((g,i)=>'<button type="button" class="ready-gate" aria-pressed="false" data-rg="'+i+'"><div class="rg-k">'+esc(g[0])+'</div><div class="rg-q">'+esc(g[1])+'</div><div class="rg-h">'+esc(g[2])+'</div></button>').join('')+
      '</div></div>';
    const buttons=[...area.querySelectorAll('.ready-gate')],n=area.querySelector('.rs-n span'),state=area.querySelector('.rs-state');
    function sync(){const score=buttons.filter(b=>b.getAttribute('aria-pressed')==='true').length;n.textContent=score;state.textContent=score===4?'Ready for After-Class':score===3?'Almost ready — revisit one gate':score>0?'Developing — revisit the unchecked gates':'Not ready yet';state.style.color=score===4?'var(--green)':score===3?'var(--sand)':'var(--sand)'}
    buttons.forEach(b=>b.addEventListener('click',()=>{b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true');sync()}));sync();
    slide.dataset.vready='1';
  }

  function practiceHtml(){
    const items=[
      ['Limit visibility','Keep state private.'],
      ['Validate input','Reject invalid state early.'],
      ['Handle exceptions','Turn abnormal states into controlled behaviour.'],
      ['Avoid risky constructs','Reduce error-prone language and design choices.'],
      ['Support restart','Recover without forcing a full restart.'],
      ['Check bounds','Stop invalid memory access.'],
      ['Time out calls','Make silent dependency failure explicit.'],
      ['Name constants','Change one controlled value, not many magic numbers.']
    ];
    let h='<div class="practice-map"><div class="practice-core"><div class="pc-k">DEPENDABLE PROGRAMMING · s.53–69</div><div class="pc-big">Eight guardrails.<br>One purpose.</div><div class="pc-sub">Prevent a local programming mistake from becoming a service failure.</div></div><div class="practice-grid">';
    items.forEach((x,i)=>{h+='<div class="practice-item"><div class="pn">'+String(i+1).padStart(2,'0')+'</div><div><div class="pt">'+esc(x[0])+'</div><div class="px">'+esc(x[1])+'</div></div></div>'});
    h+='<div class="practice-transfer">TRANSFER · Which guardrail would prevent the most dangerous silent failure in your project?</div></div></div>';
    return h;
  }

  function patchCh11(w,d){
    if(!Array.isArray(w.U)||w.__ch11ProgrammingPatch) return;
    const idx=w.U.findIndex(u=>u&&u.k==='R11');
    if(idx<0) return;
    const u=w.U[idx];
    u.phase='SOURCE EXPANSION / DEPENDABLE PROGRAMMING';u.rule='SOURCE EXPANSION - eight guardrails for dependable code';u.accent='sand';
    u.learn='Explain how dependable programming prevents, exposes, and contains faults.';
    u.title='Dependable code: eight guardrails, one purpose';
    u.sub='Reliability is also built at code level: prevent bad state, expose abnormal state, and recover deliberately.';
    u.timebox='3 min';u.task='Choose one guardrail your project needs most and name the failure it prevents.';
    u.say='These are engineering controls, not style rules.';
    u.notes='Three minutes. This restores the Chapter 11 dependable-programming section to the in-class spine. Group the eight by intent rather than asking students to memorise a list: prevent faults, expose invalid state, and recover deliberately.';
    u.blocks=[{t:'raw',src:'P1 · s.53-69',html:practiceHtml()},{t:'principle',txt:'At code scale, dependability means: prevent what you can, expose what remains, and recover deliberately.'}];
    const slide=d.querySelector('.slide[data-i="'+idx+'"]');
    if(slide){heading(slide,u.title,u.sub,u.rule,'sand');const eye=slide.querySelector('.eyebrow');if(eye){eye.textContent=u.phase;eye.style.color='var(--sand)'}const area=slide.querySelector('.area');if(area)area.innerHTML=w.T(w.rBlocks(u.blocks));slide.dataset.vprogramming='1'}
    const bi=w.U.findIndex(x=>x&&x.k==='B01');if(bi>=0&&w.U[bi].blocks&&w.U[bi].blocks[1])w.U[bi].blocks[1].src='P1 · s.62-65';
    if(w.LECTURE?.coverage?.sections?.[4]) delete w.LECTURE.coverage.sections[4].why;
    const ci=w.U.findIndex(x=>x&&x.k==='C01');if(ci>=0)w.U[ci].notes='The coverage ledger is evidence-derived. Dependable programming is now explicitly taught through the source expansion and build bridge.';
    if(typeof w.renderCoverage==='function') w.renderCoverage();
    w.__ch11ProgrammingPatch=true;
  }

  function markDensity(d){
    d.querySelectorAll('.slide .area').forEach(a=>{
      if(a.querySelector('.practice-map,.vflow,.vduo,.vquestions,.ready-shell,.ai-learning,.splitfig,.cov,.pm,.jah,.qz,.bridge')) return;
      const major=[...a.children].filter(x=>!x.classList.contains('src'));
      if(major.length<=2)a.dataset.vdensity='sparse';
    });
  }

  function closeFlow(d,w){
    const end=d.querySelector('.slide[data-i="'+(w.U.length-1)+'"]');if(!end)return;
    end.dataset.vend='1';const area=end.querySelector('.area');if(!area||area.querySelector('.vflow'))return;
    const grid=area.querySelector('.grid.g5');if(!grid)return;
    const cards=[...grid.querySelectorAll('.card')],clone=d.createElement('div');clone.className='vflow compact';clone.style.setProperty('--vn','5');
    cards.forEach((card,i)=>{const n=d.createElement('div');n.className='vstep';n.dataset.c=colorOf(card);n.innerHTML='<div class="vnode"><span>'+String(i+1).padStart(2,'0')+'</span></div><div class="vlab">'+esc(cardLab(card))+'</div>';clone.appendChild(n)});
    grid.insertAdjacentElement('afterend',clone);
  }

  function apply(frame,ch){
    const w=frame?.contentWindow,d=w?.document;
    if(!w||!d||!d.getElementById('stage')||!Array.isArray(w.U))return false;
    if(d.documentElement.dataset.iscarbVisualV2==='3') return true;
    addCss(d);
    if(ch==='11')patchCh11(w,d);
    patchCrisis(w,d);patchQuestions(w,d);patchAI(w,d,ch);patchReadiness(w,d,ch);
    w.U.forEach((u,i)=>{
      const slide=d.querySelector('.slide[data-i="'+i+'"]');if(!slide)return;
      if(/five-step engineering flow/i.test(u.title||''))flowFromCards(d,slide,false);
      compactFigureCards(d,slide);
      if((u.k==='END')||i===w.U.length-1)slide.dataset.vend='1';
    });
    closeFlow(d,w);markDensity(d);
    d.documentElement.dataset.iscarbVisualV2='3';
    if(typeof w.renderCoverage==='function')w.renderCoverage();
    if(typeof w.renderPath==='function')w.renderPath();
    return true;
  }
  window.ISCARBVisualV2={apply};
})();
