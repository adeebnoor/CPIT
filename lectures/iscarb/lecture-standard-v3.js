(()=>{
'use strict';
const ch=(document.title.match(/Chapter\s+(\d+)/i)||[])[1];
if(!['12','13','14','15','16','17','20'].includes(ch))return;
const DATA={
'12':{
 sections:['Safety-critical systems','Safety requirements','Safety engineering processes','Safety cases'],
 concepts:['Hazard → possible harm','Risk → likelihood × consequence','“Shall not” safety requirements','Safety case → argument + evidence'],
 mechanism:['Identify hazard','Assess & analyze risk','Derive risk-reduction requirements','Assemble safety evidence'],
 map:['Hazard register','Safety requirements','V&V / static analysis','Safety case & regulator'],
 trade:['More protection → less functionality','More assurance → higher cost/time','More automation → new failure modes'],
 evidence:['Hazard/risk analysis','Traceability to safety requirements','Verification & validation records','Review/change-management evidence'],
 caption:'Adapted from Sommerville Ch.12: hazard-driven specification and safety-case structure'
},
'13':{
 sections:['Security and dependability','Security and organizations','Security requirements','Secure systems design','Security testing & assurance'],
 concepts:['Asset → what must be protected','Threat / attack → source of loss','Vulnerability → exploitable weakness','Control → prevention, detection or recovery'],
 mechanism:['Identify assets & losses','Analyze threats/vulnerabilities','Derive security requirements','Design + test controls'],
 map:['Organization & policy','Architecture & trust boundaries','Secure programming','Risk-based security testing'],
 trade:['More restriction → less usability','More centralization → larger blast radius','More monitoring → privacy/operational cost'],
 evidence:['Asset/threat model','Security requirements trace','Architecture/config review','Risk-based penetration & assurance tests'],
 caption:'Adapted from Sommerville Ch.13: risk-based security requirements, design and assurance'
},
'14':{
 sections:['Cybersecurity','Sociotechnical resilience','Resilient systems design'],
 concepts:['Critical service','Recognition','Resistance','Recovery / reinstatement'],
 mechanism:['Identify business resilience need','Identify critical services/assets','Design recognition/resistance/recovery','Test recovery & reinstatement'],
 map:['Business requirements','Critical services','Failure/attack scenarios','Recovery + reinstatement plan'],
 trade:['More redundancy → higher cost/complexity','More isolation → less integration','Faster recovery → more standby capacity'],
 evidence:['Service dependency map','Failure/attack exercises','Recovery-time evidence','Reinstatement tests & incident records'],
 caption:'Adapted from Sommerville Ch.14: critical services, survivability and resilience engineering'
},
'15':{
 sections:['The reuse landscape','Application frameworks','Software product lines','Application system reuse'],
 concepts:['System/application/component reuse','Frameworks','Product lines','Configurable application systems'],
 mechanism:['Define need & constraints','Search reusable assets','Evaluate fit/lifecycle risk','Configure/adapt/integrate'],
 map:['Schedule & lifetime','Team expertise','Criticality/NFRs','Domain + supplier constraints'],
 trade:['Faster delivery → requirements compromise','More reuse → less control over evolution','Greater generality → lower understandability'],
 evidence:['Fit-gap analysis','Lifecycle/support evidence','Integration & regression tests','Licensing/maintainability record'],
 caption:'Adapted from Sommerville Ch.15: reuse landscape, selection factors and reuse strategies'
},
'16':{
 sections:['Components & component models','CBSE processes','Component composition'],
 concepts:['Independent component','Provides / requires interfaces','Component model & middleware','Composition + adapters'],
 mechanism:['Specify required services','Discover/evaluate components','Adapt interfaces/requirements','Compose, certify and test'],
 map:['CBSE for reuse','CBSE with reuse','Acquisition/management','Certification/repository'],
 trade:['More generality → harder understanding','More adaptation → weaker reuse benefit','More independence → stricter interface contracts'],
 evidence:['Interface/semantic contract','Component certification record','Adapter/composition tests','Dependency & fault-injection evidence'],
 caption:'Adapted from Sommerville Ch.16: component models, CBSE processes and composition'
},
'17':{
 sections:['Distributed systems','Client–server computing','Architectural patterns','Software as a service'],
 concepts:['Client / server processes','Logical layers','Distribution pattern','SaaS deployment'],
 mechanism:['Identify NFRs & state','Choose distribution pattern','Place layers/state/services','Test performance & failure behavior'],
 map:['Presentation','Data handling','Application processing','Database / transaction services'],
 trade:['More distribution → more failure modes','More replication → consistency complexity','More transparency → harder diagnosis'],
 evidence:['Load/latency tests','Failover/partition tests','Replication & consistency traces','Operational ownership + observability'],
 caption:'Adapted from Sommerville Ch.17: client–server layers, distributed patterns and SaaS'
},
'20':{
 sections:['System complexity','SoS classification','Reductionism & complex systems','SoS engineering','SoS architecture'],
 concepts:['Operational independence','Managerial independence','Emergent behavior','Evolution across constituent systems'],
 mechanism:['Classify the SoS/control reality','Identify stakeholders & interfaces','Design governance + architecture','Monitor emergence & evolution'],
 map:['Constituent systems','Independent owners','Shared interfaces/data','Cross-system governance'],
 trade:['More central control → less constituent autonomy','More coupling → more emergent risk','More standardization → slower independent evolution'],
 evidence:['Interface conformance','Cross-system traces','Change/governance records','Failure exercises & stakeholder acceptance'],
 caption:'Adapted from Sommerville Ch.20: complexity, classification, SoS engineering and architecture'
}};
const D=DATA[ch];
const slides=[...document.querySelectorAll('#stage .slide')];
if(!slides.length)return;
const byTitle=t=>slides.find(s=>(s.dataset.title||'').trim()===t);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cols=['#F0189A','#4FC6CB','#DDB27E','#8E7DEA','#4FBF8B'];
function flowSvg(labels,title){
 const n=labels.length,w=1180,h=220,g=18,bw=(w-80-g*(n-1))/n,x0=40;
 let boxes='';
 labels.forEach((lab,i)=>{const x=x0+i*(bw+g),c=cols[i%cols.length];boxes+=`<rect x="${x}" y="72" width="${bw}" height="92" rx="16" fill="#15121C" stroke="${c}" stroke-width="2.5"/><text x="${x+bw/2}" y="107" text-anchor="middle" fill="${c}" font-size="15" font-weight="800" font-family="Inter">${i+1}</text><foreignObject x="${x+10}" y="116" width="${bw-20}" height="40"><div xmlns="http://www.w3.org/1999/xhtml" style="font:700 16px/1.15 Inter;color:#F5F0EA;text-align:center;display:flex;align-items:center;justify-content:center;height:40px">${esc(lab)}</div></foreignObject>`;if(i<n-1)boxes+=`<line x1="${x+bw}" y1="118" x2="${x+bw+g-4}" y2="118" stroke="#DDB27E" stroke-width="2.5" marker-end="url(#a)"/>`;});
 return `<div class="isc-v3-diagram"><svg viewBox="0 0 1180 ${h}" role="img" aria-label="${esc(title)}"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#DDB27E"/></marker></defs><text x="590" y="37" text-anchor="middle" fill="#DDB27E" font-size="21" font-weight="800" font-family="Inter">${esc(title)}</text>${boxes}</svg><div class="isc-caption">${esc(D.caption)}</div></div>`;
}
function cards(items,kind='g4'){
 return `<div class="grid ${kind}">${items.map((x,i)=>`<div class="card"><div class="lab">${String(i+1).padStart(2,'0')}</div><div class="txt">${esc(x)}</div></div>`).join('')}</div>`;
}
function replaceArea(title,html,note){const s=byTitle(title);if(!s)return;const a=s.querySelector('.area');if(!a)return;a.innerHTML=(note?`<div class="isc-v3-note"><b>SOURCE-GROUNDED</b> ${esc(note)}</div>`:'')+html;}
replaceArea('The source spine',flowSvg(D.sections,'Chapter source spine'),'Core sections retained from Sommerville');
replaceArea('The reveal',cards(D.concepts,D.concepts.length===4?'g4':'g5'),'Key concepts before application');
replaceArea('Mechanism before vocabulary',flowSvg(D.mechanism,'Mechanism → decision chain'),'Mechanism, not vocabulary dumping');
replaceArea('Map the system before you judge',flowSvg(D.map,'Decision map'),'Map the system before choosing a verdict');
replaceArea('The attractive answer still has a cost',cards(D.trade,'g3'),'Every option carries a visible trade-off');
replaceArea('What would another professional inspect?',cards(D.evidence,'g2'),'Evidence must be inspectable by another professional');

function phase(slide){const t=(slide.dataset.title||'').toLowerCase();const ey=(slide.querySelector('.ey')?.textContent||'').toLowerCase();const z=t+' '+ey;if(z.includes('crisis')||t.includes('sign before'))return'CRISIS';if(z.includes('map')||t.includes('source spine')||t.includes('mechanism'))return'MAP';if(z.includes('trade-off')||z.includes('tradeoff'))return'TRADE-OFF';if(z.includes('evidence')||z.includes('known, unknown'))return'EVIDENCE';if(z.includes('verdict')||t.includes('leave with')||t.includes('ready for after-class'))return'VERDICT';return'';}
slides.forEach(s=>{const p=phase(s);if(p)s.dataset.iscPhase=p;const h=s.querySelector('h1');if(h){const len=h.textContent.trim().length;if(len>42)s.classList.add('isc-long-title');if(len>60)s.classList.add('isc-very-long-title');}});

function fits(s){const a=s.querySelector('.area');return (!a||a.scrollHeight<=a.clientHeight+2)&&s.scrollHeight<=s.clientHeight+2&&s.scrollWidth<=s.clientWidth+2;}
function tune(s){s.classList.remove('isc-compact-1','isc-compact-2','isc-compact-3');if(fits(s))return;for(const k of ['isc-compact-1','isc-compact-2','isc-compact-3']){s.classList.add(k);if(fits(s))break;}}
function tuneAll(){slides.forEach(s=>{if(s.classList.contains('on'))tune(s);});}
requestAnimationFrame(()=>requestAnimationFrame(tuneAll));
addEventListener('resize',()=>requestAnimationFrame(tuneAll));
const mo=new MutationObserver(()=>requestAnimationFrame(tuneAll));slides.forEach(s=>mo.observe(s,{attributes:true,attributeFilter:['class']}));
window.__ISCARB_LECTURE_STANDARD_V3__={chapter:ch,slides:slides.length,tune:tuneAll};
})();
