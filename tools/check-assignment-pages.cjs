// Audit of every assessed assignment page (A1–A9) in a real browser: rubric criteria, every level visible with marks,
// points add up, rubric before the commit step, strong/weak examples and other-answer rule (A3–A9), the lecture boundary
// sentence on the page and in the export (A3–A9), the practical-hour line, the separate TESTS RUN row and the coverage
// step (A3–A9), no horizontal scroll at 1366 and 390 px, no page errors.
// Run: COURSE_BASE_URL=http://localhost:8766/ node tools/check-assignment-pages.cjs  → test-results/assignments/audit.json
const {chromium}=require('playwright');const fs=require('fs');const PUB=JSON.parse(fs.readFileSync(require('path').resolve(__dirname,'../curriculum/publication.json'),'utf8'));
const B=process.env.COURSE_BASE_URL||'http://localhost:8766/';
(async()=>{const b=await chromium.launch();let pass=0,fail=0;const rows=[];const ok=(c,m)=>{if(c)pass++;else{fail++;console.log('  FAIL',m)}return c};
for(const [n,a] of PUB.assignments.entries()){const ch=+a.chapter,no=n+1,graded=ch>=12;const html=fs.readFileSync(require('path').resolve(__dirname,'..',a.path),'utf8');const keys=[...new Set([...html.matchAll(/(?:"access": "|accessKey ?= ?')(fbr:access:[^"']+)/g)].map(m=>m[1]))];if(!keys.length)keys.push(`fbr:access:ch${ch}:path:v1`);const errs=[];const row={assignment:no,chapter:ch};
 for(const vp of [[1366,768],[390,844]]){
  const ctx=await b.newContext({viewport:{width:vp[0],height:vp[1]}});
  await ctx.addInitScript(([ch,keys])=>{for(const k of keys)sessionStorage.setItem(k,JSON.stringify({sid:'AUDIT'+ch,acknowledged:true}));localStorage.setItem(`iscarb:classroom:ch${ch}:v3`,JSON.stringify({schema:'iscarb-classroom-v3',chapter:ch,state:{fields:{commit_bound:'AUDIT boundary sentence for chapter '+ch+'.'}}}));},[ch,keys]);
  const p=await ctx.newPage();p.on('pageerror',e=>errs.push(e.message));await p.goto(B+a.path);await p.waitForTimeout(900);
  const r=await p.evaluate(()=>{const h=document.getElementById('rubric-heading');if(!h)return null;const sec=h.closest('section');const tb=sec.querySelector('table.rubric');
    const testsRow=tb.querySelector('tr[data-row="tests-run"]');const crit=[...tb.querySelectorAll('tbody tr')].filter(tr=>tr.querySelector('th[scope=row]')&&!tr.matches('[data-row="tests-run"],[data-row="their-change"]')).map(tr=>{const name=tr.querySelector('th').textContent.trim();const txt=tr.textContent;const pts=parseFloat((name.match(/·\s*([\d.]+)\s*point/)||[])[1]);const shown=[...tr.querySelectorAll('b')].filter(b=>!b.closest('details:not([open])')&&(b.checkVisibility?b.checkVisibility():b.getClientRects().length>0)&&/^(1|0\.75|0\.5|0):$/.test(b.textContent.trim())).map(b=>b.textContent.trim());return {name,pts,levels:new Set(shown).size}});
    const total=parseFloat((h.textContent.match(/([\d.]+)\s*points/)||[])[1]);
    const commit=[...document.querySelectorAll('h2,h3,button,summary,legend')].find(e=>/Review & commit/.test(e.textContent));
    const hidden=!!h.closest('details:not([open])');const rect=sec.getBoundingClientRect();
    const ex=document.getElementById('rubricExamples');const exNames=ex?[...ex.querySelectorAll('tr[data-criterion]')].map(t=>({name:t.dataset.criterion,strong:/Strong:/.test(t.textContent)&&/Why:/.test(t.textContent),weak:/Weak:/.test(t.textContent)})):[];
    const hour=document.querySelector('header.top .practical-hour');const hourBox=hour?hour.getBoundingClientRect():null;const cov=document.getElementById('coverageStep');return {testsRow:testsRow?{visible:testsRow.getBoundingClientRect().height>0,text:testsRow.textContent}:null,hour:hour?{text:hour.textContent,top:hourBox.top+scrollY,before:!!(hour.compareDocumentPosition(h)&Node.DOCUMENT_POSITION_FOLLOWING)}:null,coverage:cov?{visible:cov.getBoundingClientRect().height>0,field:!!cov.querySelector('textarea#coverageNote')}:null,total,crit,hidden,visible:rect.height>0,before:commit?!!(h.compareDocumentPosition(commit)&Node.DOCUMENT_POSITION_FOLLOWING):null,exNames,other:ex?/Other answers are accepted when/.test(ex.textContent):false,lectureBound:document.getElementById('lectureBound')?.textContent||null,hscroll:document.documentElement.scrollWidth>innerWidth+2}});
  if(vp[0]===1366){
   ok(r,`A${no}: rubric section present`);if(!r){await ctx.close();continue;}
   row.criteria=r.crit.length;row.points=r.total;
   ok(r.crit.length>=3,`A${no}: ${r.crit.length} criteria`);
   ok(r.crit.every(c=>c.levels===4),`A${no}: every criterion shows 4 levels (1 · 0.75 · 0.5 · 0) without opening anything: `+r.crit.filter(c=>c.levels!==4).map(c=>c.name+'='+c.levels).join(', '));
   const sum=r.crit.reduce((s,c)=>s+(c.pts||0),0);ok(Math.abs(sum-r.total)<1e-9,`A${no}: criterion points ${sum} = heading total ${r.total}`);
   ok(r.visible&&!r.hidden,`A${no}: rubric visible without opening anything`);ok(r.before===true,`A${no}: rubric before the commit step`);
   row.examples=r.exNames.length;
   if(graded){ok(r.exNames.length===r.crit.length&&r.exNames.every(x=>x.strong&&x.weak),`A${no}: strong + weak example for each of ${r.crit.length} criteria (found ${r.exNames.length})`);ok(r.other,`A${no}: other-answer conditions`);
    ok((r.lectureBound||'').includes('AUDIT boundary sentence for chapter '+ch),`A${no}: lecture boundary sentence shown`);
    const md=await p.evaluate(()=>typeof md==='function'?md(false):'');ok(md.includes('## Chapter boundary sentence (written in the lecture)\nAUDIT boundary sentence for chapter '+ch),`A${no}: boundary sentence in the export`);row.bound='in export';}
   if(graded){ok(r.hour&&/not submitted without it/.test(r.hour.text)&&r.hour.text.includes('تشغيل الاختبارات صف مستقل في السلّم')&&/outcome 11/.test(r.hour.text)&&r.hour.before,`A${no}: practical-hour line (English + Arabic, course outcomes) at the top, before the rubric`);
    ok(r.testsRow&&r.testsRow.visible&&/longer writing does not make up/.test(r.testsRow.text),`A${no}: separate TESTS RUN row visible in the rubric`);
    ok(r.coverage&&r.coverage.visible&&r.coverage.field,`A${no}: coverage step with its sentence field`);row.hour=!!r.hour;row.testsRun=!!r.testsRow;row.coverageStep=!!r.coverage;}
   else{row.bound='frozen (lecture only)';row.note=r.exNames.length?'examples':'no per-criterion examples (frozen page)';}
  }
  ok(!r||!r.hscroll,`A${no}: no horizontal scroll at ${vp[0]}px`);
  await ctx.close();}
 ok(errs.length===0,`A${no}: no page errors ${errs.slice(0,2)}`);rows.push(row);console.log(JSON.stringify(row));}
console.log('TOTAL PASS',pass,'FAIL',fail);fs.mkdirSync('test-results/assignments',{recursive:true});fs.writeFileSync('test-results/assignments/audit.json',JSON.stringify({checked:new Date().toISOString().slice(0,10),pass,fail,assignments:rows},null,1)+'\n');await b.close();process.exit(fail?1:0);})();
