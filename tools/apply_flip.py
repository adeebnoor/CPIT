"""Flipped lectures: seat booking page, admin page and seed data (idempotent).

- flip.html: the idea, the full rubric (Arabic and English), one card per lecture (2-5) with date, registration close
  (72 h before), draft deadline (48 h before), "X of 3 left" and three seats (part, slides, available / booked /
  closed). Booking form (student ID, full name, university email, rubric checkbox), confirmation with a six-character
  code, and "cancel my booking" (student ID + code). Names and IDs of booked students are never shown.
- flip-admin.html: sign-in for arnoor@kau.edu.sa; bookings per lecture; move, cancel or add a student (also after
  registration has closed); the four rubric scores with an automatic total out of 3; CSV export for Blackboard;
  roster entry; deletion of all bookings and the roster after final grades.
- supabase/flip/seed.sql: lectures and seats from curriculum/flip-config.json.
- iscarb.html: an update card in "This semester" linking to the booking page.

Booking rules are enforced on the server (supabase/flip/schema.sql). The page uses only the project's publishable
key; no service key and no student data are in the repository.
"""
from pathlib import Path
from html import escape as E
import json, sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from course_shell import header, footer, dependencies, VERSION  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'curriculum/flip-config.json').read_text(encoding='utf-8'))

RUBRIC = [  # criterion, marks, full, half, zero
    (('صحة المعلومة', 'Accuracy'), '1',
     ('كل معلومة صحيحة ومربوطة برقم شريحة المصدر', 'Every point is correct and tied to its source slide number'),
     ('خطأ واحد أو نقطة ناقصة صححها الدكتور', 'One error or a missing point the instructor corrected'),
     ('أكثر من خطأ أساسي', 'More than one basic error')),
    (('الفهم', 'Understanding'), '1',
     ('يجيب سؤال الدكتور المفاجئ ويشرح الفكرة على حالة غير المذكورة في الشرائح', "Answers the instructor's unannounced question and explains the idea on a case not in the slides"),
     ('إجابة صحيحة جزئيًا أو يكرر مثال الشرائح', 'A partly correct answer, or repeats the slide example'),
     ('لا يستطيع الإجابة', 'Cannot answer')),
    (('وصول المعلومة', 'Class quiz'), '0.5',
     ('70% فأكثر من الطلاب أجابوا سؤال جزئه في كويز الخروج', '70% or more of the class answer his part\'s question in the exit quiz'),
     ('من 50% إلى أقل من 70%', '50% to under 70%'),
     ('أقل من 50%', 'Under 50%')),
    (('الالتزام', 'Commitment'), '0.5',
     ('سلّم المسودة قبل 48 ساعة والتزم بالوقت (12–15 دقيقة)', 'Draft submitted 48 hours before, and the 12–15 minute time kept'),
     ('أحدهما فقط', 'Only one of the two'),
     ('لا هذا ولا ذاك', 'Neither')),
]

MESSAGES = {
    'taken': ('هذا المقعد حُجز قبل لحظات، اختر مقعدًا آخر.', 'This seat was booked moments ago. Choose another seat.'),
    'already': ('لديك حجز مسبق، لكل طالب مقعد واحد.', 'You already have a booking. One seat per student.'),
    'not_in_roster': ('الرقم الجامعي غير مسجل في الشعبة، تواصل مع الدكتور.', 'This student ID is not registered in the section. Contact the instructor.'),
    'closed': ('التسجيل مغلق لهذه المحاضرة.', 'Registration is closed for this lecture.'),
    'bad_code': ('الرقم الجامعي أو رمز التأكيد غير صحيح.', 'The student ID or confirmation code is incorrect.'),
    'locked': ('تجاوزت عدد المحاولات المسموح، تواصل مع الدكتور.', 'Too many attempts. Contact the instructor.'),
    'no_seat': ('هذا المقعد غير موجود.', 'This seat does not exist.'),
    'network': ('تعذّر الاتصال بخدمة التسجيل، حاول مرة أخرى بعد قليل.', 'The booking service could not be reached. Try again shortly.'),
    'not_open': ('التسجيل لم يُفتح بعد.', 'Registration is not open yet.'),
}


def bi(ar, en, tag='span'):
    return f'<{tag} lang="ar">{E(ar)}</{tag}><{tag} class="en" lang="en" dir="ltr">{E(en)}</{tag}>'


