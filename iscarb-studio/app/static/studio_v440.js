'use strict';
const $ = id => document.getElementById(id);
const SOURCE_NAMES = ['Dependable Systems','Reliability Engineering','Safety Engineering','Security Engineering','Resilience Engineering','Software Reuse','Component-Based Engineering','Distributed Software Engineering'];
const JOBS = ['Professional crisis','Domain spine','Five measurable CLOs','Six H-Stack capabilities','Predict · Constrain · Derive · Name','First-principles mechanism','Implementation structure','Alternatives & trade-offs','Measurement & falsification','Known · Unknown · Monitor','Contextual application','Accountability','Contemporary practice','Practitioner consequences','Critical AI literacy','Portfolio challenge','Constraint mutation','Evidence policy','Four-level rubric','Bounded assurance'];
const PHASES = ['UNDERSTAND','PRACTISE','MASTER','DISTINGUISH'];
let jobId = null, timer = null, failures = 0, busy = false, renderedStage = '';
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function setBusy(value) { busy = value; $('compileBtn').disabled = value; $('compileBtn').innerHTML = value ? 'Building your lecture…' : 'Build & audit my lecture <span>↗</span>'; }
function sourceSelection() {
  const file = $('primaryFile').files[0];
  $('fileName').textContent = file ? file.name : 'Drop your lecture here';
  document.querySelectorAll('.source').forEach(card => card.classList.toggle('selected', !file && card.dataset.url === $('primaryUrl').value.trim()));
}
SOURCE_NAMES.forEach((title, i) => {
  const url = `https://adeebnoor.github.io/CPIT/lectures/cimt/CPIT455-class${i+2}-NooR.pdf`;
  const card = document.createElement('article'); card.className = 'source'; card.dataset.url = url;
  card.innerHTML = `<div class="sourceTop"><span>CIMT / CLASS ${String(i+2).padStart(2,'0')}</span><span>PDF ↗</span></div><h3>${escapeHTML(title)}</h3><p>Original CPIT-455 lecture · Direct PDF</p><div class="sourceBottom"><button type="button" aria-label="Use ${escapeHTML(title)} as primary source">Use this source →</button><a href="${url}" target="_blank" rel="noopener noreferrer" aria-label="Open ${escapeHTML(title)} PDF">View</a></div>`;
  card.querySelector('button').addEventListener('click', () => { if (busy) return; $('primaryUrl').value=url; $('primaryFile').value=''; sourceSelection(); $('sourceHint').textContent=`Selected: ${title}. The original PDF and its figures will be used as P1.`; $('upgrade').scrollIntoView({behavior:'smooth'}); });
  $('sourceGrid').appendChild(card);
});
$('primaryFile').addEventListener('change', () => { if ($('primaryFile').files.length) $('primaryUrl').value=''; sourceSelection(); });
$('primaryUrl').addEventListener('input', () => { if ($('primaryUrl').value.trim()) $('primaryFile').value=''; sourceSelection(); });
['dragenter','dragover'].forEach(name => $('dropzone').addEventListener(name,e=>{e.preventDefault();$('dropzone').classList.add('dragging');}));
['dragleave','drop'].forEach(name => $('dropzone').addEventListener(name,e=>{e.preventDefault();$('dropzone').classList.remove('dragging');}));
$('dropzone').addEventListener('drop',e=>{if(busy)return;const file=e.dataTransfer.files[0];if(!file)return;const transfer=new DataTransfer();transfer.items.add(file);$('primaryFile').files=transfer.files;$('primaryUrl').value='';sourceSelection();});

