"""National belonging and digital awareness, in the course's own reasoning (idempotent).

The university asked every section to give ten minutes at the start of one lecture in the week from Sunday
25 October 2026 (14/5/1448 AH) to four themes: the Kingdom's standing and the blessing of security; unity, trust in
the leadership and appreciation of those who protect the country; digital awareness and responsibility in
publishing; and the student's role in awareness and reassurance.

- national-awareness.html: the four themes, each linked to an idea students already use in CPIT-455 (trust is
  earned, one official channel, evidence and limits, a barrier that stops propagation); a ten-minute activity,
  "verify before you share", in which a message is treated as a claim and checked with FIT, EVIDENCE, BOUND and ACT;
  and the ten-minute plan for the lecturer. The scenarios are fictional and name no real service or person.
- iscarb.html: a short panel that points to the page.
- nelc-alignment.html: an English note on the activity (that page stays in English).
- Registers the page in the public build, the classroom audit, the site design check and the offline packages.
"""
from pathlib import Path
from html import escape as E
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from course_shell import header, footer, dependencies, VERSION  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'national-awareness.html'

THEMES = [
    ('١', 'مكانة المملكة ونعمة الأمن', 'الأمن نعمة نعيشها كل يوم، وحفظه مسؤولية مشتركة. بلاد الحرمين الشريفين لها مكانة دينية وتاريخية، وأمنها ومقدّراتها أمانة عند كل واحد منا.',
     'في الفصل العاشر تعلّمنا أن الثقة في النظام تُبنى بالعمل ولا تُفترض. وكذلك أمن الوطن: يحفظه وعي أهله في كل يوم.'),
    ('٢', 'وحدة الصف والثقة بالقيادة وتقدير حماة الوطن', 'قوتنا في اجتماعنا والتفافنا حول قيادتنا. نستقي المعلومة من مصادرها الرسمية، ونقدّر تضحيات القوات العسكرية والأجهزة الأمنية، ونتعاون معها ونلتزم بتعليماتها.',
     'في الفصل الرابع عشر رأينا أن التعافي من أي أزمة يحتاج إلى تنسيق وقناة رسمية واحدة. تعدّد الأصوات غير الموثوقة يربك الاستجابة.'),
    ('٣', 'الوعي الرقمي والمسؤولية في النشر', 'الكلمة المنشورة مسؤولية: منشورًا كانت أو تعليقًا أو إعادة إرسال. قبل النشر اسأل عن المصدر، وعن التاريخ والسياق، وعن الصورة أو المقطع: هل هو قديم أو مقتطع أو مصنوع بالذكاء الاصطناعي؟ والشكوى تُقدَّم عبر قنواتها الرسمية لا عبر وسائل التواصل.',
     'في كل واجب لا نقبل ادعاءً بلا دليل وحدود. الرسالة التي تصلك ادعاء أيضًا: افحصها بالطريقة نفسها قبل أن تنشرها.'),
    ('٤', 'دورك في الوعي والطمأنينة', 'كن مصدر طمأنينة لأسرتك وزملائك: تجنّب التهويل وخطاب الكراهية، وعلّم غيرك كيف يتحقق من الخبر، واجعل وقتك على المنصات فيما ينفع، وتفوّق في تخصصك خدمةً لوطنك.',
     'في الفصل الثاني عشر الحاجز يوقف الخطر قبل أن ينتشر. كن حاجزًا لا ناقلًا: الرسالة التي تتوقف عندك لا تصل إلى غيرك.'),
]

STEPS = [
    ('FIT', 'ما الادعاء بالضبط؟', 'اكتب في سطر واحد ما تقوله الرسالة، ومن يُنسب إليه.'),
    ('EVIDENCE', 'ما المصدر الرسمي؟', 'هل صدر عن جهة رسمية في حسابها الموثق أو موقعها؟ كثرة التداول وعدد المتابعين ليسا دليلًا.'),
    ('BOUND', 'متى يكون غير صحيح أو ناقصًا؟', 'هل هو قديم، أو مقتطع من سياقه، أو صورة أو صوت مصنوع بالذكاء الاصطناعي، أو من حساب حديث بلا هوية واضحة؟'),
    ('ACT', 'ما القرار، ومن المسؤول عنه؟', 'أنشر الرابط الرسمي فقط، أو أتوقف، أو أوصل الملاحظة إلى الجهة المختصة عبر قناتها الرسمية.'),
]