STYLE = '''<style>
.fl-intro{max-width:72ch}
.fl .en{display:block;color:var(--muted);font-size:.92em}
.fl[dir=rtl] .en{text-align:right}
.fl h1 .en,.fl h2 .en{font-size:.6em;font-weight:600}
.fl table td .en,.fl table th .en{font-size:.85em}
.fl-cards{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr))}
.fl-card{min-width:0;border:1px solid var(--line);border-radius:14px;padding:16px;background:var(--panel);display:grid;gap:10px;align-content:start}
.fl-card h3{margin:0;text-wrap:balance}
.fl-card dl{display:grid;grid-template-columns:minmax(0,11em) 1fr;gap:6px 12px;margin:0;font-size:.95em}
@media (max-width:480px){.fl-card dl{grid-template-columns:1fr}.fl-card dd{margin-bottom:6px}}
.fl-card dt{color:var(--muted)}.fl-card dd{margin:0;font-variant-numeric:tabular-nums}
.fl-left{font-weight:800;color:var(--accent);margin:0}.fl-card h3 .en{font-size:.75em;font-weight:600}
.fl-seat{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;border-top:1px dashed var(--line);padding-top:10px}
.fl-seat b{display:block}.fl-seat small{color:var(--muted);display:block}
.fl-seat button{font:inherit;border-radius:10px;padding:8px 14px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);cursor:pointer;white-space:nowrap}
.fl-seat button[disabled]{background:transparent;color:var(--muted);border-color:var(--line);cursor:not-allowed}
.fl-closed{color:var(--muted)}
.fl-free{display:inline-block;font-size:.75em;font-weight:700;color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:0 8px;margin-inline-end:4px}
.fl-panel{border:2px solid var(--accent);border-radius:14px;padding:16px;background:var(--panel);display:grid;gap:12px}
.fl-panel[hidden]{display:none}
.fl-form{display:grid;gap:10px;max-width:520px}
.fl-form label{display:grid;gap:4px}
.fl-form input[type=text],.fl-form input[type=email]{font:inherit;padding:10px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink)}
.fl-form .check{display:flex;gap:8px;align-items:flex-start}
.fl-form button,.fl-btn{font:inherit;border-radius:10px;padding:10px 16px;border:1px solid var(--accent);background:var(--accent);color:var(--bg);cursor:pointer;justify-self:start}
.fl-btn.ghost{background:transparent;color:var(--accent)}
.fl-msg{padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg)}
.fl-msg:empty{display:none}
.fl-msg.err{border-color:#b4462f}
.fl-code{font:800 2rem/1.2 ui-monospace,monospace;letter-spacing:.25em;text-align:center;padding:12px;border:2px dashed var(--accent);border-radius:12px;direction:ltr}
.fl-warn{font-weight:700}
@media (max-width:480px){.fl-seat{grid-template-columns:1fr}.fl-seat button{width:100%}}
</style>'''


def rubric_table():
    rows = ''.join(f'<tr><td>{bi(*c)}</td><td>{m}</td><td>{bi(*f)}</td><td>{bi(*h)}</td><td>{bi(*z)}</td></tr>' for c, m, f, h, z in RUBRIC)
    rows += f'<tr><td>{bi("المجموع", "Total")}</td><td><b>3</b></td><td></td><td></td><td></td></tr>'
    head = ''.join(f'<th scope="col">{bi(a, b)}</th>' for a, b in [('المعيار', 'Criterion'), ('الدرجة', 'Marks'), ('كاملة', 'Full'), ('نصف', 'Half'), ('صفر', 'Zero')])
    return f'<div class="table-scroll"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def public_lectures():
    return [{k: l[k] for k in ('id', 'number', 'chapter', 'title_en', 'title_ar', 'assignment_en', 'assignment_ar', 'starts_at')}
            | {'seats': l['seats']} for l in CFG['lectures']]


def page_head(title, desc, extra=''):
    return ('<!DOCTYPE html>\n<html data-iscarb-standalone="1" data-theme="dark" lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta content="width=device-width,initial-scale=1" name="viewport"><meta content="#006b62" name="theme-color">'
            f'<meta content="{E(desc)}" name="description">{extra}<title>{E(title)}</title>'
            f'<link href="iscarb-hub.css?v={VERSION}" rel="stylesheet"><link rel="stylesheet" href="course-design.css?v={VERSION}">'
            + dependencies() + STYLE + '</head>')


