/* Deterministic teaching models. No eval, packages, service calls or production access. */
var StudyLab=(function(){
'use strict';
function casesFrom(text,ch){
 var cases=JSON.parse(text);if(!Array.isArray(cases)||cases.length<(ch===16?3:2)||cases.length>8)throw Error(ch===16?'Write 3–8 test cases.':'Write 2–8 test cases.');
 var names=new Set();cases.forEach(function(t){if(!t||typeof t.name!=='string'||!t.name.trim()||names.has(t.name))throw Error('Give each case a distinct nonempty name.');names.add(t.name);
 if(ch===16){if(!Object.prototype.hasOwnProperty.call(t,'durationMinutes')||!['accepted','rejected'].includes(t.expectedStatus))throw Error('Each contract case needs durationMinutes and expectedStatus (accepted or rejected).');if(t.expectedStatus==='accepted'&&(!Number.isFinite(t.expectedSeconds)||t.expectedSeconds<1||t.expectedSeconds>7200))throw Error('For accepted input, state numeric expectedSeconds in the component range.');if(t.expectedStatus==='rejected'&&t.expectedSeconds!==null)throw Error('For rejected input, use expectedSeconds: null.');}
 else {if(!Array.isArray(t.events)||t.events.length<2||t.events.length>12||!Number.isInteger(t.expectedReservations)||t.expectedReservations<1)throw Error('Each retry case needs 2–12 events and a positive integer expectedReservations.');var seenRequest=false;t.events.forEach(function(e){if(typeof e!=='string'||!(/^(send|retry):[A-Za-z0-9_-]{1,30}$/.test(e)||['lose-response','restart'].includes(e)))throw Error('Use send:ID, retry:ID, lose-response or restart events.');if(e.startsWith('send:'))seenRequest=true;if(!seenRequest)throw Error('Begin each sequence with a send:ID event.');});}
 });
 if(ch===16){var valid=cases.some(t=>typeof t.durationMinutes==='number'&&t.durationMinutes>=1/60&&t.durationMinutes<=120);var boundary=cases.some(t=>t.durationMinutes===120);var invalid=cases.some(t=>typeof t.durationMinutes!=='number'||!Number.isFinite(t.durationMinutes)||t.durationMinutes<1/60||t.durationMinutes>120);if(!valid||!boundary||!invalid)throw Error('Include a valid input, the 120-minute upper boundary, and an invalid input.');}
 if(ch===17){if(!cases.some(t=>t.events.includes('restart')))throw Error('Include a restart case.');if(!cases.some(t=>new Set(t.events.filter(e=>/^(send|retry):/.test(e)).map(e=>e.split(':')[1])).size>1))throw Error('Include a case with a genuinely different request ID.');}
 return cases;
}
function contract(t,mode){var seconds=mode==='baseline'?t.durationMinutes:t.durationMinutes*60;var accepted=typeof t.durationMinutes==='number'&&Number.isFinite(t.durationMinutes)&&Number.isFinite(seconds)&&seconds>=1&&seconds<=7200;var actual={status:accepted?'accepted':'rejected',storedSeconds:accepted?seconds:null};return{name:t.name,actual:actual,passed:actual.status===t.expectedStatus&&(actual.storedSeconds===null?t.expectedSeconds===null:Math.abs(actual.storedSeconds-t.expectedSeconds)<1e-8)};}
function retry(t,mode){var durable=new Map(),memory=new Map(),count=0,trace=[];t.events.forEach(function(event){if(event==='restart'){memory.clear();trace.push('Service restart: volatile request records cleared.');return;}if(event==='lose-response'){trace.push('Response lost after execution; database changes remain.');return;}var id=event.split(':')[1],cache=mode==='baseline'?memory:durable;if(cache.has(id)){trace.push(event+' returns reservation '+cache.get(id));}else{count++;cache.set(id,count);trace.push(event+' commits reservation '+count);}});return{name:t.name,actual:{reservations:count,trace:trace},passed:count===t.expectedReservations};}
function run(ch,mode,cases){if(![16,17].includes(ch)||!['baseline','corrected'].includes(mode))throw Error('Unknown teaching model or mode.');return cases.map(t=>ch===16?contract(t,mode):retry(t,mode));}
function mount(ch){
 var el=id=>document.getElementById(id),input=el('labCases');if(!input)return;
 var evidence=el('labEvidence'),prediction=el('labPrediction'),output=el('labOutput'),state={};
 try{state=JSON.parse(evidence.value||'{}');}catch(e){}
 function render(){output.textContent=state.runs?JSON.stringify(state.runs,null,2):'Predict the results and define your test cases before running either model.';}
 function reset(){if(input.readOnly)return;state={};evidence.value='';prediction.readOnly=false;render();evidence.dispatchEvent(new Event('input',{bubbles:true}));}
 input.addEventListener('input',reset);
 document.querySelectorAll('[data-lab-mode]').forEach(function(button){button.disabled=input.readOnly;button.addEventListener('click',function(){if(input.readOnly)return;try{if(prediction.value.trim().length<30)throw Error('Record a specific prediction before running the tests (at least 30 characters).');var cases=casesFrom(input.value,ch),mode=button.dataset.labMode;if(!state.cases||JSON.stringify(state.cases)!==JSON.stringify(cases))state={chapter:ch,model:'teaching-model-v2',scope:ch===16?'Duration adapter only; no room-conflict, concurrency or deployed-service behavior.':'Sequential single-store simulation; no network, concurrency or external-payment implementation.',cases:cases,prediction:prediction.value,runs:{}};state.runs[mode]=run(ch,mode,cases);state.recordedAt=new Date().toISOString();evidence.value=JSON.stringify(state,null,2);prediction.readOnly=true;evidence.dispatchEvent(new Event('input',{bubbles:true}));render();el('labStatus').textContent='Executed locally. Compare each actual result with your expected result; explain discrepancies in the artifact field. Passing these cases supports only this small model.';}catch(e){el('labStatus').textContent=e.message;}});});
 if(state.runs)prediction.readOnly=true;render();
}
return{casesFrom:casesFrom,run:run,mount:mount};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=StudyLab;