CASES = [
    ('رسالة صوتية في قروب الدفعة', 'رسالة صوتية تُنسب إلى «مسؤول في الجامعة» تقول إن محاضرات الغد أُلغيت، والكل يطلب إعادة إرسالها.',
     [('أعيد إرسالها حتى يعرف الجميع.', False, 'إعادة الإرسال تنشر ادعاءً بلا مصدر. إن كان غير صحيح فقد ضيّعت على زملائك محاضرة أو اختبارًا.'),
      ('أتحقق من إعلانات البلاك بورد وحسابات الجامعة الموثقة قبل أي شيء.', True, 'EVIDENCE: المصدر الرسمي للإلغاء هو إعلان الجامعة أو المقرر. BOUND: الصوت يمكن تقليده، والرسالة بلا اسم ولا تاريخ. ACT: إن صحّ الخبر فأرسل رابط الإعلان الرسمي، لا التسجيل.'),
      ('أؤكد صحتها لأن الصوت يشبه صوته.', False, 'تشابه الصوت ليس دليلًا؛ الأصوات تُصنع اليوم بالذكاء الاصطناعي.')]),
    ('مقطع يُتداول على أنه حدث اليوم', 'مقطع فيديو مثير للقلق يُتداول على أنه وقع اليوم في مدينتك، دون ذكر مصدره.',
     [('أنشره مع كلمة «انتبهوا».', False, 'التحذير لا يجعل المقطع صحيحًا، والنشر يضاعف القلق.'),
      ('أنشره وأكتب «غير متأكد».', False, 'عبارة «غير متأكد» لا توقف انتشاره، والمسؤولية تبقى على من نشر.'),
      ('لا أنشره، وأبحث عن تاريخه ومصدره، وأرجع إلى المصادر الرسمية.', True, 'BOUND: كثير من المقاطع قديمة أو مقتطعة. ابحث عن الصورة عكسيًا. EVIDENCE: في الشأن الأمني يُرجع إلى المصادر الرسمية المعنية، ويُتوقف عمّا لم يثبت.')]),
    ('حساب لا تعرفه', 'حساب أُنشئ قريبًا، صورته عامة، ينشر مقطعًا يثير الخلاف بين الناس ويطلب إعادة النشر.',
     [('أعيد النشر لأن المشاهدات كثيرة.', False, 'عدد المشاهدات ليس دليلًا على الصحة، والحساب الوهمي يعتمد على من يعيد النشر.'),
      ('لا أعيد النشر، وأتحقق من علامات الحساب الوهمي، وأبلّغ المنصة عنه.', True, 'FIT: الادعاء هنا هدفه إثارة الخلاف. علامات الحساب الوهمي: حديث، صورة عامة، يدور حول موضوع واحد يثير الخلاف، تفاعل متشابه، تهويل واستعجال. ACT: التبليغ عبر المنصة، ولا جدال.'),
      ('أرد عليه بتعليق حاد.', False, 'الرد الحاد يرفع انتشار المنشور، والتعليق مسؤولية مثل النشر.')]),
    ('ثغرة في نظام تستخدمه الجامعة', 'أثناء استخدامك نظامًا إلكترونيًا في الجامعة ظهرت لك بيانات طالب آخر.',
     [('أنشر لقطة شاشة لأنبّه الطلاب.', False, 'النشر يكشف خصوصية زميلك ويضاعف الضرر، ويعرّضك للمساءلة.'),
      ('أجرّب أكثر لأتأكد من الثغرة.', False, 'التجربة الإضافية وصول غير مصرّح به، حتى لو كانت النية حسنة. هذا ما ناقشناه في هندسة الأمن (الفصل الثالث عشر).'),
      ('أتوقف، ولا أنشر شيئًا، وأبلّغ الجهة المسؤولة عن النظام في الجامعة عبر قناتها الرسمية بوصف ما رأيت.', True, 'ACT: هذا هو الإفصاح المسؤول: وصف دقيق لما ظهر ومتى، إلى الجهة التي تملك المعالجة، دون نشر ولا تجربة. EVIDENCE: احتفظ بالوصف لنفسك ولا تشارك البيانات.')]),
]

