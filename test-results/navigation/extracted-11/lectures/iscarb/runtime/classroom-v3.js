/* iSCARB shared classroom runtime. Authored hints are not AI grading.
 * Source availability, draft completeness, self-report and assessed competence
 * are deliberately different states. No responses are sent to a server.
 */
(()=>{'use strict';
const D=JSON.parse(document.getElementById('lecture-data').textContent),AHREF=D.assignmentHref||'https://adeebnoor.github.io/CPIT/fbr-submission.html?chapter='+D.chapter,ALABEL=D.assignmentLabel||'Open Assignment '+D.assignment,$=s=>document.querySelector(s),qa=s=>Array.from(document.querySelectorAll(s));
if(D.presentationMode==='single-canvas')document.body.classList.add('single-canvas');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const key=`iscarb:classroom:ch${D.chapter}:v3`,validField=k=>/^[a-z][a-z0-9_]{0,59}$/.test(k)&&!['constructor','prototype','__proto__'].includes(k);
// Story v3 + stage v4: one narrative series, act structure and in-class engagement over the same 20 slides.
const SERIES=window.ISCARB_STORY||null,STORY=SERIES&&(D.chapter>=(SERIES.firstChapter||0)||(SERIES.extraChapters||[]).includes(+D.chapter))?SERIES.chapters?.[D.chapter]||null:null;
if(STORY)document.documentElement.dataset.stage='v4';
const ACTS=(D.roadmap?.branches||[]).map((b,i)=>{const at=(b.units||[]).map(u=>D.slides.findIndex(s=>s.id===u)).filter(n=>n>=0);return {b,i,first:Math.min(...at),last:Math.max(...at)};}).filter(a=>Number.isFinite(a.first));
const TWIST_AT=D.slides.find(x=>x.twist)?.id||D.stations?.[2]?.at;
// req-v5 (lecture design requirements, 14 Oct 2026): glossary with first-use definitions (LANG-2/3), coverage table and
// study list (COV-1/3/5), transfer case (CASE-1/3), station rubrics (RUB-1/2/4), time budget and pace log (TIME-1..6),
// course-addition labels (KEEP-6) and split questions (LANG-4). All content comes from the lecture data.
const escRe=t=>t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const GLOSSARY=(D.glossary||[]).filter(g=>g.term&&g.short);
const GL_RE=GLOSSARY.length?new RegExp('(?<![\\w-])('+GLOSSARY.map(g=>escRe(g.term)).sort((a,b)=>b.length-a.length).join('|')+')(s|es)?(?![\\w-])','gi'):null;
const GL_TEST=GL_RE?new RegExp(GL_RE.source,'i'):null;
function slideStudentText(s){const parts=[s.title,s.takeaway,s.question,s.answer,s.question2,s.answer2,s.extra];(s.bullets||[]).forEach(b=>parts.push(Array.isArray(b)?b.join(' '):b));(s.rows||[]).forEach(r=>parts.push(r.join(' ')));(s.lists||[]).forEach(L=>parts.push(L.title,...(L.items||[])));return parts.filter(Boolean).join(' ');}
const firstUse={};
GLOSSARY.forEach(g=>{const re=new RegExp('(?<![\\w-])'+escRe(g.term)+'(s|es)?(?![\\w-])','i');const i=D.slides.findIndex(s=>re.test(slideStudentText(s)));if(i>=0){firstUse[g.term]=i;return;}const st=D.stations.find(x=>re.test([x.think,x.pair,x.write,x.hint].join(' ')));if(st)firstUse[g.term]=D.slides.findIndex(s=>s.id===st.at);});
function glossaryWrap(root,slideIndex,inModal){
 if(!GL_RE||!root)return;const nodes=[];
 const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>{const p=n.parentElement;if(!p||p.closest('pre,code,script,style,textarea,dfn,button,a,svg,.source-line,.gl-def,.gl-strip,.counter,.pace-chip,.tier-chip,.case-thread'))return NodeFilter.FILTER_REJECT;return GL_TEST.test(n.nodeValue)?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;}});
 while(w.nextNode())nodes.push(w.currentNode);
 const defined=new Set();
 nodes.forEach(n=>{const txt=n.nodeValue,frag=document.createDocumentFragment();let last=0,m;GL_RE.lastIndex=0;
  while((m=GL_RE.exec(txt))){const g=GLOSSARY.find(x=>x.term.toLowerCase()===m[1].toLowerCase());if(!g)continue;frag.append(txt.slice(last,m.index));
   const d=document.createElement('dfn');d.className='gl';d.tabIndex=0;d.textContent=m[0];d.dataset.def=g.short;if(g.ar)d.dataset.ar=g.ar;d.title=g.short+(g.ar?' · '+g.ar:'');d.setAttribute('aria-label',m[0]+': '+g.short);frag.append(d);
   const first=inModal?!(g.term in firstUse):firstUse[g.term]===slideIndex;
   if(first&&inModal&&!defined.has(g.term))defined.add(g.term);
   last=m.index+m[0].length;}
  frag.append(txt.slice(last));n.replaceWith(frag);});
 if(defined.size){const t=GLOSSARY.filter(g=>defined.has(g.term));root.insertAdjacentHTML('beforeend',`<p class="gl-strip gl-def"><b>NEW TERMS</b>${t.map(g=>`<span>${esc(g.term)} = ${esc(g.short)}${g.ar?' · '+esc(g.ar):''}</span>`).join('')}</p>`);}  // modal text stays contiguous; terms are listed after it
}
function termsStrip(slideIndex){const t=GLOSSARY.filter(g=>firstUse[g.term]===slideIndex);if(!t.length)return '';return `<p class="gl-strip"><b>NEW TERMS</b>${t.map(g=>`<span><dfn class="gl" tabindex="0" data-def="${esc(g.short)}"${g.ar?` data-ar="${esc(g.ar)}"`:''} title="${esc(g.short)}${g.ar?' · '+esc(g.ar):''}">${esc(g.term)}</dfn> = ${esc(g.short)}${g.ar?' · '+esc(g.ar):''}</span>`).join('')}</p>`;}
function tierChip(s){if(!PRESENTER||!s||!s.tier)return '';return `<span class="tier-chip ${esc(s.tier)}" title="${s.tier==='optional'?'Optional: drop first if the lecture runs over time':'Core: part of the planned lecture'}">${s.tier==='optional'?'OPTIONAL':'CORE'} · ${esc(s.minutes||0)} min</span>`;}
function addedTag(s){return s&&s.added?' · COURSE ADDITION · NOT IN THE SOURCE':'';}
function figsBlock(s){if(!s||!s.sourceFigs||!s.sourceFigs.length)return '';const F=window.ISCARB_SOURCE_FIGURES||{};const vec=n=>{for(const e of Object.values(F)){if(+e.chapter!==+D.chapter)continue;const v=(e.variants||[]).find(x=>+x.sourceSlide===+n);if(v)return v.src;}return '';};return `<section class="src-list src-figs"><h3>FROM THE SOURCE · FIGURE${s.sourceFigs.length>1?'S':''}</h3><div class="src-fig-row">${s.sourceFigs.map(n=>{const v=vec(n);return v?`<a class="src-fig" href="${esc(v)}" target="_blank" rel="noopener"><img src="${esc(v)}" alt="Original source figure, slide ${esc(n)}"><span>Source slide ${esc(n)} · open full size</span></a>`:`<a class="src-fig" href="sources/Ch${D.chapter}-Study.html#source-slide-${esc(n)}" target="_blank" rel="noopener"><span>Source slide ${esc(n)} · open the original slide in the source ledger</span></a>`;}).join('')}</div></section>`;}
function listsBlock(s){if(!s||((!s.lists||!s.lists.length)&&!(s.sourceFigs&&s.sourceFigs.length)))return '';if(!s.lists||!s.lists.length)return `<div class="src-lists">${figsBlock(s)}</div>`;return `<div class="src-lists">${s.lists.map(L=>`<section class="src-list"><h3>FROM THE SOURCE · SLIDE ${esc(L.source)} · ${esc(L.title||'')}</h3><ol>${(L.items||[]).map(i=>`<li>${esc(i)}</li>`).join('')}</ol></section>`).join('')}${figsBlock(s)}</div>`;}
// GATE-1..5: in self-study the chapter is complete only after the transfer case is solved.
// The student writes a reason first; a wrong choice explains and allows another try. Off in presenter mode.
function gateOn(){return !PRESENTER&&!!D.transfer?.check;}
function gateSolved(){return !gateOn()||state.fields.gate_solved==='1';}
function gateButton(){return gateOn()?`<button class="gate-btn${gateSolved()?' done':''}" data-open="GATE">${gateSolved()?'Transfer check · solved ✓':'Transfer check · required to complete the chapter'}</button>`:'';}
function transferCheck(msg){if(!gateOn()){modal('Transfer check','<p>The transfer check is for self-study. In class, discuss the transfer case together.</p>');return;}
 const t=D.transfer,c=t.check,f=state.fields,line=(f.gate_line||'').trim(),solved=gateSolved(),pick=f.gate_pick!==undefined&&f.gate_pick!==''?Number(f.gate_pick):null;
 modal('Transfer check · '+t.title,`<p>${kindTag(t.kind||(t.fictional?'fictional':'source'))} ${esc(t.text)}</p><p class="tc-q"><b>${esc(t.question)}</b></p>
 <label class="commit-box"><span>YOUR REASON · one line, before you choose</span><textarea data-field="gate_line" data-gate-line rows="1" maxlength="400" placeholder="Why do you think so?">${esc(f.gate_line||'')}</textarea></label>
 <div class="tc-opts" role="group" aria-label="Choose one answer">${c.options.map((o,k)=>`<button data-gate-pick="${k}" class="${pick===k?(k===c.answer?'right':'wrong'):''}"${line?'':' disabled'}>${'ABC'[k]} · ${esc(o)}</button>`).join('')}</div>
 <div class="tc-result" aria-live="polite">${pick===null?'<p class="small">Write your reason first; then choose. A wrong choice shows why, and you can try again.</p>':`<p class="${pick===c.answer?'tc-right':'tc-wrong'}"><b>${pick===c.answer?'Correct.':'Not this one.'}</b> ${esc(c.why[pick])}</p>${pick===c.answer?`<p class="you-wrote"><b>Your reason:</b> ${esc(line)}</p><p><b>Model answer.</b> ${esc(t.answer)}</p>`:'<p class="small">Try another option. Your reason stays as you wrote it; you may edit it.</p>'}`}</div>
 <p class="small">${solved?'Solved on this device. In this browser, the course page now lets you mark this chapter as reviewed.':'Until you solve it, the chapter shows “Transfer case not solved”.'} Tries so far: ${esc(f.gate_tries||'0')}.</p>`);}
