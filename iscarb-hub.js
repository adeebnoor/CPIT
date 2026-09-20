(()=>{'use strict';
const prefs={get(key){try{return localStorage.getItem(key)}catch{return null}},set(key,value){try{localStorage.setItem(key,value);return true}catch{return false}}};
const theme=document.getElementById('themeBtn');const apply=t=>{document.documentElement.dataset.theme=t;if(theme){theme.textContent=t==='dark'?'Light mode':'Dark mode';theme.setAttribute('aria-label','Switch to '+(t==='dark'?'light':'dark')+' mode')}};
apply(prefs.get('iscarb-theme')==='light'?'light':'dark');theme?.addEventListener('click',()=>{const t=document.documentElement.dataset.theme==='dark'?'light':'dark';apply(t);prefs.set('iscarb-theme',t)});
document.querySelectorAll('.review-check[data-review-chapter]').forEach(check=>{const chapter=check.dataset.reviewChapter,key='iscarb-ch'+chapter+'-reviewed',status=check.closest('.lesson')?.querySelector('.review-status');check.checked=prefs.get(key)==='1';const render=()=>{if(status)status.textContent=check.checked?'Marked as reviewed on this device.':'Your review status stays on this device.'};render();check.addEventListener('change',()=>{if(prefs.set(key,check.checked?'1':'0'))render();else if(status)status.textContent='Browser storage is unavailable. This mark will reset when the page closes.'})});
const legacy=document.getElementById('reviewed'),legacyStatus=document.getElementById('reviewStatus');if(legacy){const key='iscarb-ch10-v7-reviewed';legacy.checked=prefs.get(key)==='1';const render=()=>{if(legacyStatus)legacyStatus.textContent=legacy.checked?'Marked as reviewed on this device.':'Your review status stays on this device.'};render();legacy.addEventListener('change',()=>{if(prefs.set(key,legacy.checked?'1':'0'))render()})}
})();

// Course-level progress is a local review mark, never a mastery score.
(function(){
 const chapters=[10,11,12,13,14,15,16,17,20];
 const render=()=>{const checks=[...document.querySelectorAll('.review-check')];if(!checks.length)return;const n=checks.filter(x=>x.checked).length;const t=document.getElementById('courseProgress'),bar=document.getElementById('courseProgressBar');if(t)t.textContent=n+' / '+chapters.length;if(bar)bar.value=n;const next=checks.find(x=>!x.checked),link=document.getElementById('continueCourse');if(next&&link){const lesson=next.closest('.lesson'),a=lesson.querySelector('.actions a');link.href=a.href;link.textContent=n?'Continue with Chapter '+next.dataset.reviewChapter:'Start Chapter 10'}else if(link){link.href='course-resources.html#outcomes';link.textContent='Review course outcomes'}};
 document.querySelectorAll('.review-check').forEach(x=>x.addEventListener('change',render));render();
})();