STUDENT_JS = r'''<script>
(function(){
var CFG=__CFG__, MSG=__MSG__, LEC=__LEC__;
var $=function(s){return document.querySelector(s);}, H=function(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
var fmtAr=new Intl.DateTimeFormat('ar-SA-u-ca-gregory-nu-latn',{timeZone:'Asia/Riyadh',weekday:'long',day:'numeric',month:'long',hour:'numeric',minute:'2-digit'});
var fmtEn=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Riyadh',weekday:'short',day:'numeric',month:'short',hour:'numeric',minute:'2-digit',hour12:true});
function when(iso,h){var d=new Date(new Date(iso).getTime()-h*3600000);return '<span lang="ar">'+H(fmtAr.format(d))+'</span><span class="en" lang="en" dir="ltr">'+H(fmtEn.format(d))+'</span>';}
function msg(code){var m=MSG[code]||MSG.network;return '<span lang="ar">'+H(m[0])+'</span><span class="en" lang="en" dir="ltr">'+H(m[1])+'</span>';}
function rpc(name,body){return fetch(CFG.url+'/rest/v1/rpc/'+name,{method:'POST',headers:{'apikey':CFG.key,'Content-Type':'application/json'},body:JSON.stringify(body||{})}).then(function(r){if(!r.ok)throw Error('http '+r.status);return r.json();});}
var status={}, chosen=null;
function render(){
  var html=LEC.map(function(l){
    var free=l.seats.filter(function(s){return status[s.id]&&!status[s.id].booked;}).length;
    var closed=l.seats.every(function(s){return status[s.id]&&status[s.id].closed;});
    var known=l.seats.every(function(s){return status[s.id];});
    var seats=l.seats.map(function(s){var st=status[s.id];var label,dis=true;
      if(!st){label='…';}else if(st.closed){label='مغلق · Closed';}else if(st.booked){label='محجوز · Booked';}else{label='احجز · Book';dis=false;}
      return '<div class="fl-seat"><div><b>'+(st&&!st.booked&&!st.closed?'<span class="fl-free">متاح · Available</span> ':'')+'الجزء '+s.part_no+' · '+H(s.title_ar)+'</b><small lang="en" dir="ltr">Part '+s.part_no+' · '+H(s.title_en)+'</small><small lang="en" dir="ltr">'+H(s.slides)+'</small></div>'
        +'<button type="button" data-seat="'+s.id+'"'+(dis?' disabled':'')+'>'+label+'</button></div>';}).join('');
    return '<article class="fl-card'+(closed?' fl-closed':'')+'" id="lecture-'+l.number+'"><p class="ey">المحاضرة '+l.number+' · Lecture '+l.number+(closed?' · مغلق · Closed':'')+'</p>'
      +'<h3>'+H(l.title_ar)+'<span class="en" lang="en" dir="ltr">'+H(l.chapter)+' · '+H(l.title_en)+'</span></h3><p style="margin:0">'+H(l.assignment_ar)+'<span class="en" lang="en" dir="ltr">'+H(l.assignment_en)+'</span></p>'
      +'<dl><dt>الموعد · Date</dt><dd>'+when(l.starts_at,0)+'</dd><dt>إغلاق التسجيل · Registration closes</dt><dd>'+when(l.starts_at,72)+'</dd><dt>آخر موعد للمسودة · Draft due</dt><dd>'+when(l.starts_at,48)+'</dd></dl>'
      +'<p class="fl-left">'+(known?('باقي '+free+' من 3<span class="en" lang="en" dir="ltr">'+free+' of 3 left</span>'):'…')+'</p>'+seats+'</article>';}).join('');
  $('#flCards').innerHTML=html;
}
function load(){
  if(!CFG.url||!CFG.key){LEC.forEach(function(l){l.seats.forEach(function(s){status[s.id]={booked:false,closed:true};});});render();$('#flStatus').innerHTML=msg('not_open');return;}
  rpc('seat_status').then(function(rows){status={};rows.forEach(function(r){status[r.seat_id]={booked:r.booked,closed:r.closed};});render();$('#flStatus').innerHTML='';})
  .catch(function(){render();$('#flStatus').innerHTML=msg('network');});
}
document.addEventListener('click',function(e){
  var b=e.target.closest&&e.target.closest('button[data-seat]');if(!b||b.disabled)return;
  var id=+b.getAttribute('data-seat');var l=LEC.find(function(x){return x.seats.some(function(s){return s.id===id;});});var s=l.seats.find(function(x){return x.id===id;});
  chosen=id;$('#flChosen').innerHTML='المحاضرة '+l.number+' · '+H(l.chapter)+' · الجزء '+s.part_no+': '+H(s.title_ar)+'<span class="en" lang="en" dir="ltr">Lecture '+l.number+' · Part '+s.part_no+': '+H(s.title_en)+' · '+H(s.slides)+'</span>';
  $('#flBookMsg').textContent='';$('#flBookMsg').className='fl-msg';$('#flBook').hidden=false;$('#flDone').hidden=true;$('#flBook').scrollIntoView({behavior:'smooth',block:'start'});$('#flSid').focus({preventScroll:true});
});
$('#flBookForm').addEventListener('submit',function(e){
  e.preventDefault();var out=$('#flBookMsg');var sid=$('#flSid').value.trim(),name=$('#flName').value.trim(),mail=$('#flMail').value.trim();
  if(!/^[0-9]{7}$/.test(sid)){out.className='fl-msg err';out.innerHTML='<span lang="ar">الرقم الجامعي 7 أرقام.</span><span class="en" lang="en" dir="ltr">The student ID has 7 digits.</span>';return;}
  if(!$('#flAgree').checked){out.className='fl-msg err';out.innerHTML='<span lang="ar">أكّد أنك قرأت الروبريك.</span><span class="en" lang="en" dir="ltr">Confirm that you have read the rubric.</span>';return;}
  var btn=e.submitter||$('#flBookForm button');btn.disabled=true;out.className='fl-msg';out.textContent='…';
  rpc('book_seat',{p_student_id:sid,p_email:mail,p_full_name:name,p_seat_id:chosen}).then(function(r){
    if(!r.ok){out.className='fl-msg err';out.innerHTML=msg(r.error);load();return;}
    $('#flBook').hidden=true;$('#flBookForm').reset();
    $('#flDoneText').innerHTML='المحاضرة '+r.lecture+' · '+H(r.chapter)+' · الجزء '+r.part+': '+H(r.title_ar)+'<span class="en" lang="en" dir="ltr">Lecture '+r.lecture+' · Part '+r.part+': '+H(r.title_en)+' · '+H(r.slides)+'</span>'
      +'<p style="margin:8px 0 0"><b>آخر موعد للمسودة · Draft due:</b> '+when(r.draft_due,0)+'</p><p style="margin:4px 0 0">أرسل المسودة إلى arnoor@kau.edu.sa <span class="en" lang="en" dir="ltr">Send the draft to arnoor@kau.edu.sa</span></p>';
    $('#flCode').textContent=r.code;$('#flDone').hidden=false;$('#flDone').scrollIntoView({behavior:'smooth',block:'start'});load();
  }).catch(function(){out.className='fl-msg err';out.innerHTML=msg('network');}).then(function(){btn.disabled=false;});
});
$('#flCancelBook').addEventListener('click',function(){$('#flBook').hidden=true;});
$('#flCancelForm').addEventListener('submit',function(e){
  e.preventDefault();var out=$('#flCancelMsg');var sid=$('#flCSid').value.trim(),code=$('#flCCode').value.trim();
  var btn=$('#flCancelForm button');btn.disabled=true;out.className='fl-msg';out.textContent='…';
  rpc('cancel_booking',{p_student_id:sid,p_code:code}).then(function(r){
    if(!r.ok){out.className='fl-msg err';out.innerHTML=msg(r.error);return;}
    out.className='fl-msg';out.innerHTML='<span lang="ar">أُلغي حجزك، والمقعد متاح الآن لغيرك.</span><span class="en" lang="en" dir="ltr">Your booking is cancelled and the seat is available again.</span>';$('#flCancelForm').reset();load();
  }).catch(function(){out.className='fl-msg err';out.innerHTML=msg('network');}).then(function(){btn.disabled=false;});
});
load();setInterval(load,60000);
})();
</script>'''