function transferBlock(s){const t=D.transfer;if(!t||!s.transfer)return '';return `${gateButton()}<div class="transfer-case"><span>TRANSFER CASE · DIFFERENT CASE, SAME CONCEPT</span>${kindTag(t.kind||(t.fictional?'fictional':'source'))}<b>${esc(t.title)}</b><p>${esc(t.text)}</p>${t.source?`<small>${esc(t.source)}</small>`:''}</div>`;}
/* Before the assignment (Chapters 15, 16, 17, 20): run 1 is green, then one line the student did not write changes. */
function theirBlock(s){const T=D.their;if(!T||T.at!==s.id)return '';const ck='commit_their';return `<div class="their-block"><p class="ey">BEFORE THE ASSIGNMENT · THEIR CHANGE</p><pre class="their-run">${esc(T.run1)}\n- ${esc(T.before)}\n+ ${esc(T.after)}   ← ${esc(T.who)}</pre><p class="their-q"><b>${esc(T.question)}</b></p>${commitBox(ck)}<div class="buttons"><button data-their-save data-commit-for="${ck}"${commitReady(ck)?'':' disabled'}>Save my prediction</button>${skipBtn(ck)}</div><p class="their-next small" hidden>Assignment ${esc(String(D.assignment||''))} runs this change as run 3. Check your prediction there.</p></div>`;}
function yourCall2(s){if(!s.question2)return '';const ck=commitKey(s.id,2);return `<div class="question your-call q2"><p class="question-text"><b>YOUR CALL · 2</b>${esc(s.question2)}</p>${commitBox(ck)}<div class="actions"><div class="buttons"><button class="think-btn" data-think="30">Think · 30 s</button><button data-answer2="${esc(s.id)}" data-commit-for="${ck}" aria-expanded="false"${commitReady(ck)?'':' disabled'}>Reveal answer</button>${skipBtn(ck)}</div></div><div class="inline-answer" hidden><div class="you-wrote-slot"></div><b>One defensible answer · after you have committed yours</b><p>${esc(s.answer2||'')}</p><small>Illustrative, not the only acceptable wording or a grade.</small></div></div>`;}
function rubricPanel(st){const rb=st.rubric;if(!rb||!rb.criteria)return '';return `<details class="station-rubric"><summary>How this is judged · rubric with a strong and a weak example</summary><table><thead><tr><th>Criterion</th>${rb.criteria[0].levels.map(l=>`<th>${esc(l[1])} · ${esc(l[0])}</th>`).join('')}</tr></thead><tbody>${rb.criteria.map(c=>`<tr><th scope="row">${esc(c.name)}</th>${c.levels.map(l=>`<td>${esc(l[2])}</td>`).join('')}</tr>`).join('')}</tbody></table><div class="rub-ex"><div class="strong"><b>Strong example</b><p>${esc(rb.strong?.text||'')}</p><small>Why: ${esc(rb.strong?.why||'')}</small></div><div class="weak"><b>Weak example</b><p>${esc(rb.weak?.text||'')}</p><small>Why: ${esc(rb.weak?.why||'')}</small></div></div><p class="small">${esc(rb.marks||'')} ${esc(rb.other||'')}</p></details>`;}
function coverageTable(){const cov=D.coverage||[];if(!cov.length)return '';const n={slide:0,full:0,no:0};cov.forEach(c=>{n[c.cls]=(n[c.cls]||0)+1;});const where={slide:'On a classroom slide',full:'Full explanation only',no:'Not covered'};return `<h3>Every original slide · ${cov.length}</h3><p class="small">${n.slide} on classroom slides · ${n.full} in a full explanation only · ${n.no} not covered, each with its reason. Reading-list slides are marked ★.</p><div class="table-scroll"><table class="coverage-table"><tr><th>#</th><th>Original slide</th><th>Where</th><th>Classroom slide or reason</th></tr>${cov.map(c=>`<tr class="cov-${esc(c.cls)}"><td>${c.n}${c.kind?' ★':''}</td><td><a href="sources/Ch${D.chapter}-Study.html#source-slide-${c.n}" target="_blank" rel="noopener">${esc(c.title||'')}</a></td><td>${esc(where[c.cls]||c.cls||'')}</td><td>${c.cls==='no'?esc(c.reason||''):c.unit?jumpButton(c.unit):''}</td></tr>`).join('')}</table></div>`;}
function studyList(){const L=D.studyList||[];modal('What to study for the exam',`<div class="callout">Examinable content that is not on the classroom slides. Each item links to the original slides and the textbook pages. The classroom slides, their full explanations and the required readings are examinable too.</div><ol class="study-list">${L.map(it=>`<li><b>${esc(it.topic)}</b>${it.note?`<p>${esc(it.note)}</p>`:''}<p class="small">Original slides: ${(it.sources||[]).map(n=>`<a href="sources/Ch${D.chapter}-Study.html#source-slide-${n}" target="_blank" rel="noopener">${n}</a>`).join(', ')}${it.book?(it.book.page?` · Textbook ${esc(it.book.label||'')}: <a href="sources/Ch${D.chapter}-Study.html#book-page-${it.book.page}" target="_blank" rel="noopener">PDF page ${esc(it.book.page)}</a>`:` · Textbook section ${esc(it.book.label||'')}${it.book.where?` · ${esc(it.book.where)}`:''}`):''}</p></li>`).join('')}</ol><div class="actions">${button('Required source review','READING')}${button('Five-objective practice','QUIZ')}${button('Source coverage map','COVERAGE')}</div>`);}
function paceLog(){try{return JSON.parse(localStorage.getItem('iscarb-pace-log')||'[]');}catch(e){return [];}}
function recordPace(){if(!PRESENTER||!PLAN||!paceStart())return;const actual=Math.round((Date.now()-paceStart())/60000);if(actual<5)return;const log=paceLog().filter(x=>!(x.chapter===D.chapter&&x.date===new Date().toISOString().slice(0,10)));log.push({chapter:D.chapter,date:new Date().toISOString().slice(0,10),planned:Math.round(PLAN.total),actual,mode:PLAN.mode});try{localStorage.setItem('iscarb-pace-log',JSON.stringify(log.slice(-60)));}catch(e){}}
setInterval(()=>{const c=document.querySelector('.pace-chip');if(c&&PLAN)c.outerHTML=paceChip();},20000);
let extraIndex=null;
let stationSeconds=180,savedOK=true,state={fields:{},seen:[],quiz:{},ai:{},self:{},votes:{},gut:{},theme:'night'},index=0,stationMode=false,voteMode=null,voteStage=0,quizIndex=0,returnFocus=null;
try{const s=JSON.parse(localStorage.getItem(key)||'null');if(s&&s.schema==='iscarb-classroom-v3'&&s.chapter===D.chapter){state={...state,...sanitize(s).state};}}catch(e){savedOK=false;}
let remaining=180,deadline=0,ticker=null,nationalIndex=null;
// Presenter mode (Faculty-Presenter.html or ?presenter=1) shows instructor notes; students do not see them.
const PRESENTER=(()=>{try{const q=new URLSearchParams(location.search);if(q.has('presenter'))sessionStorage.setItem('iscarb-presenter',q.get('presenter')==='0'?'0':'1');return sessionStorage.getItem('iscarb-presenter')==='1';}catch(e){return /[?&]presenter=1\b/.test(location.search);}})();
if(PRESENTER)document.body.classList.add('presenter');
// Pace v1: a 50-minute plan is the presenter default (&pace=60 or &pace=full to change). It chooses which
// class votes and stations fit, and shows the planned finish minute for each slide against elapsed time.
const PACE=(()=>{if(!PRESENTER)return null;let p='core';try{const q=new URLSearchParams(location.search).get('pace');if(q)sessionStorage.setItem('iscarb-pace',q);p=sessionStorage.getItem('iscarb-pace')||'core';}catch(e){}return p==='full'?'full':'core';})();
function buildPlan(mode){
 // TIME-1/2/3: the plan is the sum of the data's minutes for core slides, votes and stations (pace=full adds the optional ones).
 const full=mode==='full',inc=x=>full||x.tier==='core',acts=D.activities||[],stations=D.stations||[];let t=0;
 const end=D.slides.map(s=>{let m=inc(s)?(Number(s.minutes)||0):0;acts.filter(a=>a.at===s.id&&inc(a)).forEach(a=>m+=Number(a.minutes)||0);stations.filter(st=>st.at===s.id&&inc(st)).forEach(st=>m+=Number(st.minutes)||0);t+=m;return t;});
 const voteActs=acts.filter(a=>inc(a)&&/^VOTE/i.test(a.id)).map(a=>ACTS.findIndex(x=>(x.b.units||[]).includes(a.at))).filter(i=>i>=0);
 return {B:Number(D.lectureMinutes)||50,total:t,voteActs,stationNos:stations.filter(st=>inc(st)).map(st=>st.no),end,mode};
}
const PLAN=PACE&&D.slides.some(s=>s.minutes)?buildPlan(PACE):null;
const paceKey='iscarb-pace-start-ch'+D.chapter;
function paceStart(){try{return Number(sessionStorage.getItem(paceKey))||0;}catch(e){return 0;}}
function paceHelp(){return `<tr><th>Lesson pace</th><td>${PLAN?`${PLAN.mode==='full'?'Full plan':'Core plan'}: ${Math.round(PLAN.total)} planned minutes of ${PLAN.B}; class votes after acts ${PLAN.voteActs.map(i=>i+1).join(' and ')||'none'}; stations ${PLAN.stationNos.length?PLAN.stationNos.join(', ')+' planned, others':'are'} optional. Add &amp;pace=full to the address to include the optional slides and stations.`:'Open presenter mode for the time plan.'} The chip beside the slide number shows the planned finish and the actual elapsed time; click it to restart the clock from here. Optional slides are marked; drop them first when over time, never a think point or the assumption-change slide.</td></tr>`;}
function paceChip(){
 if(!PLAN)return '';
 const start=paceStart(),plannedFrom=index?PLAN.end[index-1]:0,plannedTo=PLAN.end[index];
 let state='',label='actual: clock starts when you leave the cover';
 if(start){const el=(Date.now()-start)/60000,d=Math.round(el-plannedFrom);label=`actual ${Math.floor(el)} min`;state=d>=3?'behind':d<=-3?'ahead':'on';label+=state==='behind'?` · ${d} min behind`:state==='ahead'?` · ${-d} min ahead`:' · on time';}
 return `<button class="pace-chip ${state}" data-pace-reset title="Planned finish for this slide (${Math.round(PLAN.total)} planned minutes of ${PLAN.B}). Click to restart the clock.">⏱ planned ${Math.round(plannedTo)} / ${PLAN.B} · ${label}</button>`;
}
const quizOrder={};
function shuffledIndexes(n,i){if(!quizOrder[i]){const a=[...Array(n).keys()];for(let k=n-1;k>0;k--){const j=Math.floor(Math.random()*(k+1));[a[k],a[j]]=[a[j],a[k]];}quizOrder[i]=a;}return quizOrder[i];}
function installNELCShortcut(){const top=document.querySelector('.topnav');if(!top||document.getElementById('nelcBtn'))return;top.insertAdjacentHTML('beforeend','<button id="readinessBtn" class="nelc-shortcut" data-open="READINESS">Jaheziah readiness</button><button id="nelcBtn" class="nelc-shortcut" data-open="NELC" title="Saudi national AI-supported learning design alignment">NELC alignment</button>');}
installNELCShortcut();
const profileLink='<a class="lecture-profile" href="https://adeebnoor.github.io/">About &amp; contact ↗</a>';
$('.footer-left').insertAdjacentHTML('beforeend',profileLink);
const labels={claim:'CLAIM · what you say is true',evidence:'EVIDENCE · what another person can check',warrant:'REASON · why the mechanism supports your claim',uncertainty:'UNCERTAINTY · what you are not sure of',counter:'COUNTER-EVIDENCE · the new fact against your claim',verdict:'VERDICT',owner:'DECISION OWNER',reviewer:'EVIDENCE REVIEWER',signoff:'SIGN-OFF ROLE',initial:'INITIAL DECISION',revision:'REVISED DECISION',ai_disclosure:'AI DISCLOSURE / INDEPENDENT CHECK',constraint:'CONSTRAINT',derive:'DERIVE',principle:'NAME THE PRINCIPLE',prediction:'PREDICT',known:'KNOWN',unknown:'UNKNOWN',monitor:'MONITOR',architecture:'ARCHITECTURE / IMPLEMENTATION',practice:'CONTEMPORARY PRACTICE',workload:'WORKLOAD / HANDOVER',local_context:'LOCAL CONTEXT / AUTHORITY',evidence_gap:'EVIDENCE GAP',self_level:'SELF-PLACEMENT / REASON'};
function pack(){return {schema:'iscarb-classroom-v3',chapter:D.chapter,release:D.release,exportedAt:new Date().toISOString(),state};}
function save(){try{localStorage.setItem(key,JSON.stringify(pack()));savedOK=true;}catch(e){savedOK=false;}qa('[data-save-status]').forEach(e=>e.textContent=savedOK?'Draft saved on this device · not submitted or graded':'Local saving unavailable · export a backup before leaving');}
function field(k,label,ph='',value){return `<label class="field"><span>${esc(label||fieldLabel(k))}</span><textarea data-field="${esc(k)}" maxlength="15000" placeholder="${esc(ph)}">${esc(value??state.fields[k]??'')}</textarea></label>`;}
function button(label,open,cls=''){return `<button class="${cls}" data-open="${esc(open)}">${esc(label)}</button>`;}
function jumpButton(k,label){return `<button data-jump="${esc(k)}">${esc(label||titleOf(k))}</button>`;}
function titleOf(k){return D.slides.find(s=>s.id===k)?.title||({RULES:'20-rule map',CARD:'Decision card',READING:'Required source review',QUIZ:'Five-objective practice',STUDY:'What to study for the exam',READINESS:'NCAAA / Jaheziah',NELC:'NELC alignment',RUBRIC:'Four-level rubric',HSTACK:'H-Stack',PREDICT:'Prediction',MONITOR:'Known / Unknown / Monitor',AI:'AI gate',PORTFOLIO:'Portfolio and assignment',EVIDENCE:'Evidence policy',LOCAL:'Saudi context',PRACTICE:'Contemporary practice',WELLBEING:'Practitioner wellbeing',BRIDGE:'Implementation annotation'}[k]||k);}
function sourceLink(s,label='Open source detail'){let a=s.sourceStart||firstNumber(s.sourceRange)||1;return `<a href="sources/Ch${D.chapter}-Study.html#source-slide-${a}" target="_blank" rel="noopener">${esc(label)}</a>`;}
function firstNumber(s){return Number(String(s||'').match(/\d+/)?.[0]||1);}
function ref(s){return s.sourceLabel|| (s.sourceRange?`Sommerville Ch.${D.chapter} · source slides ${s.sourceRange}`:'Course example · fictional case');}
function points(ps){return `<ul class="points">${(ps||[]).map(p=>`<li><strong>${esc(p[0])}.</strong> ${esc(p[1])}</li>`).join('')}</ul>`;}
function table(v){return `<table class="table-main"><thead><tr>${(v.heads||['CONCEPT','MEANING']).map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${v.rows.map(r=>`<tr>${r.map((x,i)=>`<${i?'td':'th'}${i?'':' scope="row"'}>${esc(x)}</${i?'td':'th'}>`).join('')}</tr>`).join('')}</tbody></table>`;}
function classroomRedraw(s){
 const items=(s.nodes?.length?s.nodes:(s.bullets||[]).map(p=>[p[0],p[1]||''])).filter(Boolean).slice(0,5);
 if(!items.length)return '';
 const cls='redraw-count-'+Math.min(items.length,5);
 return `<div class="figure-button classroom-redraw-wrap">
  <div class="classroom-redraw ${cls}" role="img" aria-label="Projection-safe redesign of ${esc(s.title)}">
   <span class="redraw-kicker">PROJECTION-SAFE REDESIGN · SOURCE-GROUNDED</span>
   <span class="redraw-title">${esc(s.title)}</span>
   <span class="redraw-flow">
    ${items.map((n,i)=>`<span class="redraw-node"><i>${i+1}</i><b>${esc(n[0])}</b>${n[1]?`<small>${esc(n[1])}</small>`:''}</span>`).join('')}
   </span>
   <span class="redraw-source-note">Redrawn for classroom legibility; meaning remains anchored to the preserved source figure.</span>
   <button class="redraw-open" type="button" data-image="${esc(s.figure)}" data-caption="${esc(s.caption||s.title)}" aria-label="Open preserved original source figure: ${esc(s.title)}">View preserved original · native resolution ↗</button>
  </div>
 </div><p class="caption">${esc(s.caption||'Resolution-independent classroom redesign · preserved source available at native resolution')}</p>`;
}
function sourceVector(s){const entry=window.ISCARB_SOURCE_FIGURES?.[s.figure];if(!entry)return '';return `<div class="source-vector-panel">${entry.variants.length>1?`<div class="vector-tabs" aria-label="Source figures">${entry.variants.map((v,i)=>`<button data-vector-tab="${i}" aria-pressed="${i===0}">${v.label?esc(v.label):`Source ${v.sourceSlide}${i===0?' · activities':' · planning'}`}</button>`).join('')}</div>`:''}${entry.variants.map((v,i)=>`<button class="figure-button source-vector" data-vector-pane="${i}" ${i?'hidden':''} data-image="${esc(v.src)}?v=20260928-campus-v3" data-caption="${esc(s.title)} · ${v.teaching?`teaching diagram (source slide ${v.sourceSlide} shows OR gates only)`:`original source slide ${v.sourceSlide}`}" data-vector="1" aria-label="Enlarge ${v.teaching?'teaching':'original vector'} figure: ${esc(s.title)}"><img src="${esc(v.src)}?v=20261004-andor" alt="${esc(s.title)} · ${v.teaching?'teaching diagram with AND and OR gates and a common cause':`original diagram from source slide ${v.sourceSlide}`}" decoding="async"></button>`).join('')}<p class="caption">${entry.variants.some(v=>v.teaching)?'Teaching diagram (AND + OR) · original source figure in the second tab · select to enlarge':'Original source diagram · vector quality · select to enlarge'}</p></div>`;}
// When a slide has no figure, table or comparison, its cards and its bullet list said the same thing twice
// (often as label-only cards). Merge them: one card per idea, label plus meaning.
function mergedCards(s){
 if(s.rows||s.visual?.rows||s.approaches||s.figure||s.banner)return '';
 const bullets=(s.bullets||[]).filter(b=>Array.isArray(b)&&b[0]);if(!bullets.length)return '';
 const norm=t=>String(t||'').toLowerCase().replace(/^\s*\d+\s*·\s*/,'').replace(/[^a-z0-9]+/g,' ').trim();
 const nodes=s.nodes||[];
 if(nodes.length){const labels=new Set(bullets.map(b=>norm(b[0])));if(!nodes.every(n=>labels.has(norm(n[0]))))return '';}
 const numbered=nodes.length&&/^\s*\d+\s*·/.test(nodes[0][0]);
 return `<ul class="concepts merged" style="--cards:${Math.min(bullets.length,5)}">${bullets.map((b,i)=>`<li class="concept"><b>${numbered?`${i+1} · `:''}${esc(b[0])}</b><span>${esc(b[1]||'')}</span></li>`).join('')}</ul>`;
}
function visual(s){if(s.rows)return table(s);if(s.visual?.rows)return table(s.visual);if(s.approaches)return `<div class="two-approaches">${s.approaches.map(a=>`<section class="approach"><h2 class="approach-label">${esc(a.label)}</h2><p>${esc(a.title||'')}</p><div class="arrow-chain">${(a.nodes||[]).map(n=>`<span>${esc(n)}</span>`).join('')}</div><p>${esc(a.text||'')}</p></section>`).join('')}</div>`;
if(s.figure&&window.ISCARB_SOURCE_FIGURES?.[s.figure])return sourceVector(s);
if(s.figure){if(/\.(?:png|jpe?g|webp)(?:$|[?#])/i.test(s.figure))return classroomRedraw(s);return `<button class="figure-button" data-image="${esc(s.figure)}" data-caption="${esc(s.caption||s.title)}" aria-label="Enlarge figure: ${esc(s.title)}"><img src="${esc(s.figure)}" alt="${esc(s.caption||s.title)}" decoding="async"></button><p class="caption">${esc(s.caption||'Original source figure · select to enlarge')}</p>`;}
let ns=s.nodes?.length?s.nodes:(s.bullets||[]).slice(0,3).map(p=>[p[0],'']);return `<div class="concepts ${s.flow?'flow':''}">${ns.map(n=>`<div class="concept"><b>${esc(n[0])}</b>${n[1]?`<span>${esc(n[1])}</span>`:''}</div>`).join('')}</div>`;}
// Readable presentation sections preserve all authored content and the 20-slide sequence.
let sectionIndex=0,sectionNodes=[];
function readingLayout(){return document.body.classList.contains('reading')||matchMedia('(max-width:1000px), (max-height:620px)').matches;}
function sectionNode(label,nodes){const e=document.createElement('section');e.className='lecture-section';e.dataset.sectionLabel=label;e.setAttribute('aria-label',label);nodes.filter(Boolean).forEach(n=>e.append(n));return e;}
function buildReadable(s){
 const main=$('#chapter-main');sectionIndex=0;sectionNodes=[];
 const heading=main.querySelector('.heading');if(!heading||stationMode)return;
 if(D.presentationMode==='single-canvas'){main.classList.add('single-canvas-slide');return;}
 const get=sel=>main.querySelector(sel),groups=[];
 const add=(label,nodes)=>{const live=nodes.filter(Boolean);if(live.length)groups.push(sectionNode(label,live));};
 if(s.id==='TITLE'){add('Start here',[get('.hero'),get('.scope-note')]);}
 else if(s.id==='MAP'){
  const cases=document.createElement('div');cases.className='map-connections';
  main.querySelectorAll('.map-step').forEach(step=>{const c=document.createElement('section');c.className='connection-card';const title=document.createElement('h3');title.textContent=step.querySelector('strong').textContent;c.append(title);step.querySelectorAll('.step-case,.step-lens').forEach(n=>c.append(n));cases.append(c);});
  const storyContext=get('.map-question p');
  if(storyContext)storyContext.remove();
  add('Concept map',[get('.map-question'),get('.concept-path'),get('.mind-link')]);
  add('Your chapter tasks',[get('.student-roadmap'),get('.map-bottom')]);
  add('Story connections',[storyContext,cases]);
 }else if(s.id==='START'){
  const situation=get('.story-grid section');
  if(situation)situation.classList.add('story-situation');
  add('The scenario',[get('.story-head'),situation]);
  add('Your decision',[get('.story-grid')]);
  add('AI context & route',[get('.story-lens'),get('.story-route'),get('.story-note'),get('.story-action')]);
 }else if(s.id==='END'){
  const hero=get('.end-hero'),copy=get('.end-copy');
  const tasks=document.createElement('div');tasks.className='closing-tasks';
  copy.querySelectorAll('.end-required,.end-boundary,.end-disclosure,.actions').forEach(n=>tasks.append(n));
  add('What you can now do',[hero]);add('Finish the chapter',[tasks]);
 }else{
  const v=get('.visual'),meaning=get('.meaning'),tableEl=v?.querySelector('table');
  if(tableEl&&tableEl.tBodies[0].rows.length>4){
   const rows=[...tableEl.tBodies[0].rows];
   for(let i=0;i<rows.length;i+=3){const wrap=document.createElement('div');wrap.className='visual';const tableCopy=tableEl.cloneNode(true);tableCopy.tBodies[0].replaceChildren(...rows.slice(i,i+3));wrap.append(tableCopy);const takeaway=get('.takeaway');add('Explore '+(i/3+1),[takeaway?.cloneNode(true),wrap]);}
  }else add('Explore',[get('.takeaway'),v]);
  add('Understand',[meaning?.querySelector('.points li')?meaning:null,meaning?.contains(get('.src-lists'))?null:get('.src-lists')]);
  add('Apply & discuss',[get('.case-thread'),get('.ai-banner'),get('.ai-lens'),get('.transfer-case'),get('.question'),get('.question.q2')]);
 }
 // Keep unclassified authored blocks visible rather than dropping them.
 const remaining=[...main.children].filter(n=>n!==heading&&!groups.includes(n)&&!n.matches('.body-grid,.takeaway'));
 if(remaining.length)add('More',[...remaining]);
 [...main.children].filter(n=>n!==heading).forEach(n=>n.remove());
 const nav=document.createElement('nav');nav.className='section-tabs';nav.setAttribute('aria-label','Sections in this slide');
 const stage=document.createElement('div');stage.className='lecture-stage';
 groups.forEach((g,i)=>{g.id='lecture-section-'+i;stage.append(g);const b=document.createElement('button');b.dataset.slideSection=i;b.textContent=g.dataset.sectionLabel;b.setAttribute('aria-controls',g.id);nav.append(b);});
 if(groups.length>1)main.append(nav);main.append(stage);sectionNodes=groups;showSection(0,false);
 // Overflow is an explicit readable fallback, never a smaller font or clipped text.
 requestAnimationFrame(()=>{if(sectionNodes===groups)checkSectionFit();});
}
function showSection(n,focus=false){
 if(n<0||n>=sectionNodes.length)return;sectionIndex=n;
 const reading=readingLayout();sectionNodes.forEach((s,i)=>{s.hidden=!reading&&i!==n;});
 qa('[data-slide-section]').forEach(b=>{const on=+b.dataset.slideSection===n;b.setAttribute('aria-pressed',String(on));b.classList.toggle('active',on);});
 $('#prevBtn').disabled=index===0&&n===0;$('#nextBtn').disabled=index===D.slides.length-1&&n===sectionNodes.length-1;
 $('#prevBtn').title=n?'Previous section':'Previous slide';$('#nextBtn').title=n<sectionNodes.length-1?'Next section':'Next slide';
 $('#live').textContent=`Slide ${index+1} of ${D.slides.length}: ${D.slides[index].title}. ${sectionNodes[n].dataset.sectionLabel}, section ${n+1} of ${sectionNodes.length}.`;
 if(focus){sectionNodes[n].setAttribute('tabindex','-1');sectionNodes[n].focus({preventScroll:true});}
 checkSectionFit();
}
function checkSectionFit(){
 const stage=$('.lecture-stage');if(!stage||readingLayout())return;
 const current=sectionNodes[sectionIndex];if(!current)return;
 const footer=$('.footerbar').getBoundingClientRect();
 const overflow=current.scrollHeight>stage.clientHeight+2||[...current.querySelectorAll('p,li,td,th,img,button')].some(e=>e.getBoundingClientRect().bottom>footer.top-8);
 stage.classList.toggle('needs-scroll',overflow);
}
function advanceSection(delta){
 if(extraIndex!==null){const n=extraIndex+delta;if(n>=0&&n<EXTRAS.length){renderExtra(n);return;}const back=n<0;extraIndex=null;go(back?index:D.slides.length-1);return;}
 if(voteMode===null&&!stationMode&&delta>0&&EXTRAS.length&&index===D.slides.length-2){renderExtra(0);return;}
 if(voteMode!==null){if(delta>0&&voteStage<3){voteStage++;render();return;}voteMode=null;voteStage=0;if(delta>0&&index<D.slides.length-1)go(index+1);else render();return;}
 if(nationalIndex!==null){const n=nationalIndex+delta;if(n>=0&&n<2)nationalSlide(n);else go(index);return;}
 if(!stationMode&&!readingLayout()&&sectionNodes.length){const n=sectionIndex+delta;if(n>=0&&n<sectionNodes.length){showSection(n);return;}}
 go(index+delta);
 if(delta<0&&!readingLayout()&&sectionNodes.length)showSection(sectionNodes.length-1);
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-slide-section]');if(b){showSection(+b.dataset.slideSection);if(readingLayout())sectionNodes[sectionIndex].scrollIntoView({behavior:'smooth',block:'start'});}});
let layoutFrame;window.addEventListener('resize',()=>{cancelAnimationFrame(layoutFrame);layoutFrame=requestAnimationFrame(()=>{if(sectionNodes.length)showSection(sectionIndex);});});

function nationalSlide(n){
 closeModal();pauseTimer();stationMode=false;sectionNodes=[];nationalIndex=n;
 const c=window.ISCARB_NATIONAL.chapters[D.chapter],isReady=n===0;
 const title=isReady?'Jaheziah: what can you demonstrate?':'NELC: how we design your learning';
 $('#chapter-main').className='chapter-main national-slide';
 $('#chapter-main').innerHTML=`<div class="heading"><div><p class="ey">SAUDI ALIGNMENT · CHAPTER ${D.chapter} · ${esc(D.title)}</p><h1 lang="en" dir="ltr">${title}</h1></div><span class="counter">${n+1} / 2 · reference</span></div>
 <section class="national-canvas" lang="en" dir="ltr" aria-label="${title}">
 <div class="national-brand"><div class="national-logo"><img src="assets/national/${isReady?'etec-logo.svg':'nelc-logo.png'}" alt="${isReady?'Education and Training Evaluation Commission':'National eLearning Center'}"></div><div><p class="national-kicker">${isReady?'Jaheziah · Learning outcomes':'AI-supported Teaching and Learning Design Framework'}</p><h2>${isReady?'Knowledge → skills → responsibility':'Learning first. Human judgment at the center.'}</h2></div></div>
 ${isReady?`<div class="national-readiness"><article><span>01 · Knowledge</span><h3>${esc(c.knowledge)}</h3></article><article><span>02 · Skills</span><h3>${esc(c.skill)}</h3></article><article><span>03 · Values</span><h3>${esc(c.value)}</h3></article></div><p class="national-evidence"><b>Your chapter evidence</b><span>${esc(c.evidence)}</span></p>`:`<div class="national-principles">${window.ISCARB_NATIONAL.principles.map((p,i)=>`<div><span>0${i+1}</span><b>${esc(p)}</b></div>`).join('')}</div><div class="national-roles"><span><b>Learner</b> explains and verifies</span><span><b>AI</b> suggests alternatives</span><span><b>Instructor</b> reviews and judges</span></div><div class="national-cycle" aria-label="Six framework stages">${window.ISCARB_NATIONAL.stages.map((p,i)=>`<span><i>${i+1}</i>${esc(p)}</span>`).join('')}</div>`}
 </section>
 <div class="national-actions"><button data-open="${isReady?'READINESSDETAIL':'NELCDETAIL'}">${isReady?'Objectives & evidence':'Alignment & evidence'}</button><button data-open="${isReady?'QUIZ':'AI'}">${isReady?'Check your understanding':'AI-use boundaries'}</button><button data-national-return>Return to lecture</button></div>
 <p class="national-scope" lang="en" dir="ltr">${isReady?'Proposed educational mapping; official codes require program approval.':'Aligned to the September 2026 framework; this is not certification or partnership.'} The logo identifies the reference organization.</p>`;
 $('#prevBtn').disabled=false;$('#nextBtn').disabled=false;
 $('#topic-location').textContent=isReady?'Jaheziah · readiness':'NELC · learning design';
 $('#progress').textContent='2 reference slides · classroom sequence stays 20';
 $('#live').textContent=title;
 history.replaceState(null,'','#NATIONAL-'+(isReady?'JAHEZIAH':'NELC'));
}
function render(){nationalIndex=null;clearInterval(thinkTimer);thinkTimer=null;const s=D.slides[index],stop=D.stations.find(x=>x.at===s.id);$('#chapter-main').style.removeProperty('--cf');$('#chapter-main').className='chapter-main'+(s.fullTable?' full-table':'')+(s.skin?' skin-'+String(s.skin).replace(/[^a-z0-9-]/gi,''):'');$('#chapter-main').dataset.act=String((actOf(s)?.i??-1)+1);
$('#chapter-main').innerHTML=`<div class="heading"><div><p class="ey">${esc(stationMode?'CLASSROOM STATION':s.phase||'LEARN')} · CHAPTER ${D.chapter}</p><h1>${esc(s.id==='TITLE'?(STORY?STORY.episode:'A decision you can explain'):s.id==='MAP'?'Chapter mind map':s.id==='START'?(STORY?'The case file':'The story we will solve'):s.id==='END'?(STORY?'Episode close · readiness':'Readiness & next step'):s.title)}</h1></div>${tierChip(s)}<span class="counter" title="The slide you are on">Slide ${index+1} of ${D.slides.length}</span>${paceChip()}</div>`;
if(s.added){const ey=$('#chapter-main .heading .ey');if(ey)ey.textContent+=addedTag(s);}
if(stationMode&&stop){renderStation(stop);updateNav();return;}
if(voteMode!==null&&voteItem(voteMode)){$('#chapter-main .heading .ey').textContent='CLASS VOTE · CHAPTER '+D.chapter+(voteItem(voteMode)===D.transfer?.vote?' · TRANSFER CASE':'');renderVote(voteMode);updateNav();return;}
if(s.id==='TITLE'&&STORY){$('#chapter-main').classList.add('cold-open-page');$('#chapter-main').insertAdjacentHTML('beforeend',`<div class="hero cold-open"${coverArt()?'':' style="grid-template-columns:1fr"'}><div><p class="ey">CHAPTER ${D.chapter} · ${esc(D.title)} · ${esc(SERIES.series)}</p><h2>${esc(D.title)}</h2><p class="cold-scene">${kindTag('training')} ${esc(STORY.coldOpen)}</p>${kindLine()}<div class="cold-meta"><span class="clock">⏱ ${esc(STORY.clock)}</span>${SERIES.principle?`<span class="principle-chip">${esc(SERIES.principle)}</span>`:''}${(STORY.hook||D.hook)?`<span class="hero-hook"><i class="ai-tag">AI</i>${esc(STORY.hook||D.hook)}</span>`:''}${STORY.real?`<span class="real-chip"><b>REAL INCIDENT</b>${esc(STORY.real.title)} · ${esc(STORY.real.when)}</span>`:''}</div><div class="actions">${jumpButton('MAP','See the chapter map →')}${D.aiAssignment?button('AI challenge · practice, not graded','AIASSIGN','ai-cta'):''}${button('Resume draft','CARD')}</div><p class="small"><a href="https://adeebnoor.github.io/">Professor Adeeb Noor ↗</a> · King Abdulaziz University · fictional teaching case</p></div>${coverArt()}</div>${gutBlock('before')}`);}
else if(s.id==='TITLE'){$('#chapter-main').insertAdjacentHTML('beforeend',`<div class="hero"${coverArt()?'':' style="grid-template-columns:1fr"'}><div><p class="ey">iSCARB · CPIT-455</p><h2>${esc(D.title)}</h2><p>${esc(D.case.headline)}</p>${kindLine()}<div class="route-tags"><span>SEE</span><span>EXPLAIN</span><span>TEST</span><span>DECIDE</span></div>${D.hook?`<p class="hero-hook"><i class="ai-tag">AI</i><span>${esc(D.hook)}</span></p>`:''}<p class="small"><a href="https://adeebnoor.github.io/">Professor Adeeb Noor ↗</a> · King Abdulaziz University${D.hook?'':`<br>${D.slides.length} classroom slides · five objectives · one evolving artifact`}</p><div class="actions">${jumpButton('MAP','See the chapter map →')}${D.aiAssignment?button('AI challenge · practice, not graded','AIASSIGN','ai-cta'):''}${button('Resume draft','CARD')}</div></div>${coverArt()}</div><p class="scope-note">Required: the class slides and the named source review. The extra tools are optional unless your instructor assigns them.</p>`);}
else if(s.id==='MAP'){renderMindMap();}
else if(s.id==='START'){renderStory();}
else if(s.id==='END'){renderClosing();}
else if(CHECK_V2&&s.phase==='CHECK'){$('#chapter-main').classList.add('checkpoint-page');$('#chapter-main').insertAdjacentHTML('beforeend',`${storyThread(s)}${termsStrip(index)}${checkpointBlock(s)}${yourCall(s,stop)}`);}
else{const merged=mergedCards(s),twist=twistBlock(s);$('#chapter-main').insertAdjacentHTML('beforeend',`${s.banner?bannerBlock(s):storyThread(s)}${practiceBlock(s)}<p class="takeaway">${esc(s.takeaway||s.title)}${s.aiTag?AI_TAG:''}</p>${termsStrip(index)}${twist}${merged?`<div class="body-grid body-merged ${STORY?layoutFor(s):''}">${merged}</div>${listsBlock(s)}`:`<div class="body-grid"><div class="visual">${visual(s)}</div><div class="meaning"><h2>WHAT IT MEANS</h2>${points(s.bullets)}${listsBlock(s)}</div></div>`}${lensStrip(s)}${transferBlock(s)}${yourCall(s,stop)}${yourCall2(s)}${theirBlock(s)}`);}
if(s.id==='END')recordPace();
if(s.lists?.length||s.sourceFigs?.length||s.transfer||s.question2||(D.their&&D.their.at===s.id))$('#chapter-main').classList.add('dense');  // req-v5: extra blocks may scroll; the body grid never collapses
glossaryWrap($('#chapter-main'),index);updateNav();buildReadable(s);requestAnimationFrame(fitText);}
function updateNav(){$('#prevBtn').disabled=index===0;$('#nextBtn').disabled=index===D.slides.length-1;$('#progress').innerHTML=`You have opened ${new Set(state.seen).size} of ${D.slides.length} slides${gateOn()&&!gateSolved()?' · <button class="gate-note" data-open="GATE">Transfer case not solved</button>':''}<span class="nav-shortcuts">Enter → · Backspace ←</span>`;$('#live').textContent=`Slide ${index+1} of ${D.slides.length}: ${D.slides[index].title}`;updateMapLocation();save();}
function go(n,history=true){if(!Number.isInteger(n)||n<0||n>=D.slides.length)return;extraIndex=null;if(PLAN&&n>0&&!paceStart())try{sessionStorage.setItem(paceKey,String(Date.now()-PLAN.end[0]*60000));}catch(e){}pauseTimer();stationMode=false;voteMode=null;voteStage=0;index=n;if(!state.seen.includes(D.slides[index].id))state.seen.push(D.slides[index].id);render();if(history)try{window.history.replaceState(null,'','#'+D.slides[index].id);}catch(e){}if(matchMedia('(max-width:1000px)').matches)window.scrollTo(0,0);}
function jump(k){const aliases=D.aliases||{};k=aliases[k]||k;let n=D.slides.findIndex(s=>s.id===k);closeModal();if(n>=0)go(n);else open(k);}
function modal(title,html){pauseTimer();returnFocus=document.activeElement;$('#modal-title').textContent=title;$('#modal-body').innerHTML=html;glossaryWrap($('#modal-body'),index,true);$('#modal').hidden=false;$('#modal-close').focus();save();}
function closeModal(){if($('#modal').hidden)return;$('#modal').hidden=true;$('#modal-body').innerHTML='';if(returnFocus?.isConnected)returnFocus.focus();}
function full(k){const s=D.slides.find(x=>x.id===k);if(!s)return;modal('Full explanation · '+s.title,`<div class="callout">${esc(ref(s))}. Source detail remains required; the short classroom bullets do not replace it.</div>${s.full||`<p>${esc(s.explanation||'')}</p>`}${s.extra?`<p>${esc(s.extra)}</p>`:''}<h3>Source and qualifications</h3><p>${sourceLink(s,'Read the original explanation, examples and caveats')}</p><p class="small">Textbook examples are historical. The course scenarios are fictional, and proposed tests are not measured results.</p>`);}
/* An open inline answer never covers the slide: the slide scrolls inside the stage and the body keeps its height. */
function holdBody(){const m=$('#chapter-main'),g=m?.querySelector('.body-grid');if(g&&!m.classList.contains('answer-open'))g.style.height=g.getBoundingClientRect().height+'px';}
function answerLayout(box){const m=$('#chapter-main');if(!m)return;const open=!!m.querySelector('.inline-answer:not([hidden])');m.classList.toggle('answer-open',open);if(!open){const g=m.querySelector('.body-grid');if(g)g.style.height='';}if(box&&!box.hidden)requestAnimationFrame(()=>box.scrollIntoView({block:'nearest'}));}
function answer(k){const s=D.slides.find(x=>x.id===k);if(!s)return;const ck=commitKey(k);if(!commitReady(ck)){document.querySelector(`[data-commit="${ck}"]`)?.focus();return;}const inline=[...document.querySelectorAll('#chapter-main .inline-answer')].find(e=>!e.closest('.q2')),btn=$('#chapter-main [data-answer]');if(inline&&D.slides[index].id===k){holdBody();inline.hidden=!inline.hidden;const yw=inline.querySelector('.you-wrote-slot');if(yw)yw.innerHTML=inline.hidden?'':youWrote(ck);btn?.setAttribute('aria-expanded',String(!inline.hidden));if(btn)btn.textContent=inline.hidden?'Reveal answer':'Hide answer';requestAnimationFrame(fitText);answerLayout(inline);return;}modal('Model answer · attempt first',`<p>${esc(s.question)}</p>${youWrote(ck)}<div class="callout">${esc(s.answer||'A defensible response identifies the mechanism, states its assumptions and names evidence that could support or defeat it.')}</div><p class="small">An illustrative response, not the only acceptable wording or an automatic grade. The assessed assignment uses its own case and commit/reveal sequence.</p>${sourceLink(s)}`);}
function stationReady(st){return !COMMIT||(st.fields||[]).some(k=>(state.fields[k]||'').trim())||state.fields['commit_station'+st.no+'_skip']==='1';}
function stationWrote(st){if(!COMMIT)return '';const got=(st.fields||[]).filter(k=>(state.fields[k]||'').trim());return got.length?`<div class="you-wrote"><b>You wrote:</b>${got.map(k=>`<p><i>${esc(fieldLabel(k))}</i> ${esc(state.fields[k])}</p>`).join('')}</div>`:`<p class="you-wrote none"><b>You did not write a decision.</b> Compare the reasoning with what you would have said.</p>`;}
function renderStation(st){stationSeconds=st.seconds||180;remaining=stationSeconds;$('#chapter-main').insertAdjacentHTML('beforeend',`<div class="station"><div class="station-top"><div><p class="ey">STATION ${st.no} / 3 · THE SAME DECISION CARD ${kindTag('training')}</p><h2>${esc(st.title)}</h2></div><div class="timer"><output id="timer-output" class="timer-output">${String(Math.floor(stationSeconds/60)).padStart(2,'0')}:${String(stationSeconds%60).padStart(2,'0')}</output><button id="timer-start">Start</button><button id="timer-reset">Reset</button></div></div><div class="station-steps"><div><b>THINK · 30 SECONDS${aiTag(st,'think')}</b>${esc(st.think)}</div><div><b>PAIR · 60 SECONDS${aiTag(st,'pair')}</b>${esc(st.pair)}</div><div><b>WRITE · 90 SECONDS${aiTag(st,'write')}</b>${esc(st.write)}</div></div>${st.transfer&&D.transfer?`<div class="station-transfer"><b>TRANSFER · 30 SECONDS · DIFFERENT CASE, SAME CONCEPT · INCLUDED IN THE TIMER</b><span>${esc(D.transfer.title)}</span><p>${esc(D.transfer.question)}</p></div>`:''}<div class="station-fields">${st.fields.map(k=>field(k,labels[k],st.prompts?.[k]||'Use facts, a source concept or a clearly labelled proposed check.')).join('')}</div>${rubricPanel(st)}<div class="hint-box" id="coach">${esc('Authored coach: attempt first. Label evidence as supplied, derived, proposed or executed. Name who owns and who reviews the decision. State what would change the verdict.')}</div><div class="actions"><button id="hintBtn" data-no="${st.no}">Hint before the answer</button><button id="station-answer" data-no="${st.no}"${stationReady(st)?'':' disabled'}>Discuss a possible answer</button>${skipBtn('commit_station'+st.no)}${button('Whole card / export','CARD')}<button id="station-back">Return to explanation</button></div><p class="scope-note">${esc(st.note||'Use the same artifact. Discuss reasoning; do not award a level from field length or a timer.')} <span data-save-status></span></p></div>`);glossaryWrap($('#chapter-main .station'),index);timerLabel();}
function timerLabel(){const o=$('#timer-output');if(!o)return;o.textContent=String(Math.floor(remaining/60)).padStart(2,'0')+':'+String(remaining%60).padStart(2,'0');$('.timer')?.classList.toggle('over',remaining===0);$('#timer-start').textContent=ticker?'Pause':remaining===0?'Restart':'Start';}
function pauseTimer(){if(ticker){remaining=Math.max(0,Math.ceil((deadline-Date.now())/1000));clearInterval(ticker);ticker=null;}timerLabel();}
function startTimer(){if(ticker){pauseTimer();return;}if(remaining<=0)remaining=stationSeconds;deadline=Date.now()+remaining*1000;ticker=setInterval(()=>{remaining=Math.max(0,Math.ceil((deadline-Date.now())/1000));timerLabel();if(!remaining){pauseTimer();$('#live').textContent='Station time complete. Finish the reasoning; this is not a grade.';}},250);timerLabel();}
function indexModal(){const L=D.slides.length,item=(s,i)=>`<button data-go="${i}" class="${i===index&&extraIndex===null?'active':''}${s.tier==='optional'?' optional':''}"><b>${String(shownNo(i)).padStart(2,'0')}</b><span>${esc(s.id==='MAP'?'Chapter mind map':s.title)}${s.tier==='optional'?' · optional':''}</span></button>`;
 if(!EXTRAS.length){modal('20 classroom slides',`<div class="index-grid">${D.slides.map(item).join('')}</div>`);return;}
 modal(`${L} classroom slides · ${EXTRAS.length} optional extras`,`<div class="index-grid">${D.slides.map(item).join('')}</div><h3>Optional extras · not assessed · outside the lecture time</h3><div class="index-grid">${EXTRAS.map((x,k)=>`<button data-open="${esc(x.id)}" class="optional${extraIndex===k?' active':''}"><b>E${k+1}</b><span>${esc(x.title)}</span></button>`).join('')}</div>`);}
function reading(){modal('Required source review',`<div class="callout"><b>Classroom + named source detail are required.</b> The original source is preserved separately and loads only when opened. Finishing a chapter includes its named review, not only its main-slide count.</div><table><tr><th>Required selection</th><th>Original slide numbers</th><th>Action</th></tr>${D.readings.map(r=>`<tr><td>${esc(r.title)}</td><td>${esc(r.range)}</td><td><a href="sources/Ch${D.chapter}-Study.html#source-slide-${firstNumber(r.range)}" target="_blank" rel="noopener">Read selected source</a></td></tr>`).join('')}</table><h3>Observable work</h3><p>Explain how one named source concept changes or supports your artifact. Keep the source number, reasoning and limit together. A checkbox or a copied quotation alone is not enough.</p><div class="actions">${button('Five-objective practice','QUIZ')}${D.studyList?.length?button('What to study for the exam','STUDY'):''}${button('Source-to-lesson map','COVERAGE')}<a href="sources/Ch${D.chapter}-Study.html">All original slides and textbook reference</a></div><p class="small">Calendar deadlines and grade contributions remain in Blackboard. Toolkit extensions are optional unless assigned. Do not repeat an already completed submission under this edition.</p>`);}
function coverage(){modal('Source-to-lesson map',`<div class="callout">Which original source slides feed each lesson. Source slide numbers and textbook PDF pages are labelled separately.</div><table><tr><th>Original section</th><th>Source slides</th><th>Classroom locations</th></tr>${D.groups.map(g=>`<tr><td>${esc(g.title)}</td><td>${g.start}–${g.end}</td><td>${g.units.map(k=>jumpButton(k)).join(' ')}</td></tr>`).join('')}</table>${coverageTable()}<p><a href="sources/Ch${D.chapter}-Study.html">Complete source ledger · ${D.sourceCount} original slides</a></p><p><a href="${esc(D.original)}" target="_blank" rel="noopener">Original supplied slide pack</a>${D.textbook?` · <a href="${esc(D.textbook)}" target="_blank" rel="noopener">Original textbook chapter · ${D.bookPages} PDF pages</a>`:''}</p><h3>Original figures</h3><p>The source ledger retains all original source text and links each diagram to its source pack. Preserved diagram assets are available in its figure gallery.</p>`);}
function rules(){modal('The 20 iSCARB rules · canonical map',`<div class="callout">The 20 rules behind every chapter, in their approved order. Each link shows where a rule appears in this lecture. The three stations build one decision card; the rules are not 20 extra tasks.</div><div class="rule-grid">${D.rules.map(r=>`<section class="rule-card" data-rule="${r.no}"><h3><b>${String(r.no).padStart(2,'0')}</b>${esc(r.title)}</h3><p>${esc(r.evidence)}</p><div class="actions">${r.targets.map(k=>button(titleOf(k),k)).join(' ')}</div></section>`).join('')}</div>`);}
function legacyTools(){modal('iSCARB toolkit',`<div class="callout">Use these tools to strengthen the same artifact. Only the classroom stations and named source review are required by default; extra tasks need an explicit instructor assignment.</div><div class="tool-grid">${['RULES','CARD','HSTACK','PREDICT','BRIDGE','MONITOR','LOCAL','PRACTICE','WELLBEING','AI','EVIDENCE','RUBRIC','READINESS','PORTFOLIO'].map(k=>button(titleOf(k),k)).join('')}${D.chapter===11?button('Metric calculator','CALCULATOR'):''}</div>`);}
function card(){modal('One decision card · classroom worksheet',`<div class="callout">Your work is saved locally when storage is available. Keep evidence status, decision boundary and human responsibility explicit: supplied/derived/proposed/executed; owner/reviewer; what would change the verdict. No cloud sync, grade, LMS submission or operational approval occurs here. The assessed case is separate.</div><div class="two-col">${['claim','evidence','warrant','counter','uncertainty','verdict'].map(k=>field(k,labels[k])).join('')}</div><h3>Revision and responsibility</h3>${field('initial')}${field('revision')}<div class="two-col">${['owner','reviewer','signoff','ai_disclosure'].map(k=>field(k,labels[k])).join('')}</div><div class="actions"><button data-export="json">Export backup · JSON</button><button data-export="md">Export readable card</button><button id="import">Import backup</button><button id="copy">Copy card</button><button id="clear">Clear classroom draft</button></div><p class="status" data-save-status></p>${D.noPrevious?'':`<p class="small">Earlier lecture drafts have not been erased. <a href="previous-lectures/Ch${D.chapter}-Previous-Lecture.html" target="_blank" rel="noopener">Open the previous lecture to recover its local draft</a>. Assignment drafts and locked Part A are untouched by this worksheet.</p>`}`);}
function hstack(){const names=['Analyze','Judge','Evidence','System','Risk','Ethics'];const texts=['Separate the concepts and trace the mechanism.','Compare alternatives under stated constraints.','Connect the claim to a source or inspectable result.','Follow interfaces, dependencies and operating context.','State uncertainty, counter-evidence and fallback.','Disclose assistance and name human responsibility.'];modal('Six H-Stack capabilities',`<p>The approved course capability vocabulary—not a national classification or an automatic score.</p><table><tr><th>Capability</th><th>Visible in your chapter artifact</th></tr>${names.map((x,i)=>`<tr><th>${x}</th><td>${texts[i]}</td></tr>`).join('')}</table>${button('Review the card','CARD')}`);}
function predict(){modal('Predict → Constraint → Derive → Name',`<div class="callout">${esc(D.case.text)}</div>${field('initial','INITIAL DECISION','Your tentative decision before the explanation.')}${field('prediction')}${field('constraint','CONSTRAINT','What operating condition limits this answer?')}${field('derive','DERIVE','Why does the mechanism support your prediction? Show units if calculating.')}${field('principle','NAME','Name the source concept you used.')}<p class="small">Keep the original view and write later changes under revision. This is reflective practice, not a secure assessment lock.</p>`);}
function bridge(){modal('Architecture / implementation structure',`<p>${esc(D.bridge)}</p>${field('architecture','IMPLEMENTATION ANNOTATION','Input / component / interface → decision or transformation → output / fallback. Name one shared dependency.')}${field('evidence_gap','VERIFICATION ARTIFACT','The actual or proposed test, model, table or trace that checks this implementation.')}<div class="actions">${jumpButton(D.mechanism,'Return to the chapter mechanism')}${button('Evidence policy','EVIDENCE')}</div>`);}
function monitor(){modal('Known / Unknown / Monitor',`${field('known','KNOWN','Only supplied source/case facts and derived calculations.')}${field('unknown','UNKNOWN','The missing condition, dependency or unexecuted check.')}${field('monitor','MONITOR','Quantity or event + window + proposed/approved trigger + owner + action.')}<p class="small">A proposed threshold is not an observed result or an approved operating limit.</p>`);}
function local(){modal('Saudi-aligned engineering context',`<p>This is a fictional teaching context, not a description of a live KAU system. Identify the actual service owner, affected users, language/access needs and authority before applying the argument to a real organization.</p>${field('local_context','LOCAL CONSTRAINT → EVIDENCE → EFFECT','Which institutional document, version or owner establishes this constraint? How would it change the chapter artifact?')}${field('owner')}${field('signoff')}<p class="small">No regulatory approval, national compliance or official mapping is inferred from a Saudi setting.</p>`);}
function practice(){modal('Trend / contemporary practice',`<p>Connect a source mechanism to a tool or workflow you have actually used. This is an evidence-seeking exercise, not a claim that the textbook’s historical examples are the latest standard.</p>${field('practice','CURRENT PRACTICE → SOURCE → VERSIONED ARTIFACT',D.practice)}<p class="small">Name the tool/version and authoritative documentation date. Keep an untested suggestion labelled proposed.</p>`);}
function wellbeing(){modal('Practitioner wellbeing as a system variable',`<p>${esc(D.workload)}</p>${field('workload','WORKLOAD / HANDOVER → DESIGN CHANGE → CHECK','Identify an operator burden, a feasible change and evidence that would evaluate it.')}<p class="small">The course exercise treats workload as a design variable; it does not diagnose a person or claim a measured wellbeing effect.</p>`);}
function aiVerdict(a){if(a[0]===undefined)return 'Record whether the output enters the evidence chain.';if(a[0]==='no')return 'Preparation only: check factual claims and disclose assistance; do not file generated text as verified evidence.';if(a[3]==='no')return 'Not permitted as assurance evidence: named human review is missing.';if(a[1]==='no'&&a[2]==='no')return 'Not permitted as assurance evidence: neither independent re-derivation nor testing is available.';if(a[3]!=='yes')return 'Incomplete: identify the responsible human review.';if(a[1]==='yes')return 'Conditionally permitted under the course policy: retain the independent derivation and named review.';if(a[2]==='yes')return 'Conditionally permitted: retain the independently executed test and its result, not the generated answer alone.';return 'Incomplete: establish an independent checking route.';}
function ai(){const qs=['Will this output enter the evidence chain?','Can its relevant result be independently re-derived?','Can its relevant claim be independently tested?','Is a named human responsible for review and sign-off?'];modal('Critical AI literacy · permissibility gate',`<p>Use only authorized, non-sensitive teaching inputs. No AI service is called by this page.</p>${qs.map((q,i)=>`<div class="ai-row"><span>${i+1}. ${esc(q)}</span>${['yes','no'].map(v=>`<button data-ai="${i}" data-value="${v}" aria-pressed="${state.ai[i]===v}">${v==='yes'?'Yes':'No'}</button>`).join('')}</div>`).join('')}<div id="ai-result" class="result" role="status">${esc(aiVerdict(state.ai))}</div>${field('ai_disclosure','ASSISTANCE + INDEPENDENT CHECK + HUMAN OWNER','No AI used, or describe the assistance, check and review.')}`);}
function evidence(){modal('Evidence policy / proof of capability',`<table><tr><th>Evidence type</th><th>Required honest record</th></tr><tr><td>Source explanation</td><td>Exact source/slide/page, relevant meaning and limitations.</td></tr><tr><td>Fictional case input</td><td>Label as supplied teaching data—not live operational measurement.</td></tr><tr><td>Derived result</td><td>Inputs, method/formula, units, independent arithmetic and scope.</td></tr><tr><td>Proposed test</td><td>Unexecuted plan, expected result, owner and conditions.</td></tr><tr><td>Executed test</td><td>Actual version, inputs, date, log, outcome and reviewer.</td></tr><tr><td>AI assistance</td><td>Disclosure and independent verification; not authority by itself.</td></tr></table><p>Opening pages is not learning evidence by itself. Field completeness is not correctness. A plan is not a passed test.</p>${field('evidence_gap')}`);}
function rubric(){const rows=[['L1 · Asserting','Names a decision but lacks sufficient mechanism or inspectable support.'],['L2 · Reasoning','Explains a relevant mechanism and source concept; major evidence remains missing.'],['L3 · Justifying','Provides a checkable artifact, counter-evidence and explicit assumptions/limits.'],['L4 · Accountable','Defends a revision under the changed constraint and names review and decision responsibility.']];modal('Four-level capability rubric',`<table><tr><th>Level</th><th>What a reviewer examines</th></tr>${rows.map(r=>`<tr><th>${r[0]}</th><td>${r[1]}</td></tr>`).join('')}</table>${field('self_level','PROVISIONAL SELF-PLACEMENT + REASON','Use the descriptor and identify the next evidence gap.')}<p class="small">Descriptors support human review. The assignment retains its published raw-point rubric; no grade or level is awarded automatically by this lecture.</p>`);}
function readiness(){const c=window.ISCARB_NATIONAL.chapters[D.chapter];modal('Jaheziah · Chapter '+D.chapter,`<div class="callout" lang="en" dir="ltr"><b>Chapter evidence:</b> ${esc(c.evidence)}<br><b>What does the instructor review?</b> ${esc(c.check)}</div><div class="callout warning"><b>Required practice; official mapping is not asserted.</b> The supplied sources do not establish an approved program mapping for these authored chapter objectives. Exact national codes, exam weights and attainment are not invented.</div><table><tr><th>Chapter objective</th><th>Practice evidence</th><th>Assignment field / opportunity</th></tr>${D.objectives.map((o,i)=>`<tr><td><b>Objective ${D.chapter}.${i+1}</b> ${esc(o)}</td><td>${esc(D.alignment[i].evidence)}</td><td>${esc(D.alignment[i].field)}</td></tr>`).join('')}</table><p>Candidate domains are knowledge, skills, and values/responsibility. The program must approve the formal crosswalk. These opportunities do not mean one multiple-choice item certifies an outcome.</p><div class="actions">${button('Five-objective practice','QUIZ')}${button('Four-level rubric','RUBRIC')}${button('Card','CARD')}</div>`);}
function portfolio(){modal('One portfolio artifact · transfer to the assignment',`<p>${esc(D.artifact)}</p><ol><li>Explain the chapter-specific concept using the named source.</li><li>Build the requested technical artifact; do not invent executed tests.</li><li>State counter-evidence, uncertainty and a bounded decision.</li><li>Retain the initial view and justify a revision when the constraint changes.</li></ol><div class="callout">The three classroom stations feed one practice card. ${D.gradedNote?esc(D.gradedNote):`The separate assignment keeps its own case, existing ${D.points}-point rubric, commit/reveal sequence and Blackboard deadline.`} Do not add another full report merely to satisfy the 20 rules.</div><div class="actions"><a href="${esc(AHREF)}">${esc(ALABEL)}</a>${button('Card / export','CARD')}${button('Outcome crosswalk','READINESS')}</div>`);}
function quiz(){const q=D.quiz[quizIndex],r=state.quiz[quizIndex]||{};modal(`Five-objective practice · Objective ${D.chapter}.${quizIndex+1}`,`<div class="quiz-dots">${D.quiz.map((_,i)=>`<button data-quiz="${i}" class="${i===quizIndex?'active':''}">${i+1}</button>`).join('')}</div><p><b>${esc(q.q)}</b></p><div class="quiz-options">${shuffledIndexes(q.options.length,quizIndex).map(i=>`<label><input type="radio" name="quiz" value="${i}" ${r.answer===i?'checked':''}><span>${esc(q.options[i])}</span></label>`).join('')}</div><div class="actions" style="margin-top:16px"><button id="quiz-check" class="primary">Check after attempting</button><button data-quiz="${Math.min(4,quizIndex+1)}" ${quizIndex===4?'disabled':''}>Next objective</button></div><div id="quiz-feedback" role="status" hidden></div><p class="small" style="margin-top:15px">Practice questions written for this course. They are not graded and are not exam items.</p>`);if(r.checked)quizFeedback();}
function quizFeedback(){const r=state.quiz[quizIndex],q=D.quiz[quizIndex],b=$('#quiz-feedback');b.hidden=false;b.className='feedback'+(r?.answer===q.answer?'':' wrong');b.textContent=(r?.answer===q.answer?'Correct for this case. ':'Review this distinction. ')+q.why;}
function calculator(){modal('Reliability metric calculator · observed ratios',`<div class="callout">Define the failure event and exposure. These are observed estimates, not a reliability certificate. The chapter’s reciprocal-rate convention for MTTF is used.</div><div class="two-col">${[['demands','Demands',10000],['failed','Failed demands',20],['events','Outage events',2],['time','Service window (hours)',1000],['down','Unavailable hours',1]].map(([k,l,v])=>`<label class="field"><span>${l}</span><input id="calc-${k}" type="number" min="0" step="any" value="${v}"></label>`).join('')}</div><button id="calculate">Calculate with units</button><div id="calc-result" class="result" role="status"></div><p class="small">Do not compare a rate per hour to a probability per demand without the relevant denominator. Zero observed events are not proof of infinite reliability.</p>`);compute();}
function compute(){const vs=['demands','failed','events','time','down'].map(k=>$('#calc-'+k)?.value);const b=$('#calc-result');if(vs.some(x=>x===undefined||x.trim()==='')){b.textContent='Enter every value; a blank is not zero.';return;}const [n,f,e,t,d]=vs.map(Number);if(![n,f,e,t,d].every(Number.isFinite)||n<=0||t<=0||f<0||f>n||e<0||d<0||d>t||![n,f,e].every(Number.isInteger)){b.textContent='Invalid observations: positive demand/window; whole non-negative counts; failed ≤ demands; downtime ≤ window.';return;}const fmt=n=>Number(n.toPrecision(8));b.innerHTML=`<p>POFOD estimate = ${f}/${n} = <b>${fmt(f/n)} per demand</b></p><p>ROCOF = ${e}/${t} = <b>${fmt(e/t)} outage events/hour</b></p><p>Reciprocal-rate MTTF = <b>${e?fmt(t/e)+' hours':'not estimable from zero observed events'}</b></p><p>AVAIL = (${t}−${d})/${t} = <b>${fmt(100*(t-d)/t)}%</b></p>`;}
function notes(){const s=D.slides[index];if(!PRESENTER){modal('Instructor notes','<p>Teaching notes are shown only in presenter mode, which your instructor uses in class.</p>');return;}const log=paceLog().filter(x=>x.chapter===D.chapter);modal('Instructor notes · '+s.title,`<p>${esc(s.notes||'Ask students to distinguish the source concept, the mechanism and its operating assumptions. Attempt before revealing; use the named source for detail rather than shrinking the main slide.')}</p>${s.commonError?`<h3>Common student error</h3><p>${esc(s.commonError)}</p>`:''}${D.timeRule?`<h3>Time rule</h3><p>${esc(D.timeRule)}</p><p class="small">This slide: ${s.tier==='optional'?'optional':'core'} · ${esc(s.minutes||0)} min${PLAN?` · plan total ${Math.round(PLAN.total)} of ${PLAN.B} min (${PLAN.mode})`:''}.${log.length?` Pace log: ${log.map(x=>`${x.date} planned ${x.planned}, actual ${x.actual}`).join('; ')}.`:' No actual duration recorded yet; it is saved on the closing slide.'}</p>`:''}<h3>Teaching move</h3><p>Use the three stations to develop one artifact. Sample reasoning orally. If a source topic is not finished, announce the precise required review rather than making it optional.</p><p>${esc(ref(s))}</p>${sourceLink(s)}`);}
function help(){modal('Navigation, sources and saving',`<p><a href="https://adeebnoor.github.io/">Professor Adeeb Noor · Profile, research &amp; contact ↗</a></p><p>Start at the cover, then the Chapter mind map on slide 2. Use Chapter map to return, Slides to jump, and Study &amp; tools for required review, your card, methodology and display settings.</p><table><tr><th>Enter / Backspace</th><td>Next / previous slide. On a focused button or link, Enter activates that control.</td></tr><tr><th>Mouse click / Shift + click</th><td>Next / previous slide when you click empty slide space in desktop presentation mode. Dragging to select text does not navigate.</td></tr><tr><th>← / →</th><td>Previous / next classroom slide.</td></tr><tr><th>Home / End</th><td>First / final slide.</td></tr><tr><th>O / C${PRESENTER?' / N':''}</th><td>Slide index / decision card${PRESENTER?' / instructor notes':''}.</td></tr><tr><th>Escape</th><td>Close a dialog; typing fields do not trigger navigation.</td></tr>${STORY&&PRESENTER?'<tr><th>Class vote</th><td>Enter steps through vote → discuss → revote → reveal.</td></tr>'+paceHelp()+'<tr><th>Counting hands</th><td>Tap an option once per raised hand. Counts stay on this device and appear again at the episode close.</td></tr>':''}</table><p>Use Jaheziah and NELC for two full reference slides inside this lecture; Return or Escape restores the classroom slide. The same 20 scientific slides remain in their original order. Reading view and smaller screens show every section in order. Large tables continue in labelled sections; no font is shrunk to fit. Sources open separately on demand. Keep the accompanying runtime/assets folders when using an offline ZIP.</p><p>Classroom drafts are local. Export JSON to restore them, or Markdown to read them. The assessed assignment preserves its own identity, draft storage and commitment rules.</p><div class="actions">${button('Source coverage','COVERAGE')}${button('Export card','CARD')}</div>`);}
// Mind-map v1: source concepts and student workflow are distinct layers.
// This is an authored learning organizer, not an original textbook figure.
// Story v2: simpler concept path, one persistent case thread, and an explicit close.
function storyBranch(s){
 return D.roadmap?.branches?.find(x=>(x.units||[]).includes(s.id));
}
function bannerBlock(s){ const b=s.banner||{}; return `<figure class="ai-banner"><img src="${esc(b.src)}" alt="${esc(b.alt||'')}" decoding="async"><figcaption><span>${esc(b.label||'')}</span>${esc(b.caption||'')}</figcaption></figure>`; }
const AI_TAG='<i class="ai-tag" title="This part involves the AI component">AI</i>';
function aiTag(st,k){ return (st&&Array.isArray(st.ai)&&st.ai.includes(k))?AI_TAG:''; }
function lensStrip(s){ if(!s||!s.lens)return ''; return `<div class="ai-lens"><span>AI LENS</span>${kindTag('training')}<em>${esc(s.lens)}</em></div>`; }
// A class vote held on the transfer slide asks the transfer case itself (CASE-3).
function voteItem(i){const a=ACTS[i];return (D.transfer?.vote&&a&&D.slides[a.last]?.id===D.transfer.at)?D.transfer.vote:D.quiz?.[i];}
function actOf(s){return ACTS.find(a=>(a.b.units||[]).includes(s.id))||null;}
// REAL-1/REAL-2: every mention of a story or an incident carries a fixed tag.
function kindTag(k){const t={training:STORY?'TRAINING STORY':'TRAINING CASE',real:'REAL INCIDENT',source:'FROM THE TEXTBOOK',fictional:'FICTIONAL CASE'}[k]||'';return `<i class="kind-tag kind-${k}">${t}</i>`;}
function kindLine(){const who=STORY?`${esc(SERIES.lead.name)}’s story`:`The ${esc((D.case.headline||'case').replace(/[.?!]+$/,'').toLowerCase())} case`;return `<p class="kind-line">${kindTag('training')} ${who} is fictional teaching material.${STORY?.real?` ${kindTag('real')} ${esc(STORY.real.title)} (${esc(STORY.real.when)}) is a documented event, shown separately.`:' No real incident is used in this lecture.'}</p>`;}
function storyThread(s){
 if(['TITLE','MAP','START','END'].includes(s.id))return '';
 const a=actOf(s),b=a?.b,lens=b?.caseLens||D.case.question,n=a?a.i+1:0,i=D.slides.indexOf(s);
 const opening=!!(STORY&&a&&i===a.first&&STORY.acts?.[a.i]);
 const dots=STORY&&a?`<span class="act-dots" aria-hidden="true">${ACTS.map((x,k)=>`<i class="${k<a.i?'done':k===a.i?'on':''}"></i>`).join('')}</span>`:'';
 return `<div class="case-thread${opening?' act-open':''}"><span>CASE THREAD${STORY&&n?` · ACT ${n} OF ${ACTS.length}`:''}</span>${kindTag('training')}<b>${esc(b?.label||D.case.headline)}</b><em>${esc(lens)}</em>${dots}</div>${opening?`<div class="act-scene"><span class="scene-who">${esc(SERIES.lead.name)}</span>${kindTag('training')}<p>${esc(STORY.acts[a.i])}</p></div>`:''}`;
}
// Checkpoints read as review questions (rolled out from Chapter 12 first): the question is the headline,
// the routine is a numbered strip, and chips name what the checkpoint reviews.
const CHECK_V2=!!(STORY&&[12].includes(Number(D.chapter)));
function checkpointBlock(s){
 const i=D.slides.indexOf(s),checks=D.slides.map((x,k)=>x.phase==='CHECK'?k:-1).filter(k=>k>=0),n=checks.indexOf(i)+1,prev=n>1?checks[n-2]:D.slides.findIndex(x=>x.id==='START');
 const covered=D.slides.slice(prev+1,i).filter(x=>x.phase!=='CHECK'&&x.title);
 const steps=(s.bullets||[]).filter(b=>Array.isArray(b)&&b[0]).slice(0,3),time=['30 s alone','60 s with a neighbour','1 min on your card'];
 return `<div class="checkpoint"><div class="cp-q"><span class="cp-mark" aria-hidden="true">?</span><div><p class="cp-ey">CHECKPOINT ${n} OF ${checks.length} · REVIEW QUESTION</p><p class="cp-text">${esc(s.question||s.takeaway)}</p></div></div>`
 +`<div class="cp-recap"><span>Reviews</span>${covered.map(x=>`<button class="cp-chip" data-jump="${esc(x.id)}">${esc(x.title)}</button>`).join('')}</div>`
 +`<ol class="cp-steps">${steps.map((b,k)=>`<li><b>${esc(b[0])}<small>${time[k]||''}</small></b><span>${esc(b[1])}</span></li>`).join('')}</ol></div>`;
}
// Layout follows the content, so consecutive slides do not all become four equal cards.
function layoutFor(s){const n=(s.bullets||[]).filter(b=>Array.isArray(b)&&b[0]).length,i=D.slides.indexOf(s);if(s.phase==='CHECK'&&n===3)return 'lay-flow lay-check';if(/^\s*\d+\s*·/.test(s.nodes?.[0]?.[0]||''))return n===4?'lay-quad':n===3?'lay-flow':'lay-trio';if(n<=2)return 'lay-split';if(n===3)return s.flow?'lay-flow':'lay-trio';if(n===4)return i%2?'lay-quad':'lay-steps';return 'lay-steps';}
// COMMIT-1..3: the student writes before the reveal; their sentence sits beside the model answer.
// Saved on this device only (state.fields), and never shown or asked for in presenter mode.
const COMMIT=!PRESENTER;
function commitKey(id,n){return 'commit_'+String(id).toLowerCase().replace(/[^a-z0-9]/g,'_')+(n?'_'+n:'');}
function commitReady(key){return !COMMIT||!!(state.fields[key]||'').trim()||state.fields[key+'_skip']==='1';}
function commitBox(key){if(!COMMIT)return '';return `<label class="commit-box"><span>YOUR ANSWER · one sentence, before you reveal</span><textarea data-field="${key}" data-commit="${key}" rows="1" maxlength="600" placeholder="Write your decision and one reason.">${esc(state.fields[key]||'')}</textarea></label>`;}
function skipBtn(key){return COMMIT?`<button class="skip-btn" data-skip="${key}">Skip writing</button>`:'';}
function youWrote(key){if(!COMMIT)return '';const v=(state.fields[key]||'').trim();return v?`<p class="you-wrote"><b>You wrote:</b> ${esc(v)}</p>`:`<p class="you-wrote none"><b>You did not write a decision.</b> Compare the answer with what you would have said.</p>`;}
function yourCall(s,stop){
 const ck=commitKey(s.id),ready=commitReady(ck);
 const a=actOf(s),vote=!!(STORY&&a&&D.slides.indexOf(s)===a.last&&voteItem(a.i)&&(!PLAN||PLAN.voteActs.includes(a.i))),later=!!(PLAN&&stop&&!PLAN.stationNos.includes(stop.no));
 return `<div class="question${STORY?' your-call':''}"><p class="question-text"><b>${s.transfer?'YOUR CALL · TRANSFER CASE':STORY?'YOUR CALL':'BACK TO THE STORY'}</b>${!STORY&&!s.transfer?kindTag('training'):''}${esc(s.question||'Explain the concept using the teaching case.')}</p>${commitBox(ck)}<div class="actions"><div class="buttons">${STORY?`<button class="think-btn" data-think="30">Think · 30 s</button><button data-answer="${esc(s.id)}" data-commit-for="${ck}" aria-expanded="false"${ready?'':' disabled'}>Reveal answer</button>${skipBtn(ck)}<button data-full="${esc(s.id)}">Full explanation</button>`:`<button data-full="${esc(s.id)}">Full explanation</button><button data-answer="${esc(s.id)}" data-commit-for="${ck}"${ready?'':' disabled'}>Model answer</button>${skipBtn(ck)}`}${vote?`<button class="vote-btn" data-vote="${a.i}">Class vote · Act ${a.i+1}${voteItem(a.i)===D.transfer?.vote?' · transfer case':''}</button>`:''}${stop?`<button class="${later?'if-time':'primary'}" id="stationBtn">Station ${stop.no} · ${later?'if time allows':'build the card'}</button>`:''}</div><span class="source-line">${esc(ref(s))} · ${sourceLink(s)}</span></div>${STORY?`<div class="inline-answer" hidden><div class="you-wrote-slot"></div><b>One defensible answer · after you have committed yours</b><p>${esc(s.answer||'A defensible response identifies the mechanism, states its assumptions and names evidence that could support or defeat it.')}</p><small>Illustrative, not the only acceptable wording or a grade.</small></div>`:''}</div>`;
}
// In-class COMMIT → STRESS without clicks: the slide before the twist asks for a written decision,
// the twist slide then states the new information openly.
function twistBlock(s){
 if(!STORY)return '';
 const i=D.slides.indexOf(s),tw=D.slides.findIndex(x=>x.id===TWIST_AT);
 if(i===tw)return `<div class="twist"><div class="twist-scene"><span>NEW INFORMATION</span>${kindTag('training')}<p>${esc(STORY.twist)}</p></div></div>`;
 if(tw>0&&i===tw-1)return `<div class="twist"><div class="twist-commit"><span>BEFORE THE NEXT SLIDE</span>${kindTag('training')}<p>Write your decision in one sentence now. New information reaches ${esc(SERIES.lead.name)} on the next slide, and you will revise from what you wrote.</p></div></div>`;
 return '';
}
const AI_SLIDE=D.slides.findIndex(x=>x.banner||x.aiTag);
function practiceBlock(s){
 if(!STORY?.practice||D.slides.indexOf(s)!==AI_SLIDE)return '';
 if(!STORY.aiSystem)return `<div class="practice-scene"><span class="practice-tag">AI = PRACTICE · JUDGMENT = ASSESSED</span>${kindTag('training')}<p>${esc(STORY.practice)}</p></div>`;
 return `<div class="ai-roles" aria-label="Two roles of AI"><section class="ai-role sys"><span>AI IN THE SYSTEM · WE ANALYSE IT</span>${kindTag('training')}<p>${esc(STORY.aiSystem)}</p></section><section class="ai-role desk"><span>AI AT YOUR DESK</span><p>Practice only: it rehearses with you, it never decides or signs.</p></section></div>`;
}
// Extra track v1: up to three slides outside the pinned 20 (live lab, explain it, assignment steps).
// Presenter flow enters them after the slide before the close; students reach them from the close.
const EXTRAS=STORY?[...(STORY.real?[{id:'X-REAL',title:'This really happened'}]:[]),...(STORY.build?[{id:'X-LAB',title:'Live lab 1 of 2 · read the code, predict'},{id:'X-LAB2',title:'Live lab 2 of 2 · Python’s result and the fix'}]:[{id:'X-LAB',title:'Live lab · predict, then run'}]),{id:'X-EXPLAIN',title:'Explain it in two minutes'},...(STORY.noSteps?[]:[{id:'X-STEPS',title:'Your assignment, step by step'}])]:[];
function caseInputs(c){return Object.entries(c).filter(([k])=>k!=='name'&&!/^expected/.test(k)).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(' → '):v}`).join(' · ');}
function caseExpected(c){return Object.entries(c).filter(([k])=>/^expected/.test(k)).map(([,v])=>Array.isArray(v)?v.join(', '):String(v)).join(' · ');}
function labRow(r){if(!r)return '<td class="pending">—</td>';const a=r.actual,v=a.action??a.decision??a.status??a.display??(a.lookups?a.lookups.join(', ')+(a.lostChanges?` · lost ${a.lostChanges}`:''):undefined)??(a.reservations!==undefined?a.reservations+' reservation(s)':a.storedSeconds!==undefined?(a.status+(a.storedSeconds!==null?' · '+a.storedSeconds+' s':'')):JSON.stringify(a));return `<td class="${r.passed?'pass':'fail'}">${esc(v)} <b>${r.passed?'✓':'✗'}</b></td>`;}
let labRuns={};const extraSeen=new Set();
// Extras sit between slide 19 and the close. The counter counts the 20 lecture slides only; extras read “Extra k / n”.
function shownNo(i){return i+1;}
function coverArt(){const fig=STORY&&STORY.caseFigure;if(fig&&fig.src)return `<img src="${esc(fig.src)}" alt="${esc(fig.alt||'Teaching illustration')}">`;return '';}
function renderExtra(k){
 closeModal();pauseTimer();clearInterval(thinkTimer);thinkTimer=null;stationMode=false;voteMode=null;sectionNodes=[];nationalIndex=null;extraIndex=k;
 const x=EXTRAS[k],main=$('#chapter-main');extraSeen.add(x.id);main.className='chapter-main extra-slide';main.dataset.act='5';
 let body='';
 if(x.id==='X-REAL'){const R=STORY.real;body=`<p class="extra-q">${kindTag('real')} ${esc(R.title)} · ${esc(R.when)}</p><div class="real-grid"><ol class="real-facts">${R.facts.map(f=>`<li>${esc(f)}</li>`).join('')}</ol><table class="real-map"><thead><tr><th>In today’s lecture</th><th>In the real case</th></tr></thead><tbody>${R.map.map(([a,b])=>`<tr><th>${esc(a)}</th><td>${esc(b)}</td></tr>`).join('')}</tbody></table></div><p class="real-lesson"><b>Lesson from the investigation.</b> ${esc(R.lesson)}</p>${R.differs?`<p class="real-differs"><b>How it differs from the training story.</b> ${esc(R.differs)}</p>`:''}<p class="real-src">Sources: ${R.sources.map(([l,u])=>`<a href="${esc(u)}" target="_blank" rel="noopener">${esc(l)}</a>`).join(' · ')}</p>`;}
 else if(x.id==='X-LAB'&&STORY.build){const B=STORY.build;
  body=`<p class="extra-q">${esc(B.question)}</p><div class="cb-grid"><div class="cb-code"><p class="cb-label">TODAY’S CODE · as designed</p>${B.helpers?`<pre class="cb-given" aria-label="Given">${esc(B.helpers.trimEnd())}</pre>`:''}<pre>${esc(B.buggy.trimEnd())}</pre></div><div class="cb-tests"><p class="cb-label">THREE TESTS · predict ✓ or ✗ for each</p><pre>${esc(B.tests.trimEnd())}</pre></div></div><p class="cb-next"><b>Hands up for each test: pass or fail?</b> The next slide shows what Python says.</p>`;}
 else if(x.id==='X-LAB2'&&STORY.build){const B=STORY.build,R=B.result.buggy,F=B.result.fixed;
  const marks=R.tests.map(t=>`<li class="${t[1]?'pass':'fail'}"><b>${t[1]?'✓':'✗'}</b> <code>${esc(t[0])}</code>${!t[1]&&t[2]?`<span>${esc(t[2])}</span>`:''}</li>`).join('');
  body=`<div class="cb-grid"><div class="cb-tests"><p class="cb-label">PYTHON’S RESULT · code as designed</p><ul class="cb-list">${marks}</ul>${R.show?`<p class="cb-show"><code>${esc(R.show)}</code></p>`:''}</div><div class="cb-code"><p class="cb-label">THE FIX · ${F.tests.filter(t=>t[1]).length} of ${F.tests.length} tests pass ✓</p><pre>${esc(B.fixed.trimEnd())}</pre>${F.show?`<p class="cb-show"><code>${esc(F.show)}</code></p>`:''}</div></div><ol class="cb-map">${B.map.map(m=>`<li><b>Slide ${esc(m[0])}</b> ${esc(m[1])}<code>${esc(m[2])}</code></li>`).join('')}</ol><p class="cb-next">${esc(B.bridge)} <a href="../../assignment-example.html#build" target="_blank" rel="noopener">Practice build ↗</a></p>`;}
 else if(x.id==='X-LAB'){const L=STORY.lab,ok=window.StudyLab&&L;const runs=labRuns[D.chapter]||{};
  body=ok?`<p class="extra-q">${esc(L.question)}</p><p class="extra-how"><b>1.</b> For each case, the class predicts what the <i>baseline</i> does. <b>2.</b> Run it. <b>3.</b> Run the corrected model. <b>4.</b> Ask: what did the failing case have that the others did not?</p><div class="lab-table-wrap"><table class="lab-table"><thead><tr><th>Case</th><th>Inputs</th><th>Expected</th><th>Baseline</th><th>Corrected</th></tr></thead><tbody>${L.cases.map((c,i)=>`<tr><th>${esc(c.name)}</th><td>${esc(caseInputs(c))}</td><td>${esc(caseExpected(c))}</td>${labRow(runs.baseline?.[i])}${labRow(runs.corrected?.[i])}</tr>`).join('')}</tbody></table></div><div class="actions"><button class="primary" data-xlab="baseline">Run baseline</button><button data-xlab="corrected">Run corrected</button><button data-xlab="reset">Clear</button><span class="small">Same teaching model as Assignment ${D.assignment}. In the assignment you write your own cases.</span></div>`:`<p>The lab model is not available offline in this copy.</p>`;}
 else if(x.id==='X-EXPLAIN'){body=`<p class="extra-q">Pairs. Partner A has 60 seconds; then swap.</p><ol class="explain-steps"><li><b>Say your decision</b> for: ${esc(D.case.question)}</li><li><b>Say where it stops holding:</b> the observation that would make you reopen it.</li><li><b>Say what evidence would change it,</b> and who would check it.</li></ol><div class="explain-ask"><b>Partner B asks one:</b><ul><li>Why that boundary and not another?</li><li>What did the new information change, and what did it not?</li><li>Which part are you least sure of?</li></ul></div>${SERIES.desk?`<div class="desk-uses"><b>AI at your desk · before the real check, practise:</b><ul>${SERIES.desk.map(d=>`<li>${esc(d)}</li>`).join('')}</ul><p>You sign the decision. AI does not.</p></div>`:''}<div class="actions"><button class="think-btn" data-think="60">Start 60 s</button><span class="small">This is the same two-minute ownership check your instructor may run after each assignment. ${esc(SERIES.principle||'')}</span></div>`;}
 else{const a=D.assignment,fmt={15:'Format: critique a colleague’s recommendation.',20:'Format: review another team’s design.'}[D.chapter]||'';
  body=`<p class="extra-q">Assignment ${a} · about 80–90 minutes in total${fmt?` · ${esc(fmt)}`:''}</p><ol class="steps-grid"><li><b>Prepare</b><span>Read ${D.readings.map(r=>esc(r.title)+' ('+esc(r.range)+')').join(' and ')}; do the five-objective check.</span></li><li><b>Part A</b><span>FIT · the chapter artifact · BOUND · ACT + EVIDENCE, 120–180 words, supplied facts only.${STORY.build?' <i>Practised today: claim and evidence (station 1), uncertainty = BOUND (station 2).</i>':''}</span></li><li><b>Python build</b><span>Write the code and at least three tests; run them with the course checks in the browser; use what it shows.${STORY.build?' <i>Practised today: the live lab.</i>':''}</span></li><li><b>Commit</b><span>Review &amp; commit Part A. The new evidence opens on the page straight away.</span></li><li><b>New evidence → REFIT</b><span>Read it; retain, revise or replace, and say why.${STORY.build?' <i>Practised today: station 3.</i>':''}</span></li><li><b>Declare and submit</b><span>AI use (or “No AI used”), final PDF to Blackboard. Be ready to explain it in two minutes.</span></li></ol><div class="actions"><a class="btn-link" href="${esc(AHREF)}">${esc(ALABEL)}</a><a class="btn-link" href="../../assignment-example.html">Worked example</a><a class="btn-link" href="../../student-guide.html#assignments-3-9">Step-by-step guide</a></div>`;}
 main.innerHTML=`<div class="heading"><div><p class="ey">EXTRA ${k+1} OF ${EXTRAS.length} · CHAPTER ${D.chapter} · OPTIONAL · NOT ASSESSED · COURSE ADDITION</p><h1>${esc(x.title)}</h1></div><span class="counter">Extra ${k+1} of ${EXTRAS.length}</span>${paceChip()}</div><section class="extra-body extra-${x.id.toLowerCase()}">${body}</section>`;
 $('#prevBtn').disabled=false;$('#nextBtn').disabled=false;$('#progress').innerHTML=`Optional extra ${k+1} of ${EXTRAS.length} · then the close`;$('#live').textContent=x.title;
 try{history.replaceState(null,'','#'+x.id);}catch(e){}
 requestAnimationFrame(fitExtra);
}
function gutBlock(round){
 const g=STORY?.gut;if(!g)return '';
 const counts=state.gut[round]||g.options.map(()=>0),total=counts.reduce((x,y)=>x+y,0),before=state.gut.before;
 return `<div class="gut" data-gut-round="${round}"><p class="gut-q"><span>${round==='before'?'GUT CHECK · BEFORE ANY THEORY':'VOTE AGAIN · SAME QUESTION'}</span>${esc(g.q)}</p><div class="gut-options">${g.options.map((o,i)=>`<button class="gut-opt" data-gut="${round}" data-opt="${i}"><i>${i+1}</i><span>${esc(o)}</span><b>${counts[i]||''}</b>${total?`<em style="--w:${Math.round(100*(counts[i]||0)/total)}%"></em>`:''}</button>`).join('')}</div><p class="gut-help"><span class="gut-how">Show 1, 2 or 3 fingers. Tap an option to count hands.</span>${round==='after'&&before?` <b class="gut-before">at the start: ${g.options.map((_,i)=>`${i+1} → ${before[i]||0}`).join(', ')}</b>`:''} <button class="link-btn" data-gut-reset="${round}">Reset</button></p></div>`;
}
function renderVote(i){
 const q=voteItem(i),v=state.votes[i]||{},labels='ABCDEF',round=voteStage<2?'r1':'r2',show=voteStage===3;
 const bar=(r,k)=>{const c=v[r]||[],t=c.reduce((x,y)=>x+y,0);return t?`<em class="bar ${r}" style="--w:${Math.round(100*(c[k]||0)/t)}%"><span>${c[k]||0}</span></em>`:'';};
 const steps=['Vote alone','Convince a neighbour · 60 s','Vote again','Reveal'];
 $('#chapter-main').classList.add('vote-page');
 $('#chapter-main').insertAdjacentHTML('beforeend',`<div class="vote"><div class="vote-top"><div><p class="ey">CLASS VOTE · ACT ${i+1} · OBJECTIVE ${D.chapter}.${i+1}</p><h2>${esc(q.q)}</h2></div><ol class="vote-steps">${steps.map((t,k)=>`<li class="${k<voteStage?'done':k===voteStage?'on':''}">${t}</li>`).join('')}</ol></div>
 <div class="vote-options">${q.options.map((o,k)=>`<button class="vote-opt${show&&k===q.answer?' correct':''}${show&&k!==q.answer?' muted':''}" data-vote-opt="${k}" ${voteStage===1||show?'disabled':''}><i>${labels[k]}</i><span>${esc(o)}</span><span class="bars">${bar('r1',k)}${bar('r2',k)}</span></button>`).join('')}</div>
 ${show?`<div class="vote-why"><b>Why</b><p>${esc(q.why)}</p></div>`:voteStage===1?`<div class="vote-why discuss"><b>Find someone who voted differently.</b><p>Convince them in 60 seconds, or let them convince you. Use the case, not the slide wording.</p></div>`:''}
 <div class="actions"><button class="primary" data-vote-next>${voteStage<3?steps[voteStage+1]+' →':'Back to the lecture'}</button>${voteStage!==1&&!show?`<button data-vote-minus>Undo last count</button>`:''}<button data-vote-back>Return to slide</button><span class="small">Tap an option to count raised hands (${round==='r1'?'first':'second'} vote). Practice, not assessment: what we assess is your own reasoning in Assignment ${D.assignment}.</span></div></div>`);
}
// Fit v1: grow the evidence text until it fills the space the slide gives it (never shrink below the
// designed size, never overflow). Recomputed on every render, resize and answer reveal.
// The case file grows to fill the slide (zoom on its blocks, binary search), never past the footer.
function fitCase(){
 const m=$('#chapter-main');if(!m||!STORY||!['case-file','cold-open-page','end-page'].some(c=>m.classList.contains(c)))return;
 if(readingLayout()||matchMedia('(max-width:1000px)').matches){m.style.removeProperty('--cf');return;}
 const fits=()=>{const r=m.getBoundingClientRect(),lim=r.bottom-parseFloat(getComputedStyle(m).paddingBottom)-6;if(m.scrollWidth>m.clientWidth+1)return false;for(const c of m.querySelectorAll('.hero,.end-hero,.end-copy,.gut,.story-grid section,.story-head,.cast-card,.case-side'))if(c.scrollHeight>c.clientHeight+1||c.scrollWidth>c.clientWidth+1)return false;for(const e of m.querySelectorAll('p,li,button,a,h2,h3,img')){const q=e.getBoundingClientRect();if(q.width&&(q.bottom>lim||q.right>r.right+1))return false;}return true;};
 let lo=.8,hi=1.6;m.style.setProperty('--cf','1');if(fits())lo=1;else{m.style.setProperty('--cf',String(lo));if(!fits()){m.style.setProperty('--cf','1');return;}}
 for(let k=0;k<8;k++){const x=(lo+hi)/2;m.style.setProperty('--cf',x.toFixed(3));if(fits())lo=x;else hi=x;}
 m.style.setProperty('--cf',lo.toFixed(3));
}
function fitText(){
 fitCase();fitGrid();fitLists();
}
function fitGrid(){
 const g=$('#chapter-main .body-grid');if(!g||!STORY||readingLayout()||matchMedia('(max-width:1000px)').matches){g?.style.removeProperty('--fit');return;}
 const main=$('#chapter-main'),hasLists=!!main.querySelector('.src-lists');  // req-v5: source lists share the slide, so the grid may not grow past 1 and must leave room for them
 const boxes=[g,...g.querySelectorAll('.concept,.meaning,.visual,.approach')];
 const fits=()=>boxes.every(e=>e.scrollHeight<=e.clientHeight+1)&&g.scrollWidth<=g.clientWidth+1&&[...g.querySelectorAll('.concept b,.concept span,.points li,td,th')].every(t=>t.scrollWidth<=t.clientWidth+1)&&(!hasLists||main.scrollHeight<=main.clientHeight+1);
 g.style.setProperty('--fit','1');let lo=1,hi=hasLists?1:1.65;
 if(!fits()){lo=.75;hi=1;g.style.setProperty('--fit','.75');if(!fits()){g.style.setProperty('--fit',hasLists?'.75':'1');return;}}for(let k=0;k<8;k++){const m=(lo+hi)/2;g.style.setProperty('--fit',m.toFixed(3));if(fits())lo=m;else hi=m;}
 g.style.setProperty('--fit',lo.toFixed(3));
}
function fitLists(){
 // req-v5 (COV-2): the source lists stay on the slide in full; shrink them a little, then scroll inside the block rather than clip.
 const main=$('#chapter-main'),L=main&&main.querySelector('.src-lists');if(!L)return;
 L.style.removeProperty('--lfit');
 if(readingLayout()||matchMedia('(max-width:1000px)').matches)return;
 const over=()=>main.scrollHeight-main.clientHeight;let f=1;
 while(over()>1&&f>0.8){f-=0.05;L.style.setProperty('--lfit',f.toFixed(2));}
}
function fitExtra(){
 const g=$('#chapter-main .extra-body');if(!g)return;if(matchMedia('(max-width:1000px)').matches){g.style.removeProperty('--fit');return;}
 const m=$('#chapter-main'),room=()=>m.getBoundingClientRect().bottom-parseFloat(getComputedStyle(m).paddingBottom)-g.getBoundingClientRect().top;
 const fits=()=>g.scrollHeight<=room()+1&&g.scrollWidth<=g.clientWidth+1&&[...g.querySelectorAll('pre')].every(p=>p.scrollWidth<=p.clientWidth+1);
 let lo=.8,hi=1.6;g.style.setProperty('--fit','.8');if(!fits())return;
 for(let k=0;k<9;k++){const m=(lo+hi)/2;g.style.setProperty('--fit',m.toFixed(3));if(fits())lo=m;else hi=m;}
 g.style.setProperty('--fit',lo.toFixed(3));
}
window.addEventListener('resize',()=>requestAnimationFrame(()=>{fitText();fitExtra();}));
let thinkTimer=null;
function think(b){clearInterval(thinkTimer);let t=Number(b.dataset.think)||30;const show=()=>{b.textContent=t>0?`Think · ${t} s`:'Now compare with a neighbour';};b.classList.remove('done');b.classList.add('running');show();thinkTimer=setInterval(()=>{t--;show();if(t<=0){clearInterval(thinkTimer);thinkTimer=null;b.classList.replace('running','done');}},1000);}
function renderMindMap(){
 const r=D.roadmap;
 $('#chapter-main').classList.add('mindmap-page');
 $('#chapter-main').insertAdjacentHTML('beforeend',`
 <div class="map-question">
   <span>CHAPTER ${D.chapter} · BIG QUESTION</span>
   <h2>${esc(r.question)}</h2>
   <p>${esc(D.case.headline)}</p>
 </div>
 <div class="concept-path" aria-label="Five connected chapter concepts">
   ${r.branches.map((b,i)=>`<button class="map-step" data-jump="${esc(b.target)}" aria-label="${esc(b.label)}. Open the related lesson.">
      <span class="step-number">${i+1}</span>
      <span class="step-verb">${esc(b.verb)}</span>
      <strong>${esc(b.label)}</strong>
      <span class="step-detail">${esc(b.detail)}</span>
      <span class="step-case"><i>In our story</i>${esc(b.caseLens||'Use this concept to narrow the decision.')}</span>${b.aiLens?`<span class="step-lens">AI lens · ${esc(b.aiLens)}</span>`:''}
   </button>`).join('')}
 </div>
 <p class="mind-link"><b>WHY THIS ORDER</b> ${esc(r.connection)}</p>
 <div class="student-roadmap" aria-label="What happens in class and after class">
   <section class="road-stage"><h3><span>01</span> In class</h3><p><b>Instructor:</b> Explain the mechanism and guide three short stations.</p><p><b>You:</b> ${esc(r.inClass)}</p><p class="road-result">One evolving practice card—not several reports.</p></section>
   <section class="road-stage"><h3><span>02</span> Required review</h3><p><b>Instructor:</b> Name the exact source selections.</p><p><b>You:</b> Review source slides ${D.readings.map(x=>esc(x.range)).join(' + ')} and complete the five-objective practice.</p><p class="road-result">Fix misunderstandings before the assignment.</p></section>
   <section class="road-stage"><h3><span>03</span> Assignment ${D.assignment}</h3><p><b>Instructor:</b> Review using the published rubric.</p><p><b>You:</b> ${esc(r.deliverable)}</p><p class="road-result">New case → commit → STRESS → REFIT → Blackboard.</p></section>
 </div>
 <div class="map-bottom"><p><b>REQUIRED:</b> class + named review + assignment. Other tools support the same work unless explicitly assigned.</p><div class="actions">${button('Case connections','CASEMAP')}${jumpButton('START','Start the story →')}</div></div>`);
}
function renderStory(){
 if(STORY){renderCaseFile();return;}
 const r=D.roadmap;
 $('#chapter-main').classList.add('story-page');
 $('#chapter-main').insertAdjacentHTML('beforeend',`
 <div class="story-head"><span>OUR STORY · FICTIONAL TEACHING CASE ${kindTag('training')}</span><h2>${esc(D.case.headline)}</h2><p>Keep this same case in mind as every concept is introduced.</p></div>
 <div class="story-grid">
   <section><h3>1 · Situation</h3><p>${esc(D.case.text)}</p></section>
   <section><h3>2 · Your decision</h3><p>${esc(D.case.question)}</p></section>
   <section><h3>3 · Evidence rule</h3><p>Use supplied facts and transparent calculations. Keep missing tests and unknowns visible; do not invent measurements.</p></section>
 </div>
 ${(STORY?.lens||D.case.lens)?`<div class="story-lens"><b>${STORY?'AI IN THE SYSTEM · PART OF THE CASE':'AI LENS · ADDED TO THE CASE'}</b>${esc(STORY?.lens||D.case.lens)}</div>`:''}
 <div class="story-route" aria-label="How the story will be revisited">
   ${r.branches.map((b,i)=>`<span><b>${i+1}</b>${esc(b.label)}</span>`).join('')}
 </div>
 <div class="story-note"><b>One story, five lenses.</b> Each main slide will show a CASE THREAD that tells you which part of this decision the concept helps you answer. The changed constraint is revealed later—do not guess it now.</div>
 <div class="actions story-action">${jumpButton(r.branches[0].target,'Start learning →')}</div>`);
}
function renderCaseFile(){
 const r=D.roadmap,cast=[SERIES.lead,SERIES.mentor,STORY.client];
 $('#chapter-main').classList.add('story-page','case-file');
 $('#chapter-main').insertAdjacentHTML('beforeend',`
 <div class="story-head"><span>${esc(STORY.episode)} · FICTIONAL TEACHING CASE ${kindTag('training')}</span><h2>${esc(D.case.headline)}</h2><p>${esc(STORY.setting)} <b class="clock">⏱ ${esc(STORY.clock)}</b></p></div>
 ${STORY.caseFigure?`<div class="case-body"><figure class="case-fig"><button class="figure-button" data-image="${esc(STORY.caseFigure.src)}" data-caption="${esc(STORY.caseFigure.alt)}" aria-label="Enlarge: ${esc(STORY.caseFigure.alt)}"><img src="${esc(STORY.caseFigure.src)}" alt="${esc(STORY.caseFigure.alt)}"></button><figcaption><b>One story, five lenses.</b> Five acts, one concept each; something changes before the end. Supplied facts only. · ${esc(STORY.caseFigure.caption||'')}</figcaption></figure><div class="case-side">
 <div class="cast compact" aria-label="People in this episode">${cast.map(c=>`<div class="cast-card"><i aria-hidden="true">${esc(c.name.replace(/^Dr\.\s*/,'').charAt(0))}</i><b>${esc(c.name)}</b><span>${esc(c.role)}</span></div>`).join('')}</div>
 <div class="story-grid stacked">
   <section><h3>What we know</h3><p>${esc(D.case.text)}</p></section>
   <section><h3>The decision</h3><p>${esc(D.case.question)}</p></section>
   <section><h3>What is at stake</h3><p>${esc(STORY.stakes)}</p></section>
 </div></div></div>
 <div class="case-foot">${(STORY?.lens||D.case.lens)?`<div class="story-lens"><b>AI IN THE SYSTEM · PART OF THE CASE</b>${esc(STORY?.lens||D.case.lens)}</div>`:''}<span class="actions story-action">${jumpButton(r.branches[0].target,'Act 1 →')}</span></div>`:`<div class="cast" aria-label="People in this episode">${cast.map(c=>`<div class="cast-card"><i aria-hidden="true">${esc(c.name.replace(/^Dr\.\s*/,'').charAt(0))}</i><b>${esc(c.name)}</b><span>${esc(c.role)}</span></div>`).join('')}</div>
 <div class="story-grid">
   <section><h3>What we know</h3><p>${esc(D.case.text)}</p></section>
   <section><h3>The decision</h3><p>${esc(D.case.question)}</p></section>
   <section><h3>What is at stake</h3><p>${esc(STORY.stakes)}</p></section>
 </div>
 ${(STORY?.lens||D.case.lens)?`<div class="story-lens"><b>${STORY?'AI IN THE SYSTEM · PART OF THE CASE':'AI LENS · ADDED TO THE CASE'}</b>${esc(STORY?.lens||D.case.lens)}</div>`:''}
 <div class="story-route" aria-label="Five acts">${r.branches.map((b,i)=>`<span><b>${i+1}</b>${esc(b.label)}</span>`).join('')}</div>`}
 ${STORY.caseFigure?'':`<div class="story-note"><p><b>One story, five lenses.</b> Five acts, one concept each, with class votes along the way; something changes before the end. Evidence rule: supplied facts and transparent calculations only, and keep unknowns visible. <b>${esc(SERIES.principle||'')}</b></p><span class="actions story-action">${jumpButton(r.branches[0].target,'Act 1 →')}</span></div>`}`);
}
// BOUND-1..4: each chapter ends with one sentence on when its mechanism is the wrong choice.
// The student writes first (COMMIT), then compares; the sentence is saved for the assignment export.
function boundBlock(){const B=D.bound;if(!B)return '';const ck='commit_bound';return `<div class="bound-block"><p class="ey">WHEN IS THIS CHAPTER’S MECHANISM THE WRONG CHOICE? · ONE SENTENCE</p>${commitBox(ck)}<div class="buttons"><button data-bound-reveal data-commit-for="${ck}"${commitReady(ck)?'':' disabled'}>Compare with the model sentence</button>${skipBtn(ck)}</div><div class="bound-answer" hidden><div class="you-wrote-slot"></div><p><b>Model sentence.</b> ${esc(B.model)}</p><p class="small">The test is an observable condition: ${esc(B.condition)}.${COMMIT?' Your sentence is saved on this device and added to your assignment export.':''}</p></div></div>`;}
function renderClosing(){
 const r=D.roadmap;
 $('#chapter-main').classList.add('end-page');
 $('#chapter-main').insertAdjacentHTML('beforeend',`
 <div class="end-hero"${coverArt()?'':' style="grid-template-columns:1fr"'}><div class="end-copy">
  <p class="ey">CHAPTER ${D.chapter} · ${gateSolved()?'COMPLETE':'NOT COMPLETE YET · SOLVE THE TRANSFER CASE'} · READINESS</p>${gateOn()&&!gateSolved()?gateButton():''}<h2>${esc(D.title)}</h2>
  ${STORY?`<div class="epilogue"><span>${esc(STORY.episode)} · ${esc(STORY.epilogueTag||'YOUR TURN: SAME REASONING, NEW CASE IN THE ASSIGNMENT')}</span>${kindTag('training')}<p>${esc(STORY.epilogue)}</p><p class="assess-line"><b>Assessed:</b> ${STORY.assessLine?esc(STORY.assessLine):'your FIT, BOUND, ACT, EVIDENCE and REFIT, in your own words. AI may help you practise, not decide or sign. Expect a two-minute check that you can explain it.'}</p></div>${gutBlock('after')}<div class="exit-ticket"><b>Exit ticket · one minute, on paper or Blackboard</b><ol><li>One idea you can now explain to Layan.</li><li>The muddiest point from today.</li><li>Did your vote change? What changed it?</li></ol></div>`:''}
  ${boundBlock()}<p class="end-success">Ready means you can <b>explain, verify and own</b> the decision—not merely repeat the content.</p>
  <div class="readiness-strip" aria-label="Readiness checks"><section><b>Explain</b><span>Use the mechanism without outsourcing the core judgment to AI.</span></section><section><b>Verify</b><span>Use inspectable evidence; label unknowns and any AI assistance.</span></section><section><b>Own</b><span>Revise under changed evidence and name the responsible human role.</span></section></div>
  <div class="end-required"><section><span>1</span><div><b>Required review</b><p>${D.readings.map(x=>esc(x.title)+' · '+esc(x.range)).join(' | ')}</p></div></section><section><span>2</span><div><b>Five-objective check</b><p>Correct misunderstandings before the assessed case.</p></div></section><section><span>3</span><div><b>Assignment ${D.assignment}</b><p>${esc(r.deliverable)} Submit through Blackboard.</p></div></section></div>
  <div class="actions">${EXTRAS.length?`<button data-open="${esc(EXTRAS[0].id)}">${STORY?.real?'Real case, lab &amp; practice':'Lab &amp; practice'} · ${EXTRAS.length} extra slides</button>`:''}${STORY&&PRESENTER?'<button data-evidence title="Counts from this device only, for the instructor evidence page">Export class evidence (CSV)</button>':''}${button('Preparation & sources','DISCLOSURE')}${D.studyList?.length?button('What to study for the exam','STUDY'):''}${button('Open required review','READING','primary')}<a href="${esc(AHREF)}">${esc(ALABEL)}</a></div>
 </div>${coverArt()}</div>`);
}
function nelcAlignment(){
 const r=D.roadmap||{};
 modal('NELC alignment · Chapter '+D.chapter,`
 <div class="nelc-reference"><div class="national-logo"><img src="assets/national/nelc-logo.png" alt="National eLearning Center"></div><div><p class="ey">SAUDI NATIONAL ALIGNMENT · VERSION 1.0 · SEPTEMBER 2026</p><h3 lang="en" dir="ltr">AI-supported Teaching and Learning Design Framework</h3><p>National eLearning Center · Saudi Arabia</p></div></div>
 <div class="callout"><b>Alignment, not endorsement.</b> This chapter operationalizes the framework as a design crosswalk. It does not claim NELC certification, approval or partnership.</div>
 <div class="callout" lang="en" dir="ltr"><b>AI’s purpose in this chapter:</b> ${esc(window.ISCARB_NATIONAL.chapters[D.chapter].ai)}. The learner starts independently, then verifies and discloses any assistance.<br><b>Verification evidence:</b> ${esc(window.ISCARB_NATIONAL.chapters[D.chapter].evidence)}.<br><b>Review criterion:</b> ${esc(window.ISCARB_NATIONAL.chapters[D.chapter].check)}</div><h3>Five design principles → this chapter</h3><div class="nelc-principles"><article><b>1 · Learning first</b><span>Five measurable objectives and named source review come before the AI layer.</span></article><article><b>2 · Clear educational value</b><span>AI is used for transfer, critique, practice or simulation when it adds a defined learning benefit.</span></article><article><b>3 · Human-centered</b><span>The learner explains and decides; the instructor retains educational and professional judgment.</span></article><article><b>4 · Responsible design</b><span>Evidence, uncertainty, disclosure, human review and bounded AI roles stay visible.</span></article><article><b>5 · Evidence-based improvement</b><span>Readiness, transfer and revision evidence matter; output quality alone is not treated as learning.</span></article></div>
 <h3>Six-stage crosswalk</h3><div class="nelc-stages"><article><i>1</i><b>Define</b><span>${D.objectives.length} objectives + observable evidence.</span></article><article><i>2</i><b>Design</b><span>Mind map → story → source-grounded explanation → three stations.</span></article><article><i>3</i><b>Enhance</b><span>AI lens/challenge adds practice after the core concept is established.</span></article><article><i>4</i><b>Distribute roles</b><span>Student reasons; AI supports; instructor validates and judges.</span></article><article><i>5</i><b>Assess</b><span>Independent reasoning, commitment, changed evidence, REFIT and disclosure.</span></article><article><i>6</i><b>Verify & improve</b><span>Readiness check, rubric evidence, feedback and course evaluation inform improvement.</span></article></div>
 <h3>Role boundary in Chapter ${D.chapter}</h3><table class="nelc-roles"><tr><th>Learner</th><th>AI</th><th>Instructor</th></tr><tr><td>Explain the mechanism, make and revise the bounded decision, verify any AI-supported claim.</td><td>Support practice, critique, alternatives or simulation; never become the evidence or final authority by itself.</td><td>Select the source and case, guide practice, sample reasoning and retain final educational judgment.</td></tr></table>
 <p class="small"><b>Chapter design question:</b> ${esc(r.question||D.case?.question||'What must the learner be able to do independently?')}</p>
 <div class="actions"><a class="primary-link" href="../../nelc-alignment.html#chapter-${D.chapter}" target="_blank" rel="noopener">Open full NELC × iSCARB crosswalk ↗</a>${button('Readiness crosswalk','READINESS')}</div>`);
}
function mapObjectives(){
 modal('Five chapter objectives · source outline',`<div class="callout">The mind map groups the existing source concepts for learning. It does not replace the five objectives, original sections or assigned source review.</div><ol class="objective-list">${D.objectives.map((x,i)=>`<li>${esc(x)}${D.objectiveLens?.[i]?`<small class="obj-lens">AI lens · ${esc(D.objectiveLens[i])}</small>`:''}</li>`).join('')}</ol>${D.cs2023?`<h3>International alignment · ACM/IEEE-CS/AAAI CS2023</h3><table class="align"><tr><th>CS2023 unit</th><th>How this chapter addresses it</th></tr>${D.cs2023.map(r=>`<tr><td><b>${esc(r[0])}</b><br><small>${esc(r[1])}</small></td><td>${esc(r[2])}</td></tr>`).join('')}</table><p class="small">Mapped against the CS2023 Software Engineering knowledge-area text and, for other areas, at knowledge-area level. Alignment describes coverage, not accreditation.</p>`:''}<h3>Original chapter spine</h3><ul>${D.sections.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><h3>Check your understanding</h3><p>${esc(D.roadmap.success)}</p><h3>Our fictional classroom case</h3><p>${esc(D.case.text)}</p><p><b>${esc(D.case.question)}</b></p><div class="actions">${jumpButton('MAP','Back to chapter map')}${button('Five-objective practice','QUIZ')}</div>`);
}
function updateMapLocation(){
 const s=D.slides[index],r=D.roadmap,b=r.branches.find(x=>x.units.includes(s.id)),label=$('#topic-location');
 if(label)label.textContent=s.id==='MAP'?'Your overview':s.id==='TITLE'?'Start here':b?b.label:stationMode?'Practice station':'Case and learning path';
 const mapButton=$('#mapBtn');if(mapButton)mapButton.setAttribute('aria-current',s.id==='MAP'?'step':'false');
}

function open(k){k=(D.aliases||{})[k]||k;const xi=EXTRAS.findIndex(x=>x.id===k);if(xi>=0){if(!PRESENTER)index=D.slides.length-2;renderExtra(xi);return;}if(D.slides.some(s=>s.id===k)){jump(k);return;}const aliases={PREP:'QUIZ',C01:'COVERAGE',J01:'READINESS',J02:'QUIZ',AIGATE:'AI',READING:'READING'};k=aliases[k]||k;({GATE:()=>transferCheck(),UNITS:indexModal,READING:reading,COVERAGE:coverage,RULES:rules,TOOLS:studyTools,OBJECTIVES:mapObjectives,CASEMAP:()=>modal('Five concepts in our case',`<p>${esc(D.case.question)}</p><div class="case-map-details">${D.roadmap.branches.map(b=>`<section><h3>${esc(b.label)}</h3><p>${esc(b.caseLens||'Use this concept to narrow the decision.')}</p>${b.aiLens?`<p>AI lens · ${esc(b.aiLens)}</p>`:''}${jumpButton(b.target,'Open this concept')}</section>`).join('')}</div>`),CARD:card,HSTACK:hstack,PREDICT:predict,BRIDGE:bridge,MONITOR:monitor,LOCAL:local,PRACTICE:practice,WELLBEING:wellbeing,AI:ai,EVIDENCE:evidence,RUBRIC:rubric,READINESS:()=>nationalSlide(0),NELC:()=>nationalSlide(1),DISCLOSURE:()=>modal('Preparation, sources and national alignment',`<p>${esc(D.disclosure||'Source-grounded classroom materials; instructor review remains required.')}</p><p>National alignment: learning outcomes first; bounded AI assistance; accountable human judgment; improvement from evidence.</p><div class="actions">${button('Jaheziah readiness','READINESS')}${button('NELC alignment','NELC')}${button('Source coverage','COVERAGE')}</div>`),READINESSDETAIL:readiness,NELCDETAIL:nelcAlignment,'NATIONAL-JAHEZIAH':()=>nationalSlide(0),'NATIONAL-NELC':()=>nationalSlide(1),PORTFOLIO:portfolio,QUIZ:quiz,STUDY:studyList,CALCULATOR:calculator,HELP:help,NOTES:notes,AIASSIGN:aiChallenge}[k]||(()=>modal('Source or tool',`<p>This earlier unit is available in the complete source review.</p><a href="sources/Ch${D.chapter}-Study.html">Open the source ledger</a>`)))();}
function fieldLabel(k){if(labels[k])return labels[k];if(k==='commit_their')return 'THEIR CHANGE · your prediction before the assignment';if(k==='commit_their_skip')return 'THEIR CHANGE · prediction skipped';if(k==='commit_bound')return 'WHEN THIS CHAPTER’S MECHANISM IS THE WRONG CHOICE · your sentence';if(k==='commit_bound_skip')return 'WHEN THIS CHAPTER’S MECHANISM IS THE WRONG CHOICE · skipped';const g={gate_line:'TRANSFER CASE · your reason',gate_pick:'TRANSFER CASE · your last choice',gate_tries:'TRANSFER CASE · tries',gate_solved:'TRANSFER CASE · solved'}[k];if(g)return g;if(!k.startsWith('commit_'))return k;let r=k.slice(7);const skip=r.endsWith('_skip');if(skip)r=r.slice(0,-5);const st=r.match(/^station(\d+)$/);if(st)return `STATION ${st[1]} · your sentence before the discussion`+(skip?' · skipped':'');const two=/_2$/.test(r);if(two)r=r.slice(0,-2);const s=D.slides.find(x=>x.id.toLowerCase().replace(/[^a-z0-9]/g,'_')===r);return `YOUR CALL · ${s?s.title:r}`+(two?' · second question':'')+(skip?' · skipped':'');}
function fieldValue(k,v){if(/_skip$/.test(k))return v==='1'?'Skipped writing before the reveal.':'[not skipped]';if(k==='gate_solved')return v==='1'?'Yes':'Not yet';if(k==='gate_pick'&&D.transfer?.check){const o=D.transfer.check.options[Number(v)];return o?`${'ABC'[Number(v)]} · ${o}`:v;}return v||'[not entered]';}
function readable(){return [`# Chapter ${D.chapter}: ${D.title}`,'Professor Adeeb Noor · CPIT-455',`Release ${D.release}`,'Fictional teaching case. Student draft; not a grade, submission or certification.','',...Object.entries(state.fields).flatMap(([k,v])=>['## '+fieldLabel(k),fieldValue(k,v),'']),'## AI gate',aiVerdict(state.ai)].join('\n');}
function evidenceCSV(){
 const q=v=>/[",\n]/.test(v=String(v??''))?'"'+v.replace(/"/g,'""')+'"':v,day=new Date().toISOString().slice(0,10),rows=[['chapter','date','item','kind','option','option_text','correct','round1','round2']];
 const g=STORY?.gut;if(g)g.options.forEach((o,k)=>rows.push([D.chapter,day,'gut','gut',k+1,o,'',state.gut.before?.[k]??'',state.gut.after?.[k]??'']));
 D.quiz.forEach((_,i)=>{const x=voteItem(i),v=state.votes[i];if(!x||(!v?.r1&&!v?.r2))return;x.options.forEach((o,k)=>rows.push([D.chapter,day,'act'+(i+1),'vote',k+1,o,k===x.answer?1:0,v.r1?.[k]??'',v.r2?.[k]??'']));});
 paceLog().filter(x=>x.chapter===D.chapter).forEach(x=>rows.push([D.chapter,x.date,'lecture','duration','',x.mode,'',x.planned,x.actual]));
 return rows.map(r=>r.map(q).join(',')).join('\n')+'\n';
}
function download(text,name,type){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),10000);}
function sanitize(p){if(!p||p.schema!=='iscarb-classroom-v3'||p.chapter!==D.chapter||!p.state)throw Error('This backup belongs to a different chapter or format.');let x=p.state,st={fields:{},seen:[],quiz:{},ai:{},self:{},votes:{},gut:{},theme:x.theme==='day'?'day':'night'};for(const [k,v]of Object.entries(x.fields||{})){if(!validField(k)||typeof v!=='string'||v.length>15000)throw Error('Invalid text field.');st.fields[k]=v;}for(const [k,v]of Object.entries(x.quiz||{})){if(!/^[0-4]$/.test(k)||!v||!Number.isInteger(v.answer)||v.answer<0||v.answer>=D.quiz[k].options.length)throw Error('Invalid quiz record.');st.quiz[k]={answer:v.answer,checked:!!v.checked};}for(const[k,v]of Object.entries(x.ai||{})){if(!/^[0-3]$/.test(k)||!['yes','no'].includes(v))throw Error('Invalid AI record.');st.ai[k]=v;}st.seen=(Array.isArray(x.seen)?x.seen:[]).filter(k=>D.slides.some(s=>s.id===k));const counts=(a,n)=>Array.isArray(a)&&a.length===n&&a.every(c=>Number.isInteger(c)&&c>=0&&c<=999);for(const[k,v]of Object.entries(x.votes||{})){if(/^[0-4]$/.test(k)&&voteItem(k)&&v&&['r1','r2'].every(r=>v[r]===undefined||counts(v[r],voteItem(k).options.length)))st.votes[k]={r1:v.r1,r2:v.r2};}const g=STORY?.gut?.options?.length||0;for(const r of['before','after'])if(g&&counts(x.gut?.[r],g))st.gut[r]=x.gut[r];return {state:st};}
async function restore(file){try{if(file.size>1000000)throw Error('Backup is too large.');const p=sanitize(JSON.parse(await file.text()));if(!confirm('Replace this chapter’s current classroom draft with the imported backup? Assignment work will not change.'))return;state=p.state;save();render();card();}catch(e){modal('Import did not complete',`<p>${esc(e.message)}</p><p>Your existing draft was not changed.</p>`);}}
/* ===== iSCARB GenAI edition additions (v11): tool tiles + embedded AI challenge ===== */
const ICON={
 CARD:'<path d="M5 4h11l3 3v13H5z"/><path d="M8 11h8M8 15h6"/>',
 OBJECTIVES:'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
 NOTES:'<path d="M4 5h16v11H9l-5 4z"/>',
 CALCULATOR:'<rect x="6" y="3" width="12" height="18" rx="2"/><path d="M9 7h6M9 12h1M14 12h1M9 16h1M14 16h1"/>',
 READING:'<path d="M3 5h7a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H3zM21 5h-7a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h7z"/>',
 QUIZ:'<path d="M9 9a3 3 0 1 1 4 2.8c-.7.3-1 .8-1 1.5V14"/><circle cx="12" cy="18" r=".6"/><circle cx="12" cy="12" r="9"/>',
 ASSIGN:'<path d="M9 4h6v3H9z"/><path d="M7 5H5v16h14V5h-2"/><path d="M9 13l2 2 4-4"/>',
 PORTFOLIO:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V4h6v3M3 12h18"/>',
 RULES:'<path d="M5 6h14M5 12h14M5 18h9"/><circle cx="3" cy="6" r=".6"/><circle cx="3" cy="12" r=".6"/><circle cx="3" cy="18" r=".6"/>',
 COVERAGE:'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
 READINESS:'<path d="M12 3l8 4v5c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7z"/><path d="M9 12l2 2 4-4"/>',
 AI:'<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
 AIASSIGN:'<path d="M12 2l2.4 5.6L20 10l-5.6 2.4L12 18l-2.4-5.6L4 10l5.6-2.4z"/><path d="M19 17l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>',
 NELC:'<path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/>',
 HELP:'<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
 DEFAULT:'<circle cx="12" cy="12" r="8"/><path d="M12 8v8M8 12h8"/>'
};
function icon(k){return `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICON[k]||ICON.DEFAULT}</svg>`;}
function tile(title,desc,k,cls=''){return `<button class="tile ${cls}" data-open="${esc(k)}"><span class="ti">${icon(k)}</span><span class="tt"><b>${esc(title)}</b><small>${esc(desc)}</small></span></button>`;}
function tileLink(title,desc,href,k,cls=''){return `<a class="tile ${cls}" href="${esc(href)}"><span class="ti">${icon(k)}</span><span class="tt"><b>${esc(title)}</b><small>${esc(desc)}</small></span></a>`;}
const MORE_DESC={HSTACK:'Layer the human and technical checks',PREDICT:'Commit a prediction before the evidence',BRIDGE:'Annotate how the idea is implemented',MONITOR:'Sort known, unknown and what to watch',LOCAL:'Saudi and regional context',PRACTICE:'How industry does this today',WELLBEING:'Sustainable engineering practice',EVIDENCE:'What counts as honest evidence',RUBRIC:'Four-level rubric used in this course'};
function studyTools(){
 const A=D.aiAssignment;
 modal('Study & tools',`${A?`<button class="tile tile-feature" data-open="AIASSIGN"><span class="ti">${icon('AIASSIGN')}</span><span class="tt"><em>AI challenge · Chapter ${D.chapter} · not graded</em><b>${esc(A.title)}</b><small>Practice only, not graded · same topic, new AI case · commit first, then face the change</small></span><span class="go">Start →</span></button>`:''}
 <div class="study-groups">
 <section class="grp grp-class"><h3><span>1</span>In class · one practice card</h3><div class="tiles">
  ${tile('Decision card','Your evolving claim, evidence and verdict · save a backup','CARD')}
  ${tile('Objectives & alignment','Five objectives, source spine and CS2023 alignment','OBJECTIVES')}
  ${PRESENTER?tile('Instructor notes','Teaching notes for the current slide · presenter mode','NOTES'):''}
  ${D.chapter===11?tile('Reliability calculator','POFOD, ROCOF and availability','CALCULATOR'):''}
 </div></section>
 <section class="grp grp-req"><h3><span>2</span>Required after class</h3><div class="tiles">
  ${tile('Required self-study','Named source slides to review','READING')}
  ${tile('Five-objective practice','One question per objective · attempt first','QUIZ')}
  ${D.studyList?.length?tile('What to study for the exam','Examinable content that is not on the slides, with source and textbook pages','STUDY'):''}
  ${tileLink('Assignment '+D.assignment,D.assignmentNote||('Separate case · '+D.points+' points · Blackboard'),AHREF,'ASSIGN','tile-req')}
  ${tile('Assignment workflow','Artifact, commit/reveal and rubric','PORTFOLIO')}
 </div><p class="small">Blackboard gives dates and confirms submission. A local draft is not submitted work.</p></section>
 <section class="grp grp-src"><h3><span>3</span>Sources, methodology & support</h3><div class="tiles">
  ${tile('20 iSCARB rules','The method behind every slide','RULES')}
  ${tile('Source coverage','Which source slide feeds which lesson','COVERAGE')}
  ${tile('NCAAA / Jaheziah','Outcome and readiness crosswalk','READINESS')}
  ${tile('NELC alignment','Saudi AI-supported teaching & learning design framework','NELC')}
  ${tile('AI use & checking','Permissibility gate and disclosure','AI')}
 </div><details class="tool-details"><summary>More iSCARB tools · use when relevant or assigned</summary><div class="tiles">${['HSTACK','PREDICT','BRIDGE','MONITOR','LOCAL','PRACTICE','WELLBEING','EVIDENCE','RUBRIC'].map(k=>tile(titleOf(k),MORE_DESC[k]||'',k)).join('')}</div></details></section>
 <section class="grp grp-disp"><h3><span>4</span>Display</h3><div class="actions"><button id="themeBtn">Day / night</button><button id="fullBtn">Fullscreen</button>${button('Navigation and saving help','HELP')}</div></section></div>`);
}
const AIX=['aix_fit','aix_bound','aix_act','aix_evidence'];
const AIX_LABEL={aix_fit:'FIT · what fits now, and why',aix_bound:'BOUND · the observable condition where it stops fitting',aix_act:'ACT · the concrete engineering action',aix_evidence:'EVIDENCE · what another engineer could inspect',aix_ai:'AI DECLARATION · tools used, what you checked yourself',aix_refit:'REFIT · justify your verdict using the new information',aix_owner:'OWNER · who accepts the residual risk, and who must be told'};
function aixField(k,ph,locked){const v=state.fields[k]||'';return `<label class="field ${locked?'locked':''}"><span>${esc(AIX_LABEL[k])}</span><textarea data-field="${esc(k)}" maxlength="6000" placeholder="${esc(ph||'')}" ${locked?'readonly':''}>${esc(v)}</textarea></label>`;}
function aixWords(){return AIX.map(k=>(state.fields[k]||'').trim().split(/\s+/).filter(Boolean).length).reduce((a,b)=>a+b,0);}
function aixReady(){return AIX.every(k=>(state.fields[k]||'').trim().length>=20);}
function aixText(){const A=D.aiAssignment,f=state.fields;return [`# CPIT-455 · Chapter ${D.chapter} · AI challenge`,`## ${A.title}`,`Committed: ${f.aix_commit||'not committed'}`,'',`### Scenario`,A.scenario,'',...AIX.map(k=>`### ${AIX_LABEL[k]}\n${f[k]||''}`),'',`### ${AIX_LABEL.aix_ai}\n${f.aix_ai||''}`,'',`### STRESS`,f.aix_commit?A.stress:'(revealed after commitment)','',`### Verdict: ${f.aix_verdict||'—'}`,`### ${AIX_LABEL.aix_refit}\n${f.aix_refit||''}`,`### ${AIX_LABEL.aix_owner}\n${f.aix_owner||''}`,'',`Words in FIT–EVIDENCE: ${aixWords()} (target ${A.words||'180–260'})`].join('\n');}
function aiChallenge(){
 const A=D.aiAssignment;if(!A){modal('AI challenge','<p>No AI challenge is defined for this chapter.</p>');return;}
 const f=state.fields,locked=!!f.aix_commit;
 modal('AI challenge · Chapter '+D.chapter+' · practice, not graded',`<div class="aix-head"><span class="ai-tag">AI</span>${kindTag('fictional')}<b>${esc(A.title)}</b><span class="aix-badge">Practice only · not graded · this is not Assignment ${esc(D.assignment)}</span></div>
 <div class="aix-case"><h3>Scenario</h3><p>${esc(A.scenario)}</p><ul>${(A.facts||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p class="aix-q"><b>Your decision:</b> ${esc(A.question)}</p></div>
 <ol class="aix-steps"><li class="${locked?'done':'on'}">Decide</li><li class="${locked?'done':''}">Commit</li><li class="${locked?'on':''}">Face the change</li><li class="${f.aix_verdict?'done':''}">Revise & own</li></ol>
 <div class="two-col">${aixField('aix_fit',A.hints?.fit,locked)}${aixField('aix_bound',A.hints?.bound,locked)}${aixField('aix_act',A.hints?.act,locked)}${aixField('aix_evidence',A.hints?.evidence,locked)}</div>
 <p class="small" id="aix-count">Words in FIT–EVIDENCE: ${aixWords()} · target ${esc(A.words||'180–260')}</p>
 ${aixField('aix_ai','None, or: which tool, for what, and how you checked its output independently.',false)}
 ${aixRubric(A,!locked)}
 ${locked?`<div class="aix-stress"><h3>New information · ${esc(f.aix_commit)}</h3><p>${esc(A.stress)}</p></div>
  <div class="aix-verdict" role="group" aria-label="Verdict">${['Retain','Revise','Replace'].map(v=>`<button data-aix-verdict="${v}" aria-pressed="${f.aix_verdict===v}">${v}</button>`).join('')}</div>
  <div class="two-col">${aixField('aix_refit','Name the assumption the new information broke.',false)}${aixField('aix_owner','A role and a scope, never “the system”.',false)}</div>`
 :`<div class="actions"><button id="aix-commit" class="primary" ${aixReady()?'':'disabled'}>Commit and reveal the change</button><span class="small">Commit locks FIT–EVIDENCE so your first reasoning is preserved. Each field needs a sentence first.</span></div>`}
 <div class="actions"><button id="aix-copy">Copy submission</button><button id="aix-download">Download .md</button><button id="aix-reset">Reset challenge</button></div>
 <p class="status" data-save-status></p><p class="small">Saved on this device only. Practice only: nothing to submit and no grade. ${D.gradedNote?esc(D.gradedNote):`The graded work is Assignment ${esc(D.assignment)} (${esc(D.points)} points), a separate case on its own page.`}</p>`);
}
function aixRubric(A,open){const R=A.rubric;if(!R||!R.criteria){return `<details class="tool-details aix-rubric"${open?' open':''}><summary>How this is judged · rubric</summary><table><tr><th>Criterion</th><th>Strong</th><th>Developing</th></tr>${AIX_RUBRIC.map(r=>`<tr><td><b>${esc(r[0])}</b></td><td>${esc(r[1])}</td><td>${esc(r[2])}</td></tr>`).join('')}</table></details>`;}
 const lv=R.criteria[0].levels;return `<details class="tool-details aix-rubric"${open?' open':''}><summary>Check your own answer · ${esc(R.marks||'')} · read before you commit</summary><div class="table-scroll"><table><thead><tr><th scope="col">Criterion</th>${lv.map(l=>`<th scope="col">${esc(l[1])} · ${esc(l[0])}</th>`).join('')}</tr></thead><tbody>${R.criteria.map(c=>`<tr><th scope="row">${esc(c.name)}</th>${c.levels.map(l=>`<td>${esc(l[2])}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="rub-ex"><div class="strong"><b>Strong example</b><p>${esc(R.strong?.text||'')}</p><small>Why: ${esc(R.strong?.why||'')}</small></div><div class="weak"><b>Weak example</b><p>${esc(R.weak?.text||'')}</p><small>Why: ${esc(R.weak?.why||'')}</small></div></div><p class="small"><b>Other answers are accepted when</b> ${esc(R.other||'')}</p><p class="small">${esc(A.framing||'Changing your mind with specific counter-evidence is rewarded; a lucky first answer is not.')}</p></details>`;}
const AIX_RUBRIC=[
 ['Fit','Uses a named chapter concept to justify the choice for this AI case.','Names a concept but does not connect it to the case.'],
 ['Bound','States an observable condition that would end the claim.','Boundary is vague (“if it fails”).'],
 ['Evidence','Inspectable evidence that stays valid even if the AI component is wrong.','Relies on the AI’s own output or a vendor claim.'],
 ['Revision','Verdict uses the specific new information and names the broken assumption.','Repeats the first answer or changes it without reason.'],
 ['Ownership & AI use','Names a role and scope; declares any AI assistance and how it was checked.','No owner, or undeclared assistance.']];
document.addEventListener('click',e=>{const b=e.target.closest('[data-answer2]');if(!b)return;const ck2=commitKey(b.dataset.answer2,2);if(!commitReady(ck2)){document.querySelector(`[data-commit="${ck2}"]`)?.focus();return;}const box=b.closest('.q2')?.querySelector('.inline-answer');if(!box)return;holdBody();box.hidden=!box.hidden;const yw=box.querySelector('.you-wrote-slot');if(yw)yw.innerHTML=box.hidden?'':youWrote(ck2);b.setAttribute('aria-expanded',String(!box.hidden));b.textContent=box.hidden?'Reveal answer':'Hide answer';requestAnimationFrame(fitText);answerLayout(box);});
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
 if(b.id==='aix-commit'){if(!aixReady())return;state.fields.aix_commit=new Date().toLocaleString();save();aiChallenge();return;}
 if(b.dataset.aixVerdict){state.fields.aix_verdict=b.dataset.aixVerdict;save();aiChallenge();return;}
 if(b.id==='aix-copy'){const t=aixText();(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(()=>{b.textContent='Copied ✓';},()=>{b.textContent='Copy blocked · use Download';});return;}
 if(b.id==='aix-download'){download(aixText(),`Ch${D.chapter}-AI-challenge.md`,'text/markdown');return;}
 if(b.id==='aix-reset'){if(!confirm('Clear this AI challenge, including the committed answer?'))return;[...AIX,'aix_ai','aix_refit','aix_owner','aix_verdict','aix_commit'].forEach(k=>delete state.fields[k]);save();aiChallenge();return;}
});
document.addEventListener('input',e=>{const k=e.target.dataset.field;if(k&&k.startsWith('aix_')&&validField(k)){state.fields[k]=e.target.value;const c=document.getElementById('aix-count');if(c)c.textContent=`Words in FIT–EVIDENCE: ${aixWords()} · target ${(D.aiAssignment&&D.aiAssignment.words)||'180–260'}`;const btn=document.getElementById('aix-commit');if(btn)btn.disabled=!aixReady();}});
document.addEventListener('input',e=>{const k=e.target.dataset.field;if(k&&validField(k)){state.fields[k]=e.target.value;save();document.querySelectorAll(`[data-commit-for="${k}"]`).forEach(x=>x.disabled=!commitReady(k));const sa=document.getElementById('station-answer');if(sa){const st=D.stations.find(x=>x.no===Number(sa.dataset.no));if(st)sa.disabled=!stationReady(st);}}});
document.addEventListener('click',e=>{const b=e.target.closest('[data-their-save]');if(!b)return;if(!commitReady('commit_their')){document.querySelector('[data-commit="commit_their"]')?.focus();return;}const n=b.closest('.their-block')?.querySelector('.their-next');if(n)n.hidden=false;save();});
document.addEventListener('click',e=>{const b=e.target.closest('[data-bound-reveal]');if(!b)return;if(!commitReady('commit_bound')){document.querySelector('[data-commit="commit_bound"]')?.focus();return;}const box=b.closest('.bound-block')?.querySelector('.bound-answer');if(!box)return;box.hidden=false;const yw=box.querySelector('.you-wrote-slot');if(yw)yw.innerHTML=youWrote('commit_bound');});
document.addEventListener('click',e=>{const b=e.target.closest('[data-gate-pick]');if(!b||!gateOn())return;const f=state.fields,k=Number(b.dataset.gatePick);if(!(f.gate_line||'').trim())return;f.gate_pick=String(k);f.gate_tries=String(Number(f.gate_tries||0)+1);if(k===D.transfer.check.answer)f.gate_solved='1';save();transferCheck();updateNav();});
document.addEventListener('input',e=>{if(!e.target.matches('[data-gate-line]'))return;const on=!!e.target.value.trim();document.querySelectorAll('[data-gate-pick]').forEach(x=>x.disabled=!on);});
document.addEventListener('click',e=>{const b=e.target.closest('[data-skip]');if(!b)return;const k=b.dataset.skip;if(!validField(k+'_skip'))return;state.fields[k+'_skip']='1';save();document.querySelectorAll(`[data-commit-for="${k}"]`).forEach(x=>{x.disabled=false;x.click();});const sa=document.getElementById('station-answer');if(sa&&k==='commit_station'+sa.dataset.no){sa.disabled=false;sa.click();}b.remove();});
document.addEventListener('change',e=>{if(e.target.name==='quiz'){state.quiz[quizIndex]={answer:Number(e.target.value),checked:false};save();$('#quiz-feedback').hidden=true;}});
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;if(b.hasAttribute('data-national-return')){go(index);return;}if(b.dataset.vectorTab!==undefined){qa('[data-vector-pane]').forEach(x=>x.hidden=x.dataset.vectorPane!==b.dataset.vectorTab);qa('[data-vector-tab]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));return;}if(b.dataset.open){open(b.dataset.open);return;}if(b.dataset.jump){jump(b.dataset.jump);return;}if(b.dataset.go!==undefined){closeModal();go(Number(b.dataset.go));return;}if(b.dataset.full){full(b.dataset.full);return;}if(b.dataset.answer){answer(b.dataset.answer);return;}if(b.dataset.image){modal(b.dataset.caption||'Preserved source figure',`<div class="source-original ${b.dataset.vector?'source-vector-expanded':''}"><img class="zoom-figure source-natural" src="${esc(b.dataset.image)}" alt="${esc(b.dataset.caption)}"><p class="small"><b>Original source figure.</b> Vector figures retain the source labels and relationships at any zoom. Consult the source pack for the surrounding explanation and assumptions.</p></div>`);return;}if(b.dataset.quiz!==undefined){quizIndex=Number(b.dataset.quiz);quiz();return;}if(b.dataset.ai!==undefined){state.ai[b.dataset.ai]=b.dataset.value;save();qa('[data-ai="'+b.dataset.ai+'"]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.value===b.dataset.value)));$('#ai-result').textContent=aiVerdict(state.ai);return;}if(b.dataset.export){download(b.dataset.export==='json'?JSON.stringify(pack(),null,2):readable(),`Ch${D.chapter}-classroom-${b.dataset.export==='json'?'backup.json':'card.md'}`,b.dataset.export==='json'?'application/json':'text/markdown');return;}
switch(b.id){case 'prevBtn':advanceSection(-1);break;case 'nextBtn':advanceSection(1);break;case 'modal-close':closeModal();break;case 'stationBtn':stationMode=true;render();break;case 'station-back':pauseTimer();stationMode=false;render();break;case 'timer-start':startTimer();break;case 'timer-reset':pauseTimer();remaining=stationSeconds;timerLabel();break;case 'hintBtn':{const st=D.stations.find(x=>x.no===Number(b.dataset.no));$('#coach').innerHTML='<b>Authored hint.</b> '+esc(st.hint);break;}case 'station-answer':{const st=D.stations.find(x=>x.no===Number(b.dataset.no));if(!stationReady(st)){document.querySelector('.station-fields textarea')?.focus();break;}modal('Station discussion · illustrative reasoning',`${stationWrote(st)}<p>${esc(st.answer)}</p>${st.transfer&&D.transfer?`<h3>Transfer case · ${esc(D.transfer.title)}</h3><p>${esc(D.transfer.answer)}</p>`:''}<p class="small">Check the mechanism and assumptions. This is not an answer to the separately assessed case.</p>`);break;}case 'quiz-check':if(state.quiz[quizIndex]?.answer===undefined){$('#quiz-feedback').hidden=false;$('#quiz-feedback').textContent='Choose an answer before opening feedback.';}else{state.quiz[quizIndex].checked=true;save();quizFeedback();}break;case 'calculate':compute();break;case 'import':{const i=document.createElement('input');i.type='file';i.accept='.json,application/json';i.onchange=()=>i.files[0]&&restore(i.files[0]);i.click();break;}case 'clear':if(confirm('Clear this chapter’s classroom draft? Export a backup first. Assignment work will not change.')){state.fields={};state.quiz={};state.ai={};save();card();}break;case 'copy':try{await navigator.clipboard.writeText(readable());$('#live').textContent='Card copied.';}catch(e){download(readable(),`Ch${D.chapter}-card.md`,'text/markdown');}break;case 'viewBtn':document.body.classList.toggle('reading');b.setAttribute('aria-pressed',String(document.body.classList.contains('reading')));b.textContent=document.body.classList.contains('reading')?'Presentation':'Reading view';if(sectionNodes.length)showSection(sectionIndex);break;case 'themeBtn':state.theme=state.theme==='day'?'night':'day';try{localStorage.setItem('iscarb-theme',state.theme==='day'?'light':'dark')}catch(e){}document.body.classList.toggle('day',state.theme==='day');save();break;case 'fullBtn':try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch(e){$('#live').textContent='Fullscreen was not allowed; normal and reading views remain available.';}break;case 'notesBtn':notes();break;case 'helpBtn':help();break;}
});
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
 if(b.hasAttribute('data-pace-reset')){try{sessionStorage.setItem(paceKey,String(Date.now()-(index?PLAN.end[index-1]:0)*60000));}catch(e){}b.outerHTML=paceChip();return;}
 if(b.hasAttribute('data-evidence')){download(evidenceCSV(),`iscarb-ch${D.chapter}-class-evidence-${new Date().toISOString().slice(0,10)}.csv`,'text/csv');return;}
 if(b.dataset.xlab){const L=STORY?.lab;if(!L||!window.StudyLab)return;const r=labRuns[D.chapter]=labRuns[D.chapter]||{};if(b.dataset.xlab==='reset')delete labRuns[D.chapter];else{const cs=StudyLab.casesFrom(JSON.stringify(L.cases),Number(D.chapter));r[b.dataset.xlab]=StudyLab.run(Number(D.chapter),b.dataset.xlab,cs);}renderExtra(extraIndex??0);return;}
 if(b.dataset.think){think(b);return;}
 if(b.dataset.vote!==undefined){voteMode=Number(b.dataset.vote);voteStage=0;render();$('#chapter-main').scrollTo?.(0,0);return;}
 if(b.dataset.voteOpt!==undefined&&voteMode!==null){const q=voteItem(voteMode),r=voteStage<2?'r1':'r2',v=state.votes[voteMode]=state.votes[voteMode]||{};v[r]=v[r]||q.options.map(()=>0);v[r][Number(b.dataset.voteOpt)]=Math.min(999,v[r][Number(b.dataset.voteOpt)]+1);v.last=Number(b.dataset.voteOpt);save();render();return;}
 if(b.hasAttribute('data-vote-minus')&&voteMode!==null){const v=state.votes[voteMode],r=voteStage<2?'r1':'r2';if(v?.[r]&&v.last!==undefined&&v[r][v.last]>0){v[r][v.last]--;save();render();}return;}
 if(b.hasAttribute('data-vote-next')){if(voteStage<3){voteStage++;render();}else{voteMode=null;voteStage=0;render();}return;}
 if(b.hasAttribute('data-vote-back')){voteMode=null;voteStage=0;render();return;}
 if(b.dataset.gut){const g=STORY.gut,r=b.dataset.gut;state.gut[r]=state.gut[r]||g.options.map(()=>0);const k=Number(b.dataset.opt);state.gut[r][k]=Math.min(999,state.gut[r][k]+1);save();b.closest('.gut').outerHTML=gutBlock(r);return;}
 if(b.dataset.gutReset){delete state.gut[b.dataset.gutReset];save();b.closest('.gut').outerHTML=gutBlock(b.dataset.gutReset);return;}
});
$('#modal').addEventListener('click',e=>{if(e.target===$('#modal'))closeModal();});

