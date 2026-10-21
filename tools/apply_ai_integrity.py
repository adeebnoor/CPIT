"""AI rules, an AI-drafted answer to critique, and an in-class check in Assignments 6–9.

Chapters 15, 16, 17 and 20 only. Three changes, decided by the instructor after the midterm
(assignment marks were near full while the paper midterm averaged 73%):

1. AI rules per step. Part A is written without AI; the build may use AI only to explain an
   error message; after commitment AI may question the student's reasoning. Shown in English
   and Arabic in a card under "Before you start", and named again in the AI-use declaration.
2. An AI assistant's draft with planted errors. Assignments 6 and 9 already reviewed a flawed
   draft; it is now labelled as an AI assistant's draft. Assignments 7 and 8 gain one. Every
   planted error is contradicted by a supplied fact, so the critique counts inside FIT.
3. An in-class check. Two questions on paper, no devices, in the lecture after the deadline,
   about the student's own submission. Both correct: the mark stands; one: the mark is halved;
   neither: a two-minute conversation decides. A required rubric row that adds no points.
   It applies the ownership rule already stated on every assignment page.

The authored wording of the scenario prompts also lives in
curriculum/learning-path/plain-language.json, so a later run of
apply_assignment_plain_language.py keeps it. Scores, fields, storage keys, Python builds,
tests and commitment behaviour are unchanged.

Run after the other assignment builders.  Idempotent:  python3 tools/apply_ai_integrity.py
"""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAIN = ROOT / 'curriculum/learning-path/plain-language.json'
CHAPTERS = (15, 16, 17, 20)
ESC = html.escape

# ---- 2. AI drafts -------------------------------------------------------------------------
REVIEW = {
    15: ("An AI assistant's draft recommendation — review it; do not copy it", None),
    16: ("An AI assistant's draft answer — review it; do not copy it",
         'Use the component as it is. The sample request with duration = 30 returned a reservation ID, '
         'so the connection works correctly. Both sides call the value duration, so the adapter only needs '
         'to pass it through. Any duration up to 7200 is accepted, so a three-hour booking (180 minutes) is '
         'safe. No more tests are needed before the trial.'),
    17: ("An AI assistant's draft answer — review it; do not copy it",
         'Keep the current design. Normal requests succeed, so the booking flow is reliable. Sending the '
         'request again with a new request ID is safe, because the database creates exactly one reservation '
         'for each request ID. If a reply is lost, the browser\'s retry fixes the problem. A longer timeout '
         'would remove the risk completely.'),
    20: ("An AI assistant's draft design for the transport team — review it before the trial", None),
}
FORMAT = {
    15: ('Critique a colleague’s recommendation.', 'Critique an AI assistant’s recommendation.'),
    20: ('Review another team’s design.', 'Review an AI assistant’s design.'),
    16: (None, 'Review an AI assistant’s answer.'),
    17: (None, 'Review an AI assistant’s answer.'),
}
CRITIQUE = ' Name one claim in the AI draft that the supplied facts do not support, and the fact that shows it.'
# Prompt wording: (field, old, new). Applied to plain-language.json and to the page (hint and placeholder).
PROMPTS = {
    15: [('fit', "the colleague's draft", 'the AI draft'),
         ('build_task', "Use the output to check the claims in the colleague's draft.", 'Use the output to check the claims in the AI draft.')],
    16: [('fit', None, CRITIQUE)],
    17: [('fit', None, CRITIQUE)],
    20: [('fit', 'that the proposed design wrongly assumes', 'that the AI draft wrongly assumes'),
         ('measure', 'Review the proposed design.', 'Review the AI draft design.'),
         ('measure', "which weakness in the team's design it addresses", 'which weakness in the AI draft it addresses'),
         ('build_task', "Use the actual result when reviewing the team's design.", 'Use the actual result when reviewing the AI draft.')],
}
FIELD_ID = {'fit': 'fit', 'measure': 'measure'}