def build_student():
    model = CFG['model_lecture']
    main = f'''<main class="wrap fl" id="main" lang="ar" dir="rtl"><div class="document-heading"><p class="ey">CPIT-455 · المحاضرات المقلوبة · Flipped lectures</p>
<h1>اشرح جزءًا من المحاضرة، واحصل على 3 درجات</h1>
<p class="en" lang="en" dir="ltr">Explain part of a lecture and earn 3 marks</p>
<div class="fl-intro"><p>في المحاضرات من الثانية إلى الخامسة يشرح ثلاثة منكم جزءًا من الفصل لزملائهم في 12 إلى 15 دقيقة، وأنا معكم أصحّح وأكمّل. لكل محاضرة 3 مقاعد، ولكل طالب مقعد واحد، والحجز بالأسبقية. المقعد عليه 3 درجات تُحسب من درجة المشاركة (10)، فهي ليست درجة إضافية فوق الـ100. المشاركة اختيارية، ومن لا يسجل لا تُخصم منه أي درجة. المحاضرة الأولى ({E(model['chapter'])}، الخميس 29 أكتوبر) يقدمها الدكتور نموذجًا.</p>
<p class="en" lang="en" dir="ltr">In lectures 2 to 5, three of you each explain one part of the chapter to the class in 12 to 15 minutes, and I correct and complete. Each lecture has 3 seats, one seat per student, first come first served. A seat is worth 3 marks counted within the participation grade (10), not extra marks above 100. Taking part is optional and nobody loses marks for not booking. Lecture 1 ({E(model['chapter'])}, Thursday 29 October) is given by the instructor as a model.</p></div></div>

<section class="section" id="rubric"><h2>الروبريك (3 درجات) <span class="en" lang="en" dir="ltr">Rubric (3 marks)</span></h2>
{rubric_table()}
<p><b>المسودة:</b> صفحة واحدة تلخّص جزءك، لكل معلومة رقم شريحة المصدر، ومعها مثال جديد من عندك، وسؤال اختيار من متعدد للكويز. تُرسل إلى arnoor@kau.edu.sa قبل المحاضرة بـ48 ساعة، وأراجعها وأرد عليك بالتصحيحات.</p>
<p class="en" lang="en" dir="ltr"><b>Draft:</b> one page summarizing your part, with the source slide number for every point, a new example of your own and one multiple-choice question for the quiz. Send it to arnoor@kau.edu.sa 48 hours before the lecture; I review it and reply with corrections.</p></section>

<section class="section" id="seats"><h2>المحاضرات والمقاعد <span class="en" lang="en" dir="ltr">Lectures and seats</span></h2>
<p>كل الأوقات بتوقيت الرياض. يغلق التسجيل والإلغاء قبل المحاضرة بـ72 ساعة، وبعد الإغلاق لا يتغير المقعد إلا عن طريق الدكتور.</p>
<p class="en" lang="en" dir="ltr">All times are Riyadh time. Booking and cancelling close 72 hours before each lecture; after that, only the instructor can change a seat.</p>
<div class="fl-msg" id="flStatus" aria-live="polite"></div>
<div class="fl-cards" id="flCards" aria-live="polite"></div></section>

<section class="fl-panel" id="flBook" hidden aria-labelledby="flBookTitle"><h2 id="flBookTitle">احجز المقعد <span class="en" lang="en" dir="ltr">Book this seat</span></h2>
<p id="flChosen"></p>
<form class="fl-form" id="flBookForm" novalidate autocomplete="on">
<label>الرقم الجامعي (7 أرقام) <span class="en" lang="en" dir="ltr">Student ID (7 digits)</span><input type="text" id="flSid" inputmode="numeric" maxlength="7" pattern="[0-9]{{7}}" required dir="ltr" autocomplete="off"></label>
<label>الاسم الكامل <span class="en" lang="en" dir="ltr">Full name</span><input type="text" id="flName" required maxlength="120"></label>
<label>البريد الجامعي <span class="en" lang="en" dir="ltr">University email</span><input type="email" id="flMail" required dir="ltr" placeholder="name0000@stu.kau.edu.sa"></label>
<label class="check"><input type="checkbox" id="flAgree" required> <span>قرأت الروبريك وألتزم بتسليم المسودة قبل 48 ساعة <span class="en" lang="en" dir="ltr">I have read the rubric and will submit the draft 48 hours before</span></span></label>
<div style="display:flex;gap:8px;flex-wrap:wrap"><button type="submit">احجز · Book</button><button type="button" class="fl-btn ghost" id="flCancelBook">رجوع · Back</button></div>
<div class="fl-msg" id="flBookMsg" aria-live="polite"></div></form></section>

<section class="fl-panel" id="flDone" hidden aria-labelledby="flDoneTitle"><h2 id="flDoneTitle">تم الحجز <span class="en" lang="en" dir="ltr">Booked</span></h2>
<div id="flDoneText"></div>
<p class="fl-warn">رمز التأكيد. صوّر هذه الرسالة الآن، فهو الطريقة الوحيدة لإلغاء حجزك ولن يظهر مرة أخرى. <span class="en" lang="en" dir="ltr">Confirmation code. Take a screenshot now: it is the only way to cancel your booking and it will not be shown again.</span></p>
<p class="fl-code" id="flCode"></p></section>

<section class="section" id="cancel"><h2>إلغاء حجزي <span class="en" lang="en" dir="ltr">Cancel my booking</span></h2>
<p>متاح حتى يغلق التسجيل قبل المحاضرة بـ72 ساعة. <span class="en" lang="en" dir="ltr">Available until registration closes, 72 hours before the lecture.</span></p>
<form class="fl-form" id="flCancelForm" novalidate>
<label>الرقم الجامعي <span class="en" lang="en" dir="ltr">Student ID</span><input type="text" id="flCSid" inputmode="numeric" maxlength="7" required dir="ltr" autocomplete="off"></label>
<label>رمز التأكيد <span class="en" lang="en" dir="ltr">Confirmation code</span><input type="text" id="flCCode" maxlength="6" required dir="ltr" autocomplete="off" style="text-transform:uppercase;letter-spacing:.2em"></label>
<button type="submit">ألغِ حجزي · Cancel my booking</button>
<div class="fl-msg" id="flCancelMsg" aria-live="polite"></div></form>
<p><a href="iscarb.html">العودة إلى مسار التعلم · Back to the learning path</a></p></section>
</main>'''
    js = (STUDENT_JS.replace('__CFG__', json.dumps({'url': CFG['supabase_url'], 'key': CFG['publishable_key']}))
          .replace('__MSG__', json.dumps(MESSAGES, ensure_ascii=False))
          .replace('__LEC__', json.dumps(public_lectures(), ensure_ascii=False)))
    html = (page_head('المحاضرات المقلوبة · iSCARB CPIT-455', 'Book a seat to explain part of a flipped lecture in CPIT-455.')
            + '<body class="course-page" id="top"><a class="skip" href="#main">Skip to content</a>' + header('', '') + '\n'
            + main + footer('') + js + '</body></html>\n')
    (ROOT / 'flip.html').write_text(html, encoding='utf-8')