PLAN = [
    ('الدقيقة 0–2', 'الفكرة: «في هذا المقرر لا نقبل ادعاءً بلا دليل وحدود، وكذلك الأخبار.» المحوران الأول والثاني باختصار.'),
    ('الدقيقة 2–7', 'المحور الثالث: الخطوات الأربع، ثم بطاقتان من النشاط يصوّت عليهما الطلاب برفع اليد، ثم التحليل.'),
    ('الدقيقة 7–9', 'المحور الرابع: «كن حاجزًا لا ناقلًا»، وبطاقة الثغرة مثالًا على الإفصاح المسؤول.'),
    ('الدقيقة 9–10', 'الختام بقول النبي ﷺ: «احرص على ما ينفعك، واستعن بالله ولا تعجز» (رواه مسلم)، ثم الانتقال إلى موضوع المحاضرة.'),
]


def themes():
    return ''.join(f'<article class="na-card"><p class="na-num">{n}</p><h3>{E(t)}</h3><p>{E(a)}</p>'
                   f'<p class="na-link"><b>بلغة المقرر:</b> {E(b)}</p></article>' for n, t, a, b in THEMES)


def steps():
    return ''.join(f'<li><span class="na-tag" lang="en" dir="ltr">{k}</span><b>{E(q)}</b><span>{E(d)}</span></li>' for k, q, d in STEPS)


def cases():
    out = []
    for i, (title, text, opts) in enumerate(CASES, 1):
        btns = ''.join(f'<button type="button" class="na-opt" data-ok="{1 if ok else 0}" data-why="{E(why)}">{E(o)}</button>' for o, ok, why in opts)
        key = next(o for o, ok, _ in opts if ok)
        why = next(w for _, ok, w in opts if ok)
        out.append(f'<article class="na-case" id="case-{i}"><p class="na-eyebrow">موقف {i} · افتراضي للتدريب</p><h3>{E(title)}</h3><p>{E(text)}</p>'
                   f'<p class="na-q">ماذا تفعل؟</p><div class="na-opts">{btns}</div><p class="na-fb" aria-live="polite"></p>'
                   f'<details><summary>التحليل</summary><p><b>الأنسب:</b> {E(key)}</p><p>{E(why)}</p></details></article>')
    return ''.join(out)


STYLE = '''<style>
.na-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:14px}
.na-card,.na-case{min-width:0;border:1px solid var(--line);border-radius:12px;padding:16px;background:var(--panel)}
.na-card h3,.na-case h3{margin:.2em 0 .4em;text-wrap:balance}
.na-num{margin:0;font-size:1.6rem;font-weight:800;color:var(--gold)}
.na-link{border-top:1px dashed var(--line);padding-top:8px;color:var(--muted)}
.na-steps{list-style:none;padding:0;display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr))}
.na-steps li{display:grid;gap:4px;border-inline-start:4px solid var(--accent);padding:6px 12px;min-width:0}
.na-tag{font:700 .75rem/1 ui-monospace,monospace;letter-spacing:.06em;color:var(--accent);justify-self:start}
.na-eyebrow{margin:0;font-size:.8rem;color:var(--muted)}
.na-q{font-weight:700;margin-bottom:6px}
.na-opts{display:grid;gap:8px}
.na-opt{text-align:start;font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);cursor:pointer}
.na-opt:hover{border-color:var(--accent)}
.na-opt[data-picked="1"][data-ok="1"]{border-color:#1a7f4b;outline:2px solid #1a7f4b}
.na-opt[data-picked="1"][data-ok="0"]{border-color:#b4462f;outline:2px solid #b4462f}
.na-fb:empty{display:none}
.na-fb{padding:8px 12px;border-radius:8px;background:var(--bg);border:1px solid var(--line)}
.na-plan td:first-child{white-space:nowrap;font-weight:700}
.na-barrier{font-size:1.25rem;font-weight:800;text-align:center;margin:8px 0 0}
</style>'''