# ---- 1. AI rules and 3. in-class check ------------------------------------------------------
RULES = [
    ('Studying the lecture before you start', 'AI may explain an idea and ask you to restate it in your own words. It may not answer this case.',
     'قبل البدء: مذاكرة المحاضرة', 'يمكن للذكاء الاصطناعي أن يشرح فكرة ويطلب منك إعادة صياغتها بكلامك، ولا يجيب عن حالة هذا الواجب.'),
    ('Part A answers (FIT, COMPARE, BOUND, ACT + EVIDENCE, reading, second idea)', 'No AI. Write them yourself.',
     'إجابات الجزء A', 'بدون ذكاء اصطناعي. اكتبها بنفسك.'),
    ('The AI draft in the scenario', 'It is the material you critique. Find the claims the supplied facts do not support.',
     'مسودة الذكاء الاصطناعي في الحالة', 'هي المادة التي تنقدها: حدّد الادعاءات التي لا تدعمها الحقائق المعطاة.'),
    ('Python build', 'AI may explain an error message. It may not write your functions or your tests.',
     'البناء في بايثون', 'يمكن للذكاء الاصطناعي أن يشرح رسالة الخطأ، ولا يكتب دوالك ولا اختباراتك.'),
    ('After you commit (STRESS and REFIT)', 'AI may question your reasoning. The final decision and the words are yours.',
     'بعد تثبيت الجزء A', 'يمكن للذكاء الاصطناعي أن يسألك عن تفكيرك، والقرار الأخير وصياغته لك.'),
    ('AI-use declaration', 'Name the tool and the steps where you used it, what you changed because of it, and what you chose not to take, and why.',
     'تصريح استخدام الذكاء الاصطناعي', 'اذكر الأداة والخطوات التي استخدمتها فيها، وما غيّرته بسببها، وما رفضت أخذه ولماذا.'),
]
CHECK_EN = ('<b>In-class check.</b> In the lecture after the deadline you answer two short questions on paper, '
            'with no devices, about your own submission: a small change to your code (which test fails, and why) '
            'and one new fact (does your decision change?). It takes about 10 minutes. Both answers correct: your '
            'assignment mark stands. One correct: your mark is halved. Neither: a two-minute conversation with the '
            'instructor decides the mark. If you miss that lecture with an accepted excuse, the check is done in '
            'office hours. This applies the ownership rule on every assignment: your written work and your own '
            'explanation must agree.')
CHECK_AR = ('<b>التحقق في المحاضرة.</b> في المحاضرة التي تلي موعد التسليم تجيب على ورق، وبدون أي جهاز، عن سؤالين قصيرين '
            'حول واجبك أنت: تغيير صغير في الكود (أي اختبار سيفشل ولماذا)، ومعلومة جديدة (هل يتغير قرارك؟). يستغرق نحو '
            '10 دقائق. إذا كانت الإجابتان صحيحتين تبقى درجة الواجب كما هي، وإذا كانت إجابة واحدة صحيحة تصبح نصف الدرجة، '
            'وإذا لم تصح أي منهما تُحدَّد الدرجة بعد نقاش قصير مع الأستاذ مدته دقيقتان. ومن غاب عن تلك المحاضرة بعذر مقبول '
            'يُجري التحقق في الساعات المكتبية. هذا تطبيق لقاعدة الملكية الموجودة في كل واجب: يجب أن يتفق ما كتبته مع شرحك له.')

def rules_card() -> str:
    items = ''.join(f'<li><p><b>{ESC(a)}.</b> {ESC(b)}</p><p lang="ar" dir="rtl"><b>{ESC(c)}:</b> {ESC(d)}</p></li>'
                    for a, b, c, d in RULES)
    return ('<!-- ai-rules:start --><section class="card" id="ai-rules"><h2>AI rules and the in-class check</h2>'
            '<p lang="ar" dir="rtl"><b>قواعد الذكاء الاصطناعي والتحقق في المحاضرة</b></p>'
            '<ul class="ai-rules-list">' + items + '</ul>'
            f'<p>{CHECK_EN}</p><p lang="ar" dir="rtl">{CHECK_AR}</p></section><!-- ai-rules:end -->')

OWNERSHIP_OLD = ('<li><b>Ownership check.</b> Your instructor may ask you to explain your Part A and REFIT in a two-minute '
                 'conversation. Your written work and your explanation should agree. AI may help you practise; the reasoning '
                 'you submit must be your own.</li>')
OWNERSHIP_NEW = ('<li><b>AI rules and the in-class check.</b> Part A is written without AI. After the deadline, a 10-minute '
                 'paper check on your own submission decides whether your mark stands. Read '
                 '<a href="#ai-rules">the rules for each step</a> before you start.</li>')
BEFORE_END = 'it is not a secure examination system.</p></section>'
ROW_ANCHOR = '<tr data-row="their-change">'
ROW = ('<tr data-row="in-class-check"><th scope="row">IN-CLASS CHECK · required</th><td><b>Two questions on paper</b> in the '
       'lecture after the deadline, with no devices, about your own submission: a small change to your code and one new '
       'fact. <b>Both correct:</b> the mark stands. <b>One correct:</b> the mark is halved. <b>Neither:</b> a two-minute '
       'conversation with the instructor decides. This row adds no points. See <a href="#ai-rules">AI rules and the '
       'in-class check</a>.</td></tr>')
DECL_OLD = ('If AI was used, name the tool, what it helped with, and how you independently checked any calculation or '
            'engineering claim against the lecture, scenario and supplied evidence.')
DECL_NEW = ('If AI was used, name the tool and the steps where you used it (see the AI rules at the top of this page), '
            'what you changed because of it, and what you chose not to take, and why. Check any calculation or '
            'engineering claim against the lecture, scenario and supplied evidence.')


