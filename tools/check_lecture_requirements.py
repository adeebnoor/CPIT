"""Check every lecture against the lecture design requirements (curriculum/lecture-requirements/README.md).

Codes: KEEP-1..8, COV-1..6, LANG-1..6, CASE-1..5, TIME-1..6, RUB-1..6, COMMIT-1..3, REAL-1..3, GATE-1..5, BOUND-1..4.
MUST items fail the build; PREFERRED items print a warning; MANUAL items are listed for human review.
Writes docs/lecture-requirements-status.md (the per-lecture acceptance list) and exits 1 on any MUST failure.
Run:  python3 tools/check_lecture_requirements.py [--quiet]
"""
from __future__ import annotations
import json, re, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_lecture_requirements import BOUND_MARK
from lecture_requirements_lib import (ROOT, CHAPTERS, LECTURES, FORBIDDEN, MAX_WORDS, MAX_GRADE, NON_CONTENT, RUNTIME_PATH,
                                      common, load_lecture, load_ledger, load_story, student_texts, sentences, words,
                                      fk_grade, term_re, parse_range, strip_html, load_req, STORY_PATH)

LEVEL = {  # must | pref | manual
 'KEEP-1': 'must', 'KEEP-2': 'must', 'KEEP-3': 'manual', 'KEEP-4': 'must', 'KEEP-5': 'manual', 'KEEP-6': 'must', 'KEEP-7': 'must', 'KEEP-8': 'pref',
 'COV-1': 'must', 'COV-2': 'must', 'COV-3': 'must', 'COV-4': 'must', 'COV-5': 'must', 'COV-6': 'pref',
 'LANG-1': 'must', 'LANG-2': 'must', 'LANG-3': 'must', 'LANG-4': 'must', 'LANG-5': 'pref', 'LANG-6': 'pref',
 'CASE-1': 'must', 'CASE-2': 'must', 'CASE-3': 'must', 'CASE-4': 'must', 'CASE-5': 'must',
 'TIME-1': 'must', 'TIME-2': 'must', 'TIME-3': 'must', 'TIME-4': 'must', 'TIME-5': 'pref', 'TIME-6': 'pref',
 'RUB-1': 'must', 'RUB-2': 'must', 'RUB-3': 'manual', 'RUB-4': 'must', 'RUB-5': 'must', 'RUB-6': 'pref',
 'COMMIT-1': 'must', 'COMMIT-2': 'must', 'COMMIT-3': 'must',
 'REAL-1': 'must', 'REAL-2': 'must', 'REAL-3': 'manual',
 'GATE-1': 'must', 'GATE-2': 'must', 'GATE-3': 'must', 'GATE-4': 'must', 'GATE-5': 'must',
 'BOUND-1': 'must', 'BOUND-2': 'manual', 'BOUND-3': 'must', 'BOUND-4': 'must',
 'DATA-1': 'must',
}
TITLES = {
 'KEEP-1': 'Every content slide has title, 2–4 points, question with model answer, one-sentence takeaway, full explanation, source scope and instructor notes',
 'KEEP-2': 'Instructor notes name at least one common student error and how to handle it',
 'KEEP-3': 'One central case, shown at the start and used across the slides',
 'KEEP-4': 'An assumption-change slide: new information, and the student writes what the first decision got wrong',
 'KEEP-5': 'Questions ask for a judgment with evidence, not recall only',
 'KEEP-6': 'Course-added content is tagged as not from the source, adds at most two new terms, and ungraded parts are tagged',
 'KEEP-7': 'Original slides and textbook available; required readings numbered',
 'KEEP-8': 'Think → Pair → Record at think points, with a part without devices',
 'COV-1': 'Coverage map: every original slide is on a classroom slide, in the full explanation only, or not covered with a reason',
 'COV-2': 'Lists, classifications, tables and figures in the required readings appear in full on a classroom slide',
 'COV-3': '“What to study for the exam” names examinable content not on the slides, with source slide numbers and textbook pages',
 'COV-4': 'Key source figures in the required readings are shown on slides or linked directly',
 'COV-5': 'Coverage map available to the instructor; study list available to students',
 'COV-6': 'The build warns when a new original slide has no classification',
 'LANG-1': 'Student text in plain English; no sentence over 20 words',
 'LANG-2': 'Argument-framework terms appear in student text only when defined (glossary) at first use',
 'LANG-3': 'Every new chapter term is defined at first appearance, with a hover definition',
 'LANG-4': 'One question per ask; compound questions split',
 'LANG-5': 'Reading level of student text at or below grade 12 (Flesch–Kincaid)',
 'LANG-6': 'Chapter glossary with the Arabic equivalent',
 'CASE-1': 'One central case and at least one short transfer case whose correct answer differs',
 'CASE-2': 'No answer element is the correct answer to more than two questions; every question tagged with concept and answer element',
 'CASE-3': 'At least one think point applies to the transfer case',
 'CASE-4': 'At least one quiz question cannot be answered from the central case summary',
 'CASE-5': 'The synthetic case is tagged fictional',
 'TIME-1': 'Every slide and activity has an estimated duration in minutes',
 'TIME-2': 'Core durations total at most 85% of the lecture duration (course-level setting)',
 'TIME-3': 'Every slide is tagged core or optional; dropping optional slides keeps the sequence intact',
 'TIME-4': 'When over time, optional slides go first; think points and the assumption-change slide are never dropped (in instructor notes)',
 'TIME-5': 'Presenter display of planned versus actual time',
 'TIME-6': 'Actual duration recorded after each lecture',
 'RUB-1': 'Every open station question and every assignment has a rubric with 3–4 levels, named criteria and marks',
 'RUB-2': 'Each rubric has a strong and a weak example answer with the reason',
 'RUB-3': 'Criteria measure reasoning quality, not length or time',
 'RUB-4': 'Conditions for accepting other answers are written explicitly',
 'RUB-5': 'The student sees the assignment rubric before submitting',
 'RUB-6': 'One rubric template across all lectures',
 'COMMIT-1': 'The student’s own sentence appears beside the model answer (“You wrote: …”)',
 'COMMIT-2': 'No model answer before the student writes or explicitly skips; a skip shows “You did not write a decision”',
 'COMMIT-3': 'The sentence is saved on the device only and the commit step is absent in presenter mode',
 'REAL-1': 'One line on the cover separates the training story from the real incident',
 'REAL-2': 'Every story or incident mention carries a fixed tag (training story / real incident), checked against a case-kind field',
 'REAL-3': 'A real incident states its actual lesson and how it differs from the training story’s answer',
 'GATE-1': 'In self-study the chapter cannot be marked complete before the transfer question is answered',
 'GATE-2': 'The student writes a justification line before the answer is revealed',
 'GATE-3': 'A wrong answer shows an explanation and allows another try',
 'GATE-4': 'The progress bar shows “Transfer case not solved” until it is solved',
 'GATE-5': 'The gate is off in presenter mode',
 'BOUND-1': 'Each chapter ends with one sentence on when its mechanism is the wrong choice',
 'BOUND-2': 'That sentence names an observable condition',
 'BOUND-3': 'The student writes first; the model sentence is revealed after',
 'BOUND-4': 'The student’s sentence travels with the assignment and appears in its export',
 'DATA-1': 'No TODO placeholder in lecture data, authored requirements or coverage reasons; source lists on a slide are classified on-slide',
}
GROUP_ORDER = ['KEEP', 'COV', 'LANG', 'CASE', 'TIME', 'RUB', 'COMMIT', 'REAL', 'GATE', 'BOUND', 'DATA']


