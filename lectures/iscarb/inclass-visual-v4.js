/* ISCARB In-Class Final Polish v5 */
(function(){
  const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  function get(w,d,key){const idx=w.U.findIndex(u=>u&&u.k===key);return {idx,u:idx>=0?w.U[idx]:null,slide:idx>=0?d.querySelector('.slide[data-i="'+idx+'"]'):null}}
  function heading(slide,title,sub,rule,accent){
    if(!slide)return;
    const h=slide.querySelector('h1'),s=slide.querySelector('.sub'),p=slide.querySelector('.pill');
    if(h&&title)h.textContent=title;
    if(s&&sub!=null)s.textContent=sub;
    if(p&&rule){p.textContent=rule;if(accent){p.style.borderColor='var(--'+accent+')';p.style.color='var(--'+accent+')';}}
  }
  function addCss(d){
    if(d.getElementById('iscarb-v5-css'))return;
    const l=d.createElement('link');l.id='iscarb-v5-css';l.rel='stylesheet';l.href='inclass-visual-v4.css?v=20260912-visual5';d.head.appendChild(l);
  }
  function simplifyStaticCards(d){
    d.querySelectorAll('.card:has(.lead)').forEach(card=>{
      if(card.querySelector('textarea,.picker,button,input,select'))return;
      card.querySelectorAll('.txt,.src,.foldbar').forEach(el=>el.style.display='none');
    });
  }
  function addBadge(slide,kind,label){
    if(!slide || slide.querySelector('.v4-badge.'+kind))return;
    const b=slide.ownerDocument.createElement('div');
    b.className='v4-badge '+kind;
    b.textContent=label;
    slide.appendChild(b);
  }
  function patchAI(w,d,ch){
    const {u,slide}=get(w,d,'R15'); if(!u||!slide||slide.dataset.v5ai)return;
    addBadge(slide,'ai','AI Literacy');
    heading(slide,'AI can accelerate evidence. It cannot own the judgment.','Use AI to prepare, compare, and surface evidence — but the accountable engineering decision stays with you.','RULE 15 - Human judgment first','teal');
    const area=slide.querySelector('.area'); if(!area)return;
    area.innerHTML=''
      +'<div class="v4-ai-emphasis">'
      +  '<div class="v4-ai-pill"><b>AI CAN HELP</b><span>Summarise sources, structure evidence, and propose options faster.</span></div>'
      +  '<div class="v4-ai-pill"><b>AI CAN HIDE</b><span>Shallow understanding, unchecked assumptions, and copied confidence.</span></div>'
      +  '<div class="v4-ai-pill"><b>YOU MUST OWN</b><span>The fit, the boundary, the evidence check, and the final sign-off.</span></div>'
      +'</div>'
      +'<div class="grid g3" style="width:min(1120px,100%);align-self:center">'
      +  '<div class="card"><div class="lab">Allowed</div><div class="lead">Use AI to organise and compare evidence.</div></div>'
      +  '<div class="card"><div class="lab">Not Enough</div><div class="lead">AI output without verification does not count as engineering judgment.</div></div>'
      +  '<div class="card"><div class="lab">Learning Check</div><div class="lead">Can you explain the decision yourself and say what would change your mind?</div></div>'
      +'</div>';
    u.title='AI can accelerate evidence. It cannot own the judgment.';
    u.sub='Use AI to prepare, compare, and surface evidence — but the accountable engineering decision stays with you.';
    u.rule='RULE 15 - Human judgment first';
    u.learn='Explain what AI may support and what professional judgment the student must still own.';
    u.task='State one allowed use, one risk, and one thing the engineer must personally defend.';
    u.notes='Keep the AI message modern but strict: this is an AI era course, but AI is a support tool, not a substitute for accountability. Students may use it to organise evidence and compare options, but they must verify claims independently and defend their own decision.';
    slide.dataset.v5ai='1';
  }
  function patchStress(w,d,ch){
    const {u,slide}=get(w,d,'R13'); if(!u||!slide||slide.dataset.v5stress)return;
    const is11=ch==='11';
    heading(slide,
      is11?'What change would break your number?':'What change would break your solution?',
      is11?'A robust reliability number exposes the assumption that could make it wrong.':'A robust decision names the variable that could reverse it.',
      'RULE 13 - Breaking variable','sand');
    const items=is11?[
      ['USAGE','The operational profile changes, so the measured system no longer represents actual use.'],
      ['REPAIR','Repair time triples; availability falls even when failure frequency stays the same.'],
      ['DEFINITION','The vendor counts degraded service as “available”, but your definition did not.'],
      ['SCOPE','The figure is now reported per service, not for the whole system.']
    ]:[
      ['STAFFING','One qualified reviewer becomes one reviewer plus a trainee.'],
      ['DEADLINE','The production window closes tonight; reverting costs a full day of supply.'],
      ['DATA','Commissioning evidence comes from a different firmware baseline.'],
      ['REGULATION','The regulator asks for new evidence before unattended operation.']
    ];
    const area=slide.querySelector('.area'); if(!area)return;
    area.innerHTML='<div class="v4-stress">'
      +'<div class="v4-stress-grid">'
      + items.map(x=>'<div class="v4-stress-item"><div class="k">'+x[0]+'</div><div class="t">'+x[1]+'</div></div>').join('')
      +'</div>'
      +'<div class="v4-stress-rule">'
      +'<div><b>THINK · 30 SEC</b><span>Which variable would most change your verdict?</span></div>'
      +'<div><b>PAIR · 60 SEC</b><span>Swap variables. Argue against your partner’s verdict.</span></div>'
      +'<div><b>SHARE · 30 SEC</b><span>Which decision survived — and why?</span></div>'
      +'</div>'
      +'<div class="v4-stress-principle">If no plausible change can move the verdict, the boundary is probably not real.</div>'
      +'</div>';
    u.notes=is11?'Two minutes. Keep this reliability stress test focused on the assumptions behind the number: usage, repair time, operational definition, and reporting scope.':'Two minutes. Keep this slide clean and verbal: students choose one mutation surface, test the boundary, and explain whether the original decision survives.';
    slide.dataset.v5stress='1';
  }
  function patchAgile(w,d,ch){
    if(ch!=='10')return;
    const {u,slide}=get(w,d,'R18'); if(!u||!slide||slide.dataset.v5agile)return;
    heading(slide,'What survives of agile in dependable systems?','Iteration survives. Unowned ambiguity does not.','RULE 18 - Iterative, but defined and evidenced','teal');
    const area=slide.querySelector('.area'); if(!area)return;
    area.innerHTML='<div class="v4-agile">'
      +'<div class="v4-agile-lane"><div class="k">WHAT AGILE KEEPS</div><div class="big">Iteration · test-first · feedback</div><div class="small">Short cycles still help teams discover defects, refine requirements, and learn from evidence.</div></div>'
      +'<div class="v4-agile-lane" data-c="green"><div class="k">WHAT DEPENDABILITY ADDS</div><div class="big">Traceability · release control · sign-off</div><div class="small">Critical changes need explicit evidence, recorded reasoning, controlled releases, and a named accountable owner.</div></div>'
      +'<div class="v4-agile-rule"><div class="k">OPERATING RULE</div><div class="big">The real tension is not agile vs non-agile. It is iterative learning with evidence vs improvised change without it.</div></div>'
      +'</div>';
    u.notes='Keep this conceptual. No timetable or personal course logistics belong on the technical slide. Dependable development can still be iterative, but not unbounded.';
    slide.dataset.v5agile='1';
  }

  const readiness={
    '10':{
      title:'ETEC Readiness Check: What did you take from Dependable Systems?',
      sub:'Four short course-built practice items that connect today’s learning to the Information Technology academic standards. These are not official ETEC items.',
      links:[
        '<b>KLO2</b> · Problem Analysis — evidence, investigation, substantiated conclusions',
        '<b>KLO3</b> · Design / Development — choose solutions with safety and security considerations',
        '<b>KLO8</b> · Professionalism & Society — assess safety, security, legal and societal impact',
        '<b>GKU7 / SKU7.2</b> · Testing & Quality Assurance — testing standards and acceptance evidence'
      ],
      questions:[
        {q:'You inspect logs and measurements, then derive a conclusion you can defend. Which KLO are you exercising most directly?',a:['KLO2 · Problem Analysis','KLO5 · Team Work','KLO7 · Communication','KLO10 · Life-long Learning'],c:0,r:'KLO2 focuses on analysing problems and investigating evidence to reach sound, substantiated conclusions.'},
        {q:'Choosing redundancy or diversity to satisfy safety and security concerns aligns most directly with which outcome?',a:['KLO1 only','KLO3 · Design / Development','KLO6 · Project Management','KLO7 · Communication'],c:1,r:'KLO3 is about designing solutions while taking constraints such as safety and security into account.'},
        {q:'When you discuss the effect of a system decision on safety, security, and responsibility, which outcome are you strengthening?',a:['KLO8 · Computing Professionalism and Society','KLO4 · Modern Tools only','KLO5 · Team Work','KLO6 · Finance'],c:0,r:'KLO8 includes evaluating the professional, social, legal, and safety implications of computing practice.'},
        {q:'Which ETEC IT 2025 element explicitly covers testing standards and user acceptance testing?',a:['SKU7.1 · Requirements Engineering','SKU7.2 · Testing & Quality Assurance','SKU1.1 · Human-centered Design','EKU Mathematics'],c:1,r:'Within GKU7, SKU7.2 is the strand devoted to testing and quality assurance, including testing standards and user acceptance testing.'}
      ]
    },
    '11':{
      title:'ETEC Readiness Check: What did you take from Reliability Engineering?',
      sub:'Four short course-built practice items that connect today’s lesson directly to GKU7 System Paradigms in the Information Technology standards. These are not official ETEC items.',
      links:[
        '<b>GKU7</b> · System Paradigms — requirements engineering, testing and quality assurance',
        '<b>SKU7.1</b> · Requirements Engineering — functional vs non-functional requirements',
        '<b>SKU7.2</b> · Testing & Quality Assurance — testing standards and acceptance testing',
        '<b>KLO2 / KLO3</b> · analyse evidence, then define a defensible requirement or solution'
      ],
      questions:[
        {q:'“The service shall achieve 99.9% monthly availability” is best treated as what kind of requirement?',a:['Functional requirement','Non-functional requirement','Use-case actor','Data structure'],c:1,r:'Under SKU7.1, this is a quality target — therefore a non-functional requirement.'},
        {q:'What makes a 99.9% requirement testable rather than just a vague number?',a:['Adding more words only','Defining what “available” means, the observation window, and degraded-mode treatment','Writing a longer use case','Removing the measurement method'],c:1,r:'The number must be operationalised through a clear definition and a clear measurement boundary.'},
        {q:'Which SKU focuses on testing standards and on how acceptance testing should be carried out and evaluated?',a:['SKU7.1','SKU7.2','SKU1.2','SKU6.2'],c:1,r:'ETEC IT 2025 places testing standards and user acceptance testing inside SKU7.2 Testing & Quality Assurance.'},
        {q:'A supplier keeps the 99.9% target but changes the definition of “available” to include degraded service. What is the best engineering response?',a:['Nothing; the number did not change','Re-open the requirement because the meaning of the measure changed','Raise the target to 100% without analysis','Ignore the evidence'],c:1,r:'The operational meaning is part of the requirement. If that meaning changes, fit, measurement, and acceptance all need to be revisited.'}
      ]
    }
  };

  function patchETECReadiness(w,d,ch){
    const cfg=readiness[ch],{u,slide}=get(w,d,'R20'); if(!cfg||!u||!slide||slide.dataset.v5etec)return;
    addBadge(slide,'etec','ETEC Readiness');
    heading(slide,cfg.title,cfg.sub,'ETEC IT 2025 · Standards-aligned practice','sand');
    const area=slide.querySelector('.area'); if(!area)return;
    let i=0; const selected=new Array(cfg.questions.length).fill(null);
    area.innerHTML=''
      +'<div class="v4-etec">'
      +  '<aside class="v4-etec-map">'
      +    '<div class="tag">ETEC IT 2025 · READINESS LINK</div>'
      +    '<div class="score"><span id="v4Score">0</span>/4</div>'
      +    '<div class="state" id="v4State">Start the check</div>'
      +    '<div class="links">'+cfg.links.map(x=>'<div class="link">'+x+'</div>').join('')+'</div>'
      +    '<div class="source">Source: ETEC Academic Standards for Information Technology Programs 2025 v2.0 · KLOs pp.4–5 · GKU7/SKU7 pp.28–29.</div>'
      +  '</aside>'
      +  '<section class="v4-etec-q">'
      +    '<div><div class="qnum" id="v4Qnum"></div><div class="qtext" id="v4Qtext"></div></div>'
      +    '<div class="v4-etec-options" id="v4Opts"></div>'
      +    '<div><div class="v4-etec-feedback" id="v4Feedback">Choose one answer. After selection, you will see why it aligns — or does not align — with the standard.</div><div class="v4-etec-nav"><button type="button" id="v4Prev">Previous</button><button type="button" id="v4Next">Next</button></div></div>'
      +  '</section>'
      +'</div>'
      +'<div class="v4-etec-disclaimer">COURSE-BUILT PRACTICE · NOT AN OFFICIAL ETEC ITEM</div>';
    const qnum=area.querySelector('#v4Qnum'),qtext=area.querySelector('#v4Qtext'),opts=area.querySelector('#v4Opts'),fb=area.querySelector('#v4Feedback'),scoreEl=area.querySelector('#v4Score'),state=area.querySelector('#v4State'),prev=area.querySelector('#v4Prev'),next=area.querySelector('#v4Next');
    function status(){
      const score=selected.reduce((s,v,ix)=>s + (v===cfg.questions[ix].c ? 1:0),0);
      const done=selected.filter(v=>v!==null).length;
      scoreEl.textContent=String(score);
      if(done<cfg.questions.length) state.textContent='Answered '+done+' of '+cfg.questions.length;
      else if(score>=3) state.textContent='Strong readiness signal';
      else state.textContent='Revisit the missed concepts';
    }
    function render(){
      const q=cfg.questions[i];
      qnum.textContent='QUESTION '+(i+1)+' / '+cfg.questions.length;
      qtext.textContent=q.q;
      opts.innerHTML='';
      q.a.forEach((txt,j)=>{
        const b=d.createElement('button');
        b.type='button'; b.className='v4-etec-option'; b.innerHTML='<b>'+String.fromCharCode(65+j)+'</b> · '+esc(txt);
        if(selected[i]===j) b.setAttribute('aria-pressed','true');
        b.onclick=()=>{
          selected[i]=j;
          [...opts.children].forEach((x,k)=>{x.classList.toggle('correct',k===q.c);x.classList.toggle('wrong',k===j && j!==q.c);x.setAttribute('aria-pressed',k===j?'true':'false');});
          fb.innerHTML=(j===q.c?'<b style="color:var(--green)">Correct.</b> ':'<b style="color:var(--mag)">Not quite.</b> ')+esc(q.r);
          status();
        };
        opts.appendChild(b);
      });
      if(selected[i]!==null){
        [...opts.children].forEach((x,k)=>{x.classList.toggle('correct',k===q.c);x.classList.toggle('wrong',k===selected[i] && selected[i]!==q.c);});
        fb.innerHTML=(selected[i]===q.c?'<b style="color:var(--green)">Correct.</b> ':'<b style="color:var(--mag)">Not quite.</b> ')+esc(q.r);
      } else {
        fb.textContent='Choose one answer. After selection, you will see why it aligns — or does not align — with the standard.';
      }
      prev.disabled=i===0; next.disabled=i===cfg.questions.length-1; status();
    }
    prev.onclick=()=>{if(i>0){i--;render();}};
    next.onclick=()=>{if(i<cfg.questions.length-1){i++;render();}};
    u.learn='Connect today’s lesson to ETEC-aligned readiness targets through four short practice items.';
    u.task='Answer all four. Use 3/4 or above as a readiness signal, then revisit any concept you missed.';
    u.notes='State clearly that this is course-built, standards-aligned practice — not an official ETEC item. Chapter 10 aligns mainly through KLO2, KLO3, KLO8, and testing/QA evidence. Chapter 11 aligns directly with GKU7, SKU7.1, and SKU7.2.';
    render(); slide.dataset.v5etec='1';
  }

  function autoType(d){
    d.querySelectorAll('.slide').forEach(slide=>{
      slide.classList.remove('v4-roomy','v4-normal','v4-tight','v4-overflow');
      const area=slide.querySelector('.area'); if(!area)return;
      const text=(area.innerText||'').replace(/\s+/g,' ').trim();
      const majors=[...area.children].filter(x=>d.defaultView.getComputedStyle(x).display!=='none').length;
      const special=area.querySelector('.v4-etec,.v4-stress,.v4-agile,.v4-ai-emphasis,.ai-learning,.ready-shell,.practice-map,.vflow,.splitfig,.cov,.pm,.qz,.bridge');
      if(special){ slide.classList.add('v4-normal'); }
      else if(text.length<240 && majors<=2){ slide.classList.add('v4-roomy'); }
      else if(text.length<520 && majors<=3){ slide.classList.add('v4-roomy'); }
      else if(text.length<780 && majors<=5){ slide.classList.add('v4-normal'); }
      else { slide.classList.add('v4-tight'); }
      requestAnimationFrame(()=>{ if(area.scrollHeight>area.clientHeight+6){ slide.classList.remove('v4-roomy','v4-normal'); slide.classList.add('v4-tight','v4-overflow'); } });
    });
  }

  function apply(frame,ch){
    const w=frame?.contentWindow, d=w?.document; if(!w||!d||!d.getElementById('stage')||!Array.isArray(w.U)) return false;
    if(d.documentElement.dataset.iscarbVisualV5==='1') return true;
    addCss(d); simplifyStaticCards(d); patchAI(w,d,ch); patchStress(w,d,ch); patchAgile(w,d,ch); patchETECReadiness(w,d,ch); autoType(d); setTimeout(()=>autoType(d),160); d.documentElement.dataset.iscarbVisualV5='1'; return true;
  }
  window.ISCARBVisualV4={apply};
})();