// Navigation v1: native controls/editing win over presentation shortcuts.
const navControl='input,textarea,select,button,a[href],label,summary,audio,video,iframe,[role="button"],[role="textbox"],[role="combobox"],[role="slider"],[data-no-slide-nav]';
function navInteractive(target){return !(target instanceof Element)||target.isContentEditable||!!target.closest(navControl);}
function selectedText(){const s=window.getSelection();return !!(s&&!s.isCollapsed);}
function mousePresentation(){return !stationMode&&$('#modal').hidden&&!document.body.classList.contains('reading')&&matchMedia('(min-width:1001px)').matches;}
let navPointer=null,lastMouseSlide=-Infinity;
$('#chapter-main').addEventListener('pointerdown',e=>{
 navPointer=null;
 if(e.pointerType!=='mouse'||e.button!==0||e.ctrlKey||e.altKey||e.metaKey||!mousePresentation()||navInteractive(e.target))return;
 navPointer={x:e.clientX,y:e.clientY,index,selected:selectedText()};
});
$('#chapter-main').addEventListener('pointercancel',()=>{navPointer=null;});
$('#chapter-main').addEventListener('click',e=>{
 const p=navPointer;navPointer=null;
 if(!p||e.defaultPrevented||e.button!==0||e.detail!==1||e.ctrlKey||e.altKey||e.metaKey||!mousePresentation()||navInteractive(e.target))return;
 if(p.index!==index||p.selected||selectedText()||Math.hypot(e.clientX-p.x,e.clientY-p.y)>8||performance.now()-lastMouseSlide<260)return;
 lastMouseSlide=performance.now();e.preventDefault();advanceSection(e.shiftKey?-1:1);
});
$('#prevBtn').title='Previous slide · Backspace or Left arrow';
$('#nextBtn').title='Next slide · Enter or Right arrow';
$('#chapter-main').setAttribute('aria-keyshortcuts','Enter Backspace ArrowLeft ArrowRight Home End');

