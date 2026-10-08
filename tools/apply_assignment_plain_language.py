"""Apply the instructor's language-only revision to Assignments 4–9.

Run after the other assignment content builders. The authored wording lives in
curriculum/learning-path/plain-language.json. This does not change storage keys,
assessment versions, fields, scoring, Python code, tests, or commitment behavior.
Then run the normal package/hash refresh with a documented content revision.
"""
from pathlib import Path
import html
import json
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'curriculum/learning-path/plain-language.json').read_text())
ESC = html.escape
WORKFLOW = [
    ('FIT', 'What problem matters, and why?', 'ما المشكلة المهمة؟ ولماذا؟'),
    ('BOUND', 'When does your recommendation apply? What would make you review it?', 'متى يصلح قرارك؟ وما الذي يستدعي مراجعته؟'),
    ('ACT + EVIDENCE', 'What will you do, who is responsible, and what supports it?', 'ما الإجراء؟ ومن المسؤول؟ وما الدليل؟'),
    ('STRESS', 'New information shown after you lock Part A.', 'معلومات جديدة تظهر بعد تثبيت الجزء A.'),
    ('REFIT', 'Review your decision using the new information.', 'راجع قرارك في ضوء المعلومات الجديدة.'),
    ('RETAIN / REVISE / REPLACE', 'Keep the decision / adjust it / choose a different decision.', 'أبقِ القرار / عدّله / استبدله بقرار آخر.'),
    ('Fact / assumption / proposed', 'Given evidence / something you assume / something you suggest doing or testing.', 'حقيقة معطاة / افتراض يحتاج تحققًا / إجراء أو اختبار تقترحه.'),
    ('Artifact', 'The work you produce: for example a test plan, comparison or set of rules.', 'المخرج الذي تعدّه، مثل خطة اختبار أو مقارنة أو مجموعة قواعد.'),
    ('Transfer answer', 'Apply a second chapter idea to the question, using your own explanation.', 'طبّق فكرة ثانية من الفصل على السؤال، واشرحها بأسلوبك.'),
    ('Mutation test / micro-viva', 'Your tests try code with known bugs / a short discussion where you explain and change your code.', 'اختباراتك تكشف أخطاء مقصودة في الكود / مناقشة قصيرة تشرح فيها كودك وتعدله.')
]
LABELS = {
    'fit': 'What is the main problem? · FIT',
    'measure': 'Write the technical part of your answer.',
    'bound': 'When does your recommendation apply? · BOUND',
    'act': 'What should happen next? · ACT',
    'evidence': 'What supports your decision, and what still needs checking? · EVIDENCE',
    'sourceUse': 'Which idea from the assigned reading helps your answer?',
    'technical': 'Use another idea from this chapter.'
}
PART_B = {
    'Reassess the claim against the evidence and original boundary.': 'Check your decision against the new information and the conditions you set in Part A.',
    'Does your original engineering claim still fit?': 'Does your original decision still fit the new information? · REFIT',
    'Compare the new evidence with the boundary you committed. Do not change your answer merely because new information appeared.': 'Compare the new information with the conditions you recorded in Part A. You may keep your decision if you can explain why it still holds.',
    'What happened to your original boundary?': 'Do the conditions you set still hold?',
    'INTACT · condition still holds': 'INTACT · the conditions still hold',
    'UNDER PRESSURE · evidence or margin is weaker': 'UNDER PRESSURE · the support for your decision is weaker',
    'CROSSED · condition failed': 'CROSSED · a condition no longer holds',
    'value="RETAIN">RETAIN</label>': 'value="RETAIN">RETAIN · keep my decision</label>',
    'value="REVISE">REVISE</label>': 'value="REVISE">REVISE · adjust my decision</label>',
    'value="REPLACE">REPLACE</label>': 'value="REPLACE">REPLACE · choose a different decision</label>',
    'State the final action, artifact/requirement, applicable conditions, evidence required, mechanism, owner/reviewer and remaining uncertainty.': 'State the final action and the technical work or rule it needs. Include when it applies, the evidence still needed, how it works, who is responsible or reviews it, and what is still uncertain.',
    'What STRESS changes…': 'What the new information changes…',
    'Why RETAIN / REVISE / REPLACE…': 'Why I keep, adjust or replace my decision…'
}