def load_real() -> dict:
    """Real incidents per story chapter: {chapter: {'lesson':..., 'differs':...}} parsed from story-v3.js."""
    s = STORY_PATH.read_text(encoding='utf-8')
    out, cur, inreal = {}, None, False
    for line in s.split('\n'):
        m = re.match(r'\s{4}(\d+): \{', line)
        if m:
            cur, inreal = int(m.group(1)), False
            continue
        if cur is not None and re.match(r'\s*real: \{', line):
            inreal = True; out[cur] = {}
            continue
        if inreal:
            for key, txt in re.findall(r"(lesson|differs): '((?:[^'\\]|\\.)*)'", line):
                out[cur][key] = txt
    return out


class Report:
    def __init__(self):
        self.rows: dict[int, dict[str, tuple[str, list[str]]]] = {}
        self.assignments: list[dict] = []
    def set(self, ch, code, ok, details=None):
        status = ('PASS' if ok else ('FAIL' if LEVEL[code] == 'must' else 'WARN')) if LEVEL[code] != 'manual' else 'MANUAL'
        self.rows.setdefault(ch, {})[code] = (status, details or [])


def content_slides(data):
    return [s for s in data['slides'] if s['id'] not in NON_CONTENT]


def all_questions(data):
    """Every question a student answers, with its concept/answerKey tags."""
    qs = []
    for s in data['slides']:
        if s['id'] in NON_CONTENT:
            continue
        if s.get('question'):
            qs.append((f"{s['id']}", s.get('concept'), s.get('answerKey'), s['question']))
        if s.get('question2'):
            qs.append((f"{s['id']}#2", s.get('concept2') or s.get('concept'), s.get('answerKey2'), s['question2']))
    for st in data.get('stations', []):
        qs.append((f"station{st['no']}", st.get('concept'), st.get('answerKey'), st.get('think', '')))
    for i, q in enumerate(data.get('quiz', [])):
        qs.append((f"quiz{i+1}", q.get('concept'), q.get('answerKey'), q.get('q', '')))
    tr = data.get('transfer') or {}
    if tr.get('question'):
        qs.append(('transfer', tr.get('concept'), tr.get('answerKey'), tr['question']))
    return qs


