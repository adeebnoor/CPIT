"""The practical hour (lab credit 0) inside Assignments 3–9, stated where students and reviewers look.

- Each assignment page (Assignments 3–9) opens with a fixed bilingual line. The line says the build is the chapter's
  practical hour, the assignment is not submitted without it, and running the tests is a separate rubric row that
  longer writing does not replace. It names the course learning outcome the build practises, plus outcome 11
  (test cases) through the tests and the coverage step.
- The rubric gets a separate TESTS RUN row (required; the build itself is marked in the second row), and the export's
  rubric line names it.
- The grade tables (student guide, worked example) carry the lab-credit sentence in English and Arabic.
- Code Coverage is practised in the coverage step of every build (tools/apply_assignment_build.py), so the
  "not on this site yet" statements are replaced on every page.

Run after tools/apply_assignment_build.py, tools/apply_assignment_plain_language.py and
tools/apply_lecture_requirements.py. Idempotent:  python3 tools/apply_practical_hour.py
"""
from __future__ import annotations
import html, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_assignment_build import CLO, CLO11, CRIT

ROOT = Path(__file__).resolve().parents[1]
PUB = json.loads((ROOT / 'curriculum/publication.json').read_text(encoding='utf-8'))
esc = lambda s: html.escape(str(s), quote=True)

HOUR_EN = ('This build is this chapter’s practical hour. The assignment is not submitted without it. '
           'Running the tests is a separate row in the rubric; longer writing does not make up for it.')
HOUR_AR = 'هذا البناء هو الساعة التطبيقية لهذا الفصل. لا يُسلَّم الواجب بدونه. تشغيل الاختبارات صف مستقل في السلّم، لا يُعوَّض بطول الكتابة.'
CLO_AR = {
    4: ('تصميم السلامة في الأنظمة الحرجة', 'شجرة الخطأ'),
    5: ('تصميم الأنظمة الآمنة واختبارها', 'قاعدة الوصول في الخادم'),
    6: ('تصميم الأنظمة لدعم الصمود', 'المطابقة بعد التعافي'),
    7: ('تحديد عناصر إعادة الاستخدام وأساليبها', 'فحص الملاءمة المبني على الأدلة'),
    8: ('تركيب المكوّنات القياسية القابلة لإعادة الاستخدام', 'المهايئ'),
    9: ('شرح الأنظمة الموزعة ومعمارياتها', 'الخدمة التي لا تكرر الحجز'),
    10: ('شرح نظام الأنظمة وتحدياته الهندسية', 'العرض الصادق لحالة كل مصدر'),
}
CLO11_AR = 'تصميم حالات الاختبار وتنفيذها'
CREDIT_EN = ('Lab credit is 0. The practical hour is the coded build, the tests, and the recorded run inside Assignments 3–9, '
             'completed in the weekly 90-minute practical session. It is marked. It is not optional.')
CREDIT_AR = ('رصيد المعمل صفر. الساعة التطبيقية هي البناء البرمجي والاختبارات والتشغيل المسجَّل داخل الواجبات 3–9، '
             'وتُنجز في الحصة التطبيقية الأسبوعية ومدتها 90 دقيقة. وهي مُقيَّمة، وليست اختيارية.')

H_START, H_END = '<!-- practical-hour:start -->', '<!-- practical-hour:end -->'
C_START, C_END = '<!-- lab-credit:start -->', '<!-- lab-credit:end -->'
ROW_MARK = 'data-row="tests-run"'
MD_OLD = 'REFIT: 1. Instructor assessment required.'
MD_NEW = 'REFIT: 1. TESTS RUN: required (recorded runs and the coverage sentence; longer writing does not replace them). Instructor assessment required.'


def block(s: str, start: str, end: str, content: str, anchor_re: str, where: str) -> str:
    """Replace the marked block, or insert it once after the first match of anchor_re."""
    new = start + content + end
    if start in s:
        return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: new, s, count=1, flags=re.S)
    m = re.search(anchor_re, s, re.S)
    if not m:
        raise SystemExit(f'{where}: anchor {anchor_re!r} not found')
    return s[:m.end()] + new + s[m.end():]