document.addEventListener('keydown',e=>{if(e.defaultPrevented||e.isComposing||e.ctrlKey||e.altKey||e.metaKey)return;if(!$('#modal').hidden){if(e.key==='Escape'){e.preventDefault();closeModal();}if(e.key==='Tab'){const a=qa('.dialog button,.dialog input,.dialog textarea,.dialog select,.dialog a[href]').filter(x=>!x.disabled&&x.getClientRects().length);if(a.length){if(e.shiftKey&&document.activeElement===a[0]){e.preventDefault();a.at(-1).focus();}else if(!e.shiftKey&&document.activeElement===a.at(-1)){e.preventDefault();a[0].focus();}}}return;}if(nationalIndex!==null&&e.key==='Escape'){e.preventDefault();go(index);return;}if(navInteractive(e.target))return;if(e.key==='Enter'||e.key==='Backspace'){if(e.shiftKey)return;e.preventDefault();if(!e.repeat)advanceSection(e.key==='Enter'?1:-1);return;}if(e.key==='ArrowRight'){e.preventDefault();advanceSection(1);}else if(e.key==='ArrowLeft'){e.preventDefault();advanceSection(-1);}else if(e.key==='Home'){e.preventDefault();go(0);}else if(e.key==='End'){e.preventDefault();go(D.slides.length-1);}else if(e.key.toLowerCase()==='o')indexModal();else if(e.key.toLowerCase()==='c')card();else if(e.key.toLowerCase()==='n'&&PRESENTER)notes();});
try{state.theme=localStorage.getItem('iscarb-theme')==='dark'?'night':'day'}catch(e){state.theme='day'}
document.body.classList.toggle('day',state.theme==='day');const hash=location.hash.slice(1);const initial=D.slides.findIndex(s=>s.id===hash);go(initial>=0?initial:0,false);if(hash&&initial<0)open(hash);
window.iscarb={data:D,go,open,jump,full,answer,closeModal,aiVerdict,pack,sanitize,compute,getState:()=>JSON.parse(JSON.stringify(state)),getIndex:()=>index,startStation:no=>{const st=D.stations.find(s=>s.no===no);if(st){go(D.slides.findIndex(s=>s.id===st.at));stationMode=true;render();}},restore};
})();
