// Story v2: simpler concept path, one persistent case thread, and an explicit close.
function storyBranch(s){
 return D.roadmap?.branches?.find(x=>(x.units||[]).includes(s.id));
}
function storyThread(s){
 if(['TITLE','MAP','START','END'].includes(s.id))return '';
 const b=storyBranch(s),lens=b?.caseLens||D.case.question;
 return `<div class="case-thread"><span>CASE THREAD</span><b>${esc(b?.label||D.case.headline)}</b><em>${esc(lens)}</em></div>`;
}
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
      <span class="step-case"><i>In our story</i>${esc(b.caseLens||'Use this concept to narrow the decision.')}</span>
   </button>`).join('')}
 </div>
 <p class="mind-link"><b>WHY THIS ORDER</b> ${esc(r.connection)}</p>
 <div class="student-roadmap" aria-label="What happens in class and after class">
   <section class="road-stage"><h3><span>01</span> In class</h3><p><b>Instructor:</b> Explain the mechanism and guide three short stations.</p><p><b>You:</b> ${esc(r.inClass)}</p><p class="road-result">One evolving practice card—not several reports.</p></section>
   <section class="road-stage"><h3><span>02</span> Required review</h3><p><b>Instructor:</b> Name the exact source selections.</p><p><b>You:</b> Review source slides ${D.readings.map(x=>esc(x.range)).join(' + ')} and complete the five-objective practice.</p><p class="road-result">Fix misunderstandings before the assignment.</p></section>
   <section class="road-stage"><h3><span>03</span> Assignment ${D.assignment}</h3><p><b>Instructor:</b> Review using the published rubric.</p><p><b>You:</b> ${esc(r.deliverable)}</p><p class="road-result">New case → commit → STRESS → REFIT → Blackboard.</p></section>
 </div>
 <div class="map-bottom"><p><b>REQUIRED:</b> class + named review + assignment. Other tools support the same work unless explicitly assigned.</p><div class="actions">${jumpButton('START','Start the story →')}</div></div>`);
}
function renderStory(){
 const r=D.roadmap;
 $('#chapter-main').classList.add('story-page');
 $('#chapter-main').insertAdjacentHTML('beforeend',`
 <div class="story-head"><span>OUR STORY · FICTIONAL TEACHING CASE</span><h2>${esc(D.case.headline)}</h2><p>Keep this same case in mind as every concept is introduced.</p></div>
 <div class="story-grid">
   <section><h3>1 · Situation</h3><p>${esc(D.case.text)}</p></section>
   <section><h3>2 · Your decision</h3><p>${esc(D.case.question)}</p></section>
   <section><h3>3 · Evidence rule</h3><p>Use supplied facts and transparent calculations. Keep missing tests and unknowns visible; do not invent measurements.</p></section>
 </div>
 <div class="story-route" aria-label="How the story will be revisited">
   ${r.branches.map((b,i)=>`<span><b>${i+1}</b>${esc(b.label)}</span>`).join('')}
 </div>
 <div class="story-note"><b>One story, five lenses.</b> Each main slide will show a CASE THREAD that tells you which part of this decision the concept helps you answer. The changed constraint is revealed later—do not guess it now.</div>
 <div class="actions story-action">${jumpButton(r.branches[0].target,'Start learning →')}</div>`);
}
function renderClosing(){
 const r=D.roadmap;
 $('#chapter-main').classList.add('end-page');
 $('#chapter-main').insertAdjacentHTML('beforeend',`
 <div class="end-hero">
  <div class="end-copy">
   <p class="ey">CHAPTER ${D.chapter} · COMPLETE</p>
   <h2>${esc(D.title)}</h2>
   <p class="end-success">You should now be able to: <b>${esc(r.success)}</b></p>
   <div class="end-required">
    <section><span>1</span><div><b>Required review</b><p>${D.readings.map(x=>esc(x.title)+' · '+esc(x.range)).join(' | ')}</p></div></section>
    <section><span>2</span><div><b>Check yourself</b><p>Complete the five-objective practice and correct any misunderstanding before the assignment.</p></div></section>
    <section><span>3</span><div><b>Assignment ${D.assignment}</b><p>${esc(r.deliverable)} Submit through Blackboard according to the announced deadline.</p></div></section>
   </div>
   <p class="end-boundary">The lecture has ended. The toolkit is support—not extra required content unless your instructor assigns it.</p>
   <div class="actions">${button('Open required review','READING','primary')}<a href="../../fbr-submission.html?chapter=${D.chapter}">Open Assignment ${D.assignment}</a></div>
  </div>
  <img src="${esc(D.brand)}" alt="Approved iSCARB visual identity">
 </div>`);
}
