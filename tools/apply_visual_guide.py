"""The visual, bilingual assignment guide: one nine-step strip, used in three places, plus annotated screenshots.

- assignment-example.html: the step strip and the pictured walkthrough (real screenshots in assets/guide/).
- student-guide.html: the step strip at the top of "Assignments 3–9, step by step".
- Assignments 3–9: a compact step strip under the title (HTML and CSS only, no images, so offline copies work).

Screenshots are taken from the real pages with numbered markers. They show only public text, empty fields or neutral
placeholders, and never a STRESS text. Captions are English and Arabic.
Idempotent:  python3 tools/apply_visual_guide.py
"""
from __future__ import annotations
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
esc = lambda s: html.escape(str(s), quote=True)

STEPS = [
    ('📖', 'Prepare', 'Lecture, the two readings, the five practice questions', 'احضر المحاضرة، اقرأ المصدرين، وحلّ الأسئلة الخمسة', '15 min', 'pic-open'),
    ('🔑', 'Open', 'Open it with your Student ID, in the same browser every time', 'افتح الواجب برقمك الجامعي، ومن نفس المتصفح دائماً', '1 min', 'pic-open'),
    ('✍️', 'Part A', 'FIT · artifact · BOUND · ACT + EVIDENCE, 120–180 words', 'اكتب حكمك الأول: المشكلة، المهمة، الحدود، القرار والدليل', '20 min', 'pic-parta'),
    ('🐍', 'Build', 'Plan, complete the code, write 3+ tests, Run', 'اكتب الخطة، أكمل الكود، 3 اختبارات على الأقل، ثم Run', '30 min', 'pic-build'),
    ('🔒', 'Commit', 'Review & commit Part A. This is not submission', 'ثبّت الجزء A، وهذا ليس تسليماً', '1 min', 'pic-commit'),
    ('⬆️', 'Blackboard', 'Save the Part A PDF and upload it', 'احفظ PDF الجزء A وارفعه في Blackboard', '3 min', 'pic-blackboard'),
    ('📋', 'New evidence', 'Copy ALL of it from Blackboard, paste, Check and continue', 'انسخ الدليل الجديد كاملاً من Blackboard والصقه', '2 min', 'pic-stress'),
    ('🔄', 'Part B', 'Boundary status, then RETAIN / REVISE / REPLACE and why', 'هل تغيّر قرارك؟ اختر وبرّر، ثم اكتب القرار النهائي', '10 min', 'pic-refit'),
    ('✅', 'Submit', 'Declare AI, sign, Print / PDF, submit in Blackboard', 'صرّح بالذكاء الاصطناعي، وقّع، صدّر PDF وسلّمه في Blackboard', '3 min', 'pic-submit'),
]

FIGS = [
    ('pic-open', 'step-open', 'Step 2 · Open the assignment', 'الخطوة 2 · افتح الواجب',
     [('Type your Student ID', 'اكتب رقمك الجامعي'), ('Tick the pledge', 'ضع علامة على التعهد'), ('Open assignment', 'اضغط Open assignment')]),
    ('pic-parta', 'step-parta-1', 'Step 3 · Part A: read the case, then FIT', 'الخطوة 3 · الجزء A: اقرأ الحالة، ثم FIT',
     [('Read the case: only these facts count', 'اقرأ الحالة: الحقائق المكتوبة فقط هي المعتمدة'), ('FIT: the problem that decides the case', 'FIT: ما المشكلة التي تحكم القرار؟')]),
    ('pic-parta-2', 'step-parta-2', 'Step 3 · Part A: the other four fields', 'الخطوة 3 · الجزء A: بقية الحقول',
     [('The chapter artifact (TRACE, TEST, …)', 'مهمة الفصل (TRACE أو TEST …)'), ('BOUND: when your claim stops holding', 'BOUND: متى يتوقف حكمك عن الصحة؟'), ('ACT: what to do now, and who owns it', 'ACT: ماذا تفعل الآن ومن المسؤول؟'), ('EVIDENCE: what someone else can check', 'EVIDENCE: ما الدليل الذي يستطيع غيرك فحصه؟')], 3),
    ('pic-build', 'step-build', 'Step 4 · The Python build', 'الخطوة 4 · البناء البرمجي',
     [('Write a short plan first', 'اكتب خطة قصيرة أولاً'), ('Complete the code and write 3+ tests', 'أكمل الكود واكتب 3 اختبارات على الأقل'), ('Run my tests and the course checks', 'اضغط Run لتشغيل الاختبارات')]),
    ('pic-record', 'step-record', 'Step 4 · Read your build record', 'الخطوة 4 · اقرأ سجل البناء',
     [('Your micro-viva change request', 'طلب التعديل الخاص بك للمقابلة القصيرة'), ('Your own tests: ✗ means fix code or test', 'اختباراتك: ✗ تعني أصلح الكود أو الاختبار'), ('Course checks: the rule from the task', 'فحوصات المقرر: قواعد الواجب'), ('“Not caught”: add a test for this bug', '«not caught»: أضف اختباراً يكشف هذا الخطأ')]),
    ('pic-commit', 'step-commit', 'Step 5 · Commit Part A', 'الخطوة 5 · ثبّت الجزء A',
     [('Review & commit Part A: freezes Part A, it is not submission', 'Review & commit يثبّت الجزء A، وهو ليس تسليماً')]),
    ('pic-stress', 'step-stress', 'Steps 6–7 · Blackboard, then the new evidence', 'الخطوتان 6–7 · Blackboard ثم الدليل الجديد',
     [('Save Part A as PDF, upload it to “Assignment N · Part A”', 'احفظ الجزء A كـ PDF وارفعه في Blackboard'), ('Paste the WHOLE “New evidence” item', 'الصق نص «New evidence» كاملاً'), ('Check and continue to Part B', 'اضغط Check and continue')]),
    ('pic-refit', 'step-refit', 'Step 8 · Part B: REFIT', 'الخطوة 8 · الجزء B: المراجعة',
     [('What happened to your boundary?', 'ماذا حدث لحدود حكمك؟'), ('RETAIN, REVISE or REPLACE', 'أبقِ، عدّل، أو استبدل القرار'), ('Defend the choice from the new evidence', 'برّر اختيارك من الدليل الجديد'), ('The final decision another person can act on', 'القرار النهائي الذي ينفّذه غيرك')]),
    ('pic-submit', 'step-submit', 'Step 9 · Declare AI and sign', 'الخطوة 9 · التصريح والتوقيع',
     [('AI use, or “No AI used.”', 'استخدام الذكاء الاصطناعي، أو «No AI used.»'), ('Type your name', 'اكتب اسمك'), ('Tick: you reviewed it and take responsibility', 'ضع علامة: راجعت العمل وأتحمّل مسؤوليته')]),
    ('pic-pdf', 'step-pdf', 'Step 9 · Export and submit', 'الخطوة 9 · صدّر وسلّم',
     [('Print / PDF, check the file, upload it in Blackboard', 'Print / PDF، راجع الملف، ثم ارفعه في Blackboard')], 4),
]
SIZES = {}

