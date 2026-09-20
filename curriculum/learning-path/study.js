/* Preparation is formative practice, saved locally, never an LMS grade. */
(function(){
'use strict';
var config=LECTURE.study,form=document.getElementById('prepQuiz'),status=document.getElementById('prepStatus');
if(!config||!form)return;
var key=KEY+'-preparation-v2',record={answers:[],attempts:0},storage=true;
try{var saved=JSON.parse(localStorage.getItem(key)||'null');if(saved&&Array.isArray(saved.answers))record=saved;}catch(e){storage=false;}
function current(){return config.quiz.map(function(_,i){var el=form.querySelector('input[name="prep-'+i+'"]:checked');return el?Number(el.value):null;});}
function persist(){try{localStorage.setItem(key,JSON.stringify(record));storage=true;}catch(e){storage=false;}}
function feedback(){var score=0;config.quiz.forEach(function(q,i){var box=document.getElementById('prep-feedback-'+i),ok=record.answers[i]===q[2];score+=ok?1:0;box.hidden=false;box.textContent=(ok?'Correct. ':'Revisit this objective. ')+q[3];});status.textContent='Practice: '+score+' / 5 on this attempt. '+(score===5?'Now explain your answers without looking.':'Review the explanations and retry before the assignment.')+' This is local formative feedback, not a grade or certified mastery.'+(storage?'':' Saving is unavailable; keep a note or screenshot of your answers.');}
record.answers.forEach(function(v,i){var el=form.querySelector('input[name="prep-'+i+'"][value="'+v+'"]');if(el)el.checked=true;});
if(record.checked&&record.answers.length===5)feedback();
form.addEventListener('change',function(){record.answers=current();record.checked=false;form.querySelectorAll('[data-prep-feedback]').forEach(function(e){e.hidden=true;});persist();status.textContent='Answers changed. Check the complete set for feedback.'+(storage?'':' Local saving is unavailable.');});
document.getElementById('checkPrep').addEventListener('click',function(){var answers=current();if(answers.some(function(a){return a===null;})){status.textContent='Attempt all five questions before opening the explanations.';return;}record.answers=answers;record.attempts=(record.attempts||0)+1;record.checked=true;record.checkedAt=new Date().toISOString();if(!record.firstAttempt)record.firstAttempt=answers.slice();persist();feedback();});
document.addEventListener('click',function(e){var b=e.target.closest('[data-source-slide]');if(!b)return;e.preventDefault();var section=document.getElementById('source-slide-'+b.dataset.sourceSlide);if(!section)return;var slide=section.closest('.slide');if(slide)go(Number(slide.dataset.i),true);section.open=true;if(LECTURE.visualStory)document.dispatchEvent(new CustomEvent('iscarb-source-focus',{detail:b.dataset.sourceSlide}));else section.scrollIntoView?.({block:'start',behavior:'smooth'});});
})();