def check_chapter(ch: int, R: Report, story_all: dict, runtime: str, cfg: dict, figmap: dict, story_real: dict, hub_js: str):
    data, source, path = load_lecture(ch)
    ledger = load_ledger(ch)
    story = story_all.get(ch, []) if ch >= cfg.get('storyFirstChapter', 12) else []
    slides = data['slides']; ids = [s['id'] for s in slides]
    content = content_slides(data)
    texts = student_texts(data, story)
    minutes_total = int(data.get('lectureMinutes') or cfg['lectureMinutes'])

    # ---- KEEP ----
    bad = []
    for s in content:
        n = len(s.get('bullets') or [])
        if not (2 <= n <= 4) and not (s.get('rows') and len(s['rows']) >= 2):
            bad.append(f"{s['id']}: {n} points")
        for k in ('title', 'question', 'answer', 'takeaway', 'full', 'notes'):
            if not s.get(k):
                bad.append(f"{s['id']}: missing {k}")
        if not s.get('sourceRange') and not s.get('added'):
            bad.append(f"{s['id']}: missing sourceRange (or added tag)")
        if s.get('takeaway') and len(sentences(s['takeaway'])) > 1:
            bad.append(f"{s['id']}: takeaway is not one sentence")
    R.set(ch, 'KEEP-1', not bad, bad)
    bad = [f"{s['id']}" for s in content if words(s.get('commonError') or '') < 5]
    R.set(ch, 'KEEP-2', not bad, bad)
    R.set(ch, 'KEEP-3', True, ['Central case in D.case; story thread on each content slide (reviewed by the instructor)'])
    tw = [s for s in slides if s.get('twist')]
    bad = []
    if len(tw) != 1:
        bad.append(f'{len(tw)} slides flagged twist')
    else:
        st3 = next((x for x in data['stations'] if x.get('at') == tw[0]['id']), None)
        wrote = ((st3 or {}).get('write', '') + ' ' + tw[0].get('question', '')).lower()
        if 'first' not in wrote or 'wrong' not in wrote:
            bad.append('the assumption-change slide must ask what the first decision got wrong')
    R.set(ch, 'KEEP-4', not bad, bad)
    R.set(ch, 'KEEP-5', True, ['Questions reviewed by the instructor: each asks for a decision or a reason, with evidence'])
    bad = []
    added = [s for s in slides if s.get('added')]
    if not any(s['id'] == 'AISYS' for s in added) and any(s['id'] == 'AISYS' for s in slides):
        bad.append('AISYS (course addition) is not tagged added')
    new_terms = [g['term'] for g in data.get('glossary', []) if g.get('added')]
    if len(new_terms) > 2:
        bad.append(f'{len(new_terms)} new terms from added content: {new_terms}')
    if 'NOT ASSESSED' not in runtime.upper() or 'COURSE ADDITION' not in runtime:
        bad.append('runtime must label course additions and not-assessed parts')
    for s0 in added:
        if 'not from' not in (s0.get('sourceLabel') or '').lower() and 'course-added' not in (s0.get('sourceLabel') or '').lower():
            bad.append(f"{s0['id']}: course addition without a sourceLabel saying it is not from the textbook")
    R.set(ch, 'KEEP-6', not bad, bad)
    bad = []
    for key in ('original', 'textbook'):
        if data.get(key) and not (path.parent / data[key]).is_file():
            bad.append(f'missing {key}: {data[key]}')
    if not (ROOT / LECTURES[ch]['study_path']).is_file():
        bad.append('missing study ledger')
    for r in data.get('readings', []):
        a, b = parse_range(r.get('range'))
        if not (1 <= a <= b <= data['sourceCount']):
            bad.append(f"reading range invalid: {r}")
    R.set(ch, 'KEEP-7', not bad, bad)
    checks = [s for s in slides if s.get('phase') == 'CHECK' and s['id'] not in NON_CONTENT]
    ok8 = all(len(s.get('bullets') or []) >= 3 and [b[0].lower() for b in s['bullets'][:3]] == ['think', 'pair', 'record'] for s in checks) \
        and any('device' in (st.get('note') or '').lower() for st in data['stations'])
    R.set(ch, 'KEEP-8', ok8, [] if ok8 else ['checkpoints need Think/Pair/Record steps and a no-device note'])

    # ---- COV ----
    cov = {int(c['n']): c for c in data.get('coverage', [])}
    bad = []
    for L in ledger:
        c = cov.get(L['n'])
        if not c:
            bad.append(f"source slide {L['n']} not classified"); continue
        if c.get('cls') not in ('slide', 'full', 'no'):
            bad.append(f"source slide {L['n']}: class {c.get('cls')}")
        if c.get('cls') in ('slide', 'full') and c.get('unit') not in ids:
            bad.append(f"source slide {L['n']}: unit {c.get('unit')} not a classroom slide")
        if c.get('cls') == 'no' and words(c.get('reason') or '') < 3:
            bad.append(f"source slide {L['n']}: no reason")
    extra = sorted(set(cov) - {L['n'] for L in ledger})
    if extra:
        bad.append(f'classified but not in the ledger: {extra}')
    R.set(ch, 'COV-1', not bad, bad)
    R.set(ch, 'COV-6', not bad, [] if not bad else ['unclassified original slides (see COV-1)'])
    # COV-2: every reading-range source slide declares its kind; lists/tables must appear in full on a classroom slide
    bad = []
    lists_by_source = {}
    for s in slides:
        for L in s.get('lists') or []:
            lists_by_source.setdefault(int(L['source']), []).append((s['id'], L))
    for r in data.get('readings', []):
        a, b = parse_range(r.get('range'))
        for n in range(a, b + 1):
            c = cov.get(n) or {}
            kind = c.get('kind')
            if kind not in ('list', 'table', 'figure', 'prose', 'title'):
                bad.append(f'reading slide {n}: kind not declared (list/table/figure/prose/title)'); continue
            if kind in ('list', 'table'):
                want = c.get('items')
                if not want or len(want) < 2:
                    bad.append(f'reading slide {n}: declared {kind} without its source items'); continue
                got = lists_by_source.get(n) or []
                if not got:
                    bad.append(f'reading slide {n}: {kind} ({len(want)} items) is not on a classroom slide'); continue
                for sid, L in got:
                    if len(L.get('items', [])) != len(want):
                        bad.append(f'reading slide {n}: slide {sid} shows {len(L.get("items", []))} items, source has {len(want)}')
                    short = [it for it in L.get('items', []) if words(it) < 2]
                    if short:
                        bad.append(f'reading slide {n}: items reduced to one word on {sid}: {short}')
    R.set(ch, 'COV-2', not bad, bad)
    bad = []
    study = data.get('studyList') or []
    if not study:
        bad.append('studyList missing')
    for it in study:
        if words(it.get('topic', '')) < 2:
            bad.append(f'study item without topic: {it}')
        srcs = it.get('sources') or []
        if not srcs or any(not (1 <= int(n) <= data['sourceCount']) for n in srcs):
            bad.append(f"study item '{it.get('topic')}' has no valid source slide numbers")
        if data.get('textbook'):
            pg = (it.get('book') or {}).get('page')
            if not pg or not (1 <= int(pg) <= int(data.get('bookPages') or 0)):
                bad.append(f"study item '{it.get('topic')}' has no valid textbook page")
    study_html = (ROOT / LECTURES[ch]['study_path']).read_text(encoding='utf-8')
    for it in study:
        for n in it.get('sources') or []:
            if f'id="source-slide-{int(n)}"' not in study_html:
                bad.append(f'study link target missing: source-slide-{n}')
        pg = (it.get('book') or {}).get('page')
        if pg and f'id="book-page-{int(pg)}"' not in study_html:
            bad.append(f'study link target missing: book-page-{pg}')
    if 'studyList' not in runtime or "'STUDY'" not in runtime:
        bad.append('runtime does not render the study list')
    R.set(ch, 'COV-3', not bad, bad)
    # COV-4: figures in reading ranges
    bad = []
    shown = set()
    for s in slides:
        if s.get('figure') and s['figure'] in figmap:
            shown.update(figmap[s['figure']])
        for n in s.get('sourceFigs') or []:
            shown.add(int(n))
    for r in data.get('readings', []):
        a, b = parse_range(r.get('range'))
        for n in range(a, b + 1):
            if (cov.get(n) or {}).get('kind') == 'figure' and n not in shown:
                bad.append(f'figure on reading slide {n} is neither shown nor linked (sourceFigs)')
    if any(s0.get('sourceFigs') for s0 in slides) and 'figsBlock' not in runtime:
        bad.append('runtime does not render sourceFigs')
    R.set(ch, 'COV-4', not bad, bad)
    ok5 = 'coverageTable' in runtime and "'STUDY'" in runtime and 'What to study for the exam' in runtime
    R.set(ch, 'COV-5', ok5, [] if ok5 else ['runtime lacks the coverage table or the student study list'])

    # ---- LANG ----
    bad = []
    for loc, t in texts:
        for se in sentences(t):
            n = words(se)
            if n > MAX_WORDS:
                bad.append(f'{loc} ({n} words): {se[:90]}')
    R.set(ch, 'LANG-1', not bad, bad)
    gl = {g['term'].lower(): g for g in data.get('glossary', [])}
    bad = []
    for term in FORBIDDEN:
        hits = [loc for loc, t in texts if term_re(term).search(strip_html(t))]
        if hits and term not in gl:
            bad.append(f"'{term}' used in {len(hits)} places without a glossary definition (e.g. {hits[0]})")
    if 'firstUse' not in runtime or "className='gl'" not in runtime:
        bad.append('runtime does not define terms at first use')
    m_lab = re.search(r"const labels=\{(.*?)\};", runtime)
    for lab in re.findall(r":'([^']*)'", m_lab.group(1) if m_lab else ''):
        for term in FORBIDDEN:
            if term_re(term).search(lab) and term not in gl:
                bad.append(f"station field label uses '{term}' without a glossary definition: {lab}")
    R.set(ch, 'LANG-2', not bad, bad)
    bad = []
    if not gl:
        bad.append('glossary missing')
    for term, g in gl.items():
        if words(g.get('short') or '') < 2 or words(g.get('short') or '') > MAX_WORDS:
            bad.append(f"'{term}': short definition missing or too long")
        if not any(term_re(term).search(strip_html(t)) for _, t in texts):
            bad.append(f"'{term}' is in the glossary but never appears in student text")
    R.set(ch, 'LANG-3', not bad, bad)
    bad = []
    for qid, concept, key, q in all_questions(data):
        if strip_html(q).count('?') > 1:
            bad.append(f'{qid}: more than one question: {strip_html(q)[:80]}')
    for s in content:
        if re.search(r'\(1\)|\(2\)', s.get('question') or ''):
            bad.append(f"{s['id']}: numbered compound question")
    R.set(ch, 'LANG-4', not bad, bad)
    grade = fk_grade([t for _, t in texts])
    R.set(ch, 'LANG-5', grade <= MAX_GRADE, [f'Flesch–Kincaid grade {grade:.1f}'])
    bad = [g['term'] for g in data.get('glossary', []) if not (g.get('ar') or '').strip()]
    R.set(ch, 'LANG-6', not bad, bad)

    # ---- CASE ----
    tr = data.get('transfer') or {}
    bad = []
    for k in ('title', 'text', 'question', 'answer', 'concept', 'answerKey', 'at'):
        if not tr.get(k):
            bad.append(f'transfer.{k} missing')
    if tr and not (tr.get('fictional') or tr.get('source')):
        bad.append('transfer case must say whether it is fictional or name its source example')
    if tr.get('answerKey') and tr['answerKey'] == (data.get('case') or {}).get('answerKey'):
        bad.append('transfer answer element equals the central case answer element')
    if not (data.get('case') or {}).get('answerKey'):
        bad.append('case.answerKey missing')
    R.set(ch, 'CASE-1', not bad, bad)
    bad = []
    keys = Counter()
    for qid, concept, key, q in all_questions(data):
        if not concept or not key:
            bad.append(f'{qid}: missing concept/answerKey tag')
        else:
            keys[key.lower()] += 1
    rep = [f'{k} ×{n}' for k, n in keys.items() if n > 2]
    if rep:
        bad.append('answer element repeated in more than two questions: ' + ', '.join(rep))
    R.set(ch, 'CASE-2', not bad, bad)
    at = next((s for s in slides if s['id'] == tr.get('at')), None)
    ok3 = bool(at and at.get('transfer') and at.get('question') == tr.get('question') and at.get('answer') == tr.get('answer'))
    st_tr = [x for x in data.get('stations', []) if x.get('transfer')]
    vote_on_transfer = any(a.get('at') == tr.get('at') and a.get('id', '').startswith('VOTE') for a in data.get('activities') or [])
    if vote_on_transfer:
        v = tr.get('vote') or {}
        ok3 = ok3 and bool(v.get('q') and len(v.get('options') or []) >= 2 and isinstance(v.get('answer'), int)) and 'voteItem' in runtime
    ok3 = ok3 and len(st_tr) >= 1 and all(ids.index(x['at']) > ids.index(tr['at']) for x in st_tr) and 'station-transfer' in runtime
    R.set(ch, 'CASE-3', ok3, [] if ok3 else ['the transfer slide must carry the transfer question, and a later station must apply the transfer case as a step'])
    ok4 = any(q.get('beyondCase') for q in data.get('quiz', []))
    R.set(ch, 'CASE-4', ok4, [] if ok4 else ['no quiz item tagged beyondCase'])
    ok5 = bool((data.get('case') or {}).get('fictional')) and 'FICTIONAL TEACHING CASE' in runtime
    R.set(ch, 'CASE-5', ok5, [] if ok5 else ['case.fictional missing or runtime label missing'])

    # ---- TIME ----
    bad = []
    for s in slides:
        if not isinstance(s.get('minutes'), (int, float)) or s['minutes'] <= 0:
            bad.append(f"{s['id']}: minutes")
        if s.get('tier') not in ('core', 'optional'):
            bad.append(f"{s['id']}: tier")
    for st in data.get('stations', []):
        if not isinstance(st.get('minutes'), (int, float)) or st.get('tier') not in ('core', 'optional'):
            bad.append(f"station {st.get('no')}: minutes/tier")
        elif int(st.get('seconds') or 180) != round(st['minutes'] * 60):
            bad.append(f"station {st.get('no')}: timer {st.get('seconds') or 180} s does not match its {st['minutes']} min budget")
    for a in data.get('activities') or []:
        if not isinstance(a.get('minutes'), (int, float)) or a.get('tier') not in ('core', 'optional') or a.get('at') not in ids:
            bad.append(f"activity {a.get('id')}: minutes/tier/at")
        if a.get('id', '').startswith('VOTE') and ch < cfg.get('storyFirstChapter', 12):
            bad.append(f"activity {a.get('id')}: class votes appear only in story lectures (Chapter {cfg.get('storyFirstChapter', 12)} onwards)")
    R.set(ch, 'TIME-1', not bad, bad)
    core = sum(s.get('minutes') or 0 for s in slides if s.get('tier') == 'core')
    core += sum(st.get('minutes') or 0 for st in data.get('stations', []) if st.get('tier') == 'core')
    core += sum(a.get('minutes') or 0 for a in data.get('activities') or [] if a.get('tier') == 'core')
    budget = cfg['budgetShare'] * minutes_total
    R.set(ch, 'TIME-2', core <= budget + 1e-9, [f'core total {core:g} min of {minutes_total} ({budget:g} allowed)'])
    bad = []
    fixed = set(NON_CONTENT) | {s['id'] for s in slides if s.get('phase') == 'CHECK' or s.get('twist') or s.get('transfer')}
    fixed |= {st['at'] for st in data.get('stations', []) if st.get('tier') == 'core'}
    fixed |= {a['at'] for a in data.get('activities') or [] if a.get('tier') == 'core'}
    for s in slides:
        if s['id'] in fixed and s.get('tier') != 'core':
            bad.append(f"{s['id']} must be core (checkpoint, assumption change, transfer, or carries a core activity)")
    for b in (data.get('roadmap') or {}).get('branches', []):
        if not any(u in ids and next(x for x in slides if x['id'] == u).get('tier') == 'core' for u in b.get('units', [])):
            bad.append(f"act '{b.get('label')}' has no core slide")
    R.set(ch, 'TIME-3', not bad, bad)
    rule = (data.get('timeRule') or '').lower()
    ok4 = 'optional' in rule and 'think' in rule and 'never' in rule and 'timeRule' in runtime
    st_opt = [x['no'] for x in data.get('stations', []) if x.get('tier') != 'core']
    ok4 = ok4 and not st_opt and 'separate from slide minutes' in rule
    R.set(ch, 'TIME-4', ok4, [] if ok4 else [f'stations {st_opt} must be core (think points)'] if st_opt else ['timeRule must say optional slides go first and think points and the assumption-change slide are never dropped; runtime shows it in instructor notes'])
    R.set(ch, 'TIME-5', 'planned' in runtime and 'actual' in runtime and 'pace-chip' in runtime, [])
    R.set(ch, 'TIME-6', 'iscarb-pace-log' in runtime, [])

    # ---- RUB ----
    bad = []
    names_by_no = {}
    for st in data.get('stations', []):
        rb = st.get('rubric') or {}
        crit = rb.get('criteria') or []
        if len(crit) < 2:
            bad.append(f"station {st.get('no')}: fewer than two criteria")
        for c in crit:
            lv = c.get('levels') or []
            if not (3 <= len(lv) <= 4) or not c.get('name'):
                bad.append(f"station {st.get('no')}: criterion '{c.get('name')}' needs a name and 3–4 levels")
            for l in lv:
                if not (isinstance(l, list) and len(l) == 3 and isinstance(l[0], (int, float)) and l[1] and words(l[2]) >= 3):
                    bad.append(f"station {st.get('no')}: level must be [marks, label, description]")
        names_by_no.setdefault(st.get('no'), []).append(tuple(c.get('name') for c in crit))
    A = data.get('aiAssignment') or {}
    if A:
        ar = A.get('rubric') or {}
        crit = ar.get('criteria') if isinstance(ar, dict) else None
        if not crit or len(crit) < 2:
            bad.append('AI assignment: no rubric with named criteria')
        else:
            for c in crit:
                lv = c.get('levels') or []
                if not (3 <= len(lv) <= 4) or not all(isinstance(l, list) and len(l) == 3 and isinstance(l[0], (int, float)) for l in lv):
                    bad.append(f"AI assignment: criterion '{c.get('name')}' needs 3–4 levels with marks")
            if not ar.get('marks'):
                bad.append('AI assignment: rubric marks missing')
    R.set(ch, 'RUB-1', not bad, bad)
    bad = []
    for st in data.get('stations', []):
        rb = st.get('rubric') or {}
        for k in ('strong', 'weak'):
            ex = rb.get(k) or {}
            if words(ex.get('text') or '') < 8 or words(ex.get('why') or '') < 4:
                bad.append(f"station {st.get('no')}: {k} example needs text and why")
    ar = (data.get('aiAssignment') or {}).get('rubric') or {}
    if data.get('aiAssignment'):
        for k in ('strong', 'weak'):
            ex = ar.get(k) or {} if isinstance(ar, dict) else {}
            if words(ex.get('text') or '') < 8 or words(ex.get('why') or '') < 4:
                bad.append(f'AI assignment: {k} example needs text and why')
    R.set(ch, 'RUB-2', not bad, bad)
    R.set(ch, 'RUB-3', True, ['Criteria name reasoning moves (mechanism, limit, evidence, revision); no criterion counts words or time'])
    bad = [f"station {st.get('no')}" for st in data.get('stations', []) if words(((st.get('rubric') or {}).get('other') or '')) < 6]
    if data.get('aiAssignment') and words(((data['aiAssignment'].get('rubric') or {}).get('other') or '') if isinstance(data['aiAssignment'].get('rubric'), dict) else '') < 6:
        bad.append('AI assignment: other-answer conditions missing')
    R.set(ch, 'RUB-4', not bad, bad)
    ok_r5 = 'aixRubric(A,!locked)' in runtime and runtime.index('aixRubric(A,!locked)') < runtime.index("id=\"aix-commit\"")
    R.set(ch, 'RUB-5', ok_r5, [] if ok_r5 else ['AI assignment rubric is not shown before the commit step'])
    R.set(ch, 'RUB-6', True, [])

    # ---- COMMIT / REAL / GATE / BOUND (fourth review) ----
    need = lambda *xs: [f'runtime lacks {x}' for x in xs if x not in runtime]
    bad = need('function youWrote', 'You wrote:', 'you-wrote-slot', 'function fieldLabel', "'## '+fieldLabel(k)")
    R.set(ch, 'COMMIT-1', not bad, bad)
    bad = need('function commitReady', 'data-commit-for', 'function skipBtn', 'You did not write a decision', 'stationReady')
    R.set(ch, 'COMMIT-2', not bad, bad)
    bad = need('const COMMIT=!PRESENTER', "if(!COMMIT)return ''")
    if 'fetch(' in runtime[runtime.find('function commitBox'):runtime.find('function commitBox') + 600]:
        bad.append('the commit box must not send the sentence anywhere')
    R.set(ch, 'COMMIT-3', not bad, bad)
    bad = need('function kindLine', 'kind-line')
    R.set(ch, 'REAL-1', not bad, bad)
    bad = need('function kindTag', 'TRAINING STORY', 'REAL INCIDENT')
    if (data.get('case') or {}).get('kind') != 'training':
        bad.append("case.kind must be 'training'")
    if tr.get('kind') not in ('source', 'fictional'):
        bad.append("transfer.kind must be 'source' or 'fictional'")
    elif (tr['kind'] == 'source') != bool(tr.get('source')) and not (tr['kind'] == 'fictional' and tr.get('fictional')):
        bad.append('transfer.kind disagrees with transfer.source/fictional')
    R.set(ch, 'REAL-2', not bad, bad)
    real = story_real.get(ch)
    bad = []
    if real is not None:
        if words(real.get('lesson') or '') < 6:
            bad.append('real incident without its lesson')
        if words(real.get('differs') or '') < 6:
            bad.append('real incident without how it differs from the training story')
        if 'real-differs' not in runtime:
            bad.append('runtime does not show how the real incident differs')
    R.set(ch, 'REAL-3', not bad, bad or (['No real incident in this lecture'] if real is None else ['Lesson and difference sentences reviewed by the instructor']))
    chk = tr.get('check') or {}
    opts, why = chk.get('options') or [], chk.get('why') or []
    bad = []
    if len(opts) < 2 or len(why) != len(opts) or not isinstance(chk.get('answer'), int) or not (0 <= chk['answer'] < len(opts)):
        bad.append('transfer.check needs options, an answer index and one explanation per option')
    bad += need('function gateOn', 'function gateSolved', 'gate_solved')
    if 'gate_solved' not in hub_js or 'Solve the transfer case' not in hub_js or 'check.checked=solved&&marked' not in hub_js or "addEventListener('storage'" not in hub_js:
        bad.append('the hub must count a chapter only when its transfer case is solved (earlier marks included) and re-check when lecture progress changes')
    R.set(ch, 'GATE-1', not bad, bad)
    bad = need('data-gate-line', 'gate_line')
    R.set(ch, 'GATE-2', not bad, bad)
    bad = [f'transfer.check why[{i}] too short' for i, w in enumerate(why) if words(w) < 4] + need('gate_tries', 'you can try again', 'Try another option')
    R.set(ch, 'GATE-3', not bad, bad)
    bad = need('Transfer case not solved')
    R.set(ch, 'GATE-4', not bad, bad)
    bad = need('return !PRESENTER&&!!D.transfer?.check')
    R.set(ch, 'GATE-5', not bad, bad)
    B = data.get('bound') or {}
    bad = []
    if not B.get('model') or len(sentences(B['model'])) != 1:
        bad.append('bound.model must be one sentence')
    if not re.search(r'\bwrong\b', B.get('model') or '') or not re.search(r'\bwhen(ever)?\b', B.get('model') or ''):
        bad.append("bound.model must say when the mechanism is the wrong choice")
    bad += need('function boundBlock', 'boundBlock()')
    R.set(ch, 'BOUND-1', not bad, bad)
    R.set(ch, 'BOUND-2', bool(B.get('condition')), [f"Observable condition: {B.get('condition') or 'missing'}"])
    bad = need("data-bound-reveal data-commit-for=", 'bound-answer" hidden')
    R.set(ch, 'BOUND-3', not bad, bad)
    R.set(ch, 'BOUND-4', True, [] if ch >= cfg.get('assignmentRubricFromChapter', 12) else ['Assignments 1–2 (Chapters 10–11) are frozen; the boundary sentence is saved in the lecture only'])
    # DATA-1: placeholders never ship; a source list shown on a slide is classified on-slide at that slide
    bad = []
    if 'TODO' in json.dumps(data) or 'TODO' in json.dumps(load_req(ch) or {}):
        bad.append('TODO placeholder in lecture data or authored requirements')
    for s0 in slides:
        for L in s0.get('lists') or []:
            c = cov.get(int(L['source'])) or {}
            if c.get('cls') != 'slide':
                bad.append(f"source slide {L['source']}: list shown on {s0['id']} but classified '{c.get('cls')}'")
            elif c.get('unit') != s0['id'] and not any(int(L2['source']) == int(L['source']) for s1 in slides if s1['id'] == c.get('unit') for L2 in s1.get('lists') or []):
                bad.append(f"source slide {L['source']}: list shown on {s0['id']} but classified at {c.get('unit')}")
    R.set(ch, 'DATA-1', not bad, bad)
    return names_by_no


