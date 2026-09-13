/* One progressive-enhancement controller for every chapter. No remote dependency. */
(()=>{'use strict';
const root=document.documentElement,body=document.body,slides=[...document.querySelectorAll('.lesson-slide')],byId=id=>document.getElementById(id),chapter=body.dataset.chapter;
const safe={get(k){try{return localStorage.getItem(k)}catch{return null}},set(k,v){try{localStorage.setItem(k,v)}catch{}}};
let current=0,reading=new URLSearchParams(location.search).get('view')==='reading',size=Number(safe.get('iscarb-text-size'))||100;
if(![100,115,130].includes(size))size=100;
function setTheme(value){root.dataset.theme=value==='light'?'light':'dark';byId('theme').textContent=root.dataset.theme==='light'?'Dark theme':'Light theme';safe.set('iscarb-theme',root.dataset.theme)}
function textSize(){root.style.setProperty('--body-size',`calc(${matchMedia('(max-width:760px)').matches?'1.12rem':'1.3rem'} * ${size/100})`);byId('font').textContent=`Text ${size}%`;safe.set('iscarb-text-size',String(size))}
function closeAnswers(){document.querySelectorAll('details.answer[open]').forEach(d=>d.open=false)}
function sync(focus=false){body.classList.toggle('reading',reading);body.classList.toggle('presentation',!reading);slides.forEach((s,i)=>s.hidden=!reading&&i!==current);byId('mode').textContent=reading?'Slide view':'Reading view';byId('mode').setAttribute('aria-pressed',String(reading));byId('prev').disabled=current===0;byId('next').disabled=current===slides.length-1;byId('count').textContent=`${current+1} / ${slides.length}`;byId('progressFill').style.width=`${(current+1)/slides.length*100}%`;byId('announcer').textContent=`Unit ${current+1} of ${slides.length}: ${slides[current].dataset.title}`;document.querySelectorAll('.route span').forEach(s=>{if(s.dataset.phase===slides[current].dataset.phase)s.setAttribute('aria-current','step');else s.removeAttribute('aria-current')});safe.set('iscarb-last-unit-'+chapter,String(current));if(focus){slides[current].querySelector('h1,h2').focus({preventScroll:true});slides[current].scrollIntoView({block:'start'})}}
function go(index,focus=true){current=Math.max(0,Math.min(slides.length-1,index));closeAnswers();history.replaceState(null,'','#unit-'+(current+1));sync(focus)}
function fromHash(){const match=location.hash.match(/^#unit-(\d+)$/);if(match){const n=Number(match[1]);if(n>=1&&n<=slides.length){current=n-1;return true}}return false}
byId('prev').onclick=()=>go(current-1);byId('next').onclick=()=>go(current+1);
byId('mode').onclick=()=>{reading=!reading;const url=new URL(location.href);if(reading)url.searchParams.set('view','reading');else url.searchParams.delete('view');history.replaceState(null,'',url);sync();slides[current].scrollIntoView({block:'start'})};
byId('theme').onclick=()=>setTheme(root.dataset.theme==='dark'?'light':'dark');byId('font').onclick=()=>{size=size===100?115:size===115?130:100;textSize()};
byId('hide-answers').onclick=()=>{closeAnswers();byId('announcer').textContent='All model answers hidden.'};
byId('chapter').onchange=e=>{const url=e.target.selectedOptions[0].dataset.url;if(url)location.href=url};
byId('outline-button').onclick=()=>{const p=byId('outline-panel');p.hidden=!p.hidden;byId('outline-button').setAttribute('aria-expanded',String(!p.hidden));if(!p.hidden)p.querySelector('a').focus()};
byId('help-button').onclick=()=>{const p=byId('help-panel');p.hidden=!p.hidden;byId('help-button').setAttribute('aria-expanded',String(!p.hidden))};
byId('print').onclick=()=>window.print();
byId('fullscreen').onclick=async()=>{try{if(!document.fullscreenElement)await root.requestFullscreen();else await document.exitFullscreen()}catch{byId('announcer').textContent='Full screen is unavailable. Slide view remains usable.'}};
document.addEventListener('fullscreenchange',()=>byId('fullscreen').textContent=document.fullscreenElement?'Exit full screen':'Full screen');
document.querySelectorAll('a[href^="#unit-"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();byId('outline-panel').hidden=true;byId('outline-button').setAttribute('aria-expanded','false');go(Number(a.hash.slice(6))-1)}));
document.querySelectorAll('details.answer').forEach(d=>d.addEventListener('toggle',()=>{d.querySelector('summary').textContent=d.open?'Hide answer & explanation':'Show answer & explanation';const q=d.closest('.question');if(q?.dataset.correct!==undefined){const selected=q.querySelector('[aria-pressed=true]');const feedback=q.querySelector('.poll-feedback');feedback.hidden=!d.open||!selected;if(d.open&&selected)feedback.textContent=selected.dataset.option===q.dataset.correct?'Your choice is correct.':'Revisit your choice using the explanation below.'}}));
document.querySelectorAll('.poll-option').forEach(b=>b.onclick=()=>{const q=b.closest('.question');q.querySelectorAll('.poll-option').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));q.querySelector('details').open=false;q.querySelector('.poll-feedback').hidden=true});
addEventListener('keydown',e=>{if(e.target.closest('button,a,input,select,textarea,summary,[contenteditable=true]')||e.altKey||e.ctrlKey||e.metaKey)return;if(reading)return;if(['ArrowRight','PageDown'].includes(e.key)){e.preventDefault();go(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(current-1)}if(e.key==='Home'){e.preventDefault();go(0)}if(e.key==='End'){e.preventDefault();go(slides.length-1)}if(e.key==='Escape'){byId('outline-panel').hidden=true;byId('help-panel').hidden=true;byId('outline-button').setAttribute('aria-expanded','false');byId('help-button').setAttribute('aria-expanded','false')}});
addEventListener('hashchange',()=>{if(fromHash()){closeAnswers();sync(true)}});addEventListener('resize',textSize);
const saved=Number(safe.get('iscarb-last-unit-'+chapter));
setTheme(safe.get('iscarb-theme')||'dark');textSize();closeAnswers();fromHash();sync();
// Resume is explicit; a fresh classroom session always opens with the crisis.
const resume=byId('resume');if(saved>0&&saved<slides.length&&!location.hash){resume.hidden=false;resume.textContent='Resume unit '+(saved+1);resume.onclick=()=>{go(saved);resume.hidden=true}};
})();
