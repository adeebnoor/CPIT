const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const {root,read,load,put}=require('./classroom-harness.cjs');
const pub=JSON.parse(read('curriculum/publication.json'));
let sourceTotal=0;
for(const c of pub.lectures){const x=load(c);try{
 assert.deepEqual(x.errors,[]);assert(x.api,'Runtime initializes');const D=x.api.data;
 assert.equal(D.chapter,c.chapter);assert.equal(D.slides.length,20);assert.equal(D.objectives.length,5);assert.equal(D.quiz.length,5);assert.equal(D.stations.length,3);
 for(let i=0;i<20;i++){x.api.go(i);assert.equal(x.api.getIndex(),i);assert(x.d.querySelector('h1').textContent.trim());assert.equal(x.d.querySelectorAll('.counter').length,1);const ids=[...x.d.querySelectorAll('[id]')].map(e=>e.id);assert.equal(ids.length,new Set(ids).size);}
 x.d.getElementById('nextBtn').click();assert.equal(x.api.getIndex(),19);x.api.go(0);assert(x.d.getElementById('prevBtn').disabled);
 for(const st of D.stations){x.api.startStation(st.no);assert(x.d.getElementById('timer-start'));assert(x.d.querySelector('.station-steps').textContent.includes('PAIR'));x.d.getElementById('hintBtn').click();assert(x.d.getElementById('coach').textContent.includes(st.hint));for(const f of st.fields)put(x,f,'A source-backed draft for '+f);}
 x.api.open('CARD');assert.equal(x.d.querySelector('[data-field="claim"]').value,'A source-backed draft for claim');assert.match(x.d.getElementById('progress').textContent,/not mastery/);
 const study=read(c.study_path);const ids=[...study.matchAll(/id="source-slide-(\d+)"/g)].map(m=>+m[1]);assert.equal(new Set(ids).size,c.source_slide_count);for(let i=1;i<=c.source_slide_count;i++)assert(ids.includes(i));sourceTotal+=c.source_slide_count;
 for(const r of D.readings){const ns=r.range.match(/\d+/g).map(Number);assert(ns.every(n=>n>=1&&n<=c.source_slide_count));}
 for(const g of D.groups)for(const k of g.units)assert(D.slides.some(s=>s.id===k));
 x.api.open('RULES');assert.equal(x.d.querySelectorAll('[data-rule]').length,20);assert.equal(D.rules[18].title,'Four-level capability rubric');assert.equal(D.rules[15].title,'Portfolio task launch');
 for(const r of D.rules)for(const k of r.targets){x.api.open(k);assert(!x.d.getElementById('modal-body').textContent.includes('This earlier unit'));x.api.closeModal();}
 assert.equal(x.w.localStorage.getItem('assignment-draft-sentinel'),'unchanged');assert.deepEqual(x.errors,[]);console.log('PASS CH'+c.chapter+' · 20 slides, five objectives, three visible stations, exact source ledger and canonical rule links');
 }finally{x.dom.window.close();}}
assert.equal(sourceTotal,579);console.log('PASS 579 original source slides remain accessible in separate on-demand ledgers');