def hour_line(ch: int) -> str:
    n, outcome, artifact = CLO[ch]
    ar_outcome, ar_artifact = CLO_AR[n]
    return ('<div class="practical-hour" role="note" style="margin:12px 0;padding:10px 14px;border:2px solid currentColor;border-radius:10px">'
            f'<p style="margin:0 0 4px"><b>Practical hour.</b> {esc(HOUR_EN)}</p>'
            f'<p lang="ar" dir="rtl" style="margin:0 0 6px"><b>الساعة التطبيقية.</b> {esc(HOUR_AR)}</p>'
            f'<p class="small" style="margin:0"><b>Course learning outcome {n}:</b> {esc(outcome)}, practised by building and testing {esc(artifact)}. '
            f'The tests and the coverage step practise <b>outcome 11</b>: {esc(CLO11.lower())}.</p>'
            f'<p class="small" lang="ar" dir="rtl" style="margin:0"><b>مخرج التعلم {n}:</b> {esc(ar_outcome)}، ويُمارَس ببناء {esc(ar_artifact)} واختباره. '
            f'والاختبارات وخطوة التغطية تمارس <b>المخرج 11</b>: {esc(CLO11_AR)}.</p></div>')


def tests_row(ch: int) -> str:
    return (f'<tr {ROW_MARK}><th scope="row">TESTS RUN · required</th><td><b>Required for submission:</b> a recorded run of your own tests '
            'and the course checks on your final code, a second run after you change one test input, and the coverage sentence. '
            'Part A cannot be committed without them. <b>Not replaceable:</b> longer writing does not make up for a missing run. '
            f'A run with failing checks is accepted when your text explains it. The build itself is marked in {CRIT[ch]}.</td></tr>')


def credit() -> str:
    return (f'<div class="lab-credit" role="note"><p><b>Practical hour.</b> {esc(CREDIT_EN)}</p>'
            f'<p lang="ar" dir="rtl"><b>الساعة التطبيقية.</b> {esc(CREDIT_AR)}</p></div>')


def patch_assignment(path: Path, ch: int) -> bool:
    s0 = s = path.read_text(encoding='utf-8')
    s = block(s, H_START, H_END, hour_line(ch), r'<header class="top">.*?<p class="sub">.*?</p>', path.name)
    if ROW_MARK not in s:
        i = s.index('id="rubric-heading"'); j = s.index('</table>', i)
        rows = list(re.finditer(r'<tr><th scope="row">[^<]+</th>.*?</tr>', s[i:j], re.S))
        build_row = next((r for r in rows if '<b>Build:</b>' in r.group(0)), None)
        if not build_row:
            raise SystemExit(f'{path.name}: rubric row with the build not found')
        at = i + build_row.end()
        s = s[:at] + tests_row(ch) + s[at:]
    if MD_NEW not in s:
        if s.count(MD_OLD) != 1:
            raise SystemExit(f'{path.name}: export rubric line not found once')
        s = s.replace(MD_OLD, MD_NEW)
    if s != s0:
        path.write_text(s, encoding='utf-8'); return True
    return False


