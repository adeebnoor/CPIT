/* ISCARB v7.0.1 interface localization.
   One interface language at a time. Technical lecture content remains in the
   language of the uploaded source; this module localizes product chrome only. */
(function () {
  'use strict';

  const AR = new Map(Object.entries({
    'Skip to lecture builder':'انتقل إلى أداة بناء المحاضرة',
    'ISCARB Faculty Studio':'استوديو ISCARB للمحاضرات',
    'IT Lecture Transformation Studio':'استوديو تحويل محاضرات تقنية المعلومات',
    'Home':'الرئيسية','IT Scope':'نطاق تقنية المعلومات','Upload Lecture':'رفع محاضرة','Downloads':'التنزيلات','Guides':'الأدلة','About Us':'عن ISCARB','Sign In':'تسجيل الدخول',
    'Upload IT Lecture':'رفع محاضرة تقنية معلومات','Supported IT Areas':'مجالات تقنية المعلومات المدعومة',
    'One engine for IT & computing':'محرك واحد لتقنية المعلومات والحوسبة',
    'ISCARB is not a CPIT-455 or Software Engineering template. Upload the lecture you actually teach; the source determines its concepts, mechanisms, examples, formulas and technical vocabulary.':'ISCARB ليس قالبًا لمقرر CPIT-455 ولا لهندسة البرمجيات. ارفع المحاضرة التي تدرّسها فعليًا؛ والمصدر نفسه يحدد المفاهيم والآليات والأمثلة والمعادلات والمصطلحات التقنية.',
    'AUTO SOURCE ADAPTATION':'تكيّف تلقائي مع المصدر',
    'Programming & software development':'البرمجة وتطوير البرمجيات','Databases & data management':'قواعد البيانات وإدارة البيانات','Networks & infrastructure':'الشبكات والبنية التحتية','Cybersecurity':'الأمن السيبراني','AI & data science':'الذكاء الاصطناعي وعلوم البيانات','Cloud & distributed systems':'الحوسبة السحابية والأنظمة الموزعة','Human-computer interaction':'التفاعل بين الإنسان والحاسب','Systems & architecture':'الأنظمة والمعماريات','IT governance & service management':'حوكمة تقنية المعلومات وإدارة الخدمات','Any other IT / computing lecture':'أي محاضرة أخرى في تقنية المعلومات أو الحوسبة','Other IT / computing':'تقنية معلومات أو حوسبة أخرى',
    '1 · Upload':'١ · ارفع','2 · ISCARB transforms':'٢ · يحوّل ISCARB','3 · Download':'٣ · نزّل',
    'PDF, PPTX, DOCX, TXT or MD — one primary lecture plus optional supporting sources.':'PDF أو PPTX أو DOCX أو TXT أو MD — محاضرة أساسية واحدة مع مصادر مساندة اختيارية.',
    '20 fixed learning units; technical content stays source-locked and topic-adaptive.':'٢٠ وحدة تعلم ثابتة؛ المحتوى التقني مقيد بالمصدر ويتكيف مع موضوع المحاضرة.',
    'Presenter, PDFs, instructor guide, student pack, blueprint and one complete ZIP package.':'عرض تقديمي وملفات PDF ودليل المدرس وحزمة الطالب والمخطط وملف ZIP كامل.',
    'Upload Any IT Lecture':'ارفع أي محاضرة في تقنية المعلومات',
    'Upload the lecture source. ISCARB detects the topic and builds the teaching package.':'ارفع مصدر المحاضرة. يتعرّف ISCARB على الموضوع ويبني الحزمة التعليمية.',
    'IT Lecture Intake Sheet':'بطاقة تعريف المحاضرة','Optional context only. The uploaded source still controls the technical content.':'سياق اختياري فقط. يظل المصدر المرفوع هو المرجع التقني للمحتوى.','AUTO-DETECT BY DEFAULT':'التعرّف التلقائي افتراضيًا',
    'Course name':'اسم المقرر','Course code':'رمز المقرر','IT area':'مجال تقنية المعلومات','Learner level':'مستوى المتعلمين','Optional':'اختياري',
    'Auto-detect from uploaded source':'التعرّف تلقائيًا من المصدر المرفوع','Auto / infer from source':'تلقائي / استنتاج من المصدر','Foundation':'تأسيسي','Undergraduate — introductory':'بكالوريوس — تمهيدي','Undergraduate — intermediate':'بكالوريوس — متوسط','Undergraduate — advanced':'بكالوريوس — متقدم','Graduate':'دراسات عليا','Professional / executive':'مهني / تنفيذي',
    'No Software Engineering course selection is required. Leave IT area on Auto-detect for normal use.':'لا يلزم اختيار مقرر هندسة برمجيات. اترك مجال تقنية المعلومات على التعرف التلقائي في الاستخدام المعتاد.',
    'Drag & drop your file here':'اسحب ملف المحاضرة وأفلته هنا','Drop your lecture here':'أسقط ملف المحاضرة هنا','or click to browse':'أو اضغط لاختيار ملف','PDF, PPTX, DOCX, TXT or MD · max 25MB':'PDF أو PPTX أو DOCX أو TXT أو MD · الحد 25MB','— or paste a public link':'— أو ألصق رابطًا عامًا','Primary source URL':'رابط المصدر الأساسي','Direct PDF links retain source visuals. Some presentation hosts restrict image access.':'روابط PDF المباشرة تحفظ صور المصدر. بعض منصات العروض تقيد الوصول إلى الصور.','Analyze Source':'تحليل المصدر','Preparing your lecture…':'جاري تجهيز المحاضرة…','Create free review draft':'إنشاء مسودة مراجعة مجانية','Build & audit with free-tier AI':'البناء والتدقيق بالذكاء الاصطناعي المجاني',
    'Teaching emphasis':'التركيز التعليمي','What would you like to emphasise?':'ما الذي تريد التركيز عليه؟','Emphasis changes the teaching approach, not the mandatory source coverage.':'التركيز يغير أسلوب التدريس ولا يحذف تغطية المصدر الإلزامية.','How would you like to work?':'كيف تريد العمل؟','Free workspace · no API calls':'مساحة مجانية · دون استدعاءات API','Optional AI · Gemini free-tier quota':'ذكاء اصطناعي اختياري · حصة Gemini المجانية','Supporting sources & generation settings':'المصادر المساندة وإعدادات التوليد','Supporting files':'الملفات المساندة','Supporting URLs':'روابط المصادر المساندة','Automatic repair rounds':'جولات الإصلاح التلقائي','One URL per line':'رابط واحد في كل سطر','Your content is secure and used only for academic enhancement.':'يُستخدم محتواك فقط لتحسين المحاضرة أكاديميًا.',
    'THE RELEASE CONTRACT':'عقد الإصدار','Twenty units. Twenty real jobs.':'عشرون وحدة، عشرون مهمة حقيقية.','A page count is not a quality check. The compiler checks each unit’s role, source coverage, evidence, and readable presentation.':'عدد الصفحات ليس فحص جودة. يتحقق المحرك من وظيفة كل وحدة وتغطية المصدر والأدلة وقابلية العرض للقراءة.','Lock the source':'تثبيت المصدر','Map primary topics and exact source coordinates.':'تحديد الموضوعات الأساسية وإحداثياتها الدقيقة في المصدر.','Build the learning sequence':'بناء تسلسل التعلم','Teach major source material by Unit 15. Use the final five to demonstrate capability.':'تُدرّس عناصر المصدر الرئيسية حتى الوحدة 15، وتُستخدم الوحدات الخمس الأخيرة لإثبات القدرة.','Audit and repair':'التدقيق والإصلاح','Run deterministic checks and an independent semantic review.':'تشغيل الفحوص الحتمية والمراجعة الدلالية المستقلة.','What if a check fails?':'ماذا لو فشل أحد الفحوص؟','You receive a clearly marked review draft with the failed checks exposed. It is not a verified lecture.':'ستحصل على مسودة مراجعة واضحة تعرض الفحوص الفاشلة، ولا تُعد محاضرة موثقة.',
    'COMPILATION':'المعالجة','QUEUED':'في الانتظار','ANALYZING':'قيد التحليل','GENERATING':'قيد البناء','AUDITING':'قيد التدقيق','READY':'جاهز','BLOCKED':'تحتاج مراجعة','ERROR':'خطأ','Preparing your source…':'جاري تجهيز المصدر…','Reconnect to this job →':'إعادة الاتصال بهذه المهمة ←',
    'YOUR LECTURE WORKSPACE':'مساحة عمل المحاضرة','VERIFIED RELEASE':'إصدار موثّق','REVIEW DRAFT':'مسودة للمراجعة','FREE / NO API CALLS':'مجاني / دون استدعاءات API','Edit your lecture without API credits.':'حرّر محاضرتك دون أرصدة API.','Download authoring prompt ↓':'تنزيل تعليمات التأليف ↓','Completed Blueprint JSON':'ملف Blueprint JSON المكتمل','Import & check locally':'استيراد وفحص محلي','The 20-unit check':'فحص الوحدات العشرين','Open a unit to inspect its source, learner task, and exact check result.':'افتح أي وحدة لمراجعة مصدرها ومهمة المتعلم ونتيجة الفحص الدقيقة.','Audit details':'تفاصيل التدقيق','Primary-source coverage ledger':'سجل تغطية المصدر الأساسي','Source element':'عنصر المصدر','Source':'المصدر','First taught':'أول تدريس','Status':'الحالة',
    'Visual Presenter':'العرض المرئي','Preview ↗':'معاينة ↗','Original source · all pages':'المصدر الأصلي · جميع الصفحات','Original PDF ↓':'PDF الأصلي ↓','Reading Pack':'حزمة القراءة','Instructor Guide':'دليل المدرس','Student Pack':'حزمة الطالب','Blueprint':'المخطط','Complete IT Lecture Package':'حزمة محاضرة تقنية المعلومات الكاملة','Download all files · ZIP ↓':'تنزيل جميع الملفات · ZIP ↓','Original source + presenter PPTX/PDF + reading pack + instructor guide + student pack + blueprint + authoring prompt.':'المصدر الأصلي + العرض PPTX/PDF + حزمة القراءة + دليل المدرس + حزمة الطالب + المخطط + تعليمات التأليف.',
    'Units in the Blueprint':'وحدات في المخطط','Unit grammar checks passed':'فحوص قواعد الوحدات الناجحة','Major checkpoints mapped by U15':'العناصر الرئيسية المغطاة حتى الوحدة 15','Planned teaching minutes':'دقائق التدريس المخططة','Deterministic checks':'الفحوص الحتمية','Semantic audit':'التدقيق الدلالي','Source fidelity':'أمانة المصدر','20-unit grammar':'قواعد الوحدات العشرين','Readable text fit':'ملاءمة النص للقراءة','PASS':'ناجح','NOT PASSED':'غير ناجح','NOT CHECKED':'لم يُفحص','UNKNOWN':'غير معروف','Mapped · verify depth':'مغطى · تحقق من العمق','MISSING':'مفقود','TAUGHT TOO LATE':'دُرّس متأخرًا',
    'Professional crisis':'أزمة مهنية','Domain spine':'خريطة المجال','Five measurable CLOs':'خمسة نواتج تعلم قابلة للقياس','Six H-Stack capabilities':'قدرات H-Stack الست','Predict · Constrain · Derive · Name':'تنبأ · قيّد · اشتق · سمِّ','First-principles mechanism':'آلية من المبادئ الأولى','Implementation structure':'بنية التنفيذ','Alternatives & trade-offs':'البدائل والمفاضلات','Measurement & falsification':'القياس وقابلية الدحض','Known · Unknown · Monitor':'المعلوم · المجهول · المراقبة','Contextual application':'تطبيق سياقي','Accountability':'المساءلة','Contemporary practice':'الممارسة المعاصرة','Practitioner consequences':'آثار التشغيل على الممارس','Critical AI literacy':'وعي نقدي بالذكاء الاصطناعي','Portfolio challenge':'تحدي ملف الإنجاز','Constraint mutation':'تغيير القيد','Evidence policy':'سياسة الأدلة','Four-level rubric':'سلم تقييم بأربعة مستويات','Bounded assurance':'ضمان مقيّد بالأدلة',
    'Use a PDF, PPTX, DOCX, TXT, or MD file.':'استخدم ملف PDF أو PPTX أو DOCX أو TXT أو MD.','The primary file is too large. Use a file smaller than 25 MB.':'الملف الأساسي كبير جدًا. استخدم ملفًا أصغر من 25MB.','Choose exactly one primary source: a file or a URL.':'اختر مصدرًا أساسيًا واحدًا فقط: ملفًا أو رابطًا.','Confirm the project is on the unpaid Free Tier, or choose the no-API workspace.':'أكد أن المشروع على الخطة المجانية، أو اختر مساحة العمل دون API.','The upload timed out. No automatic retry was sent; check your connection before trying again.':'انتهت مهلة الرفع. لم تتم إعادة المحاولة تلقائيًا؛ تحقق من الاتصال ثم حاول مجددًا.','The status request timed out. Your server-side job may still be running.':'انتهت مهلة طلب الحالة. قد تكون المهمة ما تزال تعمل على الخادم.','Choose your completed Blueprint JSON file.':'اختر ملف Blueprint JSON المكتمل.','Use a JSON file smaller than 25 MB.':'استخدم ملف JSON أصغر من 25MB.','Import timed out. Your previous draft has not been overwritten.':'انتهت مهلة الاستيراد. لم تتم الكتابة فوق المسودة السابقة.'
  }));

  const PLACEHOLDER_AR = {
    'For example: emphasise SQL joins, routing trade-offs, model evaluation, or a specific lab decision.':'مثال: ركّز على SQL joins أو مفاضلات التوجيه أو تقييم النماذج أو قرار مختبر محدد.',
    'For example: help students distinguish reliability from availability.':'مثال: ساعد الطلاب على التمييز بين الاعتمادية والتوافر.',
    'e.g. Database Systems':'مثال: نظم قواعد البيانات','e.g. CPIT-240':'مثال: CPIT-240','One URL per line':'رابط واحد في كل سطر'
  };

  const originalText = new WeakMap();

  function replacePreservingSpace(node, value) {
    const raw=node.nodeValue || '';
    const lead=(raw.match(/^\s*/) || [''])[0];
    const trail=(raw.match(/\s*$/) || [''])[0];
    const next=lead+value+trail;
    if(raw!==next) node.nodeValue=next;
  }

  function localizeTextNode(node, lang) {
    if(!node || node.nodeType!==3) return;
    let raw=node.nodeValue || '', trimmed=raw.trim();
    if(!trimmed) return;
    let saved=originalText.get(node);
    if(lang==='ar') {
      if(saved && trimmed===saved.ar) return;
      if(AR.has(trimmed)) {
        const ar=AR.get(trimmed); originalText.set(node,{en:trimmed,ar}); replacePreservingSpace(node,ar); return;
      }
      // A dynamic widget may have replaced this node since last localization.
      if(saved && trimmed!==saved.ar && trimmed!==saved.en) originalText.delete(node);
    } else {
      if(saved && trimmed===saved.ar) { replacePreservingSpace(node,saved.en); return; }
      // Handles Arabic text nodes restored from browser history.
      for (const [en,ar] of AR) if(trimmed===ar) { originalText.set(node,{en,ar}); replacePreservingSpace(node,en); return; }
    }
  }

  function walk(root, lang) {
    if(!root) return;
    if(root.nodeType===3) { localizeTextNode(root,lang); return; }
    if(root.nodeType!==1 && root.nodeType!==9 && root.nodeType!==11) return;
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    let node; while((node=walker.nextNode())) localizeTextNode(node,lang);
  }

  function localizeAttributes(lang) {
    document.querySelectorAll('input[placeholder],textarea[placeholder]').forEach(el=>{
      if(!el.dataset.i18nPlaceholderEn) el.dataset.i18nPlaceholderEn=el.getAttribute('placeholder') || '';
      const en=el.dataset.i18nPlaceholderEn;
      el.setAttribute('placeholder',lang==='ar' && PLACEHOLDER_AR[en] ? PLACEHOLDER_AR[en] : en);
    });
    const theme=document.getElementById('themeToggle');
    if(theme) theme.title=lang==='ar' ? (document.documentElement.getAttribute('data-theme')==='light'?'التبديل إلى الوضع الداكن':'التبديل إلى الوضع الفاتح') : (document.documentElement.getAttribute('data-theme')==='light'?'Switch to dark':'Switch to light');
    const nav=document.querySelector('nav'); if(nav) nav.setAttribute('aria-label',lang==='ar'?'التنقل الرئيسي':'Main navigation');
    const progress=document.getElementById('progressTrack'); if(progress) progress.setAttribute('aria-label',lang==='ar'?'تقدم معالجة المحاضرة':'Compilation progress');
  }

  function apply() {
    const lang=document.documentElement.getAttribute('data-lang')==='ar'?'ar':'en';
    walk(document.body,lang); localizeAttributes(lang);
    document.body && document.body.classList.toggle('iscarb-ar',lang==='ar');
  }

  let pending=false;
  const observer=new MutationObserver(records=>{
    if(pending) return; pending=true;
    queueMicrotask(()=>{pending=false; apply();});
  });

  document.addEventListener('DOMContentLoaded',function(){
    apply(); observer.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['placeholder']});
  });
  document.addEventListener('iscarb:language',apply);
})();
