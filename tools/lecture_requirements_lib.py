"""Shared helpers for the lecture design requirements (curriculum/lecture-requirements/README.md).

Reads the pinned lecture data, the original source ledger, the story runtime and the authored requirement
files, and defines what counts as student-facing text for the language checks.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_DIR = ROOT / 'curriculum/lecture-requirements'
PUB = json.loads((ROOT / 'curriculum/publication.json').read_text(encoding='utf-8'))
LECTURES = {int(x['chapter']): x for x in PUB['lectures']}
CHAPTERS = sorted(LECTURES)
DATA_RE = re.compile(r'(<script id="lecture-data" type="application/json">)([\s\S]*?)(</script>)')
STORY_PATH = ROOT / 'lectures/iscarb/runtime/story-v3.js'
RUNTIME_PATH = ROOT / 'lectures/iscarb/runtime/classroom-v3.js'

# LANG-2: argument-framework terms that may appear in student text only when the chapter glossary defines them.
FORBIDDEN = ['claim', 'warrant', 'bounded', 'acceptance check', 'contract assumption', 'denominator']
MAX_WORDS = 20          # LANG-1
MAX_GRADE = 12.0        # LANG-5 (preferred)
NON_CONTENT = ('TITLE', 'MAP', 'START', 'END')


def common() -> dict:
    return json.loads((REQ_DIR / 'common.json').read_text(encoding='utf-8'))


def req_path(ch: int) -> Path:
    return REQ_DIR / f'ch{ch}.json'


def load_req(ch: int) -> dict | None:
    p = req_path(ch)
    return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else None


def lecture_path(ch: int) -> Path:
    return ROOT / LECTURES[ch]['path']


def load_lecture(ch: int) -> tuple[dict, str, Path]:
    p = lecture_path(ch)
    s = p.read_text(encoding='utf-8')
    m = DATA_RE.search(s)
    if not m:
        raise ValueError(f'lecture-data missing in {p}')
    return json.loads(m.group(2)), s, p


def dump_lecture(data: dict, source: str) -> str:
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return DATA_RE.sub(lambda m: m.group(1) + blob + m.group(3), source, count=1)


FOOTER = re.compile(r'^(\d{1,2}/\d{1,2}/\d{4}.*|\d*Chapter \d+ .*\d{1,2}/\d{1,2}/\d{4}|Chapter \d+ [A-Za-z ]+ \d+|\d+)$')


def load_ledger(ch: int) -> list[dict]:
    """Original source slides from sources/ChNN-Study.html: number, title and content lines (footers removed)."""
    p = ROOT / LECTURES[ch]['study_path']
    s = p.read_text(encoding='utf-8')
    out = []
    for m in re.finditer(r'<details id="source-slide-(\d+)" class="source"><summary>(.*?)</summary>(.*?)</details>', s, re.S):
        n = int(m.group(1))
        title = html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))
        title = re.sub(r'^Slide \d+ · ', '', title).strip()
        body = html.unescape(re.sub(r'<[^>]+>', '\n', m.group(3)))
        lines = [re.sub(r'\s+', ' ', x).strip() for x in body.split('\n')]
        lines = [x for x in lines if x and not FOOTER.match(x)]
        if lines and lines[0].strip() == title.strip():
            lines = lines[1:]
        out.append({'n': n, 'title': title, 'lines': lines})
    return out


def load_story() -> dict:
    """Student-facing story strings per chapter, parsed from story-v3.js (strings only; no JS evaluation)."""
    s = STORY_PATH.read_text(encoding='utf-8')
    chapters: dict[int, list[tuple[str, str]]] = {}
    cur = None
    for line in s.split('\n'):
        m = re.match(r'\s*(\d+): \{', line)
        if m:
            cur = int(m.group(1))
            chapters.setdefault(cur, [])
            continue
        if cur is None:
            continue
        for key, txt in re.findall(r"(coldOpen|twist|epilogue|stakes|setting|practice|lesson|bridge|question|q): '((?:[^'\\]|\\.)*)'", line):
            chapters[cur].append((f'story.{key}', txt.replace("\\'", "'")))
        if re.match(r"\s*'", line):
            for a in re.findall(r"'((?:[^'\\]|\\.)*)'", line):
                chapters[cur].append(('story.line', a.replace("\\'", "'")))
        for a in re.findall(r"options: \[(.*?)\]", line):
            for o in re.findall(r"'((?:[^'\\]|\\.)*)'", a):
                chapters[cur].append(('story.option', o))
    return chapters


def strip_html(t: str) -> str:
    return html.unescape(re.sub(r'<[^>]+>', ' ', t or ''))


def sentences(text: str) -> list[str]:
    t = strip_html(text).replace('·', '. ')
    parts = re.split(r'(?<=[.!?])\s+', t)
    return [p.strip() for p in parts if p.strip()]


def words(sentence: str) -> int:
    toks = [w for w in re.split(r'\s+', sentence.strip()) if re.search(r'[A-Za-z0-9؀-ۿ]', w)]
    return len(toks)


def student_texts(data: dict, story: list | None = None) -> list[tuple[str, str]]:
    """Everything a student reads on the slides, in stations, the quiz and the story.
    Instructor notes, full explanations (long-form reading) and common-error notes are excluded."""
    out: list[tuple[str, str]] = []
    add = lambda loc, t: out.append((loc, t)) if isinstance(t, str) and t.strip() else None
    for s in data['slides']:
        sid = s['id']
        if sid not in NON_CONTENT:
            add(f'{sid}.title', s.get('title'))
        for b in s.get('bullets') or []:
            if isinstance(b, list):
                add(f'{sid}.bullet', b[1] if len(b) > 1 else b[0])
            else:
                add(f'{sid}.bullet', b)
        for k in ('takeaway', 'question', 'answer', 'question2', 'answer2', 'extra'):
            add(f'{sid}.{k}', s.get(k))
        for r in s.get('rows') or []:
            for c in r:
                add(f'{sid}.row', c if isinstance(c, str) else '')
        for L in s.get('lists') or []:
            add(f'{sid}.list.title', L.get('title'))
            for it in L.get('items', []):
                add(f'{sid}.list.item', it)
    for st in data.get('stations', []):
        no = st.get('no')
        for k in ('think', 'pair', 'write', 'hint', 'answer', 'note'):
            add(f'station{no}.{k}', st.get(k))
        rb = st.get('rubric') or {}
        for c in rb.get('criteria', []):
            add(f'station{no}.rubric.criterion', c.get('name'))
            for lv in c.get('levels', []):
                add(f'station{no}.rubric.level', lv[2] if isinstance(lv, list) and len(lv) > 2 else '')
        for k in ('strong', 'weak'):
            ex = rb.get(k) or {}
            add(f'station{no}.rubric.{k}', ex.get('text'))
            add(f'station{no}.rubric.{k}.why', ex.get('why'))
        add(f'station{no}.rubric.other', rb.get('other'))
    for i, q in enumerate(data.get('quiz', [])):
        add(f'quiz{i+1}.q', q.get('q'))
        add(f'quiz{i+1}.why', q.get('why'))
        for o in q.get('options', []):
            add(f'quiz{i+1}.option', o)
    c = data.get('case') or {}
    for k in ('headline', 'text', 'question', 'mutation', 'lens'):
        add(f'case.{k}', c.get(k))
    add('hook', data.get('hook'))
    tr = data.get('transfer') or {}
    for k in ('title', 'text', 'question', 'answer'):
        add(f'transfer.{k}', tr.get(k))
    for g in data.get('glossary') or []:
        add(f'glossary.{g.get("term")}', g.get('short'))
    for it in data.get('studyList') or []:
        add('studyList.topic', it.get('topic'))
        add('studyList.note', it.get('note'))
    A = data.get('aiAssignment') or {}
    for k in ('scenario', 'question', 'stress', 'framing'):
        add(f'aiAssignment.{k}', A.get(k))
    for f in A.get('facts', []):
        add('aiAssignment.fact', f)
    for k, v in (A.get('hints') or {}).items():
        add(f'aiAssignment.hint.{k}', v)
    ar = A.get('rubric') if isinstance(A.get('rubric'), dict) else {}
    for c in ar.get('criteria', []):
        add('aiAssignment.rubric.criterion', c.get('name'))
        for lv in c.get('levels', []):
            add('aiAssignment.rubric.level', lv[2] if isinstance(lv, list) and len(lv) > 2 else '')
    for k in ('strong', 'weak'):
        add(f'aiAssignment.rubric.{k}', (ar.get(k) or {}).get('text'))
        add(f'aiAssignment.rubric.{k}.why', (ar.get(k) or {}).get('why'))
    add('aiAssignment.rubric.other', ar.get('other'))
    r = data.get('roadmap') or {}
    for k in ('question', 'connection', 'inClass', 'deliverable', 'success'):
        add(f'roadmap.{k}', r.get(k))
    for b in r.get('branches', []):
        for k in ('caseLens', 'aiLens', 'detail'):
            add(f'roadmap.branch.{k}', b.get(k))
    for loc, t in story or []:
        add(loc, t)
    return out


def syllables(word: str) -> int:
    w = re.sub(r'[^a-z]', '', word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', w)
    w = re.sub(r'^y', '', w)
    groups = re.findall(r'[aeiouy]{1,2}', w)
    return max(1, len(groups))


def fk_grade(texts: list[str]) -> float:
    """Flesch–Kincaid grade level over English sentences (Arabic-only sentences are skipped)."""
    n_sent = n_words = n_syl = 0
    for t in texts:
        for se in sentences(t):
            ws = [w for w in re.split(r'\s+', se) if re.search(r'[A-Za-z]', w)]
            if not ws:
                continue
            n_sent += 1
            n_words += len(ws)
            n_syl += sum(syllables(w) for w in ws)
    if not n_sent or not n_words:
        return 0.0
    return 0.39 * (n_words / n_sent) + 11.8 * (n_syl / n_words) - 15.59


def term_re(term: str) -> re.Pattern:
    return re.compile(r'(?<![\w-])' + re.escape(term) + r'(?:s|es)?(?![\w-])', re.I)


def parse_range(r: str) -> tuple[int, int]:
    m = re.findall(r'\d+', r or '')
    return (int(m[0]), int(m[-1])) if m else (0, -1)
