/* Added before boot. Existing commitment/reveal/export behavior remains in the reviewed engine. */
const V2_CONFIG=__V2_CONFIG__;
const beforeLockedView=lockedView;lockedView=function(){beforeLockedView();if(S.locked)document.querySelectorAll('[data-lab-mode]').forEach(button=>button.disabled=true);};
const beforeValA=valA;
valA=function(){
 const issue=beforeValA();if(issue)return issue;
 const nums=($('sourceUse').value.match(/\b\d+\b/g)||[]).map(Number);
 if(!nums.some(n=>V2_CONFIG.pages.includes(n)))return'Cite a slide from the assigned reading and explain how its concept supports your artifact. The page check only checks the reference, not understanding.';
 if(V2_CONFIG.lab){try{const r=JSON.parse($('labEvidence').value),cases=StudyLab.casesFrom($('labCases').value,V2_CONFIG.chapter);if(r.chapter!==V2_CONFIG.chapter||r.model!=='teaching-model-v2'||JSON.stringify(r.cases)!==JSON.stringify(cases)||!r.runs?.baseline||!r.runs?.corrected)throw Error('incomplete');}catch(e){return'Run both teaching-model versions with your own current test cases before commitment. Report the actual outcomes even when a test fails.';}}
 return'';
};
const beforeMD=md;
md=function(final=false){const d=bData();let result=beforeMD(final);result+='\n\n## Preparation and workload\nRequired reading: '+V2_CONFIG.reading+'\nReported total active minutes (reading, check and assignment): '+(d.activeMinutes||'Not reported')+'\n';if(d.feedbackNote||d.revisionNote)result+='\n## Feedback and revision\nFeedback received: '+(d.feedbackNote||'Not recorded')+'\nChange and recheck: '+(d.revisionNote||'Not recorded')+'\n';if(S.firstPreparedExport&&d.feedbackNote.trim()&&d.revisionNote.trim())result+='\n## Preserved first prepared export\nThis is a local export snapshot, not proof of LMS submission.\nPrepared at: '+S.firstPreparedExport.at+'\n'+S.firstPreparedExport.text;return result;};
const beforePrintSheet=printSheet;
printSheet=function(final=false){beforePrintSheet(final);const d=bData();$('print').insertAdjacentHTML('beforeend','<h2>Preparation and workload</h2><div class="box">'+esc(V2_CONFIG.reading)+'<br>Reported total active minutes: '+esc(d.activeMinutes||'Not reported')+'</div>'+(d.feedbackNote||d.revisionNote?'<h2>Feedback and revision</h2><div class="box">'+esc(d.feedbackNote||'Not recorded')+'<br>'+esc(d.revisionNote||'Not recorded')+'</div>':'')+(S.firstPreparedExport&&d.feedbackNote.trim()&&d.revisionNote.trim()?'<h2>Preserved first prepared export · '+esc(S.firstPreparedExport.at)+'</h2><div class="box" style="white-space:pre-wrap">'+esc(S.firstPreparedExport.text)+'</div>':''));};
function preserveFirstExport(){if(!S.firstPreparedExport){S.firstPreparedExport={at:now(),text:beforeMD(true)};save(false);}}
const beforeDownloadFinal=downloadFinal;downloadFinal=function(){if(valB())return;preserveFirstExport();beforeDownloadFinal();};
const beforePrintFinal=printFinal;printFinal=function(){if(valB())return;preserveFirstExport();beforePrintFinal();};
const beforeCopyFinal=copyFinal;copyFinal=async function(){if(valB())return;preserveFirstExport();await beforeCopyFinal();};
const beforeValB=valB;valB=function(){const issue=beforeValB();if(issue)return issue;const d=bData();if((d.feedbackNote.trim()&&!d.revisionNote.trim())||(!d.feedbackNote.trim()&&d.revisionNote.trim()))return'For a revised submission, record both the feedback received and the change/recheck. Leave both blank for the first submission.';return'';};
