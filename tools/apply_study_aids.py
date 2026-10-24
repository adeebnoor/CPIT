"""Study aids on the learning path (idempotent).

- code-coverage.html: a study guide for the course-plan topic "testing strategies and levels, code coverage,
  code coverage tools" (CLO 11). The nine lectures do not have a chapter for it; it is practised in the coverage
  step of every Python build (Assignments 3–9) and is within the scope of the final examination.
- iscarb.html: a "course at a glance" panel (chapter, course learning outcomes, assignment, examinations) and the
  current student update, keeping the 14 October notes in a folded section.
- Registers the guide in the public build, the offline packages and the site checks.
"""
from pathlib import Path
from html import escape as E
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from course_shell import header, footer, dependencies, VERSION  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'code-coverage.html'

# ---- code-coverage.html ------------------------------------------------------------------------
LEVELS = [
    ('Development testing · unit', 'One function, method or class on its own.', 'Every build: your test_ functions call one function.'),
    ('Development testing · component', 'Several units through their interface; interface misuse and timing.', 'Chapter 16: the interface contract.'),
    ('Development testing · system', 'The integrated system, including the interactions between components.', 'Chapter 20: cross-owner interaction testing.'),
    ('Release testing', 'A separate team checks the system against its requirements before release; requirements-based, scenario and performance testing.', 'Chapter 11: statistical testing with an operational profile.'),
    ('User testing', 'Alpha, beta and acceptance testing by users or the customer.', 'Chapter 20: staged acceptance.'),
]
STRATEGIES = [
    ('Partition (equivalence-class) testing', 'Group inputs that the program should treat the same way; test one value from each group.',
     'Loans 0–1 (allowed) and 2 or more (refused).'),
    ('Boundary values', 'Test at and next to the edges of each partition, where errors cluster.', 'Loans 1, 2 and 3; negative loans.'),
    ('Guideline-based testing', 'Use experience: empty or missing values, wrong types, very large inputs, repeated calls.', 'A record without "loans"; loans given as text.'),
    ('Requirements-based testing', 'Derive at least one test from each requirement.', 'Each course check in a build is a requirement test.'),
    ('Negative and security testing', 'Check that what must be refused is refused, and fails safely.', 'Chapter 13: misuse cases become tests.'),
    ('Test-driven development', 'Write a failing test, write the code that passes it, then refactor.', 'Run your tests after each change in a build.'),
]
CRITERIA = [
    ('Statement (line) coverage', 'Share of executable statements run at least once by the tests.', 'The build record reports it for your own code.'),
    ('Branch (decision) coverage', 'Share of decision outcomes (each if true and false; each loop entered and skipped) taken by the tests.',
     'The build record lists every branch your tests did not take.'),
    ('Path coverage', 'Share of distinct routes through the code. The number of paths grows quickly with loops, so it is rarely complete.', 'Discussed, not measured.'),
    ('Condition and MC/DC coverage', 'Each condition in a decision takes both values; MC/DC also shows that each condition independently changes the outcome. Required for the most critical avionics software (DO-178C, level A).',
     'Chapter 12: safety-critical verification.'),
]
TOOLS = [
    ('Python', 'coverage.py', 'coverage run --branch -m pytest, then coverage report -m (lists the lines not run)'),
    ('Java', 'JaCoCo', 'Maven or Gradle plugin; HTML report of line and branch coverage'),
    ('JavaScript', 'Istanbul (nyc) or c8', 'nyc npm test, or c8 node --test'),
    ('C and C++', 'gcov / lcov', 'compile with --coverage, run the tests, then gcov or lcov'),
]
QUIZ = [
    ('Does 100% statement coverage guarantee 100% branch coverage?',
     'No. An if without an else can have every statement run by a test where the condition is true, while the false outcome is never taken. Branch coverage includes statement coverage, not the other way round.'),
    ('Your tests reach 100% line coverage and all pass. Is the code correct?',
     'Not necessarily. Coverage shows that code ran, not that a test checked its result. A test without an assert can run every line. That is why the builds also use mutation testing: each known faulty version must make at least one of your tests fail.'),
    ('A rule allows a student to hold at most 2 items. Which inputs would you test, and why?',
     'One value from each partition (for example 0 and 5) and the boundary values 1, 2 and 3, plus invalid input such as −1 or text. Errors cluster at boundaries, such as < written as <=.'),
    ('At which testing level do you check that two components owned by different teams work together?',
     'Component or system testing (integration). In a system of systems (Chapter 20) this is cross-owner interaction testing.'),
    ('The coverage report lists the branch "if type(loans) is not int or loans < 0 → true" as not taken. What do you do?',
     'Add a test whose input makes the condition true, for example loans = −1 or loans = "2", and assert that the result is False. Then run the build again and confirm the branch is now taken.'),
]
EXAM = ['Name the testing levels and what each one checks.',
        'Derive partitions and boundary values for a stated rule.',
        'Define statement, branch and path coverage, and explain why branch coverage is stronger than statement coverage.',
        'Explain what coverage cannot show, and how mutation testing complements it.',
        'Read a short function and its tests, and name the line or branch that is not covered and a test that would cover it.']