REPLACE = [
    # file, old, new
    ('iscarb.html', '<p class="fact-warn">Code Coverage is on the syllabus and is not on this site yet. It will be taught as announced in class.</p>',
     '<p class="fact-warn">Code Coverage is practised in every Python build of Assignments 3–9: the build record measures which lines and branches your own tests run; you change one input, run again, and name the branch still untested.</p>'),
    ('iscarb.html', 'Code Coverage is on the syllabus and is not here yet. The outcome map shows which course outcomes each chapter supports.',
     'Code Coverage is practised in the coverage step of every build in Assignments 3–9. The outcome map shows which course outcomes each chapter supports.'),
    ('course-resources.html', '<td>Partial: 11, 12, 13, 16, 17</td><td>Test design is practised. Chapters 16 and 17 add student-authored executable test cases in small deterministic teaching models. Broader testing-strategy implementation and the separate Code Coverage topic remain incomplete.</td>',
     '<td>12, 13, 14, 15, 16, 17, 20</td><td>Every build in Assignments 3–9 has the student write and run at least three tests, a mutation test against known buggy versions, and a coverage step: the build record measures line and branch coverage of the student’s code (gate outcomes for the fault tree), the student changes one input, runs again, and names the branch still untested. The sentence is part of the submission.</td>'),
    ('instructor-guide.html', ' Code Coverage remains a separate unresolved source gap.',
     ' Code Coverage is practised in the coverage step of every build in Assignments 3–9 (course outcome 11).'),
    ('nelc-alignment.html', 'Code Coverage, listed in the syllabus, remains an identified gap in the <a href="course-resources.html#outcomes">course-outcome map</a>; these chapters do not represent complete coverage of the syllabus.',
     'Code Coverage, listed in the syllabus, is practised in the coverage step of every build in Assignments 3–9; see the <a href="course-resources.html#outcomes">course-outcome map</a> (outcome 11).'),
    ('lectures/iscarb/README.md', 'Code Coverage is an explicit outstanding topic because its source material was not supplied. Proposed tests in the assignments do not establish executable-test implementation coverage.',
     'Code Coverage is practised in the coverage step of every Python build in Assignments 3–9: the harness measures line and branch coverage of the student’s code by the student’s own tests (gate outcomes for the Chapter 12 fault tree), and the student changes one input, reruns and names the branch still untested (course outcome 11).'),
    ('assignment-example.html', '<p>The Python build in Assignments 3–9 is part of each assignment\'s 5 points (the second rubric row). It is not an extra grade. The micro-viva is a short check of that same work, not a separate exam.</p>',
     '<p>The Python build in Assignments 3–9 is marked inside each assignment\'s 5 points (the second rubric row). Running the tests is a separate rubric row, TESTS RUN: it is required, and longer writing does not replace it. The micro-viva is a short check of that same work, not a separate exam.</p>'),
]

INSTRUCTOR_OLD = re.compile(r'<h2>Two executable tasks within the existing assignments</h2>.*?(?=</section>)', re.S)
INSTRUCTOR_NEW = ('<h2>The practical hour: Python builds in Assignments 3–9</h2>'
                  f'<p>{esc(CREDIT_EN)}</p><p lang="ar" dir="rtl">{esc(CREDIT_AR)}</p>'
                  '<ul>' + ''.join(f'<li>Assignment {a} (Chapter {ch}): {esc(CLO[ch][2])} · course learning outcome {CLO[ch][0]}</li>'
                                   for a, ch in zip(range(3, 10), (12, 13, 14, 15, 16, 17, 20))) + '</ul>'
                  '<p>Each build has student code, at least three of the student’s own tests, the course checks, a mutation test and a coverage step '
                  '(course outcome 11). Part A cannot be committed without a recorded run, a second run after one test input changes, and the coverage sentence.</p>'
                  '<p>Mark the build in the second rubric row. The TESTS RUN row is required and is not replaced by longer writing. '
                  'A green report alone is insufficient: the written record must use what the build showed. Ask for the micro-viva change named in the build record.</p>')


def main() -> int:
    done = []
    for a in PUB['assignments']:
        ch = int(a['chapter'])
        if ch in CLO and patch_assignment(ROOT / a['path'], ch):
            done.append(ch)
    for rel, old, new in REPLACE:
        p = ROOT / rel; s = p.read_text(encoding='utf-8')
        if new in s:
            continue
        if s.count(old) != 1:
            raise SystemExit(f'{rel}: expected text not found once: {old[:70]!r}')
        p.write_text(s.replace(old, new), encoding='utf-8'); done.append(rel)
    p = ROOT / 'instructor-guide.html'; s = p.read_text(encoding='utf-8')
    if INSTRUCTOR_NEW not in s:
        s2, n = INSTRUCTOR_OLD.subn(lambda _: INSTRUCTOR_NEW, s, count=1)
        if n != 1:
            raise SystemExit('instructor-guide.html: executable-task section not found')
        p.write_text(s2, encoding='utf-8'); done.append('instructor-guide.html (practical hour)')
    for rel, anchor in (('student-guide.html', r'<section class="section guide-note" id="grade">\s*<h2>What the grade is</h2>\s*<p>.*?</p>'),
                        ('assignment-example.html', r'<section class="section" id="grading">.*?</table></div>')):
        p = ROOT / rel; s = p.read_text(encoding='utf-8')
        s2 = block(s, C_START, C_END, credit(), anchor, rel)
        if s2 != s:
            p.write_text(s2, encoding='utf-8'); done.append(rel + ' (lab credit)')
    print('Practical hour applied:', done or 'nothing to change')
    return 0


if __name__ == '__main__':
    sys.exit(main())
