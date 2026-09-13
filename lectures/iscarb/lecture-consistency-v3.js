/* ISCARB consistency layer v3
   Keeps Chapter 10's teaching grammar stable across Chapters 12–17 and 20
   without replacing the source-grounded base curriculum. */
(function(){
'use strict';
const L=window.LECTURE;
if(!L||!Array.isArray(L.units)) return;
const ch=(new URLSearchParams(location.search).get('chapter')||'12');
const X={
'12':{
 coverage:[['SAFETY FOUNDATIONS','Safety-critical systems, safety vs reliability, unsafe reliable systems and normal accidents.'],['HAZARD-DRIVEN ANALYSIS','Hazard identification, assessment, fault-tree analysis and risk reduction.'],['SAFETY REQUIREMENTS','Safety specification and requirements derived from identified hazards.'],['SAFETY PROCESS','Safety engineering and assurance processes, hazard logs, reviews and regulation.'],['FORMAL ANALYSIS','Formal verification, model checking and static analysis as evidence—not guarantees.'],['SAFETY CASE','Claims, structured arguments and evidence for bounded release sign-off.']],
 process:[['IDENTIFY','Name hazards and accident paths.'],['CLASSIFY','Estimate likelihood × severity and the acceptance region.'],['REDUCE','Derive protection, detection and recovery requirements.'],['ASSURE','Maintain hazard logs, reviews, verification and safety-case evidence.']],
 build:[['HAZARD LOG ROW','Hazard · cause · likelihood/severity · mitigation · owner · status.'],['SAFETY REQUIREMENT','Write a concrete shall / shall-not rule with trigger and safe response.'],['VERIFICATION EVIDENCE','Name the test, analysis or review that checks the requirement.'],['SAFETY ARGUMENT','Connect claim → reasoning → evidence before sign-off.']],
 stress:'A newly observed interaction creates a hazardous state missing from the original hazard log. Does the release boundary still hold?'
},
'13':{
 coverage:[['SECURITY LEVELS','Infrastructure, application and operational security—and the organizational policies around them.'],['RISK LANGUAGE','Assets, threats, vulnerabilities, controls and loss must remain distinct.'],['RISK ASSESSMENT','Preliminary, design and operational risk assessment drive different decisions.'],['SECURITY REQUIREMENTS','Risk analysis and misuse cases become avoid, detect and mitigate requirements.'],['SECURE DESIGN','Layering, distribution, COTS choices and technology dependencies reshape attack surface.'],['PROGRAMMING & ASSURANCE','Secure programming, testing, validation and checklists provide evidence controls actually work.']],
 process:[['IDENTIFY ASSETS','Value, ownership and security property at stake.'],['MODEL THREATS','Misuse paths, attackers and plausible loss.'],['FIND VULNERABILITIES','Where the design or technology permits the threat.'],['CONTROL & ASSURE','Specify controls, then test and validate them against the threat.']],
 build:[['RISK TABLE','Asset → threat → vulnerability → control → residual risk.'],['MISUSE CASE','Show attacker intent, misuse path and affected security property.'],['SECURITY REQUIREMENT','Write an avoid/detect/mitigate requirement that can be tested.'],['ASSURANCE RECORD','Architecture review + test/checklist evidence + named owner.']],
 stress:'After approval, the identity provider announces a token-replay vulnerability. Does the original control boundary survive?'
},
'14':{
 coverage:[['RESILIENCE BASICS','Recognition, resistance, recovery and reinstatement around critical services.'],['CYBER RESILIENCE','Threats, controls, redundancy and diversity support survival under attack.'],['SOCIOTECHNICAL RESILIENCE','Human, organizational and technical layers interact during disruption.'],['DEFENSIVE LAYERS','Swiss-cheese reasoning exposes how multiple imperfect defenses combine.'],['PROCESS RESILIENCE','Operational processes and automation can both strengthen and weaken response.'],['SURVIVABILITY & DESIGN','Critical-service availability, survivability analysis and resilient architecture.']],
 process:[['DEFINE CRITICAL SERVICE','Decide what must continue.'],['RECOGNIZE','Detect disruption and its scope.'],['RESIST / RECOVER','Contain damage and restore minimum service.'],['REINSTATE','Return to normal only when evidence supports it.']],
 build:[['CRITICAL-SERVICE MAP','Service · dependency · failure effect · owner.'],['DEGRADED-MODE RULE','What continues, what may degrade, and for how long.'],['RECOVERY PLAYBOOK','Trigger · containment · recovery · reinstatement.'],['EXERCISE EVIDENCE','Test results, logs and named operational owner.']],
 stress:'A central dependency and its fallback fail together, while cached data is stale. Which resilience assumption has crossed its boundary?'
},
'15':{
 coverage:[['REUSE ECONOMICS','Benefits, risks and planning factors determine whether reuse is worthwhile.'],['FRAMEWORKS','Application frameworks, MVC and inversion of control shape adaptation.'],['PRODUCT LINES','Variation points and configuration create families of related systems.'],['APPLICATION REUSE','Whole-system reuse trades speed for fit and local control.'],['COTS & ERP','Commercial systems bring vendor, configuration and lifecycle dependencies.'],['INTEGRATION','Service interfaces, wrappers, wrapping and adaptation determine practical fit.']],
 process:[['FIND OPPORTUNITY','What can be reused rather than rebuilt?'],['EVALUATE FIT','Functional, quality, lifecycle and ownership fit.'],['CONFIGURE / ADAPT','Change only within an explicit adaptation boundary.'],['INTEGRATE & VERIFY','Prove the reused element works in the target context.']],
 build:[['REUSE DECISION','What to reuse, why, and what remains local.'],['FIT–GAP MATRIX','Required capability vs available capability and adaptation cost.'],['INTEGRATION CONTRACT','Interfaces, assumptions, responsibilities and tests.'],['EXIT TRIGGER','Condition that makes reuse no longer defensible.']],
 stress:'The selected vendor changes its API and support terms after adoption. Does the reuse decision remain fit?'
},
'16':{
 coverage:[['COMPONENT BASICS','Components, provided/required interfaces and independently deployable services.'],['COMPONENT MODELS','Standards and middleware define interaction and deployment assumptions.'],['FOR REUSE vs WITH REUSE','Building reusable components differs from assembling systems from them.'],['IDENTIFICATION & VALIDATION','Component identification and validation must check fit beyond the interface signature.'],['COMPOSITION','Sequential, hierarchical and additive composition need glue and adapters.'],['SEMANTICS & TRADE-OFFS','Semantic contracts, OCL-style constraints and quality trade-offs decide safe composition.']],
 process:[['SPECIFY NEED','Required services, semantics and quality constraints.'],['QUALIFY','Check component, dependencies and evidence.'],['ADAPT','Use adapters only within a stated semantic boundary.'],['COMPOSE & VERIFY','Test the composed behavior, not isolated pieces only.']],
 build:[['INTERFACE CONTRACT','Provided/required operations + semantic assumptions.'],['QUALIFICATION RECORD','Evidence that the component fits this context.'],['ADAPTER CONTRACT','What is translated and what cannot be hidden.'],['COMPOSITION TEST','End-to-end behavior under normal and failure cases.']],
 stress:'A syntactically compatible update changes a semantic assumption. Does the composition remain safe?'
},
'17':{
 coverage:[['DISTRIBUTION ISSUES','Transparency, openness, scalability, security, quality of service (QoS) and failure management.'],['INTERACTION MODELS','RPC/procedural interaction and message passing create different coupling and failure behavior.'],['MIDDLEWARE','Communication, naming and coordination services mask heterogeneity—but not every failure.'],['CLIENT–SERVER','Layering, thin/fat clients and multi-tier placement determine state and latency.'],['DISTRIBUTED PATTERNS','Master–slave, distributed components and peer-to-peer allocate responsibility differently.'],['SAAS & MULTI-TENANCY','Service delivery, configuration, tenancy and scaling shift ownership and evidence needs.']],
 process:[['PARTITION RESPONSIBILITY','Place services, computation and state.'],['CHOOSE INTERACTION','Synchronous call, message or peer interaction.'],['ADD MIDDLEWARE','Naming, communication, coordination and heterogeneity support.'],['ENGINEER FAILURE & QoS','Measure latency, loss, partition, recovery, security and scale.']],
 build:[['ARCHITECTURE DECISION','Topology + state placement + interaction style + rationale.'],['QoS BUDGET','Latency / throughput / availability target with operating envelope.'],['FAILURE RULE','What happens under timeout, partial failure or network partition.'],['OBSERVABILITY EVIDENCE','Traces, metrics, failover tests and tenant-isolation evidence.']],
 stress:'A regional partition causes high latency and conflicting writes while peak load rises. Which guarantees survive?'
},
'20':{
 coverage:[['SoS CHARACTERISTICS','Operational and managerial independence plus evolutionary development.'],['COMPLEXITY & REDUCTIONISM','Interactions, organizational complexity and failed reductionist assumptions.'],['CLASSIFICATION & GOVERNANCE','Directed, acknowledged, collaborative and virtual arrangements imply different authority.'],['SoS ENGINEERING','Independent owners, development processes and interface negotiation shape what is feasible.'],['INTEGRATION & TESTING','Staged deployment and cross-system testing must work without one controlling team.'],['ARCHITECTURE PATTERNS','Frameworks, data feeds, containers and trading arrangements manage integration and evolution.']],
 process:[['MAP CONSTITUENTS','Owners, missions, interfaces, dependencies and independent value.'],['CLASSIFY AUTHORITY','How much coordination can legitimately be imposed?'],['ARCHITECT INTEGRATION','Interfaces, shared services, containers or data-feed patterns.'],['EVOLVE & OBSERVE','Stage deployment and monitor emergent cross-system effects.']],
 build:[['CONSTITUENT MAP','System · owner · local mission · interface · dependency.'],['GOVERNANCE CHARTER','Who can change what, notification rules and conflict resolution.'],['STAGED DEPLOYMENT','Integration sequence + fallback when one constituent is absent.'],['EMERGENCE MONITOR','Cross-system test/metric that exposes unintended behavior after change.']],
 stress:'A constituent changes its interface and release schedule without accepting the SoS plan. Which governance boundary has failed?'
}}
const x=X[ch]; if(!x) return;
const old=Object.fromEntries(L.units.map(u=>[u.k,u]));
const clone=o=>JSON.parse(JSON.stringify(o));
const colors=['teal','mag','sand','violet','green'];
const items=a=>a.map((r,i)=>({c:colors[i%colors.length],lab:r[0],txt:r[1],src:'Sommerville Ch.'+ch}));
const take=(k,n,rule)=>{const u=clone(old[k]);u.k=n;if(rule)u.rule=rule;return u};
const U=[];
U.push(clone(old.TITLE));
U.push(take('R01','R01','RULE 01 · Enter through a consequential decision'));
U.push(take('R02','R02','RULE 02 · Map the chapter before details'));
U.push({k:'R03',phase:'UNDERSTAND / COVERAGE',rule:'RULE 03 · See the whole chapter',title:'Chapter coverage map',sub:'Six source clusters this lecture must touch before the final verdict.',blocks:[{t:'cards',cols:3,items:items(x.coverage)}],task:'Name one cluster you know and one you expect to be difficult.',timebox:'2 min',accent:'teal'});
U.push(take('R03','R04','RULE 04 · Make outcomes observable'));
U.push(take('R04','R05','RULE 05 · Predict before inspection'));
U.push(clone(old.X01));
U.push(take('R05','R06','RULE 06 · Do not collapse confusable concepts'));
U.push(clone(old.X02));
U.push(take('R06','R07','RULE 07 · Turn mechanisms into a procedure'));
U.push(take('R07','R08','RULE 08 · Use one decision grammar every week'));
U.push({k:'R09',phase:'PRACTISE / DECISION',rule:'RULE 09 · Build the Decision Card while learning',title:'Decision Card · fit, bound, act, evidence',sub:'The same four boxes repeat every week so the reasoning becomes automatic.',blocks:[{t:'cards',cols:4,items:[{c:'teal',lab:'FIT',txt:'Which chapter mechanism fits this case?',field:{id:'dc_fit',rows:2,ph:'The best-fit mechanism is…'}},{c:'sand',lab:'BOUND',txt:'Where does that fit stop?',field:{id:'dc_bound',rows:2,ph:'This fit stops when…'}},{c:'mag',lab:'ACT',txt:'What concrete engineering action follows?',field:{id:'dc_act',rows:2,ph:'The professional action is…'}},{c:'green',lab:'EVIDENCE',txt:'What inspectable artifact or measure proves it?',field:{id:'dc_evidence',rows:2,ph:'Evidence: …'}}]}],task:'Fill the four core reasoning boxes.',timebox:'4 min',accent:'mag'});
U.push(clone(old.X03));
U.push(take('R09','R10','RULE 10 · Put the cost on screen'));
U.push({k:'R11',phase:'PRACTISE / PROCESS',rule:'RULE 11 · Execute the chapter process',title:'From concept to engineering move',sub:'The position in the learning flow stays fixed; the domain mechanism changes.',blocks:[{t:'chain',items:x.process.map((r,i)=>({c:colors[i],lab:r[0],txt:r[1]}))}],task:'Point to the step where weak teams most often lose evidence.',timebox:'3 min',accent:'violet'});
U.push({k:'R12',phase:'PRACTISE / BUILD',rule:'RULE 12 · Build something inspectable',title:'What do you actually produce?',sub:'Turn the concept into an artifact another engineer can inspect.',blocks:[{t:'cards',cols:4,items:items(x.build)}],task:'Choose the artifact you would create first and explain why.',timebox:'3 min',accent:'violet'});
U.push({k:'R13',phase:'MASTER / EVIDENCE',rule:'RULE 13 · Evidence must be able to prove you wrong',title:'Evidence + counter-evidence',sub:'Confidence is not evidence. A stronger claim states what would reverse it.',blocks:[{t:'cards',cols:2,items:[{c:'teal',lab:'EVIDENCE',txt:'Name the best artifact, measurement or test from this chapter.',field:{id:'dc_evidence',rows:2,ph:'Inspectable evidence: …'}},{c:'mag',lab:'COUNTER-EVIDENCE',txt:'Name an observation that would force you to reopen the decision.',field:{id:'dc_counter',rows:2,ph:'I would reopen the decision if…'}}]}],task:'Make both lines observable—not opinions.',timebox:'3 min',accent:'sand'});
U.push(clone(old.X04));
U.push(take('R11','R14','RULE 14 · Transfer, do not repeat'));
U.push({k:'R15',phase:'MASTER / UNCERTAINTY',rule:'RULE 15 · Convert unknowns into monitors',title:'Known · unknown · monitor',sub:'An unknown becomes manageable only when a signal and trigger are named.',blocks:[{t:'cards',cols:3,items:[{c:'green',lab:'KNOWN',txt:'What source-grounded fact can you rely on now?'},{c:'violet',lab:'UNKNOWN',txt:'Which missing fact still matters to the verdict?',field:{id:'dc_uncert',rows:2,ph:'The strongest unknown is…'}},{c:'sand',lab:'MONITOR + TRIGGER',txt:'What observable signal tells you the boundary is under pressure?'}]}],task:'Turn one uncertainty into a measurable trigger.',timebox:'3 min',accent:'violet'});
U.push({k:'R16',phase:'MASTER / ACCOUNTABILITY',rule:'RULE 16 · Name the human owner',title:'Who can sign this?',sub:'Ownership must match the consequence.',blocks:[{t:'cards',cols:3,items:items([['TECHNICAL OWNER','Who owns the mechanism or implementation?'],['EVIDENCE OWNER','Who can attest that the evidence is valid?'],['RISK ACCEPTOR','Who is authorized to accept the residual consequence?']])}],task:'Name the role—not a vague “team.”',timebox:'2 min',accent:'mag'});
U.push(take('R13','R17','RULE 17 · Every verdict has a boundary'));
U.push(clone(old.X05));
U.push({k:'R18',phase:'DISTINGUISH / STRESS',rule:'RULE 18 · Stress the boundary',title:'Constraint mutation',sub:x.stress,blocks:[{t:'cards',cols:2,items:[{c:'mag',lab:'WHAT CHANGED?',txt:x.stress},{c:'teal',lab:'REFIT',txt:'Does the original boundary remain intact, come under pressure, or fail?',picker:{g:'refit',options:['RETAIN','REVISE','REPLACE']}}]}],task:'Change the verdict only if the boundary or evidence changed.',timebox:'4 min',accent:'mag'});
U.push(take('R14','R19','RULE 19 · Human sign-off is bounded'));
U.push(take('R15','R20','RULE 20 · Audit before you leave'));
U.push(take('R16','R21','RULE 21 · Retrieve, do not reread'));
U.push(clone(old.END));
L.units=U;
L.consistencyVersion='20260913-consistent3';
L.method='CRISIS → MAP → TRADE-OFF → EVIDENCE → VERDICT';
})();