async function request(url, options={}) {
  const controller=new AbortController(); const timeout=setTimeout(()=>controller.abort(),45000);
  try {
    const response=await fetch(url,{...options,signal:controller.signal,cache:'no-store'});
    const content=await response.text(); let data; try {data=JSON.parse(content);} catch {data={detail:content.slice(0,500)};}
    if(!response.ok){const message=typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data);const error=new Error(message||`Request failed (${response.status})`);error.status=response.status;throw error;}
    return data;
  } finally {clearTimeout(timeout);}
}
function remember(id) {try {if(id)localStorage.setItem('iscarb.job.v44',id);else localStorage.removeItem('iscarb.job.v44');}catch{/* Browser storage may be disabled. */}}
$('compileForm').addEventListener('submit',async e=>{
  e.preventDefault(); if(busy)return;
  const file=$('primaryFile').files[0],url=$('primaryUrl').value.trim();
  $('formError').textContent='';
  if((!file&&!url)||(file&&url)){$('formError').textContent='Choose exactly one primary source: a file or a URL.';return;}
  if(file&&!/\.(pdf|pptx|docx|txt|md)$/i.test(file.name)){$('formError').textContent='Use a PDF, PPTX, DOCX, TXT, or MD file.';return;}
  if(file&&file.size>25*1024*1024){$('formError').textContent='The primary file is too large. Use a file smaller than 25 MB.';return;}
  clearTimeout(timer);jobId=null;remember(null);failures=0;renderedStage='';setBusy(true);
  $('status').hidden=false;$('result').hidden=true;$('retryPoll').hidden=true;$('error').textContent='';
  updateProgress({status:'queued',progress:0,message:'Uploading and locking your primary source…'});
  const fd=new FormData();if(file)fd.append('primary_lecture',file);fd.append('primary_url',url);
  [...$('supportFiles').files].forEach(f=>fd.append('supporting_files',f));
  fd.append('supporting_urls',$('supportUrls').value);fd.append('lecture_focus',$('focus').value);fd.append('model',$('model').value);fd.append('repair_rounds',$('repair').value);
  try {const result=await request('/api/compile',{method:'POST',body:fd});if(!result.job_id)throw new Error('The server did not return a job identifier.');jobId=result.job_id;remember(jobId);await poll();}
  catch(error){$('error').textContent=error.name==='AbortError'?'The upload timed out. No automatic retry was sent; check your connection before trying again.':error.message;setBusy(false);}
});
function updateProgress(job){const progress=Math.min(100,Math.max(0,Number(job.progress)||0));$('state').textContent=(job.status||'queued').toUpperCase();$('message').textContent=job.message||'';$('pct').textContent=`${progress}%`;$('bar').style.width=`${progress}%`;$('progressTrack').setAttribute('aria-valuenow',String(progress));$('error').textContent=job.error||'';}
async function poll(){
  if(!jobId)return;clearTimeout(timer);
  try {const job=await request('/api/jobs/'+encodeURIComponent(jobId));failures=0;updateProgress(job);
    if(job.blueprint && renderedStage!==job.status+':'+job.progress){render(job);renderedStage=job.status+':'+job.progress;}
    if(['ready','blocked','error'].includes(job.status)){setBusy(false);$('retryPoll').hidden=true;render(job);return;}
  } catch(error){failures++;$('error').textContent=error.name==='AbortError'?'The status request timed out. Your server-side job may still be running.':error.message;
    if(error.status===404||failures>=4){setBusy(false);$('retryPoll').hidden=error.status===404;if(error.status===404)remember(null);return;}
  }
  timer=setTimeout(poll,Math.min(15000,3000*(failures+1)));
}
$('retryPoll').addEventListener('click',()=>{failures=0;$('retryPoll').hidden=true;setBusy(true);poll();});
function unitCheck(number,checks){const prefix=`v15_unit${String(number).padStart(2,'0')}_`;const matches=Object.entries(checks).filter(([key])=>key.startsWith(prefix));return !matches.length?'unknown':matches.every(([,value])=>value===true)?'pass':'fail';}
function render(job){
  const bp=job.blueprint;if(!bp)return;const audit=job.audit||{},checks=job.deterministic_checks||{},entries=Object.entries(checks),failed=entries.filter(([,v])=>v!==true);
  $('result').hidden=false;$('lectureTitle').textContent=bp.lecture_title||'Your lecture';
  const released=job.status==='ready'&&entries.length>0&&failed.length===0&&audit.overall_pass===true;
  $('releaseBadge').textContent=released?'VERIFIED RELEASE':'REVIEW DRAFT';$('releaseBadge').className='badge '+(released?'ready':'blocked');
  $('resultSummary').textContent=released?'Both audits passed. Review the materials for your teaching context and download the files you want to keep.':'This is not a verified release. Inspect the failed checks and the source coverage below before classroom use. Downloads remain available for faculty review.';
  const units=bp.units||[],ledger=bp.coverage_ledger||[],major=(job.source_profile?.coverage_items||[]).filter(x=>x.importance==='major');
  const covered=major.filter(item=>ledger.some(row=>row.coverage_id===item.id&&row.first_taught_unit<=15));
  const grammar=units.filter(u=>unitCheck(u.number,checks)==='pass').length;
  const stats=[[`${units.length}/20`,'Units in the Blueprint'],[`${grammar}/20`,'Unit grammar checks passed'],[major.length?`${covered.length}/${major.length}`:'Not checked','Major checkpoints mapped by U15'],[String(units.reduce((sum,u)=>sum+(u.planned_minutes||0),0)),'Planned teaching minutes']];
  $('metrics').innerHTML=stats.map(([value,label])=>`<div class="metric"><strong>${escapeHTML(value)}</strong><span>${escapeHTML(label)}</span></div>`).join('');
  const id=encodeURIComponent(jobId);
  $('outputAssets').innerHTML=`<div class="asset"><b>Visual Presenter</b><a target="_blank" rel="noopener noreferrer" href="/api/jobs/${id}/presenter">Preview ↗</a><a href="/api/jobs/${id}/export/pptx">PPTX</a><a href="/api/jobs/${id}/export/presenter-pdf">PDF</a></div><div class="asset"><b>Original source · all pages</b><a href="/api/jobs/${id}/export/source-pdf">Original PDF ↓</a><small>Keep the source alongside your teaching deck. Figures and examples are never removed from this file.</small></div><div class="asset"><b>Reading Pack</b><a href="/api/jobs/${id}/export/pdf">PDF ↓</a></div><div class="asset"><b>Instructor Guide</b><a href="/api/jobs/${id}/export/docx">DOCX ↓</a></div><div class="asset"><b>Student Pack</b><a href="/api/jobs/${id}/export/student">DOCX ↓</a></div><div class="asset"><b>Blueprint</b><a href="/api/jobs/${id}/export/json">JSON ↓</a></div>`;
  if(!['ready','blocked','error'].includes(job.status)){
    $('resultSummary').textContent='Generation/audit is still running. Preview and download the saved REVIEW DRAFT now. Faculty and student packs become available when processing finishes.';
    [...$('outputAssets').children].slice(2).forEach(el=>el.hidden=true);
  }
  if(!/\.pdf(?:[?#].*)?$/i.test(job.filename||'')) $('outputAssets').children[1].hidden=true;
  $('unitGrid').replaceChildren();
  for(let n=1;n<=20;n++){const unit=units.find(u=>u.number===n),state=unit?unitCheck(n,checks):'fail';const el=document.createElement('details');el.className='unit '+state;
    el.innerHTML=`<summary><span>${String(n).padStart(2,'0')} / ${PHASES[Math.floor((n-1)/5)]} · ${state==='unknown'?'NOT CHECKED':state.toUpperCase()}</span><strong>${escapeHTML(JOBS[n-1])}</strong></summary><div class="unitBody"><p><b>${escapeHTML(unit?.title||'Missing unit')}</b></p><p>${escapeHTML(unit?.engineering_question||'')}</p><p><b>Source:</b> ${escapeHTML(unit?.source_anchor||'Not recorded')}</p><p><b>Learner task:</b> ${escapeHTML(unit?.student_action||'Not recorded')}</p></div>`;$('unitGrid').appendChild(el);}
  const summaries=[['Deterministic checks',entries.length>0&&failed.length===0],['Semantic audit',audit.overall_pass===true],['Source fidelity',audit.source_fidelity_pass===true],['20-unit grammar',checks.v15_complete_20_unit_grammar===true],['Readable text fit',checks.v15_presenter_fits_readable_canvas===true]];
  $('gates').innerHTML=summaries.map(([name,ok])=>`<div class="gate">${name}: <strong class="${ok?'pass':'fail'}">${ok?'PASS':'NOT PASSED'}</strong></div>`).join('');
  $('failureCount').textContent=`${failed.length} deterministic checks unresolved`;$('auditDetails').open=!released;
  $('failureList').replaceChildren();
  failed.forEach(([name])=>{const li=document.createElement('li');li.textContent=name.replace(/_/g,' ');$('failureList').appendChild(li);});
  (audit.issues||[]).forEach(issue=>{const li=document.createElement('li');li.textContent=`${issue.severity||'Review'} · ${(issue.unit_numbers||[]).map(n=>'U'+n).join(', ')} · ${issue.problem||issue.requirement||''} ${issue.repair_instruction||''}`;$('failureList').appendChild(li);});
  const rows=major.length?major:ledger.map(r=>({...r,id:r.coverage_id}));$('coverageBody').replaceChildren();
  rows.forEach(item=>{const row=ledger.find(r=>r.coverage_id===item.id),tr=document.createElement('tr');[item.label,item.source_anchor,row?`Unit ${row.first_taught_unit}`:'—',!row?'MISSING':row.first_taught_unit>15?'TAUGHT TOO LATE':'Mapped · verify depth'].forEach(value=>{const td=document.createElement('td');td.textContent=value||'—';tr.appendChild(td);});$('coverageBody').appendChild(tr);});
}
try {const saved=localStorage.getItem('iscarb.job.v44');if(saved&&/^[a-f0-9-]{16,64}$/i.test(saved)){jobId=saved;$('status').hidden=false;setBusy(true);poll();}}catch{/* Resume is optional. */}
