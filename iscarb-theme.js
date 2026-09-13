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

  function addHeroTheme(){
    // The CPIT landing page already has its own carefully composed camel/fortress
    // hero. Re-theming that hero duplicates the image and breaks its layout.
    if(isHome) return;
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
    // Sticky return navigation is useful inside lecture/FBR workspaces only.
    // Do not place it on top-level public pages or the landing page.
    if(!isLearningDetail||isHub||isHome||document.querySelector('.iscarb-hub-btn')) return;
    const a=document.createElement('a');
    a.className='iscarb-hub-btn';
    a.href=atRoot('iscarb.html');
    a.setAttribute('aria-label','Back to ISCARB lecture hub');
    a.innerHTML='<span>⌂ Back to Hub<small>ISCARB · CPIT-455</small></span>';
    document.body.appendChild(a);
  }

  function addSaveBadge(){
    // Only FBR pages expose the draft save state.
    if(!isFbr) return;
    const saved=document.getElementById('saved');
    const storage=document.getElementById('storage');
    if(!saved&&!storage) return;
    const existing=document.querySelector('.iscarb-save-badge');
    if(existing) return;
    const badge=document.createElement('span');
    badge.className='iscarb-save-badge';
    badge.setAttribute('role','status');
    badge.setAttribute('aria-live','polite');
    badge.textContent='Local draft enabled';
    (saved||storage).insertAdjacentElement('afterend',badge);

    const update=()=>{
      const txt=((saved?.textContent||'')+' '+(storage?.textContent||'')).toLowerCase();
      badge.classList.remove('saving','warn');
      if(txt.includes('unavailable')||txt.includes('could not')){
        badge.textContent='Local save unavailable';
        badge.classList.add('warn');
      }else if(txt.includes('unsaved')||txt.includes('saving')){
        badge.textContent='Saving locally…';
        badge.classList.add('saving');
      }else if(txt.includes('saved')){
        badge.textContent='✓ Draft saved locally';
        badge.title=saved?.textContent||'Saved locally in this browser';
      }else{
        badge.textContent='Local draft enabled';
      }
    };
    update();
    if(saved)new MutationObserver(update).observe(saved,{childList:true,characterData:true,subtree:true});
    if(storage)new MutationObserver(update).observe(storage,{childList:true,characterData:true,subtree:true});
  }

  function addA11yHint(){
    if(!isPresenter) return;
    document.documentElement.setAttribute('data-iscarb-presenter','1');
  }

  function boot(){
    document.documentElement.toggleAttribute('data-iscarb-home',isHome);
    addHeroTheme();
    addMethodologyNav();
    addHubButton();
    addSaveBadge();
    addA11yHint();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