ADMIN_JS = r'''<script>
(function(){
var CFG=__CFG__, LEC=__LEC__, ADMIN='arnoor@kau.edu.sa', KEY='flip-admin-token';
var $=function(s){return document.querySelector(s);}, H=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
var token=null;try{token=sessionStorage.getItem(KEY);}catch(e){}
var seatName={};LEC.forEach(function(l){l.seats.forEach(function(s){seatName[s.id]='L'+l.number+' · '+l.chapter+' · P'+s.part_no+' · '+s.title_en;});});
var fmt=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Riyadh',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});
function note(t,err){var m=$('#adMsg');m.textContent=t;m.className='fl-msg'+(err?' err':'');}
function call(name,body){return fetch(CFG.url+'/rest/v1/rpc/'+name,{method:'POST',headers:{'apikey':CFG.key,'Authorization':'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(body||{})})
  .then(function(r){return r.json().then(function(j){if(!r.ok){if(r.status===401||/JWT|forbidden/i.test(JSON.stringify(j)))signOut();throw Error(j.message||('http '+r.status));}return j;});});}
function signOut(){token=null;try{sessionStorage.removeItem(KEY);}catch(e){}$('#adApp').hidden=true;$('#adLogin').hidden=false;}
$('#adLoginForm').addEventListener('submit',function(e){e.preventDefault();
  fetch(CFG.url+'/auth/v1/token?grant_type=password',{method:'POST',headers:{'apikey':CFG.key,'Content-Type':'application/json'},body:JSON.stringify({email:ADMIN,password:$('#adPass').value})})
  .then(function(r){return r.json().then(function(j){if(!r.ok||!j.access_token)throw Error('Sign-in failed');return j;});})
  .then(function(j){token=j.access_token;try{sessionStorage.setItem(KEY,token);}catch(e){}$('#adPass').value='';start();})
  .catch(function(err){$('#adLoginMsg').textContent=err.message;$('#adLoginMsg').className='fl-msg err';});});
var rows=[], roster=[];
function opts(sel,cur){return Object.keys(seatName).map(function(id){return '<option value="'+id+'"'+(+id===cur?' selected':'')+'>'+H(seatName[id])+'</option>';}).join('');}
function sc(name,val,choices){return '<select data-f="'+name+'">'+['',].concat(choices).map(function(c){return '<option value="'+c+'"'+(String(val==null?'':+val)===String(c)?' selected':'')+'>'+(c===''?'–':c)+'</option>';}).join('')+'</select>';}
function render(){
  var byL={};rows.forEach(function(r){(byL[r.lecture]=byL[r.lecture]||[]).push(r);});
  $('#adList').innerHTML=LEC.map(function(l){var list=byL[l.number]||[];
    return '<h3>Lecture '+l.number+' · '+H(l.chapter)+' '+H(l.title_en)+' · '+list.length+'/3</h3>'+(list.length?'<div class="table-scroll"><table><thead><tr><th>Part</th><th>Name</th><th>ID</th><th>Email</th><th>Booked</th><th>Accuracy</th><th>Understanding</th><th>Quiz</th><th>Commitment</th><th>Total</th><th>Actions</th></tr></thead><tbody>'
      +list.map(function(r){return '<tr data-b="'+r.booking_id+'"><td>'+r.part+'</td><td>'+H(r.full_name)+'</td><td dir="ltr">'+H(r.student_id)+'</td><td dir="ltr">'+H(r.email)+'</td><td dir="ltr">'+H(fmt.format(new Date(r.created_at)))+'</td>'
        +'<td>'+sc('a',r.accuracy,[1,0.5,0])+'</td><td>'+sc('u',r.understanding,[1,0.5,0])+'</td><td>'+sc('q',r.quiz,[0.5,0.25,0])+'</td><td>'+sc('c',r.commitment,[0.5,0.25,0])+'</td><td class="tot"><b>'+(+r.total)+'</b> / 3</td>'
        +'<td><button type="button" data-act="save">Save</button> <select data-move>'+opts(0,r.seat_id)+'</select><button type="button" data-act="move">Move</button> <button type="button" data-act="cancel">Cancel</button></td></tr>';}).join('')+'</tbody></table></div>':'<p>No bookings.</p>');}).join('');
  $('#adStudent').innerHTML=roster.map(function(s){return '<option value="'+H(s.student_id)+'">'+H(s.full_name)+' · '+H(s.student_id)+(s.booked?' (booked)':'')+'</option>';}).join('');
  $('#adSeat').innerHTML=opts(0,0);
  $('#adCount').textContent=roster.length+' students in the roster · '+rows.length+' bookings';
}
function refresh(){return Promise.all([call('admin_bookings'),call('admin_roster')]).then(function(a){rows=a[0];roster=a[1];render();}).catch(function(e){note(e.message,true);});}
function start(){$('#adLogin').hidden=true;$('#adApp').hidden=false;refresh();}
$('#adList').addEventListener('change',function(e){var tr=e.target.closest('tr[data-b]');if(!tr||!e.target.dataset.f)return;var t=0;tr.querySelectorAll('select[data-f]').forEach(function(s){t+=+(s.value||0);});tr.querySelector('.tot').innerHTML='<b>'+t+'</b> / 3';});
$('#adList').addEventListener('click',function(e){var b=e.target.closest('button[data-act]');if(!b)return;var tr=b.closest('tr');var id=+tr.dataset.b;var act=b.dataset.act;
  var v=function(f){var x=tr.querySelector('select[data-f="'+f+'"]').value;return x===''?null:+x;};
  var p=act==='save'?call('admin_score',{p_booking_id:id,p_accuracy:v('a'),p_understanding:v('u'),p_quiz:v('q'),p_commitment:v('c')})
       :act==='move'?call('admin_move',{p_booking_id:id,p_seat_id:+tr.querySelector('select[data-move]').value})
       :(confirmCancel(tr)?call('admin_cancel',{p_booking_id:id}):Promise.resolve({ok:false,error:'not confirmed'}));
  p.then(function(r){note(r.ok?'Saved.':('Not done: '+(r.error||'')),!r.ok);return refresh();}).catch(function(e){note(e.message,true);});});
function confirmCancel(tr){if(tr.dataset.sure==='1')return true;tr.dataset.sure='1';note('Press Cancel again to confirm.',true);return false;}
$('#adAddForm').addEventListener('submit',function(e){e.preventDefault();call('admin_add',{p_student_id:$('#adStudent').value,p_seat_id:+$('#adSeat').value})
  .then(function(r){note(r.ok?('Added. Cancellation code for the student: '+r.code):('Not added: '+r.error),!r.ok);return refresh();}).catch(function(e){note(e.message,true);});});
$('#adRosterForm').addEventListener('submit',function(e){e.preventDefault();call('admin_roster_add',{p_student_id:$('#adRId').value,p_full_name:$('#adRName').value,p_email:$('#adRMail').value})
  .then(function(r){note(r.ok?'Student saved in the roster.':'Not saved.',!r.ok);e.target.reset();return refresh();}).catch(function(e){note(e.message,true);});});
$('#adCsv').addEventListener('click',function(){var head=['student_id','full_name','lecture','part','accuracy','understanding','quiz','commitment','total'];
  var q=function(x){x=x==null?'':String(x);return /[",\n]/.test(x)?'"'+x.replace(/"/g,'""')+'"':x;};
  var csv='﻿'+head.join(',')+'\n'+rows.map(function(r){return [r.student_id,r.full_name,r.lecture,r.part,r.accuracy,r.understanding,r.quiz,r.commitment,+r.total].map(q).join(',');}).join('\n')+'\n';
  var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.download='CPIT455-flipped-grades.csv';document.body.appendChild(a);a.click();a.remove();});
$('#adPwForm').addEventListener('submit',function(e){e.preventDefault();fetch(CFG.url+'/auth/v1/user',{method:'PUT',headers:{'apikey':CFG.key,'Authorization':'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify({password:$('#adNewPw').value})})
  .then(function(r){note(r.ok?'Password changed.':'Password not changed (at least 10 characters).',!r.ok);e.target.reset();});});
$('#adPurge').addEventListener('click',function(){var c=$('#adPurgeText').value;call('admin_purge',{p_confirm:c}).then(function(r){note(r.ok?'All bookings and the roster were deleted.':'Type DELETE to confirm.',!r.ok);return refresh();}).catch(function(e){note(e.message,true);});});
$('#adOut').addEventListener('click',signOut);
if(!CFG.url){$('#adLoginMsg').textContent='The booking service is not configured yet.';}
else if(token){start();}
})();
</script>'''


