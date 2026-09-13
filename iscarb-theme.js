(()=>{
  const script=document.currentScript;
  const root=script?.src?new URL('.',script.src):new URL('./',location.href);
  const atRoot=(name)=>new URL(name,root).href;
  const path=location.pathname.toLowerCase();
  const file=(path.split('/').pop()||'').toLowerCase();
  const isHome=file===''||file==='index.html';
  const isHub=file==='iscarb.html';
  const isPresenter=/inclass-presenter\.html$|faculty-presenter\.html$/i.test(path);
  const isFbr=/fbr-submission\.html$|fbr-student-assignment\.html$/i.test(path);
  const isLearningDetail=isPresenter||isFbr;
  const publicHeroPages=new Set(['iscarb.html','student-guide.html','course-resources.html','methodology.html','download-stats.html','iscarb-students.html']);

  function addHeroTheme(){
    // Only top-level public pages receive the shared hero treatment.
    // Never touch lecture-internal .hero elements: Chapter 10/11 already own
    // their visual grammar and the static decks use .hero for slide content.
    if(isHome||!publicHeroPages.has(file)) return;
    const hero=document.querySelector('.hero');
    if(hero) hero.classList.add('iscarb-themed-hero');
  }

  function addMethodologyNav(){
    const navs=[...document.querySelectorAll('nav,.nav')];
    navs.forEach(nav=>{
      if(nav.querySelector('a[href*="methodology.html"]')) return;
      const a=document.createElement('a');
      a.href=atRoot('methodology.html');
      a.textContent='The Methodology / For Faculty';
      a.className='iscarb-methodology-nav';
      a.setAttribute('aria-label','ISCARB methodology and faculty adoption guide');
      nav.appendChild(a);
    });
  }

  function addHubButton(){
    if(!isLearningDetail||isHub||isHome||document.querySelector('.iscarb-hub-btn')) return;
    const a=document.createElement('a');
    a.className='iscarb-hub-btn';
    a.href=atRoot('iscarb.html');
    a.setAttribute('aria-label','Back to ISCARB lecture hub');
    a.innerHTML='<span>⌂ Back to Hub<small>ISCARB · CPIT-455</small></span>';
    if(isFbr){a.classList.add("iscarb-inline-hub");document.body.prepend(a)}else{document.body.appendChild(a)}
  }

  function addSaveBadge(){
    if(!isFbr) return;
    const saved=document.getElementById('saved');
    const storage=document.getElementById('storage');
    if(!saved&&!storage||document.querySelector('.iscarb-save-badge')) return;
    const badge=document.createElement('span');
    badge.className='iscarb-save-badge';
    badge.setAttribute('role','status');
    badge.setAttribute('aria-live','polite');
    badge.textContent='Local draft enabled';
    (saved||storage).insertAdjacentElement('afterend',badge);
    const update=()=>{
      const txt=((saved?.textContent||'')+' '+(storage?.textContent||'')).toLowerCase();
      badge.classList.remove('saving','warn');
      if(txt.includes('unavailable')||txt.includes('could not')){badge.textContent='Local save unavailable';badge.classList.add('warn');}
      else if(txt.includes('unsaved')||txt.includes('saving')){badge.textContent='Saving locally…';badge.classList.add('saving');}
      else if(txt.includes('saved')){badge.textContent='✓ Draft saved locally';badge.title=saved?.textContent||'Saved locally in this browser';}
      else badge.textContent='Local draft enabled';
    };
    update();
    if(saved)new MutationObserver(update).observe(saved,{childList:true,characterData:true,subtree:true});
    if(storage)new MutationObserver(update).observe(storage,{childList:true,characterData:true,subtree:true});
  }

  function addA11yHint(){
    if(isPresenter) document.documentElement.setAttribute('data-iscarb-presenter','1');
  }

  const STATIC_META={
    '12':{lead:'Safety',accent:'Engineering',tagline:'Chapter 12: from hazards to a defended safety decision.',source:'Sommerville, <i>Software Engineering</i>, Chapter 12 &nbsp;|&nbsp; Prof. Adeeb Noor',flow:'CRISIS → HAZARD MAP → TRADE-OFF → EVIDENCE → VERDICT',lecture:'03'},
    '13':{lead:'Security',accent:'Engineering',tagline:'Chapter 13: from threats and assets to a defended security decision.',source:'Sommerville, <i>Software Engineering</i>, Chapter 13 &nbsp;|&nbsp; Prof. Adeeb Noor',flow:'CRISIS → THREAT MAP → TRADE-OFF → EVIDENCE → VERDICT',lecture:'04'},
    '14':{lead:'Resilience',accent:'Engineering',tagline:'Chapter 14: from disruption to a defended resilience decision.',source:'Sommerville, <i>Software Engineering</i>, Chapter 14 &nbsp;|&nbsp; Prof. Adeeb Noor',flow:'CRISIS → DISRUPTION MAP → TRADE-OFF → EVIDENCE → VERDICT',lecture:'05'},
    '15':{lead:'Software',accent:'Reuse',tagline:'Chapter 15: from reuse options to a defended engineering decision.',source:'Sommerville, <i>Software Engineering</i>, Chapter 15 &nbsp;|&nbsp; Prof. Adeeb Noor',flow:'CRISIS → FIT MAP → TRADE-OFF → EVIDENCE → VERDICT',lecture:'06'},
    '16':{lead:'Component-Based',accent:'Software Engineering',tagline:'Chapter 16: from components and interfaces to a defended composition decision.',source:'Sommerville, <i>Software Engineering</i>, Chapter 16 &nbsp;|&nbsp; Prof. Adeeb Noor',flow:'CRISIS → INTERFACE MAP → TRADE-OFF → EVIDENCE → VERDICT',lecture:'07'},
    '17':{lead:'Distributed',accent:'Software Engineering',tagline:'Chapter 17: from distribution choices to a defended architecture decision.',source:'Sommerville, <i>Software Engineering</i>, Chapter 17 &nbsp;|&nbsp; Prof. Adeeb Noor',flow:'CRISIS → DISTRIBUTION MAP → TRADE-OFF → EVIDENCE → VERDICT',lecture:'08'},
    '20':{lead:'Systems of',accent:'Systems',tagline:'Chapter 20: from emergence and independence to a defended systems decision.',source:'Sommerville, <i>Software Engineering</i>, Chapter 20 &nbsp;|&nbsp; Prof. Adeeb Noor',flow:'CRISIS → SYSTEM MAP → TRADE-OFF → EVIDENCE → VERDICT',lecture:'09'}
  };

  function harmonizeStaticPresenter(){
    if(!isPresenter) return;
    const ch=new URLSearchParams(location.search).get('chapter')||'';
    const meta=STATIC_META[ch];
    if(!meta) return; // Chapter 10/11 already use the full native engine.
    const frame=document.getElementById('lecture');
    if(!frame) return;
    let tries=0;
    const apply=()=>{
      tries++;
      let w,d;
      try{w=frame.contentWindow;d=w?.document;}catch(e){return false;}
      if(!w||!d||!d.getElementById('stage')) return false;
      if(Array.isArray(w.U)) return true;
      const slides=[...d.querySelectorAll('#stage .slide')];
      if(!slides.length) return false;
      if(d.documentElement.dataset.iscarbStaticHarmonized==='1') return true;

      const style=d.createElement('style');
      style.id='iscarb-static-harmonizer';
      style.textContent=`
        #rail{display:none!important}
        #iscPhaseRail{position:absolute;top:0;left:0;right:0;height:3px;display:grid;grid-template-columns:repeat(4,1fr);gap:2px;z-index:8}
        #iscPhaseRail i{display:block;background:#221C29;position:relative;overflow:hidden}#iscPhaseRail i::after{content:"";position:absolute;inset:0;background:#F0189A;transform:scaleX(0);transform-origin:left;transition:transform .25s ease}#iscPhaseRail i.done::after{transform:scaleX(1);background:#6F665F}#iscPhaseRail i.now::after{transform:scaleX(1);background:#F0189A}
        .slide{padding:22px 36px 8px!important}.slide:not(.isc-title-slide) .top h1{font-size:33px!important;line-height:1.08!important;margin-top:12px!important;max-width:22ch!important}.slide:not(.isc-title-slide) .top p{font-size:15px!important;line-height:1.36!important;max-width:74ch!important}.slide:not(.isc-title-slide) .ey{font-size:11.5px!important}.slide:not(.isc-title-slide) .pill{font-size:12.5px!important;padding:7px 19px!important;border-radius:9px!important}
        .slide:not(.isc-title-slide) .card{border-radius:14px!important;padding:15px 17px!important;gap:8px!important;background:#15121C!important}.slide:not(.isc-title-slide) .card .lab{font-size:12.5px!important}.slide:not(.isc-title-slide) .card .txt{font-size:15px!important;line-height:1.4!important;font-weight:500!important}.slide:not(.isc-title-slide) .card .sm{font-size:13.4px!important;line-height:1.4!important}.slide:not(.isc-title-slide) .wide{border-radius:14px!important;background:#15121C!important}.slide:not(.isc-title-slide) .wide .wlead{font-size:24px!important}.slide:not(.isc-title-slide) .wide .wtxt{font-size:15px!important}.slide:not(.isc-title-slide) .statement{font-size:27px!important}
        .isc-title-slide .top{display:grid!important;grid-template-columns:minmax(0,1fr) auto!important}.isc-title-slide .area{justify-content:center!important}.isc-cover{display:grid;grid-template-columns:1.02fr .98fr;gap:40px;align-items:center;width:100%;flex:1;min-height:0}.isc-cover h2{font-family:Poppins,"Segoe UI",sans-serif;font-weight:700;font-size:54px;line-height:1.02;margin:0;letter-spacing:-.022em}.isc-cover h2 em{font-style:normal;color:#DDB27E;display:block}.isc-cover .st{font-size:18px;color:#A99E95;margin:14px 0 0;line-height:1.4;max-width:44ch}.isc-brandimg{border-radius:16px;overflow:hidden;border:1px solid #2C2534;box-shadow:0 0 50px -18px #F0189A}.isc-brandimg img{display:block;width:100%;height:auto}.isc-srcbox{border:1.5px solid #4FC6CB;border-radius:13px;padding:14px 19px;margin-top:22px;width:fit-content}.isc-srcbox .l{font-size:11.5px;font-weight:700;color:#4FC6CB;letter-spacing:.06em;text-align:center}.isc-srcbox .v{font-size:15px;margin-top:5px}.isc-flowline{font-size:12.5px;font-weight:700;color:#DDB27E;letter-spacing:.055em;margin-top:20px}.isc-keys{display:flex;flex-wrap:wrap;gap:7px;margin-top:18px}.isc-keys span{font-size:11px;border:1px solid #2C2534;border-radius:7px;padding:5px 9px;color:#6F665F;background:#15121C}.isc-keys b{color:#DDB27E;font-weight:600}
        #bar{height:78px!important;background:#0C0A11!important;border-top:1px solid #2C2534!important;padding:12px 36px!important;display:grid!important;grid-template-columns:150px 1fr auto!important;gap:20px!important;align-items:center!important}#bar button{display:none!important}.isc-bar-meta .tb{font-size:11.5px;font-weight:700;color:#DDB27E;letter-spacing:.05em}.isc-bar-meta .yt{font-size:11.5px;font-weight:700;color:#F0189A;letter-spacing:.05em;margin-top:6px}.isc-bar-task{font-size:14.5px;line-height:1.35}.isc-bar-prog{display:flex;align-items:center;gap:8px;font-size:10.5px;color:#6F665F;white-space:nowrap}.isc-bar-prog .track{width:64px;height:4px;border-radius:3px;background:#2C2534;overflow:hidden}.isc-bar-prog .track i{display:block;height:100%;background:#DDB27E;width:0;transition:width .25s ease}
      `;
      d.head.appendChild(style);

      const phase=d.createElement('div');phase.id='iscPhaseRail';phase.innerHTML='<i></i><i></i><i></i><i></i>';d.getElementById('stage').appendChild(phase);
      const first=slides[0],top=first.querySelector('.top'),area=first.querySelector('.area');
      if(top&&area){
        first.classList.add('isc-title-slide');
        top.innerHTML='<div class="ey" style="color:#F0189A">CPIT-455 / LECTURE '+meta.lecture+'</div><div class="count"></div>';
        area.innerHTML='<div class="isc-cover"><div><h2>'+meta.lead+'<em>'+meta.accent+'</em></h2><p class="st">'+meta.tagline+'</p><div class="isc-srcbox"><div class="l">PRIMARY SOURCE</div><div class="v">'+meta.source+'</div></div><div class="isc-flowline">'+meta.flow+'</div><div class="isc-keys"><span><b>← / →</b> navigate</span><span><b>Notes</b> instructor notes</span><span><b>Present</b> full screen</span></div></div><div class="isc-brandimg"><img src="'+atRoot('iscarb-studio/app/static/hero_user_original.png')+'" alt="ISCARB Saudi heritage identity"></div></div>';
      }

      const bar=d.getElementById('bar');
      if(bar){
        const metaBox=d.createElement('div');metaBox.className='isc-bar-meta';metaBox.innerHTML='<div class="tb">TIMEBOX</div><div class="yt">YOUR TASK</div>';
        const task=d.createElement('div');task.className='isc-bar-task';
        const prog=d.createElement('div');prog.className='isc-bar-prog';prog.innerHTML='<span class="isc-pnum">1/'+slides.length+'</span><span class="track"><i></i></span>';
        bar.append(metaBox,task,prog);
        const sync=()=>{
          let idx=slides.findIndex(s=>s.classList.contains('on'));if(idx<0)idx=0;
          task.textContent=idx===0?'Sit down. The engineering decision starts in ninety seconds.':idx===1?'Make a bounded judgment before more evidence arrives.':'Extract the mechanism. Name the boundary. Defend what evidence would change the verdict.';
          const pn=prog.querySelector('.isc-pnum'),fill=prog.querySelector('.track i');if(pn)pn.textContent=(idx+1)+'/'+slides.length;if(fill)fill.style.width=((idx+1)/slides.length*100)+'%';
          const p=Math.min(3,Math.floor(idx/Math.max(1,Math.ceil(slides.length/4))));[...phase.children].forEach((x,i)=>{x.classList.toggle('done',i<p);x.classList.toggle('now',i===p)});
        };
        sync();new MutationObserver(sync).observe(d.getElementById('stage'),{subtree:true,attributes:true,attributeFilter:['class']});
      }
      d.documentElement.dataset.iscarbStaticHarmonized='1';
      return true;
    };
    frame.addEventListener('load',()=>setTimeout(apply,80));
    const timer=setInterval(()=>{if(apply()||++tries>30)clearInterval(timer)},180);
  }

  function boot(){
    document.documentElement.toggleAttribute('data-iscarb-home',isHome);
    addHeroTheme();
    addMethodologyNav();
    addHubButton();
    addSaveBadge();
    addA11yHint();
    harmonizeStaticPresenter();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
