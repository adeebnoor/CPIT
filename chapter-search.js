(()=>{'use strict';
const input=document.getElementById('chapterSearch');
const status=document.getElementById('chapterSearchStatus');
const lessons=Array.from(document.querySelectorAll('.lesson'));
if(!input||!lessons.length)return;
input.addEventListener('input',()=>{
 const q=input.value.trim().toLowerCase();let shown=0;
 lessons.forEach(card=>{const ok=!q||card.textContent.toLowerCase().includes(q);card.hidden=!ok;if(ok)shown++;});
 if(status)status.textContent=q?'Showing '+shown+' of '+lessons.length+' chapters.':'Showing all '+lessons.length+' chapters.';
});
})();