def table(head, rows):
    h = ''.join(f'<th scope="col">{c}</th>' for c in head)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="table-scroll"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


CODE = '''def can_borrow(student, item):
    try:                                                        # line 2
        loans = student["loans"]                                # line 3
        if type(loans) is not int or loans &lt; 0:                 # line 4
            return False                                        # line 5
        return item["available"] is True and loans &lt; LIMIT and student["overdue"] is False   # line 6
    except (KeyError, TypeError):                               # line 7
        return False                                            # line 8'''


def build_guide():
    quiz = ''.join(f'<details class="faq"><summary><b>{i}. {E(q)}</b></summary><p>{E(a)}</p></details>'
                   for i, (q, a) in enumerate(QUIZ, 1))
    main = f'''<main class="wrap" id="main"><div class="document-heading"><p class="ey">STUDY GUIDE · CLO 11 · WEEKS 14–15 OF THE COURSE PLAN</p>
<h1>Testing strategies and code coverage</h1>
<p class="intro">How to choose test cases, at which level to test, and what code coverage does and does not tell you. You practise this in the coverage step of every Python build (Assignments 3–9), and it is part of the final examination.</p></div>
<section class="panel" lang="ar" dir="rtl"><h2>باختصار</h2><p>هذا الدليل يغطي موضوع «استراتيجيات الاختبار ومستوياته، وتغطية الشيفرة وأدواتها» في خطة المقرر (مخرج التعلم 11). تتدرّب عليه في خطوة التغطية في كل بناء برمجي (الواجبات 3–9)، وهو ضمن الاختبار النهائي. اقرأ الأقسام الأربعة، ثم جرّب المثال المحلول، ثم أجب عن أسئلة المراجعة.</p></section>
<p><b>Reading:</b> I. Sommerville, <i>Software Engineering</i>, 10th edition, Chapter 8 (Software testing): 8.1 development testing, 8.2 test-driven development, 8.3 release testing, 8.4 user testing.</p>

<section class="section" id="levels"><h2>1 · Testing levels <span class="vs-ar-t" lang="ar" dir="rtl">مستويات الاختبار</span></h2>
{table(['Level', 'What it checks', 'Where you meet it in this course'], [(f'<b>{E(a)}</b>', E(b), E(c)) for a, b, c in LEVELS])}</section>

<section class="section" id="strategies"><h2>2 · Choosing test cases <span class="vs-ar-t" lang="ar" dir="rtl">اختيار حالات الاختبار</span></h2>
<p>Black-box strategies choose tests from the specification; white-box (structural) strategies choose tests from the code, and coverage measures them.</p>
{table(['Strategy', 'Idea', 'Example from the practice build'], [(f'<b>{E(a)}</b>', E(b), E(c)) for a, b, c in STRATEGIES])}</section>

<section class="section" id="criteria"><h2>3 · Coverage criteria <span class="vs-ar-t" lang="ar" dir="rtl">معايير التغطية</span></h2>
{table(['Criterion', 'Definition', 'In this course'], [(f'<b>{E(a)}</b>', E(b), E(c)) for a, b, c in CRITERIA])}
<p><b>What coverage does not show.</b> Coverage tells you which code your tests ran, not whether they checked the result. Code that was never written, such as a missing check, cannot be uncovered. Treat coverage as a map of what is still untested, not as a score. Mutation testing, used in every build, asks the stronger question: would a test fail if the code were wrong?</p>
<p lang="ar" dir="rtl"><b>ما لا تُظهره التغطية:</b> التغطية تبيّن أي جزء من الشيفرة نفّذته اختباراتك، ولا تبيّن هل تحققت الاختبارات من النتيجة. والفحص الناقص الذي لم يُكتب أصلاً لا يظهر في التغطية. لذلك تستخدم البناءات اختبار الطفرات أيضاً.</p></section>

<section class="section" id="tools"><h2>4 · Coverage tools <span class="vs-ar-t" lang="ar" dir="rtl">أدوات التغطية</span></h2>
{table(['Language', 'Tool', 'Typical use'], [(E(a), f'<b>{E(b)}</b>', f'<code>{E(c)}</code>' if a == 'Python' else E(c)) for a, b, c in TOOLS])}
<p>The build in your assignment measures line and branch coverage of your own functions (not of the test_ functions) in the browser, so you do not need to install a tool.</p></section>

<section class="section" id="example"><h2>5 · Worked example <span class="vs-ar-t" lang="ar" dir="rtl">مثال محلول</span></h2>
<p>The complete solution of the <a href="assignment-example.html#build">practice build</a> has four tests: a normal loan, a third item, an overdue student and a broken record.</p>
<pre>{CODE}</pre>
<ul><li><b>Lines run:</b> the first three tests run lines 2, 3, 4 and 6; the broken-record test runs lines 2, 3, 7 and 8.</li>
<li><b>Not covered:</b> line 5 never runs. Statement coverage is 5 of 6 statements, and the true outcome of the <code>if</code> on line 4 is never taken.</li>
<li><b>Fix:</b> add <code>test_negative_loans_are_refused</code> with <code>loans = -1</code> and assert that the result is <code>False</code>. Run the build again: the branch is now taken. This is exactly the coverage step in Assignments 3–9.</li></ul></section>

<section class="section" id="check"><h2>6 · Check yourself <span class="vs-ar-t" lang="ar" dir="rtl">راجع نفسك</span></h2>
<p>Answer first, then open each question.</p>{quiz}</section>

<section class="section" id="exam"><h2>7 · For the final examination <span class="vs-ar-t" lang="ar" dir="rtl">للاختبار النهائي</span></h2>
<ul>{''.join(f'<li>{E(x)}</li>' for x in EXAM)}</ul>
<p><a href="iscarb.html">Back to the learning path</a> · <a href="course-specification.html#spec-b">CLO 11 in the course specification</a></p></section>
</main>'''
    head = ('<!DOCTYPE html>\n<html data-iscarb-standalone="1" data-theme="dark" lang="en"><head><meta charset="utf-8">'
            '<meta content="width=device-width,initial-scale=1" name="viewport"><meta content="#006b62" name="theme-color">'
            '<meta content="Study guide for testing strategies, testing levels and code coverage (CPIT-455, CLO 11)." name="description">'
            '<title>Testing strategies and code coverage · iSCARB CPIT-455</title>'
            f'<link href="iscarb-hub.css?v={VERSION}" rel="stylesheet"><link rel="stylesheet" href="course-design.css?v={VERSION}">'
            + dependencies()
            + '<style>details.faq{border-bottom:1px solid var(--line);padding:8px 0}details.faq summary{cursor:pointer}'
              'pre{overflow-x:auto;padding:12px;border:1px solid var(--line);border-radius:8px;font-size:.85rem}'
              'p code,li code,td code{overflow-wrap:anywhere}</style></head>')
    body = ('<body class="course-page" id="top"><a class="skip" href="#main">Skip to content</a>'
            + header('', 'student-guide.html') + '\n' + main + footer('') + '</body></html>\n')
    GUIDE.write_text(head + body, encoding='utf-8')


