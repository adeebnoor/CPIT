/* ISCARB v7.1.0 — clean primary + supporting source intake.
   The existing API contract remains unchanged. This is a product-surface cleanup:
   exactly one primary source (website OR file), plus up to seven optional
   supporting sources. P1 controls scope; supporting sources clarify/evidence P1. */
(function () {
  'use strict';

  const q=(s,r)=> (r||document).querySelector(s);
  const qa=(s,r)=> Array.from((r||document).querySelectorAll(s));
  const supported=/\.(pdf|pptx|docx|txt|md)$/i;
  const maxSupporting=7;

  function styles(){
    if(document.getElementById('iscarb-v710-source-style')) return;
    const el=document.createElement('style');
    el.id='iscarb-v710-source-style';
    el.textContent=`
      .sourceModes{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0 8px}
      .sourceMode{border:1px solid rgba(255,255,255,.09);border-radius:16px;padding:16px;background:rgba(255,255,255,.025);min-height:112px}
      .sourceMode b{display:block;color:var(--iscarb-gold,#dcb56b);font-size:15px;margin-bottom:7px}.sourceMode span{font-size:12px;line-height:1.5;color:var(--iscarb-muted,#b7bdc8)}
      .sourceContract{display:grid;grid-template-columns:auto 1fr;gap:10px 14px;margin:18px 0;padding:15px 16px;border:1px solid rgba(44,220,255,.23);border-radius:16px;background:rgba(44,220,255,.035)}
      .sourceContract strong{color:var(--iscarb-cyan,#2cdcff);font-size:12px}.sourceContract p{margin:0;font-size:12px;color:var(--iscarb-muted,#b7bdc8);line-height:1.5}
      .sourcePrimaryLabel{margin:18px 0 8px;font-size:13px;font-weight:850;letter-spacing:.02em;color:var(--iscarb-text,#f5f5f8)}
      .sourcePrimaryLabel small{display:block;margin-top:4px;color:var(--iscarb-muted,#b7bdc8);font-weight:500;letter-spacing:0}
      details.advanced{border-color:rgba(220,181,107,.22)!important;background:rgba(220,181,107,.025)!important}
      details.advanced>summary{font-weight:800!important;color:var(--iscarb-gold,#dcb56b)!important}
      .supportHint{grid-column:1/-1;margin:-2px 0 2px;font-size:11.5px;color:var(--iscarb-muted,#b7bdc8);line-height:1.5}
      .sourceCount{display:inline-flex;align-items:center;gap:6px;margin-left:8px;padding:3px 8px;border-radius:999px;border:1px solid rgba(44,220,255,.28);font-size:10px;color:var(--iscarb-cyan,#2cdcff)}
      .sourceCount.warn{border-color:rgba(255,37,140,.5);color:var(--iscarb-magenta,#ff258c)}
      .sourceQuickFlow{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0 18px;font-size:11px;color:var(--iscarb-muted,#b7bdc8)}
      .sourceQuickFlow b{color:var(--iscarb-text,#f5f5f8)}.sourceQuickFlow i{color:var(--iscarb-magenta,#ff258c);font-style:normal}
      @media(max-width:900px){.sourceModes{grid-template-columns:repeat(2,minmax(0,1fr))}.sourceContract{grid-template-columns:1fr}.sourceCount{margin-left:0;margin-top:6px}}
    `;
    document.head.appendChild(el);
  }

  function cleanScopeSection(){
    const section=document.getElementById('sources'); if(!section) return;
    section.innerHTML=`
      <div class="sectionHead"><div>
        <h2><span class="ornament">❦</span><span data-lang="en">Bring the source. ISCARB builds the lecture.</span><span data-lang="ar" lang="ar" dir="rtl">أدخل المصدر، وISCARB يبني المحاضرة.</span></h2>
        <p class="itScopeIntro"><span data-lang="en">Use one primary source in any supported form. Add optional references only when they help explain, verify or contextualize the same lecture.</span><span data-lang="ar" lang="ar" dir="rtl">استخدم مصدرًا أساسيًا واحدًا بأي صيغة مدعومة، وأضف مراجع اختيارية فقط عندما تساعد في شرح أو توثيق نفس المحاضرة.</span></p>
      </div><span class="itAutoBadge">P1 SOURCE-LOCKED</span></div>
      <div class="sourceModes">
        <div class="sourceMode"><b>Website</b><span>Paste a public lecture page or direct public document URL.</span></div>
        <div class="sourceMode"><b>PowerPoint</b><span>Upload PPTX. Slide text is extracted and source visuals remain eligible.</span></div>
        <div class="sourceMode"><b>PDF</b><span>Upload a lecture deck, chapter or handout in PDF.</span></div>
        <div class="sourceMode"><b>Word</b><span>Upload DOCX. Paragraphs and tables are read as the lecture source.</span></div>
      </div>
      <div class="sourceQuickFlow"><b>PRIMARY P1</b><i>→</i><span>defines mandatory scope</span><i>→</i><b>OPTIONAL S1–S7</b><i>→</i><span>clarify/evidence</span><i>→</i><b>ISCARB 20 CORE UNITS</b><i>→</i><span>complete lecture package</span></div>
      <div class="sourceContract"><strong>P1 controls the lecture</strong><p>The primary source controls mandatory technical scope, terminology and conflict precedence.</p><strong>Supporting sources stay supporting</strong><p>Additional files or websites may clarify, exemplify, contextualize or verify P1. They do not silently replace P1 or create a new mandatory topic list.</p></div>`;
  }

  function setLabel(forId,text){const l=q('label[for="'+forId+'"]');if(l)l.textContent=text;}

  function countSupport(){
    const files=q('#supportFiles'); const urls=q('#supportUrls');
    const fileCount=files?files.files.length:0;
    const urlCount=urls?urls.value.split(/[\n;]/).map(x=>x.trim()).filter(Boolean).length:0;
    const total=fileCount+urlCount;
    const badge=q('#supportCount');
    if(badge){badge.textContent=total+' / '+maxSupporting;badge.classList.toggle('warn',total>maxSupporting);}
    return total;
  }

  function cleanForm(){
    const form=document.getElementById('compileForm'); if(!form) return;
    const drop=q('.dropRow',form); if(drop && !q('.sourcePrimaryLabel',form)){
      const h=document.createElement('div'); h.className='sourcePrimaryLabel';
      h.innerHTML='<span data-lang="en">1 · Primary lecture source</span><span data-lang="ar" lang="ar" dir="rtl">١ · المصدر الأساسي للمحاضرة</span><small>Choose exactly one: upload a file OR paste a public website/direct document URL.</small>';
      drop.parentNode.insertBefore(h,drop);
    }

    const primary=q('#primaryFile'); if(primary) primary.setAttribute('accept','.pdf,.pptx,.docx,.txt,.md');
    setLabel('primaryUrl','Primary website / document URL');
    const url=q('#primaryUrl'); if(url) url.placeholder='https://example.edu/lecture-or-document';
    const small=q('#dropzone small'); if(small) small.textContent='PDF · PPTX · DOCX · TXT · MD · max 25 MB';
    const hint=q('#sourceHint'); if(hint) hint.textContent='Public lecture pages, direct PDFs and readable public documents are supported. P1 remains authoritative.';

    const details=q('details.advanced',form);
    if(details){
      details.open=true;
      const summary=q('summary',details);
      if(summary) summary.innerHTML='<span data-lang="en">2 · Additional sources <small style="font-weight:500">optional</small></span><span data-lang="ar" lang="ar" dir="rtl">٢ · مصادر إضافية <small style="font-weight:500">اختياري</small></span> <span id="supportCount" class="sourceCount">0 / 7</span>';
      setLabel('supportFiles','Supporting files — PDF / PPTX / DOCX / TXT / MD');
      setLabel('supportUrls','Supporting websites — one URL per line');
      const support=q('#supportFiles'); if(support){support.multiple=true;support.setAttribute('accept','.pdf,.pptx,.docx,.txt,.md');support.addEventListener('change',countSupport);}
      const supportUrls=q('#supportUrls'); if(supportUrls){supportUrls.placeholder='https://reference-one\nhttps://reference-two';supportUrls.addEventListener('input',countSupport);}
      const grid=q('.grid2',details);
      if(grid && !q('.supportHint',grid)){
        const note=document.createElement('p');note.className='supportHint';note.textContent='Maximum 7 supporting sources total. They support the same lecture; they never override the primary source.';grid.appendChild(note);
      }
      const repair=q('#repair'); if(repair && repair.parentElement) repair.parentElement.hidden=true;
    }

    const focus=q('#focus');if(focus)focus.placeholder='Optional teaching emphasis — e.g. emphasize risk assessment or a specific design decision.';
    const btn=q('#compileBtn');if(btn && !btn.disabled)btn.innerHTML='Build ISCARB Lecture <span>↗</span>';

    // Friendly client-side validation before the older submit handler posts.
    form.addEventListener('submit',function(ev){
      const support=q('#supportFiles');
      const bad=support?Array.from(support.files).find(f=>!supported.test(f.name)):null;
      const count=countSupport();
      if(bad || count>maxSupporting){
        ev.preventDefault(); ev.stopImmediatePropagation();
        const err=q('#formError');
        if(err) err.textContent=bad?('Unsupported supporting file: '+bad.name+'. Use PDF, PPTX, DOCX, TXT or MD.'):('Use at most '+maxSupporting+' supporting sources total.');
      }
    },true);

    countSupport();
  }

  function keepButtonClean(){
    const btn=q('#compileBtn');if(!btn)return;
    const sync=()=>{if(!btn.disabled && !/Build ISCARB Lecture/i.test(btn.textContent||''))btn.innerHTML='Build ISCARB Lecture <span>↗</span>';};
    new MutationObserver(sync).observe(btn,{attributes:true,childList:true,subtree:true});
    sync();
  }

  document.addEventListener('DOMContentLoaded',function(){
    styles();
    cleanScopeSection();
    cleanForm();
    keepButtonClean();
  });
})();
