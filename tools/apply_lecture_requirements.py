"""Write the authored lecture requirements (curriculum/lecture-requirements/chNN.json) into each lecture.

The authored file is the source of truth for the new fields (glossary, transfer case, coverage map, study list,
time budget, tags, rubrics) and for plain-language rewrites of student text. Running it again changes nothing.
After it, re-pin with tools/refresh_release_hashes.py and run tools/check_lecture_requirements.py.
Run:  python3 tools/apply_lecture_requirements.py [chapter ...]
"""
from __future__ import annotations
import json, re, sys, html
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_requirements_lib import ROOT, PUB, CHAPTERS, LECTURES, common, load_req, load_lecture, dump_lecture, load_ledger

SLIDE_KEYS = ('minutes', 'tier', 'concept', 'answerKey', 'concept2', 'answerKey2', 'commonError', 'question', 'answer',
              'question2', 'answer2', 'bullets', 'takeaway', 'extra', 'lists', 'added', 'twist', 'transfer', 'sourceFigs',
              'rows', 'heads', 'notes', 'title', 'sourceRange', 'sourceLabel')
STATION_KEYS = ('minutes', 'seconds', 'tier', 'concept', 'answerKey', 'transfer', 'think', 'pair', 'write', 'hint', 'answer', 'note', 'rubric', 'title')
QUIZ_KEYS = ('concept', 'answerKey', 'beyondCase', 'q', 'options', 'why', 'answer')
LECTURE_KEYS = ('glossary', 'transfer', 'studyList', 'activities', 'hook', 'timeRule', 'bound', 'their')
RUB_START, RUB_END = '<!-- rubric-examples:start -->', '<!-- rubric-examples:end -->'


def apply_chapter(ch: int) -> bool:
    req = load_req(ch)
    if not req:
        print(f'Ch{ch}: no authored requirements file'); return False
    cfg = common()
    data, source, path = load_lecture(ch)
    before = json.dumps(data, sort_keys=True)
    data['lectureMinutes'] = int(req.get('lectureMinutes') or cfg['lectureMinutes'])
    data['budgetShare'] = cfg['budgetShare']
    data['timeRule'] = req.get('timeRule') or cfg['timeRule']
    for k in LECTURE_KEYS:
        if k in req and k != 'timeRule':
            data[k] = req[k]
    if 'case' in req:
        data['case'] = {**data.get('case', {}), **req['case']}
    if 'roadmap' in req:
        rm = data.setdefault('roadmap', {})
        for k, v in req['roadmap'].items():
            if k == 'branches':
                for i, b in enumerate(v):
                    if i < len(rm.get('branches', [])) and b:
                        rm['branches'][i].update(b)
            else:
                rm[k] = v
    if 'aiAssignment' in req and data.get('aiAssignment'):
        for k, v in req['aiAssignment'].items():
            if k == 'hints' and isinstance(v, dict):
                data['aiAssignment'].setdefault('hints', {}).update(v)
            else:
                data['aiAssignment'][k] = v
    # coverage: authored classification plus the source title from the ledger, one entry per original slide
    ledger = {L['n']: L for L in load_ledger(ch)}
    cov = []
    for n in sorted(ledger):
        c = dict(req.get('coverage', {}).get(str(n)) or {})
        c['n'] = n; c['title'] = ledger[n]['title']
        cov.append(c)
    data['coverage'] = cov
    byid = {s['id']: s for s in data['slides']}
    for sid, patch in (req.get('slides') or {}).items():
        s = byid[sid]
        for k, v in patch.items():
            if k not in SLIDE_KEYS:
                raise SystemExit(f'Ch{ch} {sid}: unknown slide key {k}')
            s[k] = v
        if sid == (req.get('transfer') or {}).get('at'):
            s['transfer'] = True
            s['question'] = req['transfer']['question']; s['answer'] = req['transfer']['answer']
            s['concept'] = req['transfer']['concept']; s['answerKey'] = req['transfer']['answerKey']
    for st_patch in req.get('stations') or []:
        st = next(x for x in data['stations'] if x['no'] == st_patch['no'])
        for k, v in st_patch.items():
            if k == 'no':
                continue
            if k not in STATION_KEYS:
                raise SystemExit(f'Ch{ch} station {st_patch["no"]}: unknown key {k}')
            st[k] = v
    for i, q_patch in enumerate(req.get('quiz') or []):
        if not q_patch:
            continue
        for k, v in q_patch.items():
            if k not in QUIZ_KEYS:
                raise SystemExit(f'Ch{ch} quiz {i+1}: unknown key {k}')
            data['quiz'][i][k] = v
    # data cleanliness: placeholder tags left by the first draft are removed, never published
    for s in data['slides']:
        for k in ('concept', 'answerKey', 'concept2', 'answerKey2'):
            if s.get(k) == 'TODO':
                del s[k]
    # rubric template: fill level labels from common.json when a criterion gives only texts
    after = json.dumps(data, sort_keys=True)
    if after != before:
        path.write_text(dump_lecture(data, source), encoding='utf-8')
    changed = after != before
    changed |= apply_assignment(ch, req)
    print(f'Ch{ch}: {"updated" if changed else "unchanged"}')
    return changed


