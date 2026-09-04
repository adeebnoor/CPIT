/* ISCARB generic-IT intake surface.
   The compiled source remains authoritative; this file only removes the visible
   CPIT-455/Software-Engineering bias from the product surface and collects a
   small faculty context sheet before the existing compile request is sent. */
(function () {
  'use strict';

  function q(sel, root) { return (root || document).querySelector(sel); }
  function qa(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }
  function setHTML(sel, html) { var el=q(sel); if(el) el.innerHTML=html; }
  function setText(sel, text) { var el=q(sel); if(el) el.textContent=text; }

  function addStyles() {
    if (document.getElementById('iscarb-generic-it-style')) return;
    var style=document.createElement('style');
    style.id='iscarb-generic-it-style';
    style.textContent=`
      .itScopeGrid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:18px}
      .itScopeChip{border:1px solid rgba(220,181,107,.25);background:rgba(255,255,255,.025);border-radius:14px;padding:14px 12px;min-height:82px;display:flex;align-items:flex-end;font-size:13px;font-weight:700;line-height:1.35}
      .itScopeIntro{max-width:820px;color:var(--iscarb-muted,#b7bdc8)}
      .itIntake{margin:18px 0 16px;padding:18px;border:1px solid rgba(44,220,255,.24);border-radius:18px;background:linear-gradient(135deg,rgba(44,220,255,.045),rgba(255,37,140,.025))}
      .itIntakeHead{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:14px}.itIntakeHead strong{font-size:15px}.itIntakeHead span{font-size:12px;color:var(--iscarb-muted,#b7bdc8)}
      .itIntakeGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.itIntake .field{margin:0}.itIntake label{display:block;font-size:12px;font-weight:750;margin-bottom:6px}.itIntake input,.itIntake select{width:100%;box-sizing:border-box}
      .itAutoBadge{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border:1px solid rgba(220,181,107,.35);border-radius:999px;color:var(--iscarb-gold,#dcb56b);font-size:10px;font-weight:800;letter-spacing:.04em}
      .genericUploadNote{margin-top:8px;font-size:11.5px;color:var(--iscarb-muted,#b7bdc8)}
      .asset.packageAsset{grid-column:1/-1;border-color:rgba(44,220,255,.42)!important;background:linear-gradient(100deg,rgba(44,220,255,.07),rgba(255,37,140,.035))!important}.asset.packageAsset b{font-size:15px}.asset.packageAsset a{font-weight:850}
      .genericFlow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:20px}.genericFlow>div{padding:14px;border:1px solid rgba(255,255,255,.08);border-radius:14px}.genericFlow b{display:block;margin-bottom:5px;color:var(--iscarb-gold,#dcb56b)}
      @media(max-width:900px){.itScopeGrid{grid-template-columns:repeat(2,minmax(0,1fr))}.itIntakeGrid,.genericFlow{grid-template-columns:1fr}.itIntake{padding:14px}}
    `;
    document.head.appendChild(style);
  }

  function genericiseHero() {
    document.title='ISCARB IT Lecture Studio · Source-grounded lecture transformation';
    var meta=q('meta[name="description"]');
    if(meta) meta.content='Upload any IT or computing lecture and transform it into a source-grounded ISCARB teaching package with presenter, guides, student pack and blueprint.';

    setHTML('.hero h1 [data-lang="en"]','Upload any IT lecture. Get a source-grounded <em>teaching package.</em>');
    setHTML('.hero h1 [data-lang="ar"]','ارفع أي محاضرة في تقنية المعلومات واحصل على <em>حزمة تعليمية متكاملة.</em>');
    setText('.heroSub [data-lang="en"]','Programming, databases, networks, cybersecurity, AI, cloud, HCI, governance and beyond — the uploaded source defines the technical scope.');
    setText('.heroSub [data-lang="ar"]','برمجة، قواعد بيانات، شبكات، أمن سيبراني، ذكاء اصطناعي، سحابة، تفاعل إنسان وحاسب، حوكمة وغيرها — المصدر المرفوع هو الذي يحدد المحتوى التقني.');

    var primary=q('.hero .actions .button.primary');
    if(primary){primary.setAttribute('href','#upgrade');primary.lastChild.textContent=' Upload IT Lecture';}
    var secondary=q('.hero .actions .button:not(.primary)');
    if(secondary){secondary.setAttribute('href','#sources');secondary.lastChild.textContent=' Supported IT Areas';}

    var brand=q('.brand small'); if(brand) brand.textContent='IT Lecture Transformation Studio';
    var version=q('.version'); if(version) version.textContent='6.9.4 · IT-wide';
    var navSources=q('nav a[href="#sources"]'); if(navSources) navSources.textContent='IT Scope';
    var navUpgrade=q('nav a[href="#upgrade"]'); if(navUpgrade) navUpgrade.textContent='Upload Lecture';
    var navOutputs=q('nav a[href="#outputs"]'); if(navOutputs) navOutputs.textContent='Downloads';
  }

  function replaceLibrary() {
    var section=document.getElementById('sources');
    if(!section) return;
    section.innerHTML=`
      <div class="sectionHead">
        <div>
          <h2><span class="ornament">❦</span><span data-lang="en">One engine for IT & computing</span><span lang="ar" dir="rtl" data-lang="ar">محرك واحد لكل تخصصات تقنية المعلومات والحوسبة</span></h2>
          <p class="itScopeIntro"><span data-lang="en">ISCARB is not a CPIT-455 or Software Engineering template. Upload the lecture you actually teach; the source determines its concepts, mechanisms, examples, formulas and technical vocabulary.</span><span lang="ar" dir="rtl" data-lang="ar">ISCARB ليس قالبًا لمقرر هندسة البرمجيات أو CPIT-455. ارفع المحاضرة التي تدرّسها فعليًا، والمصدر نفسه يحدد المفاهيم والآليات والأمثلة والمعادلات والمصطلحات التقنية.</span></p>
        </div>
        <span class="itAutoBadge">AUTO SOURCE ADAPTATION</span>
      </div>
      <div class="itScopeGrid" aria-label="Supported IT domains">
        <div class="itScopeChip">Programming & software development</div>
        <div class="itScopeChip">Databases & data management</div>
        <div class="itScopeChip">Networks & infrastructure</div>
        <div class="itScopeChip">Cybersecurity</div>
        <div class="itScopeChip">AI & data science</div>
        <div class="itScopeChip">Cloud & distributed systems</div>
        <div class="itScopeChip">Human-computer interaction</div>
        <div class="itScopeChip">Systems & architecture</div>
        <div class="itScopeChip">IT governance & service management</div>
        <div class="itScopeChip">Any other IT / computing lecture</div>
      </div>
      <div class="genericFlow">
        <div><b>1 · Upload</b><span>PDF, PPTX, DOCX, TXT or MD — one primary lecture plus optional supporting sources.</span></div>
        <div><b>2 · ISCARB transforms</b><span>20 fixed learning units; technical content stays source-locked and topic-adaptive.</span></div>
        <div><b>3 · Download</b><span>Presenter, PDFs, instructor guide, student pack, blueprint and one complete ZIP package.</span></div>
      </div>`;
  }

  function injectIntake() {
    var form=document.getElementById('compileForm');
    if(!form || document.getElementById('itIntake')) return;
    var drop=q('.dropRow',form);
    if(!drop) return;

    var intake=document.createElement('section');
    intake.className='itIntake'; intake.id='itIntake';
    intake.innerHTML=`
      <div class="itIntakeHead">
        <div><strong><span data-lang="en">IT Lecture Intake Sheet</span><span lang="ar" dir="rtl" data-lang="ar">بطاقة تعريف المحاضرة</span></strong><br><span><span data-lang="en">Optional context only. The uploaded source still controls the technical content.</span><span lang="ar" dir="rtl" data-lang="ar">هذه معلومات مساعدة فقط؛ المصدر المرفوع يظل المرجع التقني الأساسي.</span></span></div>
        <span class="itAutoBadge">AUTO-DETECT BY DEFAULT</span>
      </div>
      <div class="itIntakeGrid">
        <div class="field"><label for="itCourse">Course name <span class="optional">Optional</span></label><input id="itCourse" type="text" maxlength="100" placeholder="e.g. Database Systems"></div>
        <div class="field"><label for="itCode">Course code <span class="optional">Optional</span></label><input id="itCode" type="text" maxlength="30" placeholder="e.g. CPIT-240"></div>
        <div class="field"><label for="itDomain">IT area</label><select id="itDomain"><option value="Auto-detect from uploaded source">Auto-detect from uploaded source</option><option>Programming & software development</option><option>Databases & data management</option><option>Networks & infrastructure</option><option>Cybersecurity</option><option>AI & data science</option><option>Cloud & distributed systems</option><option>Human-computer interaction</option><option>Systems & architecture</option><option>IT governance & service management</option><option>Other IT / computing</option></select></div>
        <div class="field"><label for="itLevel">Learner level</label><select id="itLevel"><option>Auto / infer from source</option><option>Foundation</option><option>Undergraduate — introductory</option><option>Undergraduate — intermediate</option><option>Undergraduate — advanced</option><option>Graduate</option><option>Professional / executive</option></select></div>
      </div>`;
    drop.insertAdjacentElement('afterend',intake);

    var fileSmall=q('#dropzone small'); if(fileSmall) fileSmall.textContent='PDF, PPTX, DOCX, TXT or MD · max 25MB';
    var heading=q('#upgrade h2 [data-lang="en"]'); if(heading) heading.textContent='Upload Any IT Lecture';
    var headingAr=q('#upgrade h2 [data-lang="ar"]'); if(headingAr) headingAr.textContent='ارفع أي محاضرة في تقنية المعلومات';
    var lede=q('#upgrade .lede [data-lang="en"]'); if(lede) lede.textContent='Upload the lecture source. ISCARB detects the topic and builds the teaching package.';
    var ledeAr=q('#upgrade .lede [data-lang="ar"]'); if(ledeAr) ledeAr.textContent='ارفع مصدر المحاضرة، وISCARB يتعرّف على الموضوع ويبني الحزمة التعليمية.';

    var focus=document.getElementById('focus');
    if(focus){
      focus.placeholder='For example: emphasise SQL joins, routing trade-offs, model evaluation, or a specific lab decision.';
      var label=q('label[for="focus"]'); if(label) label.innerHTML='Teaching emphasis <span class="optional">Optional</span>';
    }
    var note=document.createElement('p'); note.className='genericUploadNote'; note.textContent='No Software Engineering course selection is required. Leave IT area on Auto-detect for normal use.';
    intake.insertAdjacentElement('afterend',note);

    // Capture phase runs before the existing studio submit listener.  We use the
    // existing lecture_focus API field so no legacy client or server contract breaks.
    form.addEventListener('submit',function(){
      var focusEl=document.getElementById('focus'); if(!focusEl) return;
      var raw=focusEl.value.replace(/^\[ISCARB IT CONTEXT\][\s\S]*?\[\/ISCARB IT CONTEXT\]\s*/,'').trim();
      var course=(document.getElementById('itCourse')||{}).value||'';
      var code=(document.getElementById('itCode')||{}).value||'';
      var domain=(document.getElementById('itDomain')||{}).value||'Auto-detect from uploaded source';
      var level=(document.getElementById('itLevel')||{}).value||'Auto / infer from source';
      var context='[ISCARB IT CONTEXT]\nCourse: '+(course||'Not specified')+'\nCourse code: '+(code||'Not specified')+'\nIT area: '+domain+'\nLearner level: '+level+'\nInstruction: adapt to this context, but P1 remains the sole mandatory technical scope.\n[/ISCARB IT CONTEXT]';
      focusEl.value=context+(raw?'\nFaculty emphasis: '+raw:'');
    },true);
  }

  function packageCard() {
    var out=document.getElementById('outputAssets'); if(!out) return;
    var link=q('a[href*="/api/jobs/"][href*="/export/"]',out); if(!link) return;
    var match=(link.getAttribute('href')||'').match(/\/api\/jobs\/([^/]+)\//); if(!match) return;
    var existing=q('.packageAsset',out); if(existing && existing.dataset.job===match[1]) return;
    if(existing) existing.remove();
    var card=document.createElement('div'); card.className='asset packageAsset'; card.dataset.job=match[1];
    card.innerHTML='<b>Complete IT Lecture Package</b><a href="/api/jobs/'+encodeURIComponent(match[1])+'/export/package">Download all files · ZIP ↓</a><small>Original source + presenter PPTX/PDF + reading pack + instructor guide + student pack + blueprint + authoring prompt.</small>';
    out.prepend(card);
  }

  function watchOutputs() {
    var out=document.getElementById('outputAssets'); if(!out) return;
    packageCard();
    new MutationObserver(function(){packageCard();}).observe(out,{childList:true,subtree:true});
  }

  document.addEventListener('DOMContentLoaded',function(){
    addStyles();
    genericiseHero();
    replaceLibrary();
    injectIntake();
    watchOutputs();
  });
})();