SCRIPT = '''<script>
document.querySelectorAll('.na-case').forEach(function(c){var fb=c.querySelector('.na-fb');
c.querySelectorAll('.na-opt').forEach(function(b){b.addEventListener('click',function(){
c.querySelectorAll('.na-opt').forEach(function(x){x.removeAttribute('data-picked');x.setAttribute('aria-pressed','false');});
b.setAttribute('data-picked','1');b.setAttribute('aria-pressed','true');
fb.textContent=(b.getAttribute('data-ok')==='1'?'✓ اختيار مسؤول. ':'✗ فكّر مرة أخرى. ')+b.getAttribute('data-why');});});});
</script>'''


def build_page():
    plan = ''.join(f'<tr><td>{E(a)}</td><td>{E(b)}</td></tr>' for a, b in PLAN)
    main = f'''<main class="wrap" id="main" lang="ar" dir="rtl"><div class="document-heading"><p class="ey">عشر دقائق في بداية محاضرة · الأسبوع الذي يبدأ الأحد 25 أكتوبر 2026 (14/5/1448هـ)</p>
<h1>وطن آمن ووعي رقمي</h1>
<p class="intro">في هذا المقرر لا نقبل ادعاءً هندسيًا بلا دليل وحدود. هذه الصفحة تطبّق الطريقة نفسها على ما يصلنا من أخبار ورسائل: المحاور الأربعة التي وجّهت بها الجامعة، ثم نشاط من عشر دقائق: <b>تحقّق قبل أن تنشر</b>.</p>
<p class="small" lang="en" dir="ltr">Safe homeland, digital awareness: the university's four themes for a ten-minute opener, linked to ideas from this course, with a short activity in which a message is checked like an engineering claim. In Arabic.</p></div>

<section class="section" id="themes"><h2>المحاور الأربعة</h2><div class="na-grid">{themes()}</div></section>

<section class="section" id="verify"><h2>تحقّق قبل أن تنشر: الرسالة ادعاء</h2>
<p>استخدم مع أي رسالة الخطوات نفسها التي تستخدمها في الواجبات:</p>
<ol class="na-steps">{steps()}</ol>
<p class="na-barrier">كن حاجزًا لا ناقلًا</p></section>

<section class="section" id="activity"><h2>نشاط: ماذا تفعل في هذا الموقف؟</h2>
<p>أربعة مواقف افتراضية للتدريب، لا تشير إلى أشخاص أو خدمات حقيقية. اختر، ثم اقرأ التحليل.</p>
<div class="na-grid">{cases()}</div></section>

<section class="section" id="plan"><h2>للمحاضر: خطة العشر دقائق</h2>
<div class="table-scroll"><table class="na-plan"><thead><tr><th scope="col">الوقت</th><th scope="col">المحتوى</th></tr></thead><tbody>{plan}</tbody></table></div>
<p>تُقدَّم المحاور بلغة تربوية هادئة تعزز الطمأنينة والمسؤولية، مع الاستناد إلى المعلومات الرسمية وتجنّب التحليلات والتوقعات غير الموثوقة. إذا كان في المحاضرة اختبار، تُقدَّم الدقائق العشر قبل بدئه ولا تُحتسب من زمنه.</p>
<p><a href="iscarb.html">العودة إلى مسار التعلم</a></p></section>
</main>'''
    head = ('<!DOCTYPE html>\n<html data-iscarb-standalone="1" data-theme="dark" lang="ar" dir="rtl"><head><meta charset="utf-8">'
            '<meta content="width=device-width,initial-scale=1" name="viewport"><meta content="#006b62" name="theme-color">'
            '<meta content="Safe homeland and digital awareness: a ten-minute opener in the reasoning of CPIT-455." name="description">'
            '<title>وطن آمن ووعي رقمي · iSCARB CPIT-455</title>'
            f'<link href="iscarb-hub.css?v={VERSION}" rel="stylesheet"><link rel="stylesheet" href="course-design.css?v={VERSION}">'
            + dependencies() + STYLE + '</head>')
    body = ('<body class="course-page" id="top"><a class="skip" href="#main">Skip to content</a>'
            + header('', '') + '\n' + main + footer('') + SCRIPT + '</body></html>\n')
    PAGE.write_text(head + body, encoding='utf-8')