def check_assignments(R: Report, cfg: dict):
    """RUB-1/2/4/5 on the assessed assignment pages (Assignments 3–9)."""
    for a in __import__('lecture_requirements_lib').PUB['assignments']:
        ch = int(a['chapter'])
        p = ROOT / a['path']
        s = p.read_text(encoding='utf-8')
        rt = s[s.find('id="rubric-heading"'):]
        rt = rt[:rt.find('</table>')]
        names = [x for x in re.findall(r'<th scope="row">([^<]+)</th>', rt) if not x.startswith(('TESTS RUN', 'THEIR CHANGE'))]
        tot = re.search(r'How your work is assessed · ([\d.]+) points', s)
        ex = s[s.find('id="rubricExamples"'):] if 'id="rubricExamples"' in s else ''
        ci = s.find('id="commitBtn"') if 'id="commitBtn"' in s else s.find('Review &amp; commit')
        R.assignments.append({'no': len(R.assignments) + 1, 'chapter': ch, 'criteria': len(names), 'points': tot.group(1) if tot else '?',
                              'levels': all(all(f'<b>{l}</b>' in rt[rt.find(n):][:rt[rt.find(n):].find('</tr>')] for l in ('1:', '0.75:', '0.5:', '0:')) for n in names) and '<details class="levels">' not in rt,
                              'before': 0 <= s.find('id="rubric-heading"') < ci, 'examples': ex.count('data-criterion='), 'other': 'Other answers are accepted when' in ex,
                              'bound': BOUND_MARK in s, 'frozen': ch < cfg.get('assignmentRubricFromChapter', 12),
                              'tests': 'data-row="tests-run"' in rt, 'coverage': 'id="coverageNote"' in s and 'must show Run 2 or later' in s,
                              'hour': '<!-- practical-hour:start -->' in s, 'their': 'id="theirStep"' in s})
        if ch < cfg.get('assignmentRubricFromChapter', 12):
            continue
        bad1, bad2, bad4, bad5 = [], [], [], []
        crit = [x for x in re.findall(r'<th scope="row">([^<]+)</th>', s[s.find('id="rubric-heading"'):]) if not x.startswith(('TESTS RUN', 'THEIR CHANGE'))]
        if 'id="rubric-heading"' not in s or len(crit) < 3:
            bad1.append('rubric table missing')
        if 'Partial credit' not in s:
            bad1.append('rubric levels (partial credit) missing')
        table = s[s.find('id="rubric-heading"'):]
        table = table[:table.find('</table>')]
        for c in [x for x in re.findall(r'<th scope="row">([^<]+)</th>', table) if not x.startswith(('TESTS RUN', 'THEIR CHANGE'))]:
            row = table[table.find(f'<th scope="row">{c}</th>'):]
            row = row[:row.find('</tr>')]
            got = [l for l in ('1:', '0.75:', '0.5:', '0:') if f'<b>{l}</b>' in row]
            if len(got) != 4:
                bad1.append(f'{c}: levels {got} (need 1 · 0.75 · 0.5 · 0 with descriptions)')
        if '<details class="levels">' in table:
            bad5.append('partial-credit levels are folded closed; the student must see every level before submitting')
        total = re.search(r'How your work is assessed · ([\d.]+) points', s)
        pts = [float(x) for x in re.findall(r'· ([\d.]+) points?</th>', table)]
        if not total or abs(sum(pts) - float(total.group(1))) > 1e-9:
            bad1.append(f'criterion points {pts} do not add up to the stated total')
        if 'id="rubricExamples"' not in s:
            bad2.append('rubricExamples block missing')
        else:
            block = s[s.find('id="rubricExamples"'):]
            block = block[:block.find('</details>')]
            for c in crit:
                name = c.split(' ·')[0].strip()
                if f'data-criterion="{name}"' not in block:
                    bad2.append(f'no strong/weak example for {name}')
            if 'Strong' not in block or 'Weak' not in block:
                bad2.append('examples must be labelled strong and weak')
            if 'Other answers' not in block:
                bad4.append('acceptance conditions for other answers missing')
        ri, ci = s.find('id="rubric-heading"'), s.find('id="commitBtn"')
        if ci < 0:
            ci = s.find('Review &amp; commit')
        if not (0 <= ri < ci):
            bad5.append('rubric must appear before the commit control')
        hour = []
        if '<!-- practical-hour:start -->' not in s or 'not submitted without it' not in s or 'تشغيل الاختبارات صف مستقل في السلّم' not in s or 'outcome 11' not in s:
            hour.append('the practical-hour line (English and Arabic, with the course outcomes) is missing at the top')
        if 'data-row="tests-run"' not in table or 'longer writing does not make up for a missing run' not in table:
            hour.append('the rubric has no separate TESTS RUN row')
        if '"labEvidence", "coverageNote"' not in s or 'id="coverageNote"' not in s or 'must show Run 2 or later' not in s or 'TESTS RUN: required' not in s:
            hour.append('the coverage step (second run, coverage sentence in Part A and the export) is missing')
        their = 'id="theirStep"' in s and 'data-row="their-change"' in table and 'THEIR-CHANGE: run 3' in s and '"theirFacts"],M=' in s
        if ch in (15, 16, 17, 20) and not their:
            hour.append('run 3 (their change), its questions, the THEIR CHANGE row or the export verdict is missing')
        if ch not in (15, 16, 17, 20) and 'id="theirStep"' in s:
            hour.append('run 3 belongs only to Chapters 15, 16, 17 and 20')
        bad1 += hour
        bad_b4 = [] if (BOUND_MARK in s and "lines.push('## Chapter boundary sentence" in s and 'id="bound"' in s) else ['the lecture boundary sentence is not carried into the assignment export']
        for code, bad in (('RUB-1', bad1), ('RUB-2', bad2), ('RUB-4', bad4), ('RUB-5', bad5), ('BOUND-4', bad_b4)):
            st, det = R.rows[ch][code]
            if bad:
                R.rows[ch][code] = ('FAIL', det + [f'assignment page: {b}' for b in bad])