CSS = '''<style>
.vs-strip{list-style:none;margin:12px 0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
@media (max-width:760px){.vs-strip{grid-template-columns:repeat(2,minmax(0,1fr))}}
h2 .vs-ar-t{display:block;font-weight:600;font-size:.8em;margin-top:4px}
.vs-strip li{position:relative;border:1px solid color-mix(in srgb,currentColor 18%,transparent);border-radius:12px;padding:10px 12px 10px 12px;background:color-mix(in srgb,#0f766e 5%,transparent)}
.vs-strip a{color:inherit;text-decoration:none;display:block}
.vs-strip .vs-n{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;background:#0f766e;color:#fff;font-weight:800;font-size:14px;margin-right:6px}
.vs-strip .vs-i{font-size:20px;vertical-align:middle}
.vs-strip b{display:block;margin-top:6px;font-size:15px}
.vs-strip .vs-en{display:block;font-size:13px;line-height:1.35;margin-top:2px}
.vs-strip .vs-ar{display:block;font-size:14px;line-height:1.5;margin-top:4px;font-weight:600}
.vs-strip .vs-t{position:absolute;top:10px;right:10px;font-size:11px;font-weight:800;opacity:.75}
.vs-fig{margin:18px 0;border:1px solid color-mix(in srgb,currentColor 15%,transparent);border-radius:14px;padding:12px;overflow:hidden}
.vs-fig h3{margin:0 0 4px}.vs-fig .vs-ar-h{display:block;font-size:16px;margin-bottom:8px}
.vs-fig img{display:block;width:100%;height:auto;border-radius:10px;border:1px solid color-mix(in srgb,currentColor 12%,transparent)}
.vs-legend{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:6px}
.vs-legend li{display:grid;grid-template-columns:30px 1fr 1fr;gap:8px;align-items:start}
.vs-legend .vs-n{display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;background:#e11d48;color:#fff;font-weight:800;font-size:14px}
.vs-legend [lang=ar]{font-weight:600}
.vs-bb{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin-top:8px}
.vs-bb div{border:2px dashed color-mix(in srgb,currentColor 25%,transparent);border-radius:12px;padding:12px}
@media (max-width:640px){.vs-legend li{grid-template-columns:30px 1fr}.vs-legend li [lang=ar]{grid-column:2}}
</style>'''


def strip(link_prefix: str = '', compact: bool = False) -> str:
    items = []
    for i, (ic, t, en, ar, mins, anchor) in enumerate(STEPS, 1):
        inner = (f'<span class="vs-n">{i}</span><span class="vs-i" aria-hidden="true">{ic}</span><span class="vs-t">{esc(mins)}</span>'
                 f'<b>{esc(t)}</b><span class="vs-en">{esc(en)}</span><span class="vs-ar" lang="ar" dir="rtl">{esc(ar)}</span>')
        items.append(f'<li><a href="{link_prefix}assignment-example.html#{anchor}">{inner}</a></li>')
    return f'<ol class="vs-strip" aria-label="The assignment in nine steps">{"".join(items)}</ol>'