def build_admin():
    main = '''<main class="wrap fl" id="main" lang="en" dir="ltr"><div class="document-heading"><p class="ey">CPIT-455 · Flipped lectures · Instructor</p><h1>Bookings and rubric scores</h1>
<p class="intro">Signed-in instructor only (arnoor@kau.edu.sa). Access is checked on the server.</p></div>
<section class="fl-panel" id="adLogin"><form class="fl-form" id="adLoginForm"><label>Email<input type="email" value="arnoor@kau.edu.sa" readonly></label>
<label>Password<input type="password" id="adPass" required autocomplete="current-password"></label><button type="submit">Sign in</button><div class="fl-msg" id="adLoginMsg" aria-live="polite"></div></form></section>
<div id="adApp" hidden>
<div class="fl-msg" id="adMsg" aria-live="polite"></div><p id="adCount"></p>
<section class="section"><h2>Bookings</h2><div id="adList"></div>
<p><button type="button" class="fl-btn" id="adCsv">Export CSV for Blackboard</button></p></section>
<section class="section"><h2>Add a student to a seat</h2><p>Also works after registration has closed.</p>
<form class="fl-form" id="adAddForm"><label>Student<select id="adStudent"></select></label><label>Seat<select id="adSeat"></select></label><button type="submit">Add</button></form></section>
<section class="section"><h2>Add or correct a student in the roster</h2>
<form class="fl-form" id="adRosterForm"><label>Student ID (7 digits)<input type="text" id="adRId" required pattern="[0-9]{7}" inputmode="numeric"></label><label>Full name<input type="text" id="adRName" required></label><label>University email<input type="email" id="adRMail" required></label><button type="submit">Save</button></form></section>
<section class="section"><h2>Account</h2><form class="fl-form" id="adPwForm"><label>New password (at least 10 characters)<input type="password" id="adNewPw" minlength="10" required autocomplete="new-password"></label><button type="submit">Change password</button></form>
<p><button type="button" class="fl-btn ghost" id="adOut">Sign out</button></p></section>
<section class="section"><h2>After final grades</h2><p>Deletes all bookings and the roster. Type DELETE, then press the button.</p>
<p><input type="text" id="adPurgeText" dir="ltr"> <button type="button" class="fl-btn ghost" id="adPurge">Delete all booking data</button></p></section>
</div></main>'''
    js = (ADMIN_JS.replace('__CFG__', json.dumps({'url': CFG['supabase_url'], 'key': CFG['publishable_key']}))
          .replace('__LEC__', json.dumps(public_lectures(), ensure_ascii=False)))
    html = (page_head('Flipped lectures · instructor · iSCARB CPIT-455', 'Instructor page for flipped-lecture bookings.', '<meta name="robots" content="noindex,nofollow">')
            .replace('lang="ar" dir="rtl"', 'lang="en" dir="ltr"', 1)
            + '<body class="course-page" id="top"><a class="skip" href="#main">Skip to content</a>' + header('', '') + '\n'
            + main + footer('') + js + '</body></html>\n')
    (ROOT / 'flip-admin.html').write_text(html, encoding='utf-8')


