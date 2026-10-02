/* Deterministic teaching models. No eval, packages, service calls or production access. */
var StudyLab=(function(){
'use strict';
var LAB_CHAPTERS=[12,13,14,16,17];
var SCOPE={
 12:'Single barrier decision from the latest camera frame; no timing, power, mechanics or real sensor data.',
 13:'Server-side access decision for one request; no sessions, logs, network or real accounts.',
 14:'Pickup-list fallback during one outage; no sign-in service, devices or real staff workload.',
 16:'Duration adapter only; no room-conflict, concurrency or deployed-service behavior.',
 17:'Sequential single-store simulation; no network, concurrency or external-payment implementation.'};
var MIN={12:3,13:3,14:2,16:3,17:2};
function distinct(cases){var names=new Set();cases.forEach(function(t){if(!t||typeof t.name!=='string'||!t.name.trim()||names.has(t.name))throw Error('Give each case a distinct nonempty name.');names.add(t.name);});}
function casesFrom(text,ch){
 var cases=JSON.parse(text),min=MIN[ch]||2;
 if(!Array.isArray(cases)||cases.length<min||cases.length>8)throw Error('Write '+min+'–8 test cases.');
 distinct(cases);
 cases.forEach(function(t){
 if(ch===16){if(!Object.prototype.hasOwnProperty.call(t,'durationMinutes')||!['accepted','rejected'].includes(t.expectedStatus))throw Error('Each contract case needs durationMinutes and expectedStatus (accepted or rejected).');if(t.expectedStatus==='accepted'&&(!Number.isFinite(t.expectedSeconds)||t.expectedSeconds<1||t.expectedSeconds>7200))throw Error('For accepted input, state numeric expectedSeconds in the component range.');if(t.expectedStatus==='rejected'&&t.expectedSeconds!==null)throw Error('For rejected input, use expectedSeconds: null.');}
 else if(ch===17){if(!Array.isArray(t.events)||t.events.length<2||t.events.length>12||!Number.isInteger(t.expectedReservations)||t.expectedReservations<1)throw Error('Each retry case needs 2–12 events and a positive integer expectedReservations.');var seenRequest=false;t.events.forEach(function(e){if(typeof e!=='string'||!(/^(send|retry):[A-Za-z0-9_-]{1,30}$/.test(e)||['lose-response','restart'].includes(e)))throw Error('Use send:ID, retry:ID, lose-response or restart events.');if(e.startsWith('send:'))seenRequest=true;if(!seenRequest)throw Error('Begin each sequence with a send:ID event.');});}
 else if(ch===12){if(!Array.isArray(t.frames)||t.frames.length<1||t.frames.length>10||!t.frames.every(function(f){return['empty','occupied','missing'].includes(f);})||!['close','hold'].includes(t.expectedAction))throw Error('Each barrier case needs frames (1–10 of empty, occupied or missing) and expectedAction (close or hold).');}
 else if(ch===13){if(!/^(student|staff):[a-z0-9_-]{1,20}$/.test(t.actor||'')||!/^project:[a-z0-9_-]{1,20}@[a-z0-9_-]{1,20}$/.test(t.object||'')||!['ui','api'].includes(t.path)||!['allow','deny'].includes(t.expected))throw Error('Each access case needs actor (student:ID or staff:GROUP), object (project:OWNER@GROUP), path (ui or api) and expected (allow or deny).');}
 else if(ch===14){if(!Array.isArray(t.events)||t.events.length<2||t.events.length>14||!Array.isArray(t.expectedLookups)||!t.expectedLookups.every(function(x){return['current','stale','missing'].includes(x);})||!Number.isInteger(t.expectedLost)||t.expectedLost<0)throw Error('Each fallback case needs events, expectedLookups (current, stale or missing per lookup) and an integer expectedLost.');var looks=0;t.events.forEach(function(e){if(typeof e!=='string'||!(/^(change|lookup):[A-Za-z0-9_-]{1,30}$/.test(e)||['refresh','outage','recover'].includes(e)))throw Error('Use refresh, outage, recover, change:ID or lookup:ID events.');if(e.startsWith('lookup:'))looks++;});if(looks!==t.expectedLookups.length)throw Error('Give one expectedLookups entry for each lookup event.');}
 else throw Error('Unknown teaching model.');
 });
 if(ch===16){var valid=cases.some(t=>typeof t.durationMinutes==='number'&&t.durationMinutes>=1/60&&t.durationMinutes<=120);var boundary=cases.some(t=>t.durationMinutes===120);var invalid=cases.some(t=>typeof t.durationMinutes!=='number'||!Number.isFinite(t.durationMinutes)||t.durationMinutes<1/60||t.durationMinutes>120);if(!valid||!boundary||!invalid)throw Error('Include a valid input, the 120-minute upper boundary, and an invalid input.');}
 if(ch===17){if(!cases.some(t=>t.events.includes('restart')))throw Error('Include a restart case.');if(!cases.some(t=>new Set(t.events.filter(e=>/^(send|retry):/.test(e)).map(e=>e.split(':')[1])).size>1))throw Error('Include a case with a genuinely different request ID.');}
 if(ch===12){var last=t=>t.frames[t.frames.length-1];if(!cases.some(t=>last(t)==='occupied')||!cases.some(t=>last(t)==='empty'))throw Error('Include a case ending with an occupied frame and one ending with an empty frame.');if(!cases.some(t=>t.frames.includes('missing')))throw Error('Include at least one case outside the recorded daylight conditions (a missing frame).');}
 if(ch===13){if(!cases.some(t=>t.path==='api'&&t.expected==='allow')||!cases.some(t=>t.path==='api'&&t.expected==='deny'))throw Error('Include an allowed and a forbidden request on the api path.');}
 if(ch===14){if(!cases.some(t=>{var o=t.events.indexOf('outage');return o>=0&&t.events.slice(o).some(e=>e.startsWith('change:'))&&t.events.slice(o).some(e=>e.startsWith('lookup:'));}))throw Error('Include a case with a change and a lookup during the outage.');}
 return cases;
}
function contract(t,mode){var seconds=mode==='baseline'?t.durationMinutes:t.durationMinutes*60;var accepted=typeof t.durationMinutes==='number'&&Number.isFinite(t.durationMinutes)&&Number.isFinite(seconds)&&seconds>=1&&seconds<=7200;var actual={status:accepted?'accepted':'rejected',storedSeconds:accepted?seconds:null};return{name:t.name,actual:actual,passed:actual.status===t.expectedStatus&&(actual.storedSeconds===null?t.expectedSeconds===null:Math.abs(actual.storedSeconds-t.expectedSeconds)<1e-8)};}
function retry(t,mode){var durable=new Map(),memory=new Map(),count=0,trace=[];t.events.forEach(function(event){if(event==='restart'){memory.clear();trace.push('Service restart: volatile request records cleared.');return;}if(event==='lose-response'){trace.push('Response lost after execution; database changes remain.');return;}var id=event.split(':')[1],cache=mode==='baseline'?memory:durable;if(cache.has(id)){trace.push(event+' returns reservation '+cache.get(id));}else{count++;cache.set(id,count);trace.push(event+' commits reservation '+count);}});return{name:t.name,actual:{reservations:count,trace:trace},passed:count===t.expectedReservations};}
// Chapter 12: the controller is asked to close after the listed frames. Baseline: closes unless the latest frame
// shows occupancy. Corrected (fail-safe): closes only when the latest frame positively shows an empty zone.
function barrier(t,mode){var f=t.frames[t.frames.length-1],close=mode==='baseline'?f!=='occupied':f==='empty';var action=close?'close':'hold';return{name:t.name,actual:{action:action,decidedOn:f},passed:action===t.expectedAction};}
// Chapter 13: baseline enforces the rule only where the interface lists links; the API serves any identifier.
// Corrected: the server checks actor against object on every path.
function access(t,mode){var a=t.actor.split(':'),o=t.object.slice(8).split('@'),rule=a[0]==='student'?a[1]===o[0]:a[1]===o[1];var allowed=t.path==='api'&&mode==='baseline'?true:rule;var d=allowed?'allow':'deny';return{name:t.name,actual:{decision:d,checkedOnServer:mode==='corrected'},passed:d===t.expected};}
// Chapter 14: one central list, a local copy refreshed on "refresh". During an outage the baseline reads the
// local copy and drops new changes; the corrected fallback also records changes on the controlled paper log,
// reads it with the local copy, and reconciles it into the central list on "recover".
function fallback(t,mode){var central=new Map(),local=new Map(),paper=new Map(),real=new Map(),down=false,lost=0,v=0,looks=[];t.events.forEach(function(e){if(e==='refresh'){if(!down)local=new Map(central);return;}if(e==='outage'){down=true;return;}if(e==='recover'){down=false;if(mode==='corrected'){paper.forEach(function(x,k){central.set(k,x);});paper.clear();}return;}var p=e.split(':'),id=p[1];if(p[0]==='change'){v++;real.set(id,v);if(!down)central.set(id,v);else if(mode==='corrected')paper.set(id,v);else lost++;return;}var truth=real.get(id)||0,seen=down?Math.max(local.get(id)||0,mode==='corrected'?(paper.get(id)||0):0):(central.get(id)||0);looks.push(!truth&&!seen?'missing':seen===truth?'current':seen?'stale':'missing');});return{name:t.name,actual:{lookups:looks,lostChanges:lost},passed:JSON.stringify(looks)===JSON.stringify(t.expectedLookups)&&lost===t.expectedLost};}
function run(ch,mode,cases){if(!LAB_CHAPTERS.includes(ch)||!['baseline','corrected'].includes(mode))throw Error('Unknown teaching model or mode.');var f={12:barrier,13:access,14:fallback,16:contract,17:retry}[ch];return cases.map(t=>f(t,mode));}
function mount(ch){
 var el=id=>document.getElementById(id),input=el('labCases');if(!input)return;
 var evidence=el('labEvidence'),prediction=el('labPrediction'),output=el('labOutput'),state={};
 try{state=JSON.parse(evidence.value||'{}');}catch(e){}
 function render(){output.textContent=state.runs?JSON.stringify(state.runs,null,2):'Predict the results and define your test cases before running either model.';}
 function reset(){if(input.readOnly)return;state={};evidence.value='';prediction.readOnly=false;render();evidence.dispatchEvent(new Event('input',{bubbles:true}));}
 input.addEventListener('input',reset);
 document.querySelectorAll('[data-lab-mode]').forEach(function(button){button.disabled=input.readOnly;button.addEventListener('click',function(){if(input.readOnly)return;try{if(prediction.value.trim().length<30)throw Error('Record a specific prediction before running the tests (at least 30 characters).');var cases=casesFrom(input.value,ch),mode=button.dataset.labMode;if(!state.cases||JSON.stringify(state.cases)!==JSON.stringify(cases))state={chapter:ch,model:'teaching-model-v2',scope:SCOPE[ch],cases:cases,prediction:prediction.value,runs:{}};state.runs[mode]=run(ch,mode,cases);state.recordedAt=new Date().toISOString();evidence.value=JSON.stringify(state,null,2);prediction.readOnly=true;evidence.dispatchEvent(new Event('input',{bubbles:true}));render();el('labStatus').textContent='Executed locally. Compare each actual result with your expected result; explain discrepancies in the artifact field. Passing these cases supports only this small model.';}catch(e){el('labStatus').textContent=e.message;}});});
 if(state.runs)prediction.readOnly=true;render();
}
return{casesFrom:casesFrom,run:run,mount:mount};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=StudyLab;