def replace_section(text, field, update):
    """Change only the section containing a known field, preserving all scripts."""
    for m in re.finditer(r'<section\b[^>]*>.*?</section>', text, re.S):
        s = BeautifulSoup(m.group(0), 'html.parser')
        if s.find(id=field):
            update(s)
            return text[:m.start()] + str(s) + text[m.end():]
    raise ValueError(f'Missing field section: {field}')

def glossary(terms):
    return '<dl>' + ''.join(
        f'<dt><b>{ESC(term)}</b></dt><dd>{ESC(en)}<br/><span lang="ar" dir="rtl">{ESC(ar)}</span></dd>'
        for term, en, ar in terms) + '</dl>'

def patch(ch, d):
    path = ROOT / f'lectures/iscarb/Ch{ch}-FBR-Student-Assignment.html'
    text = path.read_text()
    def warmup(s):
        sec = s.find(id='assignment-learning-path')
        sec.h2.string = d['warmup'][0]
        sec.select_one('.warmup-answer p').string = d['warmup'][1]
    text = replace_section(text, 'assignment-learning-path', warmup)
    # Keep whitespace between blocks: exports read scenarioText.textContent.
    scenario = '<p>' + ESC(d['scenario'][0]) + '</p>\n<ul>\n' + '\n'.join('<li>' + ESC(p) + '</li>' for p in d['scenario'][1:-1]) + '\n</ul>\n<p>' + ESC(d['scenario'][-1]) + '</p>'
    if d.get('review'):
        scenario += '\n<p class="review-item"><b>' + ESC(d['review_title']) + ':</b> “' + ESC(d['review']) + '”</p>'
    text, count = re.subn(r'(<div id="scenarioText">).*?(</div>)', lambda m: m[1] + scenario + m[2], text, count=1, flags=re.S)
    assert count == 1, ch
    # The glossary explains terms, not how to solve this case. Scenario exports remain facts only.
    text = re.sub(r'<details\b[^>]*id="plain-language-help".*?</details><!--/plain-language-help-->', '', text, flags=re.S)
    help_html = '<details class="card" id="plain-language-help"><summary><b>Quick word help · معاني المصطلحات</b></summary><p lang="ar" dir="rtl">شرح مختصر للكلمات المستخدمة في هذا الواجب. ارجع إليه أثناء الحل.</p><h3>Words in this case</h3>' + glossary(d['terms']) + '<h3>Words used in every assignment</h3>' + glossary(WORKFLOW) + '</details><!--/plain-language-help-->'
    marker = re.search(r'<section\b[^>]*id="assessed-scenario".*?</section>', text, re.S)
    assert marker
    text = text[:marker.end()] + help_html + text[marker.end():]

    prompts = {k:d[k] for k in ('fit','measure','bound','act','technical')}
    prompts['evidence'] = 'Name the test, activity record or review that supports your decision. State the conditions it covers, who checks it, and what evidence is missing. Clearly separate results already available from checks you are only proposing.'
    prompts['sourceUse'] = 'Give a slide number from the assigned reading. Explain its idea in your own words, then point to the part of your answer it supports or challenges. A slide number alone is not enough.'
    for field, prompt in prompts.items():
        def update(s, field=field, prompt=prompt):
            el = s.find(id=field)
            hint = s.find(id=field+'Hint')
            if hint is None:
                hint = el.find_previous_sibling('p')
            assert hint and hint.name == 'p', (ch,field)
            hint.clear(); hint.append(prompt)
            el['placeholder'] = prompt if field not in ('sourceUse','technical') else ('Slide number — idea — how it supports or challenges my answer…' if field=='sourceUse' else 'Two focused sentences or clear notation…')
            label = s.find('label', attrs={'for':field}); assert label
            label.clear(); label.append(LABELS[field])
        text = replace_section(text, field, update)

    def build(s):
        sec = s.find(id='practical'); sec.h2.string = d['build_title']
        sec.h2.find_next_sibling('p').string = d['build_task']
        reading = next(p for p in sec.find_all('p') if 'Primary source' in p.get_text())
        src = str(reading)
        src = re.sub(r'Read it for .*? Use the answer in your build plan\.', lambda _: ESC(d['reading']) + ' Use the answer in your build plan.', src, flags=re.S)
        reading.replace_with(BeautifulSoup(src,'html.parser'))
        viva = next(p for p in sec.find_all('p') if 'micro-viva change request' in p.get_text() or 'short discussion (micro-viva)' in p.get_text())
        viva.clear(); viva.append('Your tests also run against versions of the code with known bugs. Each bug must make at least one of your tests fail. This is called mutation testing. Your build record gives you a small code change to explain in a short discussion (micro-viva), selected using your Student ID. Be ready to make it and explain which tests change and why.')
        sec.find(id='labPrediction')['placeholder'] = 'My plan, the normal and unusual inputs I will test, and a case that must be refused or handled safely…'
    text = replace_section(text, 'practical', build)
    # Clarify wording in the rubric without changing the scores or requirements.
    def rubric(s):
        replacements = {
            'chapter-specific problem': 'problem using the chapter ideas',
            'short transfer answer': 'short answer applying a second chapter idea',
            'FIT and transfer together': 'FIT and that answer together',
            'positive and one negative authorization test': 'test of allowed access and one test of access that must be refused',
            'actor, input, observable expected result': 'user, input, expected result that you can check',
            'named required source concept to the artifact': 'idea from the assigned reading to your technical work',
            'operating assumptions, scope and an observable trigger to reconsider the claim': 'assumptions, the situations covered, and a result you can observe that would make you review the decision',
            'feasible bounded action, named responsibility and inspectable evidence': 'workable action with clear limits, who is responsible, and evidence someone else can check',
            'completed from proposed verification': 'checks already completed from checks you plan to do',
            'coherent final record': 'consistent final answer',
            'micro-viva change': 'code change for the short discussion (micro-viva)',
        }
        for node in list(s.find_all(string=True)):
            value = str(node)
            for old, new in replacements.items(): value = value.replace(old, new)
            if value != str(node): node.replace_with(value)
    text = replace_section(text, 'rubric-heading', rubric)
    # Visible wording only inside the existing Part B template. Radio values and validation stay intact.
    start = text.index('function buildB(r)')
    end = text.index('async function reveal()', start)
    fragment = text[start:end]
    for old,new in PART_B.items(): fragment = fragment.replace(old,new)
    text = text[:start] + fragment + text[end:]
    path.write_text(text)
    payload_path = ROOT / f'lectures/iscarb/reveal/r{ch}-mastery-v2.json'
    payload = json.loads(payload_path.read_text())
    assert set(payload) == {'chapter','version','label','text'}
    payload['text'] = d['stress']
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    print('Plain language applied to Chapter',ch)

