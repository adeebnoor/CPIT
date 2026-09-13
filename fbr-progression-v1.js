/* CPIT-455 After-Class progression: concept coverage + deliberate difficulty ramp */
(()=>{
'use strict';
const DATA={
 '10':{level:'1 / 9 · FOUNDATION',time:'25–35 min',concepts:['Dependability attributes','Fault → error → failure','Redundancy & diversity','Trustworthiness','Sociotechnical boundary'],ramp:'One bounded engineering decision with a visible mechanism and a relatively small constraint set. The emphasis is learning FIT → BOUND → ACT → EVIDENCE → REFIT correctly.'},
 '11':{level:'2 / 9 · MEASURE',time:'25–40 min',concepts:['Reliability metrics','POFOD / ROCOF / MTTF','Availability','Operational profile','Measurable reliability requirement'],ramp:'Adds quantitative thresholds and forces the student to connect a metric to an operating context rather than naming a property.'},
 '12':{level:'3 / 9 · SAFETY-CRITICAL',time:'30–40 min',concepts:['Hazard identification','Risk & severity','ALARP / acceptability','Hazard-driven requirements','Fault tree / safety case evidence'],ramp:'The decision now has a harm boundary. Students must distinguish reliability from safety and defend a protection requirement with explicit hazard evidence.'},
 '13':{level:'4 / 9 · ADVERSARIAL',time:'30–45 min',concepts:['Assets & losses','Threats & vulnerabilities','Security requirements','Risk treatment / layered protection','Security assurance & testing'],ramp:'Introduces an adaptive adversary and residual risk. A control name is no longer enough: asset, attack path, control, boundary and assurance evidence must form a chain.'},
 '14':{level:'5 / 9 · MULTI-DEPENDENCY',time:'35–45 min',concepts:['Critical services','Recognition','Resistance','Recovery','Reinstatement / degraded mode'],ramp:'Adds interacting dependencies and continuity priorities. Students must decide what must survive, what may degrade, and when restoration is justified.'},
 '15':{level:'6 / 9 · LIFECYCLE TRADE-OFF',time:'35–50 min',concepts:['Reuse levels','Application / service reuse','Fit-gap analysis','Adaptation & integration','Vendor / licensing / lifecycle risk'],ramp:'The correct answer is no longer purely technical. Delivery time, maintainability, ownership, commercial constraints and lifecycle evidence must be balanced together.'},
 '16':{level:'7 / 9 · CONTRACT & SEMANTICS',time:'40–50 min',concepts:['Component model','Provided / required interfaces','Semantic compatibility','Composition / adaptation','Dependency & quality contracts'],ramp:'Moves from choosing an option to defending a composition contract. Syntactic compatibility may pass while semantics, dependencies or quality assumptions fail.'},
 '17':{level:'8 / 9 · DISTRIBUTED UNCERTAINTY',time:'45–55 min',concepts:['Client–server / distributed architecture','Middleware & interaction','State placement','Scalability & QoS','Partition / failover / replication evidence'],ramp:'Multiple nodes, state, latency and partial failure interact. Students must make a decision that remains defensible when coordination or a region fails.'},
 '20':{level:'9 / 9 · CAPSTONE',time:'50–60 min',concepts:['Operational independence','Managerial independence','SoS classification','Governance & interface contracts','Evolution / emergence / fallback'],ramp:'Combines technical, organizational and governance uncertainty. No single owner controls the whole; the student must defend useful system-level value under independent change and incomplete authority.'}
};
function chapter(){
 const q=new URLSearchParams(location.search).get('chapter');
 if(q&&DATA[q]) return q;
 const m=(document.title||'').match(/Chapter\s+(10|11|12|13|14|15|16|17|20)/i);
 return m?m[1]:null;
}
function make(ch){
 const d=DATA[ch]; if(!d) return null;
 const sec=document.createElement('section');
 sec.className='card fbr-progression-card';
 sec.innerHTML=`<div class="fbr-prog-head"><div><div class="fbr-prog-ey">CONCEPT COVERAGE · CHALLENGE ${d.level}</div><h2>This week tests the chapter — not just the FBR form.</h2></div><div class="fbr-prog-time">${d.time}</div></div><div class="fbr-prog-concepts">${d.concepts.map(x=>`<span>${x}</span>`).join('')}</div><div class="fbr-prog-ramp"><b>Why this is harder than the previous challenge:</b> ${d.ramp}</div>`;
 return sec;
}
function style(){
 if(document.getElementById('fbr-progression-style'))return;
 const s=document.createElement('style');s.id='fbr-progression-style';s.textContent=`
 .fbr-progression-card{border-color:rgba(44,220,255,.34)!important;background:linear-gradient(180deg,rgba(44,220,255,.055),rgba(16,23,37,.94))!important}
 .fbr-prog-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px}.fbr-prog-ey{font-size:10px;font-weight:900;letter-spacing:.1em;color:#2cdcff;text-transform:uppercase}.fbr-prog-head h2{margin:5px 0 0!important;font-size:18px!important}.fbr-prog-time{white-space:nowrap;border:1px solid rgba(220,181,107,.46);color:#ffe8c7;border-radius:999px;padding:5px 9px;font-size:10px;font-weight:900}.fbr-prog-concepts{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}.fbr-prog-concepts span{border:1px solid #35445b;border-radius:999px;background:#0b101b;padding:6px 9px;font-size:10px;color:#d7dfeb;font-weight:800}.fbr-prog-ramp{margin-top:12px;border-left:3px solid #9d8cff;background:rgba(157,140,255,.055);padding:10px 12px;border-radius:0 10px 10px 0;color:#d8d2ef;font-size:12px;line-height:1.55}.fbr-prog-ramp b{color:#e9e5ff}@media(max-width:600px){.fbr-prog-head{display:block}.fbr-prog-time{display:inline-flex;margin-top:9px}}
 `;document.head.appendChild(s);
}
function insert(){
 const ch=chapter(); if(!ch||document.querySelector('.fbr-progression-card'))return;
 style(); const sec=make(ch); if(!sec)return;
 const top=document.querySelector('section.top,.top');
 const quick=[...document.querySelectorAll('section.card,.card')].find(x=>/Quick start|Student pathway|Professional scenario/i.test(x.textContent||''));
 if(quick) quick.insertAdjacentElement('afterend',sec); else if(top) top.insertAdjacentElement('afterend',sec); else document.body.prepend(sec);
 document.documentElement.dataset.fbrChallenge=ch;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',insert);else insert();
})();