def seed_sql():
    q = lambda s: "'" + str(s).replace("'", "''") + "'"
    out = ['-- Generated by tools/apply_flip.py from curriculum/flip-config.json. Lectures and seats only; no student data.']
    for l in CFG['lectures']:
        out.append('insert into public.lectures (id, number, chapter, title_en, title_ar, assignment_en, assignment_ar, starts_at) values '
                   f"({l['id']}, {l['number']}, {q(l['chapter'])}, {q(l['title_en'])}, {q(l['title_ar'])}, {q(l['assignment_en'])}, {q(l['assignment_ar'])}, {q(l['starts_at'])}) "
                   'on conflict (id) do update set number = excluded.number, chapter = excluded.chapter, title_en = excluded.title_en, title_ar = excluded.title_ar, '
                   'assignment_en = excluded.assignment_en, assignment_ar = excluded.assignment_ar, starts_at = excluded.starts_at;')
        for s in l['seats']:
            out.append('insert into public.seats (id, lecture_id, part_no, title_en, title_ar, slides) values '
                       f"({s['id']}, {l['id']}, {s['part_no']}, {q(s['title_en'])}, {q(s['title_ar'])}, {q(s['slides'])}) "
                       'on conflict (id) do update set lecture_id = excluded.lecture_id, part_no = excluded.part_no, title_en = excluded.title_en, '
                       'title_ar = excluded.title_ar, slides = excluded.slides;')
    (ROOT / 'supabase/flip/seed.sql').write_text('\n'.join(out) + '\n', encoding='utf-8')