def patch_gateway():
    path = ROOT / 'fbr-submission.html'
    text = path.read_text()
    match = re.search(r'Object.assign\(CONFIG,(\{.*?\})\);', text)
    assert match
    live = json.loads(match[1])
    source_path = ROOT / 'curriculum/learning-path/gateway.json'
    source = json.loads(source_path.read_text())
    titles = {'13':'Test who may open a file', '14':'Keep an essential service working during an outage', '15':'Compare existing software before choosing', '16':'Check the rules before and after a function call', '17':'Handle a lost reply without making two bookings', '20':'Connect systems run by different teams'}
    for ch in DATA['chapters']:
        wording = {
            'title': titles[ch],
            'intro': 'Use the chapter ideas to explain the case and make a decision. Complete the Python code and tests, and use the results in your answer. The assignment includes short word explanations in English and Arabic.',
            'steps': ['Read the assigned pages and try all five preparation questions.', 'Explain your decision, apply an idea from the reading, and answer the question about a second chapter idea. Complete and test your Python build.', 'Save and lock Part A. Read the new information (STRESS), then explain whether you keep, adjust or replace your decision.', 'Review your work, declare any AI use, export a PDF and submit it in Blackboard. Revise after feedback when asked.'],
            'note': 'The language is simpler; the reasoning, code, tests and marks are unchanged. Tell us how long the work actually took. Your existing drafts and completed work are kept.',
            'ack': 'I will prepare, write my own first decision, and explain how the evidence supports or changes it.',
            'commit': 'All Part A answers and the build record are saved and locked. The new information (STRESS) then opens automatically on this page. You can still write Part B. The page checks that the required work is present; the instructor assesses your understanding.'
        }
        live[ch].update(wording)
        source[ch].update(wording)
    text = text[:match.start(1)] + json.dumps(live, ensure_ascii=False) + text[match.end(1):]
    path.write_text(text)
    source_path.write_text(json.dumps(source, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    for chapter,content in DATA['chapters'].items(): patch(int(chapter),content)
    patch_gateway()