# ---- iscarb.html: course at a glance and the current update -------------------------------------
GLANCE_MARK = '<!-- study-aids:glance -->'
CHAPTERS = [  # chapter, title, CLOs, assignment, examinations
    ('10', 'Dependable Systems', '1, 2', 'Assignment 1', 'Midterm · final'),
    ('11', 'Reliability Engineering', '1, 2, 3', 'Assignment 2', 'Midterm · final'),
    ('12', 'Safety Engineering', '4, 11', 'Assignment 3', 'Midterm · final'),
    ('13', 'Security Engineering', '2, 5, 11', 'Assignment 4', 'Midterm · final'),
    ('14', 'Resilience Engineering', '6, 11', 'Assignment 5', 'Midterm · final'),
    ('15', 'Software Reuse', '7, 11', 'Assignment 6', 'Final'),
    ('16', 'Component-based Software Engineering', '8, 11', 'Assignment 7', 'Final'),
    ('17', 'Distributed Software Engineering', '9, 11', 'Assignment 8', 'Final'),
    ('20', 'Systems of Systems', '10, 11', 'Assignment 9', 'Final'),
]


def glance():
    rows = ''.join(f'<tr><td>{c}</td><td>{E(t)}</td><td>{l}</td><td>{a}</td><td>{x}</td></tr>' for c, t, l, a, x in CHAPTERS)
    rows += ('<tr><td>—</td><td><a href="code-coverage.html">Testing strategies and code coverage</a></td><td>11</td>'
             '<td>Coverage step, Assignments 3–9</td><td>Final</td></tr>')
    return (GLANCE_MARK + '<section class="glance" id="at-a-glance" aria-labelledby="glance-title" style="padding-top:24px">'
            '<p class="ey">Course at a glance</p><h2 id="glance-title">What each chapter is assessed by</h2>'
            '<div class="table-scroll"><table><thead><tr><th scope="col">Ch.</th><th scope="col">Chapter</th>'
            '<th scope="col">Course outcomes (CLO)</th><th scope="col">Assignment</th><th scope="col">Examinations</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            '<p>Grade: assignments 30, midterm examination 30, final examination 30, participation 10 '
            '(<a href="assignment-example.html#grading">how the course is graded</a>). The final examination covers the whole course, '
            'including testing strategies and code coverage. The outcomes are listed in the <a href="course-specification.html#spec-b">course '
            'specification</a>. In the revised IT program plan, this course is <b>IT 456 Dependable Systems</b>.</p>'
            '<p lang="ar" dir="rtl">الدرجة: الواجبات 30، والاختبار النصفي 30، والاختبار النهائي 30، والمشاركة 10. الاختبار النهائي يشمل المقرر كله، '
            'ومنه استراتيجيات الاختبار وتغطية الشيفرة (<a href="code-coverage.html">دليل المراجعة</a>). ويقابل هذا المقرر في الخطة المحدثة المقرر IT 456.</p>'
            '</section>')