def check_site() -> list[str]:
    """Lab credit 0 is stated under the grade tables; no public page says the lab was cancelled or Code Coverage is missing."""
    bad = []
    for rel in ('student-guide.html', 'assignment-example.html'):
        t = (ROOT / rel).read_text(encoding='utf-8')
        if '<!-- lab-credit:start -->' not in t or 'Lab credit is 0.' not in t or 'رصيد المعمل صفر' not in t:
            bad.append(f'{rel}: the lab-credit sentence (English and Arabic) is missing under the grade table')
    pages = [p for p in ROOT.glob('*.html')] + [p for p in (ROOT / 'lectures/iscarb').glob('*.html')]
    for p in pages:
        t = p.read_text(encoding='utf-8')
        if re.search(r'\blabs?\b[^.<]{0,40}cancel|cancel\w*[^.<]{0,40}\blabs?\b|not on this site yet|Code Coverage[^.<]{0,80}(gap|incomplete|not here)', t, re.I):
            bad.append(f'{p.relative_to(ROOT)}: says the lab was cancelled or Code Coverage is missing')
    return bad


def write_status(R: Report, grade_note: str) -> None:
    out = ['# Lecture design requirements · status', '', f'Generated by `tools/check_lecture_requirements.py`. {grade_note}', '',
           'Levels: **must** fails the release; **pref** warns; **manual** is reviewed by the instructor and recorded here.', '']
    codes = [c for g in GROUP_ORDER for c in LEVEL if c.startswith(g + '-')]
    out.append('| Code | Requirement | Level | ' + ' | '.join(f'Ch{ch}' for ch in sorted(R.rows)) + ' |')
    out.append('|---|---|---|' + '---|' * len(R.rows))
    for c in codes:
        cells = [R.rows[ch].get(c, ('—', []))[0] for ch in sorted(R.rows)]
        out.append(f'| {c} | {TITLES[c]} | {LEVEL[c]} | ' + ' | '.join(cells) + ' |')
    out += ['', '## Assessed assignment pages', '',
            'Static check of every assessed page; the browser audit (`tools/check-assignment-pages.cjs`, results in `test-results/assignments/audit.json`) repeats it on the rendered pages at 1366 and 390 px.', '',
            '| Assignment | Chapter | Criteria | Points | All levels visible (1 · 0.75 · 0.5 · 0) | Rubric before commit | Strong/weak examples | Other answers | Boundary sentence in export | Practical-hour line | TESTS RUN row | Coverage step | Run 3 · their change |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    yn = lambda b: 'yes' if b else 'no'
    for a in R.assignments:
        fz = ' (frozen)' if a['frozen'] else ''
        out.append(f"| A{a['no']}{fz} | {a['chapter']} | {a['criteria']} | {a['points']} | {yn(a['levels'])} | {yn(a['before'])} | "
                   f"{a['examples'] or ('—' if a['frozen'] else 'no')} | {yn(a['other']) if not a['frozen'] else '—'} | {yn(a['bound']) if not a['frozen'] else 'lecture only'} | "
                   f"{yn(a['hour']) if not a['frozen'] else '—'} | {yn(a['tests']) if not a['frozen'] else '—'} | {yn(a['coverage']) if not a['frozen'] else '—'} | {yn(a['their']) if a['chapter'] in (15, 16, 17, 20) else '—'} |")
    out += ['', 'Assignments 1–2 were published and submitted before the review; they are kept unchanged.', '', '## Acceptance list per lecture', '']
    for ch in sorted(R.rows):
        fails = [f'{c}: {"; ".join(d[:3])}' for c, (st, d) in R.rows[ch].items() if st == 'FAIL']
        warns = [f'{c}: {"; ".join(d[:3])}' for c, (st, d) in R.rows[ch].items() if st == 'WARN']
        out.append(f'### Chapter {ch}: ' + ('accepted' if not fails else f'{len(fails)} mandatory item(s) open'))
        for c, (st, d) in R.rows[ch].items():
            mark = '[x]' if st in ('PASS', 'MANUAL') else '[ ]'
            note = f' — {d[0]}' if d and st in ('MANUAL', 'WARN', 'FAIL') else ''
            out.append(f'- {mark} {c} ({st}){note}')
        out.append('')
    (ROOT / 'docs/lecture-requirements-status.md').write_text('\n'.join(out) + '\n', encoding='utf-8')


def run(quiet: bool = False) -> list[str]:
    cfg = common()
    R = Report()
    story_all = load_story()
    story_real = load_real()
    hub_js = (ROOT / 'iscarb-hub.js').read_text(encoding='utf-8')
    runtime = RUNTIME_PATH.read_text(encoding='utf-8')
    figsrc = (ROOT / 'lectures/iscarb/runtime/source-figures.js').read_text(encoding='utf-8')
    figjson = json.loads(figsrc[figsrc.index('{'):figsrc.rindex('}') + 1])
    figmap = {k: {int(v['sourceSlide']) for v in e['variants'] if v.get('sourceSlide')} for k, e in figjson.items()}
    templates = {}
    for ch in CHAPTERS:
        names = check_chapter(ch, R, story_all, runtime, cfg, figmap, story_real, hub_js)
        for no, lst in names.items():
            templates.setdefault(no, set()).update(lst)
    check_assignments(R, cfg)
    for ch in CHAPTERS:  # RUB-6: one template across lectures
        uniform = all(len(v) == 1 for v in templates.values())
        R.set(ch, 'RUB-6', uniform, [] if uniform else [f'station criteria differ across lectures: {templates}'])
    errors = []
    for ch in sorted(R.rows):
        for code, (st, det) in R.rows[ch].items():
            if st == 'FAIL':
                errors.append(f'Chapter {ch} {code}: ' + ('; '.join(det[:4]) if det else 'failed'))
            if st == 'WARN' and not quiet:
                print(f'WARN Chapter {ch} {code}: ' + '; '.join(det[:3]))
    errors += ['Site: ' + b for b in check_site()]
    write_status(R, f'{len(errors)} mandatory failure(s).')
    if not quiet:
        for e in errors:
            print('FAIL', e)
        print(f'Lecture requirements: {len(errors)} mandatory failure(s) across {len(CHAPTERS)} lectures.')
    return errors


if __name__ == '__main__':
    sys.exit(1 if run('--quiet' in sys.argv) else 0)