def figures() -> str:
    from PIL import Image
    out = []
    for fig in FIGS:
        fid, img, en, ar, legend = fig[:5]; start = fig[5] if len(fig) > 5 else 1
        w, h = Image.open(ROOT / f'assets/guide/{img}.webp').size
        lis = ''.join(f'<li><span class="vs-n">{start + k}</span><span>{esc(e)}</span><span lang="ar" dir="rtl">{esc(a)}</span></li>' for k, (e, a) in enumerate(legend))
        alt = f'{en}: screenshot of the assignment page with numbered markers. ' + '; '.join(f'{start + k}: {e}' for k, (e, _) in enumerate(legend))
        out.append(f'<figure class="vs-fig" id="{fid}"><h3>{esc(en)}</h3><span class="vs-ar-h" lang="ar" dir="rtl">{esc(ar)}</span>'
                   f'<img src="assets/guide/{img}.webp" width="{w}" height="{h}" loading="lazy" alt="{esc(alt)}"><ol class="vs-legend">{lis}</ol></figure>')
        if fid == 'pic-commit':
            out.append('<figure class="vs-fig" id="pic-blackboard"><h3>Step 6 · In Blackboard</h3><span class="vs-ar-h" lang="ar" dir="rtl">الخطوة 6 · في Blackboard</span>'
                       '<div class="vs-bb"><div><b>① Assignment N · Part A (committed record)</b><br>Upload the Part A PDF here.<br><span lang="ar" dir="rtl">ارفع ملف PDF الجزء A هنا.</span></div>'
                       '<div><b>② Assignment N · New evidence</b><br>Opens only after your upload. Copy ALL of its text.<br><span lang="ar" dir="rtl">يظهر بعد الرفع فقط. انسخ النص كاملاً.</span></div>'
                       '<div><b>③ Assignment N · final submission</b><br>At the end, upload the final PDF here.<br><span lang="ar" dir="rtl">في النهاية ارفع ملف PDF النهائي هنا.</span></div></div></figure>')
    return ''.join(out)


def put(text: str, name: str, content: str, anchor: str | None = None, before: bool = False) -> str:
    a, b = f'<!-- visual-guide:{name}:start -->', f'<!-- visual-guide:{name}:end -->'
    block = a + content + b
    if a in text:
        return re.sub(re.escape(a) + '.*?' + re.escape(b), lambda _: block, text, flags=re.S)
    if anchor is None or text.count(anchor) != 1:
        raise SystemExit(f'anchor for {name} not found exactly once')
    return text.replace(anchor, block + anchor if before else anchor + block)


def main() -> int:
    # 1 · worked-example page
    p = ROOT / 'assignment-example.html'; s = p.read_text(encoding='utf-8')
    s = put(s, 'css', CSS, '</head>', before=True)
    steps = ('<p>Each card opens the picture of that step. <span lang="ar" dir="rtl">اضغط على أي خطوة لترى صورتها الحقيقية.</span></p>' + strip())
    s = put(s, 'steps', steps, '<!-- steps-strip -->')
    s = put(s, 'pictures', figures(), '<!-- steps-pictures -->')
    p.write_text(s, encoding='utf-8')
    # 2 · student guide
    p = ROOT / 'student-guide.html'; s = p.read_text(encoding='utf-8')
    s = put(s, 'css', CSS, '</head>', before=True)
    anchor = re.search(r'<section class="section" id="assignments-3-9"><h2>[^<]*</h2>', s).group(0)
    s = put(s, 'steps', '<p><b>The assignment in nine pictures:</b> select a step to see it on the real page. <span lang="ar" dir="rtl">الواجب في تسع خطوات مصوّرة: اضغط على أي خطوة لترى صورتها.</span></p>' + strip(), anchor)
    p.write_text(s, encoding='utf-8')
    # 3 · assignments 3–9: compact strip, no images (works offline)
    pub = json.loads((ROOT / 'curriculum/publication.json').read_text(encoding='utf-8'))
    for a in pub['assignments']:
        if a['chapter'] < 12: continue
        p = ROOT / a['path']; s = p.read_text(encoding='utf-8')
        sec = ('<section class="card" id="visualSteps"><h2>The assignment in nine steps <span class="vs-ar-t" lang="ar" dir="rtl">الواجب في تسع خطوات</span></h2>'
               + CSS + strip('../../') + '<p class="hint">Select a step to see it on a picture of this page. Online guide: <a href="../../assignment-example.html">How to do an assignment</a>.</p></section>')
        s = put(s, 'steps', sec, '<section class="card" data-concise="v1"><h2>Before you start</h2>', before=True)
        p.write_text(s, encoding='utf-8')
    print('visual guide applied')
    return 0


if __name__ == '__main__':
    sys.exit(main())
