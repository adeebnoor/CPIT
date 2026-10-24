/* Ten-minute opener before the lecture: «وطن آمن ووعي رقمي» (university direction, week of 25 October 2026).
   Opens by itself only in presenter mode (?presenter=1, the in-class view), once per session at the start of the
   lecture in that week. Anyone can open it from #AWARENESS. Students studying alone are not interrupted.
   It sits outside the twenty lecture slides and does not change them. Fictional situations only. */
(function(){
  var UNTIL = Date.parse('2026-11-01T00:00:00+03:00');
  var KEY = 'iscarb:opener:awareness:v1';
  var THEMES = [
    ['مكانة المملكة ونعمة الأمن', 'الأمن نعمة نعيشها كل يوم، وحفظه مسؤولية مشتركة.', 'الثقة تُبنى ولا تُفترض (الفصل 10)'],
    ['وحدة الصف والثقة بالقيادة وتقدير حماة الوطن', 'نستقي المعلومة من مصادرها الرسمية، ونقدّر جهود القوات العسكرية والأجهزة الأمنية.', 'التعافي يحتاج قناة رسمية واحدة (الفصل 14)'],
    ['الوعي الرقمي والمسؤولية في النشر', 'الكلمة المنشورة مسؤولية: منشورًا كانت أو تعليقًا أو إعادة إرسال.', 'لا ادعاء بلا دليل وحدود'],
    ['دورك في الوعي والطمأنينة', 'كن مصدر طمأنينة، وتجنّب التهويل، واجعل وقتك فيما ينفع.', 'الحاجز يوقف الخطر قبل أن ينتشر (الفصل 12)']
  ];
  var STEPS = [['FIT','ما الادعاء بالضبط، ومن يُنسب إليه؟'],['EVIDENCE','ما المصدر الرسمي؟ كثرة التداول ليست دليلًا.'],['BOUND','هل هو قديم، أو مقتطع، أو مصنوع بالذكاء الاصطناعي؟'],['ACT','أنشر الرابط الرسمي، أو أتوقف، أو أبلّغ عبر القناة الرسمية.']];
  var CASES = [
    ['رسالة صوتية في قروب الدفعة تُنسب إلى «مسؤول في الجامعة»: محاضرات الغد أُلغيت. ماذا تفعل؟',
     'أتحقق من إعلانات البلاك بورد وحسابات الجامعة الموثقة. الصوت يمكن تقليده، والرسالة بلا اسم ولا تاريخ. إن صحّ الخبر أرسل رابط الإعلان الرسمي لا التسجيل.'],
    ['أثناء استخدامك نظامًا إلكترونيًا في الجامعة ظهرت لك بيانات طالب آخر. ماذا تفعل؟',
     'أتوقف، ولا أنشر لقطة شاشة، ولا أجرّب أكثر؛ فالتجربة الإضافية وصول غير مصرّح به (الفصل 13). أبلّغ الجهة المسؤولة عن النظام عبر قناتها الرسمية بوصف ما رأيت: هذا هو الإفصاح المسؤول.']
  ];
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var css = '#awOpener{position:fixed;inset:0;z-index:2147483000;overflow:auto;background:#0f3d2e;color:#f6f1e4;font:16px/1.6 "IBM Plex Sans Arabic","Noto Sans Arabic",Tahoma,system-ui,sans-serif;padding:max(16px,env(safe-area-inset-top,0px)) 16px 24px}'
    + '#awOpener .aw{max-width:1100px;margin:0 auto;display:grid;gap:16px}'
    + '#awOpener h2{margin:0;font-size:clamp(1.8rem,4vw,2.8rem);line-height:1.2;color:#fff}'
    + '#awOpener .ey{margin:0;color:#e0b252;font-weight:700;font-size:.9rem}'
    + '#awOpener .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:12px}'
    + '#awOpener .card{background:#164b39;border:1px solid #2d6b55;border-radius:12px;padding:12px 14px;min-width:0}'
    + '#awOpener .card b{display:block;color:#fff}#awOpener .card small{display:block;color:#e0b252;margin-top:6px}'
    + '#awOpener .tag{font:700 .75rem/1 ui-monospace,monospace;letter-spacing:.06em;color:#e0b252}'
    + '#awOpener .bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}'
    + '#awOpener button,#awOpener a.btn{font:inherit;border-radius:10px;padding:10px 16px;border:1px solid #e0b252;background:transparent;color:#f6f1e4;cursor:pointer;text-decoration:none}'
    + '#awOpener button.go{background:#e0b252;color:#0f3d2e;font-weight:800;border-color:#e0b252}'
    + '#awOpener .ans{margin:8px 0 0;color:#dfe9e4}#awOpener .ans[hidden]{display:none}'
    + '#awOpener .clock{font:700 1.4rem/1 ui-monospace,monospace;color:#e0b252;font-variant-numeric:tabular-nums}'
    + '#awOpener .motto{font-size:1.4rem;font-weight:800;text-align:center;margin:0;color:#fff}'
    + '#awOpener .hadith{text-align:center;margin:0;color:#e0b252}';
  function build(){
    var themes = THEMES.map(function(t,i){return '<div class="card"><span class="tag">'+(i+1)+'</span><b>'+esc(t[0])+'</b>'+esc(t[1])+'<small>بلغة المقرر: '+esc(t[2])+'</small></div>';}).join('');
    var steps = STEPS.map(function(s){return '<div class="card"><span class="tag" dir="ltr">'+s[0]+'</span><b>'+esc(s[1])+'</b></div>';}).join('');
    var cases = CASES.map(function(c,i){return '<div class="card"><b>موقف '+(i+1)+' · افتراضي</b>'+esc(c[0])+'<div style="margin-top:8px"><button type="button" data-aw-reveal="'+i+'">الإجابة بعد التصويت</button></div><p class="ans" id="awAns'+i+'" hidden>'+esc(c[1])+'</p></div>';}).join('');
    var d = document.createElement('div');
    d.id = 'awOpener'; d.setAttribute('role','dialog'); d.setAttribute('aria-modal','true'); d.setAttribute('aria-labelledby','awTitle'); d.lang = 'ar'; d.dir = 'rtl';
    d.innerHTML = '<style>'+css+'</style><div class="aw">'
      + '<div class="bar"><p class="ey">قبل المحاضرة · عشر دقائق لتعزيز الوعي الفكري والانتماء الوطني</p><span class="clock" id="awClock" aria-live="off">10:00</span></div>'
      + '<h2 id="awTitle">وطن آمن ووعي رقمي</h2>'
      + '<p style="margin:0">في هذا المقرر لا نقبل ادعاءً بلا دليل وحدود، وكذلك الأخبار والرسائل.</p>'
      + '<div class="row">'+themes+'</div>'
      + '<p class="ey">تحقّق قبل أن تنشر: الرسالة ادعاء</p><div class="row">'+steps+'</div>'
      + '<p class="ey">صوّتوا برفع اليد، ثم اعرض الإجابة</p><div class="row">'+cases+'</div>'
      + '<p class="motto">كن حاجزًا لا ناقلًا</p>'
      + '<p class="hadith">قال النبي ﷺ: «احرص على ما ينفعك، واستعن بالله ولا تعجز» (رواه مسلم)</p>'
      + '<div class="bar"><a class="btn" href="../../national-awareness.html" target="_blank" rel="noopener">النشاط كاملًا (أربعة مواقف)</a>'
      + '<button type="button" class="go" id="awStart">ابدأ المحاضرة</button></div></div>';
    return d;
  }
  var timer = null;
  function close(){
    var d = document.getElementById('awOpener'); if(!d) return;
    d.remove(); clearInterval(timer); document.removeEventListener('keydown', keys, true);
    try{ sessionStorage.setItem(KEY,'1'); }catch(e){}
    if(location.hash === '#AWARENESS'){ try{ history.replaceState(null,'',location.pathname+location.search); }catch(e){} }
  }
  function keys(e){
    if(e.key === 'Escape'){ e.preventDefault(); close(); }
    if(e.key !== 'Tab'){ e.stopPropagation(); }
  }
  function open(){
    if(document.getElementById('awOpener')) return;
    var d = build(); document.body.appendChild(d);
    d.addEventListener('click', function(e){
      var r = e.target.getAttribute && e.target.getAttribute('data-aw-reveal');
      if(r !== null && r !== undefined){ var a = document.getElementById('awAns'+r); if(a){ a.hidden = false; e.target.hidden = true; } }
      if(e.target.id === 'awStart') close();
    });
    document.addEventListener('keydown', keys, true);
    var end = Date.now() + 600000, clock = document.getElementById('awClock');
    timer = setInterval(function(){ var s = Math.max(0, Math.round((end-Date.now())/1000)); clock.textContent = Math.floor(s/60)+':'+('0'+s%60).slice(-2); if(!s) clearInterval(timer); }, 1000);
    var go = document.getElementById('awStart'); if(go) go.focus({preventScroll:true}); d.scrollTop = 0;
  }
  function start(){
    var asked = location.hash === '#AWARENESS';
    var seen = false; try{ seen = sessionStorage.getItem(KEY) === '1'; }catch(e){}
    var atStart = !location.hash || location.hash === '#TITLE';
    var presenter = /[?&]presenter=1\b/.test(location.search);
    if(asked || (presenter && Date.now() < UNTIL && atStart && !seen)) open();
  }
  window.addEventListener('hashchange', function(){ if(location.hash === '#AWARENESS') open(); });
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
