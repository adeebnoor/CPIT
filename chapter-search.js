(()=>{'use strict';
const input=document.getElementById('chapterSearch');
const status=document.getElementById('chapterSearchStatus');
const lessons=Array.from(document.querySelectorAll('.lesson'));
if(!input||!lessons.length)return;
input.addEventListener('input',()=>{
 const q=input.value.trim().toLowerCase();let shown=0;
 lessons.forEach(card=>{const ok=!q||card.textContent.toLowerCase().includes(q);card.hidden=!ok;if(ok)shown++;});
 document.querySelectorAll('.path-section').forEach(section=>{section.hidden=![...section.querySelectorAll('.lesson')].some(card=>!card.hidden)});
 if(status)status.textContent=q?(shown?'Showing '+shown+' of '+lessons.length+' chapters.':'No matching chapters. Try another concept or chapter number.'):'Showing all '+lessons.length+' chapters.';
});
})();