def apply_assignment(ch: int, req: dict) -> bool:
    """RUB-2/RUB-4 on the assessed assignment page: strong and weak example per criterion and acceptance conditions."""
    ex = req.get('assignmentRubric')
    a = next((x for x in PUB['assignments'] if int(x['chapter']) == ch), None)
    if not ex or not a:
        return False
    p = ROOT / a['path']; s = p.read_text(encoding='utf-8')
    rows = ''.join(
        f'<tr data-criterion="{html.escape(c["name"])}"><th scope="row">{html.escape(c["name"])}</th>'
        f'<td><b>Strong:</b> {html.escape(c["strong"])}<br><i>Why:</i> {html.escape(c["strongWhy"])}</td>'
        f'<td><b>Weak:</b> {html.escape(c["weak"])}<br><i>Why:</i> {html.escape(c["weakWhy"])}</td></tr>'
        for c in ex['criteria'])
    block = (f'{RUB_START}<details id="rubricExamples" class="rubric-examples"><summary>Strong and weak answers for each criterion · how other answers are accepted</summary>'
             f'<div class="rubric-wrap"><table class="rubric"><thead><tr><th scope="col">Criterion</th><th scope="col">Strong example</th><th scope="col">Weak example</th></tr></thead><tbody>{rows}</tbody></table></div>'
             f'<p class="hint"><b>Other answers are accepted when:</b> {html.escape(ex["other"])}</p>'
             f'<p class="hint">The examples are about a different practice case. They show the kind of reasoning that earns the mark, not the answer to this task.</p></details>{RUB_END}')
    if RUB_START in s:
        new = re.sub(re.escape(RUB_START) + r'.*?' + re.escape(RUB_END), lambda m: block, s, count=1, flags=re.S)
    else:
        anchor = '<details id="qualityExample">'
        if anchor not in s:
            raise SystemExit(f'Ch{ch} assignment: qualityExample anchor not found')
        new = s.replace(anchor, block + anchor, 1)
    if new != s:
        p.write_text(new, encoding='utf-8'); return True
    return False


def apply_levels_open(ch: int) -> bool:
    """RUB-1/RUB-5: every rubric level (1 · 0.75 · 0.5 · 0) is visible before submission; the partial-credit levels stay
    collapsible but start open. Assignments 1–2 (Chapters 10–11) are frozen and already show all levels inline."""
    a = next((x for x in PUB['assignments'] if int(x['chapter']) == ch), None)
    if not a or ch < int(common().get('assignmentRubricFromChapter', 12)):
        return False
    p = ROOT / a['path']; s = p.read_text(encoding='utf-8')
    new = s.replace('<details class="levels">', '<details class="levels" open>')
    if new != s:
        p.write_text(new, encoding='utf-8'); return True
    return False


BOUND_MARK = '/* BOUND-4: the boundary sentence written in the lecture travels with the assignment */'


def apply_bound_export(ch: int) -> bool:
    """BOUND-4: add the student's lecture boundary sentence to the assignment export and show it under BOUND."""
    a = next((x for x in PUB['assignments'] if int(x['chapter']) == ch), None)
    if not a or ch < common().get('assignmentRubricFromChapter', 12):
        return False
    p = ROOT / a['path']; s = p.read_text(encoding='utf-8')
    if BOUND_MARK in s:
        return False
    anchor = "function md(final=false){"
    push = "lines.push('## Scenario',d.scenario||'','');"
    if s.count(anchor) != 1 or s.count(push) != 1:
        raise SystemExit(f'Ch{ch} assignment: export anchors not found')
    helper = (BOUND_MARK + "\nfunction lectureBound(){try{const x=JSON.parse(localStorage.getItem('iscarb:classroom:ch" + str(ch) +
              ":v3')||'null');return String(x?.state?.fields?.commit_bound||'').trim();}catch(e){return ''}}\n"
              "setTimeout(()=>{const t=document.getElementById('bound');if(!t||document.getElementById('lectureBound'))return;const p=document.createElement('p');"
              "p.id='lectureBound';p.className='hint';const v=lectureBound();p.textContent=v?'Your boundary sentence from the lecture (included in your export): '+v:"
              "'Your boundary sentence from the Chapter " + str(ch) + " lecture is not on this device yet. Write it on the lecture\u2019s closing slide; it is then added to your export.';"
              "t.insertAdjacentElement('afterend',p);},0);\n")
    s = s.replace(anchor, helper + anchor, 1)
    s = s.replace(push, push + "lines.push('## Chapter boundary sentence (written in the lecture)',lectureBound()||'Not written in the lecture on this device.','');", 1)
    p.write_text(s, encoding='utf-8')
    return True


def main(argv: list[str]) -> int:
    chapters = [int(x) for x in argv] or CHAPTERS
    for ch in chapters:
        apply_chapter(ch)
        if apply_bound_export(ch):
            print(f'Ch{ch} assignment: boundary sentence added to the export')
        if apply_levels_open(ch):
            print(f'Ch{ch} assignment: rubric levels shown open')
    pub = json.loads((ROOT / 'curriculum/publication.json').read_text(encoding='utf-8'))
    cfg = common()
    if pub.get('lecture_minutes') != cfg['lectureMinutes']:
        pub['lecture_minutes'] = cfg['lectureMinutes']
        (ROOT / 'curriculum/publication.json').write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
