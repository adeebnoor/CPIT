/* ISCARB In-Class Final Polish v4 */
(function(){
  const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  function get(w,d,key){const idx=w.U.findIndex(u=>u&&u.k===key);return {idx,u:idx>=0?w.U[idx]:null,slide:idx>=0?d.querySelector('.slide[data-i="'+idx+'"]'):null}}
  function heading(slide,title,sub,rule,accent){
    if(!slide)return;const h=slide.querySelector('h1'),s=slide.querySelector('.sub'),p=slide.querySelector('.pill');
    if(h&&title)h.textContent=title;if(s&&sub!=null)s.textContent=sub;
    if(p&&rule){p.textContent=rule;if(accent){p.style.borderColor='var(--'+accent+')';p.style.color='var(--'+accent+')'}}
  }
  function addCss(d){if(d.getElementById('iscarb-v4-css'))return;const l=d.createElement('link');l.id='iscarb-v4-css';l.rel='stylesheet';l.href='inclass-visual-v4.css?v=20260912-visual4';d.head.appendChild(l)}

  function simplifyStaticCards(d){
    d.querySelectorAll('.card:has(.lead)').forEach(card=>{
      if(card.querySelector('textarea,.picker,button'))return;
      card.querySelectorAll('.txt,.src,.foldbar').forEach(el=>el.style.display='none');
    });
  }

  function patchStress(w,d,ch){
    const {u,slide}=get(w,d,'R13');if(!u||!slide||slide.dataset.v4stress)return;
    const is11=ch==='11';
    heading(slide,is11?'What change would break your number?':'What change would break your solution?',is11?'A robust reliability number exposes the assumption that could make it wrong.':'A robust decision names the variable that could reverse it.','RULE 13 - Breaking variable','sand');
    const area=slide.querySelector('.area');if(!area)return;
    const items=is11?[
      ['USAGE','The operational profile changes; the measured system no longer represents actual use.'],
      ['REPAIR','Repair time triples; availability falls even though failure frequency does not.'],
      ['DEFINITION','The vendor counts degraded service as available; your original definition did not.'],
      ['REGULATION','The figure must now be reported per service rather than for the whole system.']
    ]:[
      ['STAFFING','One qualified reviewer becomes one reviewer plus a trainee.'],
      ['DEADLINE','The production window closes tonight; reverting costs a full day of supply.'],
      ['DATA','Commissioning evidence comes from a different firmware baseline.'],
      ['REGULATION','The regulator requires new evidence before unattended operation.']
    ];
    area.innerHTML='<div class="v4-stress">'+
      '<div class="v4-stress-grid">'+items.map(x=>'<div class="v4-stress-item"><div class="k">'+x[0]+'</div><div class="t">'+x[1]+'</div></div>').join('')+'</div>'+
      '<div class="v4-stress-rule"><div><b>THINK · 30 SEC</b><span>Which variable would most change your verdict?</span></div><div><b>PAIR · 60 SEC</b><span>Swap variables. Argue against your partner’s verdict.</span></div><div><b>SHARE · 30 SEC</b><span>Which decision survived — and why?</span></div></div>'+
      '<div class="v4-stress-principle">If no plausible change can move the verdict, the boundary is probably not real.</div>'+ 
    '</div>';
    u.notes=is11?'Two minutes. Keep the reliability stress test focused on the assumptions behind the number: usage, repair time, operational definition and reporting scope. The embedded recall item is removed from the live slide so students can test the number itself.':'Two minutes. Keep this slide clean: one mutation surface only. The previous embedded recall question was removed from the live slide because it competed with the stress-test objective. Ask students to choose one variable, test the original boundary, and explain whether the verdict survives.';
    slide.dataset.v4stress='1';
  }

  function patchAgile(w,d,ch){
    if(ch!=='10')return;
    const {u,slide}=get(w,d,'R18');if(!u||!slide||slide.dataset.v4agile)return;
    u.title='What survives of agile in dependable systems?';
    u.sub='Iteration survives. Unowned ambiguity does not.';
    u.rule='RULE 18 - Iterative, but defined and evidenced';
    u.learn='Explain which agile practices remain useful when certification, traceability, and accountable evidence are required.';
    u.task='Name one agile practice you would keep and one assurance discipline you would add.';
    u.notes='Keep this conceptual. Do not show course timetable, contact information, or next-session logistics on the technical slide. Dependable development may remain iterative and test-first, but it needs explicit evidence, traceability, rollback/release controls, and accountable sign-off.';
    heading(slide,u.title,u.sub,u.rule,'teal');
    const area=slide.querySelector('.area');if(!area)return;
    area.innerHTML='<div class="v4-agile">'+
      '<div class="v4-agile-lane"><div class="k">WHAT AGILE KEEPS</div><div class="big">Iteration · test-first · feedback</div><div class="small">Short cycles still help teams discover defects, refine requirements, and learn from evidence.</div></div>'+
      '<div class="v4-agile-lane" data-c="green"><div class="k">WHAT DEPENDABILITY ADDS</div><div class="big">Traceability · release control · sign-off</div><div class="small">Critical changes need recorded evidence, defined rollback conditions, controlled releases, and a named owner.</div></div>'+
      '<div class="v4-agile-rule"><div class="k">OPERATING RULE</div><div class="big">The tension is not agile vs. non-agile. It is iterative learning with evidence vs. improvised change without it.</div></div>'+
    '</div>';
    slide.dataset.v4agile='1';
  }

  const readiness={
    '10':{
      title:'جاهزية / ETEC: ماذا أخذت من Dependable Systems؟',
      sub:'اختبار مراجعة قصير يربط مفاهيم اليوم بمعايير تقنية المعلومات الوطنية. هذه أسئلة مقرر مبنية على المعايير وليست أسئلة رسمية من الهيئة.',
      links:[
        '<b>KLO2</b> · Problem Analysis — evidence, investigation, substantiated conclusions',
        '<b>KLO3</b> · Design / Development — choose solutions with safety and security considerations',
        '<b>KLO8</b> · Professionalism & Society — assess safety, security, legal and societal impact',
        '<b>GKU7 / SKU7.2</b> · Testing & Quality Assurance — testing standards and acceptance evidence'
      ],
      questions:[
        {q:'أنت تراجع logs وقياسات وتستخلص منها استنتاجًا يمكن الدفاع عنه. أي KLO تمارسه بشكل مباشر؟',a:['KLO2 · Problem Analysis','KLO5 · Team Work','KLO7 · Communication','KLO10 · Life-long Learning'],c:0,r:'KLO2 يطلب تحليل المشكلات والتحقيق بالبيانات للوصول إلى استنتاجات صحيحة ومدعومة.'},
        {q:'اختيار redundancy أو diversity لتلبية متطلبات السلامة والأمن يرتبط أكثر بأي مخرج؟',a:['KLO1 فقط','KLO3 · Design / Development','KLO6 · Project Management','KLO7 · Communication'],c:1,r:'KLO3 يركز على تصميم حلول لمشكلات حوسبية مع مراعاة السلامة والأمن وغيرها من القيود.'},
        {q:'عندما تناقش أثر قرار النظام على السلامة والأمن والمسؤولية المهنية، فأنت تقوي أي مخرج؟',a:['KLO8 · Computing Professionalism and Society','KLO4 · Modern Tools فقط','KLO5 · Team Work','KLO6 · Finance'],c:0,r:'KLO8 يشمل تقييم آثار الممارسة المهنية على السلامة والأمن والأطر القانونية والمجتمع.'},
        {q:'أي جزء من معيار ETEC IT 2025 يغطي testing standards وuser acceptance testing؟',a:['SKU7.1 · Requirements Engineering','SKU7.2 · Testing & Quality Assurance','SKU1.1 · Human-centered Design','EKU Mathematics'],c:1,r:'GKU7 هو System Paradigms، وSKU7.2 مخصص للاختبار وضمان الجودة ويشمل testing standards وacceptance testing.'}
      ]
    },
    '11':{
      title:'جاهزية / ETEC: ماذا أخذت من Reliability Engineering؟',
      sub:'اختبار مراجعة قصير يربط درس اليوم مباشرة بـ GKU7 System Paradigms في معيار ETEC IT 2025. هذه أسئلة مقرر وليست أسئلة رسمية من الهيئة.',
      links:[
        '<b>GKU7</b> · System Paradigms — requirements engineering, testing and quality assurance',
        '<b>SKU7.1</b> · Requirements Engineering — functional vs. non-functional requirements',
        '<b>SKU7.2</b> · Testing & Quality Assurance — testing standards and acceptance testing',
        '<b>KLO2 / KLO3</b> · analyze evidence, then design a defensible requirement/solution'
      ],
      questions:[
        {q:'“The service shall achieve 99.9% monthly availability” هو مثال أقرب إلى ماذا؟',a:['Functional requirement','Non-functional requirement','Use case actor','Data structure'],c:1,r:'ETEC SKU7.1 يتضمن التمييز بين functional وnon-functional requirements؛ availability target هو quality/non-functional requirement.'},
        {q:'ما الذي يجعل 99.9% requirement قابلًا للفحص بدل أن يكون رقمًا غامضًا؟',a:['زيادة عدد الكلمات فقط','تحديد معنى available + observation window + degraded mode','كتابة use case أطول','إزالة طريقة القياس'],c:1,r:'الرقم يحتاج تعريفًا تشغيليًا وحدود قياس واضحة حتى يصبح requirement يمكن التحقق منه.'},
        {q:'أي SKU يركز على testing standards وطرق تنفيذ وتقييم acceptance test؟',a:['SKU7.1','SKU7.2','SKU1.2','SKU6.2'],c:1,r:'ETEC IT 2025 يضع testing standards وuser acceptance testing ضمن SKU7.2 Testing and Quality Assurance.'},
        {q:'المورّد أبقى الرقم 99.9% لكنه غيّر تعريف “available” ليشمل degraded service. ما القرار الهندسي الأفضل؟',a:['لا شيء؛ الرقم لم يتغير','إعادة فتح requirement لأن معنى القياس تغير','رفع الرقم إلى 100% دون تحليل','إلغاء evidence'],c:1,r:'المعنى التشغيلي جزء من صلاحية requirement. إذا تغير التعريف، يجب إعادة التحقق من fit والقياس والقبول.'}
      ]
    }
  };

  function patchETECReadiness(w,d,ch){
    const cfg=readiness[ch],{u,slide}=get(w,d,'R20');if(!cfg||!u||!slide||slide.dataset.v4etec)return;
    u.title=cfg.title;u.sub=cfg.sub;u.rule='ETEC IT 2025 · READINESS PRACTICE';u.learn='Connect today’s disciplinary learning to ETEC IT 2025 readiness targets and demonstrate it on four course-built items.';
    u.task='Answer all four. Use 3/4 as a readiness signal, then revisit the concept behind any missed item.';
    u.notes='This is the Jaheziah/ETEC readiness link the course needs. State explicitly that these are course-built standards-aligned practice items, not official ETEC questions. The authoritative source is ETEC Academic Standards for Information Technology Programs 2025 v2.0. Chapter 11 has a direct content link to GKU7/SKU7.1/SKU7.2. Chapter 10 is supporting readiness through KLO2, KLO3, KLO8 and testing/QA evidence; the IT standard does not name a standalone “Dependability” SKU.';
    heading(slide,u.title,u.sub,u.rule,'sand');
    const area=slide.querySelector('.area');if(!area)return;
    let i=0,score=0,answered=new Array(cfg.questions.length).fill(false);
    area.innerHTML='<div class="v4-etec">'+
      '<aside class="v4-etec-map"><div class="tag">ETEC IT 2025 · READINESS LINK</div><div class="score"><span id="v4Score">0</span>/4</div><div class="state" id="v4State">ابدأ الاختبار</div><div class="links">'+cfg.links.map(x=>'<div class="link">'+x+'</div>').join('')+'</div><div class="source">المصدر: ETEC Academic Standards for Information Technology Programs 2025 v2.0 · KLOs pp.4–5 · GKU7/SKU7 pp.28–29.</div></aside>'+
      '<section class="v4-etec-q"><div><div class="qnum" id="v4Qnum"></div><div class="qtext" id="v4Qtext"></div></div><div class="v4-etec-options" id="v4Opts"></div><div><div class="v4-etec-feedback" id="v4Feedback">اختر إجابة واحدة. بعد الاختيار ستظهر لك العلاقة بالمعيار.</div><div class="v4-etec-nav"><button type="button" id="v4Prev">السابق</button><button type="button" id="v4Next">التالي</button></div></div></section>'+ 
    '</div><div class="v4-etec-disclaimer">COURSE-BUILT PRACTICE · NOT AN OFFICIAL ETEC ITEM</div>';
    const qnum=area.querySelector('#v4Qnum'),qtext=area.querySelector('#v4Qtext'),opts=area.querySelector('#v4Opts'),fb=area.querySelector('#v4Feedback'),scoreEl=area.querySelector('#v4Score'),state=area.querySelector('#v4State'),prev=area.querySelector('#v4Prev'),next=area.querySelector('#v4Next');
    const selected=new Array(cfg.questions.length).fill(null);
    function status(){score=0;selected.forEach((v,k)=>{if(v===cfg.questions[k].c)score++});scoreEl.textContent=score;const done=selected.filter(v=>v!==null).length;if(done<4)state.textContent='أجبت '+done+' من 4';else if(score>=3)state.textContent='جاهزية جيدة · راجع أي خطأ';else state.textContent='تحتاج مراجعة قبل After-Class'}
    function render(){const q=cfg.questions[i];qnum.textContent='QUESTION '+(i+1)+' / '+cfg.questions.length;qtext.textContent=q.q;opts.innerHTML='';q.a.forEach((txt,j)=>{const b=d.createElement('button');b.type='button';b.className='v4-etec-option';b.innerHTML='<b>'+String.fromCharCode(65+j)+'</b> · '+esc(txt);if(selected[i]===j)b.setAttribute('aria-pressed','true');b.onclick=()=>{selected[i]=j;answered[i]=true;[...opts.children].forEach((x,k)=>{x.classList.toggle('correct',k===q.c);x.classList.toggle('wrong',k===j&&j!==q.c);x.setAttribute('aria-pressed',k===j?'true':'false')});fb.innerHTML=(j===q.c?'<b style="color:var(--green)">صحيح.</b> ':'<b style="color:var(--mag)">راجع الفكرة.</b> ')+esc(q.r);status()};opts.appendChild(b)});if(selected[i]!==null){[...opts.children].forEach((x,k)=>{x.classList.toggle('correct',k===q.c);x.classList.toggle('wrong',k===selected[i]&&selected[i]!==q.c)});fb.innerHTML=(selected[i]===q.c?'<b style="color:var(--green)">صحيح.</b> ':'<b style="color:var(--mag)">راجع الفكرة.</b> ')+esc(q.r)}else fb.textContent='اختر إجابة واحدة. بعد الاختيار ستظهر لك العلاقة بالمعيار.';prev.disabled=i===0;next.disabled=i===cfg.questions.length-1;status()}
    prev.onclick=()=>{if(i>0){i--;render()}};next.onclick=()=>{if(i<cfg.questions.length-1){i++;render()}};render();
    slide.dataset.v4etec='1';
  }

  function autoType(d){
    d.querySelectorAll('.slide').forEach(slide=>{
      slide.classList.remove('v4-roomy','v4-normal','v4-tight','v4-overflow');
      const area=slide.querySelector('.area');if(!area)return;
      const text=(area.innerText||'').replace(/\s+/g,' ').trim();
      const majors=[...area.children].filter(x=>d.defaultView.getComputedStyle(x).display!=='none').length;
      const special=area.querySelector('.v4-etec,.v4-stress,.v4-agile,.ai-learning,.ready-shell,.practice-map,.vflow,.splitfig,.cov,.pm,.qz,.bridge');
      if(special){slide.classList.add('v4-normal')}else if(text.length<360&&majors<=3){slide.classList.add('v4-roomy')}else if(text.length<760&&majors<=5){slide.classList.add('v4-normal')}else{slide.classList.add('v4-tight')}
      requestAnimationFrame(()=>{if(area.scrollHeight>area.clientHeight+6){slide.classList.remove('v4-roomy','v4-normal');slide.classList.add('v4-tight','v4-overflow')}});
    });
  }

  function apply(frame,ch){
    const w=frame?.contentWindow,d=w?.document;if(!w||!d||!d.getElementById('stage')||!Array.isArray(w.U))return false;
    if(d.documentElement.dataset.iscarbVisualV4==='1')return true;
    addCss(d);simplifyStaticCards(d);patchStress(w,d,ch);patchAgile(w,d,ch);patchETECReadiness(w,d,ch);autoType(d);
    setTimeout(()=>autoType(d),120);d.documentElement.dataset.iscarbVisualV4='1';return true;
  }
  window.ISCARBVisualV4={apply};
})();