def once(text: str, old: str, new: str, ch: int, what: str) -> str:
    if new in text and (old not in text or old in new):
        return text  # already applied
    n = text.count(old)
    assert n == 1, f'Chapter {ch}: {what}: expected 1 occurrence, found {n}'
    return text.replace(old, new)


def update_plain_language() -> None:
    data = json.loads(PLAIN.read_text())
    for ch in CHAPTERS:
        d = data['chapters'][str(ch)]
        title, review = REVIEW[ch]
        d['review_title'] = title
        if review:
            d['review'] = review
        for field, old, new in PROMPTS[ch]:
            if old is None:
                if not d[field].endswith(new):
                    d[field] = d[field] + new
            else:
                d[field] = d[field].replace(old, new)
    PLAIN.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def patch(ch: int) -> None:
    path = ROOT / f'lectures/iscarb/Ch{ch}-FBR-Student-Assignment.html'
    text = path.read_text()
    d = json.loads(PLAIN.read_text())['chapters'][str(ch)]
    # Task format line
    old_fmt, new_fmt = FORMAT[ch]
    if old_fmt:
        text = once(text, f'<b>Task format:</b> {old_fmt}', f'<b>Task format:</b> {new_fmt}', ch, 'task format')
    else:
        h2 = '<h2>Assessed scenario · fictional teaching case</h2>'
        line = f'\n<p class="hint" data-format="ai-review-v1"><b>Task format:</b> {new_fmt} The same five criteria apply.</p>'
        text = once(text, h2, h2 + line, ch, 'task format insert')
    # Review paragraph inside the scenario (exports read scenarioText)
    title, review = REVIEW[ch]
    start = text.index('<div id="scenarioText">')
    end = text.index('</div>', start)
    scen = text[start:end]
    if '<p class="review-item">' in scen:
        head = scen.index('<p class="review-item"><b>') + len('<p class="review-item"><b>')
        tail = scen.index(':</b>', head)
        scen = scen[:head] + ESC(title) + scen[tail:]
    else:
        scen += '\n<p class="review-item"><b>' + ESC(title) + ':</b> “' + ESC(review) + '”</p>'
    text = text[:start] + scen + text[end:]
    # Prompts: hint paragraph and placeholder carry the same text
    fields = []
    for field, old, new in PROMPTS[ch]:
        if field != 'build_task' and field not in fields:
            fields.append(field)
    for field in fields:
        fid = FIELD_ID[field]
        full = before = d[field]
        for f, old, new in PROMPTS[ch]:
            if f == field:
                before = before[:-len(new)] if old is None else before.replace(new, old)
        text = once(text, f'<p id="{fid}Hint">{before}</p>', f'<p id="{fid}Hint">{full}</p>', ch, f'{field} hint')
        text = once(text, f'id="{fid}" placeholder="{before}"', f'id="{fid}" placeholder="{full}"', ch, f'{field} placeholder')
    for field, old, new in PROMPTS[ch]:
        if field == 'build_task':
            text = once(text, old, new, ch, f'{field} text')
    # The Chapter 15 starter code names the draft in a comment (also in builds.js and the starter source)
    text = text.replace("an evidence-only fit check for the colleague's draft.", 'an evidence-only fit check for the AI draft.')
    # AI rules card, in-class check, rubric row, declaration hint
    text = once(text, OWNERSHIP_OLD, OWNERSHIP_NEW, ch, 'before-you-start item')
    if '<!-- ai-rules:start -->' in text:
        a = text.index('<!-- ai-rules:start -->')
        b = text.index('<!-- ai-rules:end -->') + len('<!-- ai-rules:end -->')
        text = text[:a] + rules_card() + text[b:]
    else:
        text = once(text, BEFORE_END, BEFORE_END + rules_card(), ch, 'rules card')
    if 'data-row="in-class-check"' not in text:
        assert text.count(ROW_ANCHOR) == 1, ch
        at = text.index('</tr>', text.index(ROW_ANCHOR)) + len('</tr>')
        text = text[:at] + ROW + text[at:]
    text = once(text, DECL_OLD, DECL_NEW, ch, 'AI-use declaration hint')
    path.write_text(text)
    print('AI rules, AI draft and in-class check applied to Chapter', ch)


def update_starter() -> None:
    for rel in ('curriculum/learning-path/builds/ch15_starter.py', 'curriculum/learning-path/builds.js'):
        p = ROOT / rel
        t = p.read_text()
        p.write_text(t.replace("an evidence-only fit check for the colleague's draft.", 'an evidence-only fit check for the AI draft.'))


if __name__ == '__main__':
    update_plain_language()
    update_starter()
    for chapter in CHAPTERS:
        patch(chapter)