HUB_MARK = '<!-- flip:card -->'
HUB = (HUB_MARK + '<div class="flip-card" style="margin-top:12px;border-top:1px solid var(--line);padding-top:10px">'
       '<p class="ey">Update · تحديث</p><p style="margin:0"><b>Flipped lectures:</b> explain part of a lecture for 3 participation marks. '
       '<a href="flip.html">Book a seat</a>.</p><p lang="ar" dir="rtl" style="margin:4px 0 0"><b>المحاضرات المقلوبة:</b> اشرح جزءًا من المحاضرة '
       'واحصل على 3 درجات من المشاركة. <a href="flip.html">احجز مقعدك</a>.</p></div>')


def patch_hub():
    p = ROOT / 'iscarb.html'
    t = p.read_text(encoding='utf-8')
    if HUB_MARK in t:
        a = t.index(HUB_MARK)
        b = t.index('</div>', a) + len('</div>')
        t = t[:a] + HUB + t[b:]
    else:
        anchor = '<li><b>1</b><span>assessed decision, on Blackboard</span></li>\n</ul>\n'
        assert t.count(anchor) == 1, 'This semester list not found'
        t = t.replace(anchor, anchor + HUB + '\n')
    p.write_text(t, encoding='utf-8')


def register():
    edits = [
        ('tools/build_public_site.py', "'national-awareness.html',", "'national-awareness.html','flip.html','flip-admin.html',"),
        ('tools/audit_classroom.py', '"national-awareness.html", ', '"national-awareness.html", "flip.html", "flip-admin.html", '),
        ('tools/check-site-design.cjs', "'national-awareness.html',", "'national-awareness.html','flip.html',"),
    ]
    for rel, old, new in edits:
        p = ROOT / rel
        t = p.read_text(encoding='utf-8')
        if new not in t:
            assert t.count(old) == 1, f'{rel}: anchor found {t.count(old)} times'
            p.write_text(t.replace(old, new), encoding='utf-8')


if __name__ == '__main__':
    build_student()
    build_admin()
    seed_sql()
    patch_hub()
    register()
    print('Flipped lectures applied: flip.html, flip-admin.html, supabase/flip/seed.sql, learning-path card')