UPDATE_MARK = '<!-- study-aids:update-24oct -->'
UPDATE = (UPDATE_MARK + '<p class="ey">24 October · update</p>'
          '<p><b>New for students.</b> A study guide for <a href="code-coverage.html">testing strategies and code coverage</a> '
          '(part of the final examination). <a href="assignment-example.html#new-6-9">Assignments 6–9: three new things</a>, with an example. '
          'The <a href="course-specification.html">course specification</a>: outcomes, content and assessment. If Python does not '
          'load in a build, it now loads from the course site automatically.</p>'
          '<p lang="ar" dir="rtl"><b>جديد للطلاب:</b> <a href="code-coverage.html">دليل مراجعة استراتيجيات الاختبار وتغطية الشيفرة</a> '
          '(ضمن الاختبار النهائي)، و<a href="assignment-example.html#new-6-9">الجديد في الواجبات 6–9 مع مثال</a>، و<a href="course-specification.html">توصيف المقرر</a>. '
          'وإذا لم يُحمَّل بايثون في البناء البرمجي فإنه يُحمَّل الآن من موقع المقرر تلقائياً.</p>'
          '<details><summary style="font-size:14px;font-weight:700;cursor:pointer">14 October · second update</summary>')


def patch_hub():
    p = ROOT / 'iscarb.html'
    t = p.read_text(encoding='utf-8')
    if UPDATE_MARK not in t:
        old = '<aside class="changes" aria-label="What changed">\n<p class="ey">14 October · second update</p>'
        assert t.count(old) == 1, 'changes aside not found'
        a = t.index(old)
        b = t.index('</aside>', a)
        t = t[:a] + '<aside class="changes" aria-label="What changed">\n' + UPDATE + t[a + len(old):b] + '</details>' + t[b:]
    else:
        a = t.index(UPDATE_MARK)
        b = t.index('14 October · second update</summary>', a) + len('14 October · second update</summary>')
        t = t[:a] + UPDATE + t[b:]
    anchor = '<section class="chapter-search">'
    if GLANCE_MARK in t:
        a = t.index(GLANCE_MARK)
        b = t.index('</section>', a) + len('</section>')
        t = t[:a] + glance() + t[b:]
    else:
        assert t.count(anchor) == 1
        t = t.replace(anchor, glance() + anchor)
    p.write_text(t, encoding='utf-8')


def register():
    edits = [
        ('tools/build_public_site.py', "'course-specification.html',", "'course-specification.html','code-coverage.html',"),
        ('tools/audit_classroom.py', '"course-specification.html", ', '"course-specification.html", "code-coverage.html", '),
        ('tools/check-site-design.cjs', "'course-specification.html',", "'course-specification.html','code-coverage.html',"),
        ('tools/prepare_readable_release.py', "'student-ux.css','chapter-search.js']", "'student-ux.css','chapter-search.js','code-coverage.html']"),
    ]
    for rel, old, new in edits:
        p = ROOT / rel
        t = p.read_text(encoding='utf-8')
        if new not in t:
            assert t.count(old) == 1, f'{rel}: anchor found {t.count(old)} times'
            p.write_text(t.replace(old, new), encoding='utf-8')


if __name__ == '__main__':
    build_guide()
    patch_hub()
    register()
    print('Study aids applied: code-coverage.html, course at a glance and the 24 October update on iscarb.html')