HUB_MARK = '<!-- national-awareness:panel -->'
HUB = (HUB_MARK + '<section class="national-week" id="national-awareness" aria-labelledby="na-title" style="padding-top:24px">'
       '<div class="panel" lang="ar" dir="rtl"><p class="ey">هذا الأسبوع · عشر دقائق</p><h2 id="na-title">وطن آمن ووعي رقمي</h2>'
       '<p>المحاور الأربعة التي وجّهت بها الجامعة، ونشاط قصير: <b>تحقّق قبل أن تنشر</b>، نفحص فيه الرسالة كما نفحص أي ادعاء هندسي، '
       'بخطوات الواجبات نفسها: <span dir="ltr" lang="en">FIT · EVIDENCE · BOUND · ACT</span>. <a href="national-awareness.html">افتح النشاط</a></p>'
       '<p class="small" lang="en" dir="ltr">Safe homeland, digital awareness: a ten-minute activity this week. '
       '<a href="national-awareness.html">Open it</a>.</p></div></section>')

NELC_MARK = '<!-- national-awareness:nelc -->'
NELC = (NELC_MARK + '<section class="panel" id="national-awareness"><h2>National belonging and digital awareness</h2>'
        '<p>In the week from 25 October 2026, each section gives ten minutes at the start of one lecture to the four themes set by the university: '
        'the Kingdom\'s standing and the blessing of security; unity, trust in the leadership and appreciation of those who protect the country; '
        'digital awareness and responsibility in publishing; and the student\'s role in awareness and reassurance. In this course the activity uses '
        'the course\'s own reasoning: a message is treated as a claim and checked with FIT, EVIDENCE, BOUND and ACT before it is shared, and '
        'a vulnerability is reported through the official channel rather than published. The activity and the lecturer\'s plan are on the '
        '<a href="national-awareness.html">activity page</a> (in Arabic).</p></section>')


def patch(rel, mark, block, anchor):
    p = ROOT / rel
    t = p.read_text(encoding='utf-8')
    if mark in t:
        a = t.index(mark)
        b = t.index('</section>', a) + len('</section>')
        t = t[:a] + block + t[b:]
    else:
        assert t.count(anchor) == 1, f'{rel}: anchor found {t.count(anchor)} times'
        t = t.replace(anchor, block + anchor)
    p.write_text(t, encoding='utf-8')


def register():
    edits = [
        ('tools/build_public_site.py', "'code-coverage.html',", "'code-coverage.html','national-awareness.html',"),
        ('tools/audit_classroom.py', '"code-coverage.html", ', '"code-coverage.html", "national-awareness.html", '),
        ('tools/check-site-design.cjs', "'code-coverage.html',", "'code-coverage.html','national-awareness.html',"),
        ('tools/prepare_readable_release.py', "'chapter-search.js','code-coverage.html']", "'chapter-search.js','code-coverage.html','national-awareness.html']"),
    ]
    for rel, old, new in edits:
        p = ROOT / rel
        t = p.read_text(encoding='utf-8')
        if new not in t:
            assert t.count(old) == 1, f'{rel}: anchor found {t.count(old)} times'
            p.write_text(t.replace(old, new), encoding='utf-8')


if __name__ == '__main__':
    build_page()
    patch('iscarb.html', HUB_MARK, HUB, '<!-- study-aids:glance -->')
    patch('nelc-alignment.html', NELC_MARK, NELC, '<section id="jaheziah">')
    register()
    print('National awareness applied: national-awareness.html, learning-path panel, Saudi alignment note')
