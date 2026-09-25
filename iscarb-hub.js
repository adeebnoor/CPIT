(()=>{'use strict';
const prefs={get(key){try{return localStorage.getItem(key)}catch{return null}},set(key,value){try{localStorage.setItem(key,value);return true}catch{return false}}};
const theme=document.getElementById('themeBtn');const apply=t=>{document.documentElement.dataset.theme=t;if(theme){theme.textContent=t==='dark'?'Light mode':'Dark mode';theme.setAttribute('aria-label','Switch to '+(t==='dark'?'light':'dark')+' mode')}};
apply(prefs.get('iscarb-theme')==='light'?'light':'dark');theme?.addEventListener('click',()=>{const t=document.documentElement.dataset.theme==='dark'?'light':'dark';apply(t);prefs.set('iscarb-theme',t)});
document.querySelectorAll('.review-check[data-review-chapter]').forEach(check=>{const chapter=check.dataset.reviewChapter,key='iscarb-ch'+chapter+'-reviewed',status=check.closest('.lesson')?.querySelector('.review-status');check.checked=prefs.get(key)==='1';const render=()=>{if(status)status.textContent=check.checked?'Marked as reviewed on this device.':'Your review status stays on this device.'};render();check.addEventListener('change',()=>{if(prefs.set(key,check.checked?'1':'0'))render();else if(status)status.textContent='Browser storage is unavailable. This mark will reset when the page closes.'})});
const legacy=document.getElementById('reviewed'),legacyStatus=document.getElementById('reviewStatus');if(legacy){const key='iscarb-ch10-v7-reviewed';legacy.checked=prefs.get(key)==='1';const render=()=>{if(legacyStatus)legacyStatus.textContent=legacy.checked?'Marked as reviewed on this device.':'Your review status stays on this device.'};render();legacy.addEventListener('change',()=>{if(prefs.set(key,legacy.checked?'1':'0'))render()})}
})();

// Course-level progress is a local review mark, never a mastery score.
(function(){
 const chapters=[10,11,12,13,14,15,16,17,20],evalKey='iscarb-qeeem-evaluation-complete',openedKey='iscarb-qeeem-opened';
 const safeGet=k=>{try{return localStorage.getItem(k)}catch{return null}},safeSet=(k,v)=>{try{localStorage.setItem(k,v);return true}catch{return false}};
 const evalBox=document.getElementById('qeeemComplete'),evalStatus=document.getElementById('qeeemStatus'),label=document.getElementById('courseProgressLabel'),qeeemLinks=[document.getElementById('openQeeem'),document.getElementById('topQeeem')].filter(Boolean);
 const unlockEval=()=>{safeSet(openedKey,'1');if(evalBox)evalBox.disabled=false;if(evalStatus&&!evalBox?.checked)evalStatus.textContent='Qeeem opened. Complete the evaluation, then confirm below.'};
 qeeemLinks.forEach(a=>a.addEventListener('click',unlockEval));
 if(evalBox){evalBox.checked=safeGet(evalKey)==='1';evalBox.disabled=safeGet(openedKey)!=='1'&&!evalBox.checked;}
 const render=()=>{const checks=[...document.querySelectorAll('.review-check')];if(!checks.length)return;const n=checks.filter(x=>x.checked).length,evaluated=evalBox?.checked===true;const t=document.getElementById('courseProgress'),bar=document.getElementById('courseProgressBar'),next=checks.find(x=>!x.checked),link=document.getElementById('continueCourse');if(bar)bar.value=n;
  if(t)t.textContent=n<chapters.length?n+' / '+chapters.length:(evaluated?'Course complete':'9 / 9 · evaluation required');
  if(label)label.textContent=n<chapters.length?'chapters reviewed · evaluation required to finish':(evaluated?'all chapters reviewed · evaluation completed':'all chapters reviewed · complete Qeeem evaluation to finish');
  if(evalStatus){evalStatus.textContent=evaluated?'Evaluation completion recorded on this device. Course completion is now unlocked.':(evalBox?.disabled?'Open Qeeem first. Then complete the evaluation and confirm below.':'Required before this browser marks the course complete.');evalStatus.classList.toggle('complete',evaluated)}
  if(next&&link){const lesson=next.closest('.lesson'),a=lesson.querySelector('.actions a');link.href=a.href;link.textContent=n?'Continue with Chapter '+next.dataset.reviewChapter:'Start Chapter 10'}
  else if(link&&!evaluated){link.href='#course-evaluation';link.textContent='Complete required course evaluation'}
  else if(link){link.href='course-resources.html#outcomes';link.textContent='Course complete · Review outcomes'}
 };
 document.querySelectorAll('.review-check').forEach(x=>x.addEventListener('change',render));
 evalBox?.addEventListener('change',()=>{safeSet(evalKey,evalBox.checked?'1':'0');render()});
 render();
})();

// Approximate unique-browser counter for the public iSCARB hub.
// The backend stores only a random browser UUID, the fixed hub path, and first-seen time.
(function(){
 const out=document.getElementById('visitorCount'),wrap=document.getElementById('visitorStat');
 if(!out)return;
 const endpoint='https://xcirpzxpcpbxpowjbpiq.supabase.co/functions/v1/iscarb-visitor-counter';
 const key='iscarb-hub-visitor-id-v1';
 const uuidRe=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
 function uuid(){
  if(globalThis.crypto?.randomUUID)return crypto.randomUUID();
  const b=new Uint8Array(16);crypto.getRandomValues(b);b[6]=(b[6]&15)|64;b[8]=(b[8]&63)|128;
  return [...b].map((x,i)=>([4,6,8,10].includes(i)?'-':'')+x.toString(16).padStart(2,'0')).join('');
 }
 function identity(){
  try{
   let id=localStorage.getItem(key);
   if(uuidRe.test(id||''))return{id,count:true};
   id=uuid();
   localStorage.setItem(key,id);
   if(localStorage.getItem(key)===id)return{id,count:true};
  }catch{}
  return{id:null,count:false};
 }
 async function load(){
  const automated=!!navigator.webdriver;
  const v=automated?{id:null,count:false}:identity();
  try{
   const options=v.count?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({visitor_id:v.id,path:'/CPIT/iscarb.html'})}:{method:'GET'};
   const r=await fetch(endpoint,options),d=await r.json();
   if(!r.ok||!d.ok||!Number.isFinite(Number(d.visitors)))throw Error('counter');
   out.textContent=Number(d.visitors).toLocaleString('en-US');
   if(wrap)wrap.title='Approximate unique browsers visiting this course hub. No name, email or IP is stored by the iSCARB counter.';
  }catch{
   out.textContent='—';
   if(wrap)wrap.title='Visitor count temporarily unavailable.';
  }
 }
 load();
})();

