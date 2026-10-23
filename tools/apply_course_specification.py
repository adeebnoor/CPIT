"""Course specification page (idempotent).

Writes course-specification.html: the course as delivered in Fall 2026, presented in the sections of
the ETEC/NCAAA course specification template (T-104, V2022), with the iSCARB teaching and assessment
framework mapped to each section. It links the page from the existing site pages, keeps the two
ETEC templates in assets/standards/ and registers the page in the public build and the site checks.

The approved course specification is held in the department course file; this page describes the
course as delivered and does not replace it.
"""
from pathlib import Path
from html import escape as E
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from course_shell import header, footer, dependencies, VERSION  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'course-specification.html'
STD = 'assets/standards/'
DATE = '24 October 2026'
CODE_NEW = 'IT 456 Dependable Systems'
TEMPLATES = {  # source path given on the command line (first run only) → published name
    't104en': 'ETEC-NCAAA-T-104-Course-Specification-V2022-EN.docx',
    't104ar': 'ETEC-NCAAA-T-104-Course-Specification-V2022-AR.docx',
}
WITHDRAWN = ['CPIT-455-Course-Specification-on-file-Fall-2024.pdf',
             'TVTC-HRDF-Supported-Professional-Certifications-Guide-2025.pdf']

# ---- iSCARB and the specification ---------------------------------------------------------------
ISCARB = [  # (element, what students do, T-104 section it serves, outcomes and domain)
    ('Split delivery', 'The lecture teaches the engineering mechanism; the consequential decision is made in a separate, bounded assignment.',
     'B · teaching strategies; C · course content', 'All CLOs'),
    ('Case-based lecture with source figures and three practice stations', 'Students work through a real case, the original source figures and three short practice stations in every chapter.',
     'B · teaching strategies', 'CLOs 1–10 · knowledge and skills'),
    ('FIT', 'Select the mechanism or option that is justified for the case.', 'B · assessment methods; D', 'Skills'),
    ('BOUND', 'Name the observable condition beyond which that choice stops being fit.', 'B · assessment methods; D', 'Skills; values, autonomy and responsibility'),
    ('ACT and EVIDENCE', 'Turn the judgment into a concrete action with a named accountable owner, and provide evidence another professional can inspect.',
     'B · assessment methods; D', 'Skills; values, autonomy and responsibility'),
    ('Python build in the weekly practical session', 'Write and run at least three tests, pass a mutation test against known faulty versions and complete a code-coverage step.',
     'B; C · practical hours; D', 'CLO 11 · skills'),
    ('Commit, then STRESS, then REFIT', 'Commit the initial reasoning before a changed condition is revealed, then retain, revise or replace the decision with justification.',
     'D · assessment design; F · effectiveness of student assessment', 'Values, autonomy and responsibility'),
    ('AI-use rules and declaration; human sign-off', 'Follow the AI rules for each step and declare any assistance; the final decision and wording remain the student\'s.',
     'F; NELC alignment', 'Values, autonomy and responsibility'),
    ('Micro-viva and in-class check', 'Explain and change one\'s own work in a short oral or written check.',
     'D; F · effectiveness of student assessment', 'Skills; values, autonomy and responsibility'),
    ('Four-level rubrics with calibration examples', 'Every criterion is assessed at 1, 0.75, 0.5 or 0, with strong and weak examples shown in advance.',
     'D; F · effectiveness of student assessment', 'All CLOs'),
]

# ---- B · course learning outcomes (wording of the specification on file) -------------------------
CLOS = [  # (domain, code, CLO no., text, SO, teaching strategies, assessment methods)
    ('1', '1.1', 7, 'Identify the elements involved in the re-use of code and describe an approach to software reuse based on the composition of standardized, reusable components', '6',
     'Case-based lecture; reuse-strategy station; primary source (Garlan, Allen and Ockerbloom 1995)', 'Assignment 6 (FIT, COMPARE, BOUND); final examination'),
    ('1', '1.2', 8, 'Describe an approach to software reuse based on the composition of standardized and reusable components', '6',
     'Case-based lecture; interface-contract station; primary source (Meyer 1992)', 'Assignment 7 (contract, BOUND, build); final examination'),
    ('1', '1.3', 9, 'Explain distributed systems engineering and distributed systems architectures', '6',
     'Case-based lecture; remote-failure station; primary source (Helland 2012)', 'Assignment 8 (remote-failure reasoning, build); final examination'),
    ('1', '1.4', 10, 'Explain the idea of a system of systems and discuss the challenges of building complex systems of software systems', '6',
     'Case-based lecture; staged-acceptance station; primary source (Maier 1998)', 'Assignment 9 (governance, BOUND, build); final examination'),
    ('2', '2.1', 1, 'Design dependability in systems by using redundancy and diversity', '2',
     'Case-based lecture; redundancy and common-cause station', 'Assignment 1 (FIT, BOUND, ACT and EVIDENCE); midterm examination'),
    ('2', '2.2', 2, 'Write functional and non-functional dependability and security requirements', '2',
     'Case-based lecture; requirement-writing station', 'Assignments 1, 2 and 4; midterm examination'),
    ('2', '2.3', 3, 'Apply metrics for reliability specification to specify measurable reliability requirements', '2',
     'Worked calculation (POFOD, ROCOF, MTTF, AVAIL); operational-profile station', 'Assignment 2 (MEASURE); midterm examination'),
    ('2', '2.4', 4, 'Design safety in safety-critical systems', '2',
     'Case-based lecture; hazard-trace station; primary source (Vesely et al. 1981)', 'Assignment 3 (TRACE, fault-tree build); midterm examination'),
    ('2', '2.5', 5, 'Design and test secure systems', '2',
     'Case-based lecture; misuse-case station; primary source (Saltzer and Schroeder 1975)', 'Assignment 4 (secure build, negative tests); midterm examination'),
    ('2', '2.6', 6, 'Design systems to support resilience', '2',
     'Case-based lecture; recovery station; primary source (Helland and Campbell 2009)', 'Assignment 5 (RECOVER, merge build); midterm examination'),
    ('2', '2.7', 11, 'Design and implementation of test cases in the different testing strategies', '2',
     'Weekly 90-minute practical session: Python build with tests, mutation testing and coverage', 'Build and TESTS RUN criteria, Assignments 3–9; micro-viva; final examination'),
]
DOMAINS = {'1': '1.0 · Knowledge and understanding · المعرفة والفهم', '2': '2.0 · Skills · المهارات'}

CONTENT = [  # (topic, weeks, number of weeks, chapter, assessment)
    ('Dependable systems', '1–2', 2, 'Chapter 10', 'Assignment 1'),
    ('Reliability engineering', '3–4', 2, 'Chapter 11', 'Assignment 2'),
    ('Safety engineering', '5', 1, 'Chapter 12', 'Assignment 3'),
    ('Security engineering', '6–7', 2, 'Chapter 13', 'Assignment 4'),
    ('Resilience engineering', '8–9', 2, 'Chapter 14', 'Assignment 5'),
    ('Software reuse', '10', 1, 'Chapter 15', 'Assignment 6'),
    ('Component-based software engineering', '11', 1, 'Chapter 16', 'Assignment 7'),
    ('Distributed software engineering', '12', 1, 'Chapter 17', 'Assignment 8'),
    ('Systems of systems', '13', 1, 'Chapter 20', 'Assignment 9'),
    ('Code coverage: testing strategies and levels, coverage tools', '14–15', 2, 'Practised in every Python build, Assignments 3–9', 'Coverage step, Assignments 3–9'),
]
ASSESS = [('Assignments 1–9 (written analysis and, from Assignment 3, a Python build)', 'After each chapter, weeks 2–14', 30),
          ('Midterm examination (written test)', 'Week 8', 30),
          ('Final examination (written test)', 'Final examination period', 30),
          ('Participation (preparation, in-class activities and questions)', 'Weeks 1–15', 10)]
MATRIX_COLS = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'Midterm', 'Final']
MATRIX = {1: {'A1', 'Midterm', 'Final'}, 2: {'A1', 'A2', 'A4', 'Midterm', 'Final'}, 3: {'A2', 'Midterm', 'Final'},
          4: {'A3', 'Midterm', 'Final'}, 5: {'A4', 'Midterm', 'Final'}, 6: {'A5', 'Midterm', 'Final'},
          7: {'A6', 'Final'}, 8: {'A7', 'Final'}, 9: {'A8', 'Final'}, 10: {'A9', 'Final'},
          11: {'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'Final'}}

SPAN = object()  # a row that spans the whole table, used for the domain headings


def table(head, rows, cls='stack'):
    h = ''.join(f'<th scope="col">{c}</th>' for c in head)
    b = ''.join(f'<tr><td class="dom" colspan="{len(head)}">{r[1]}</td></tr>' if r[0] == SPAN else
                '<tr>' + ''.join(f'<td data-label="{E(h_)}">{c}</td>' for h_, c in zip(head, r)) + '</tr>' for r in rows)
    return f'<div class="table-scroll"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


STYLE = '''<style>
.spec-toc{display:flex;flex-wrap:wrap;gap:6px 14px;margin:10px 0 0;padding:0;list-style:none}
.matrix td,.matrix th{text-align:center}.matrix td:first-child,.matrix th:first-child{text-align:left}
.spec-sub{margin-top:1.4rem}
.dom{background:color-mix(in srgb,var(--accent) 10%,transparent);font-weight:700}
@media (max-width:700px){.table-scroll table.stack{min-width:0}.stack thead{display:none}.stack,.stack tbody,.stack tr,.stack td{display:block;width:100%;box-sizing:border-box}
.stack tr{padding:10px 0;border-bottom:1px solid var(--line)}.stack td{border:0;padding:4px 12px;min-width:0!important}
.stack td:empty{display:none}.stack td[data-label]::before{content:attr(data-label);display:block;font-size:.75rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.stack td.dom::before{content:none}}
</style>'''


def build_page():
    iscarb_rows = [(f'<b>{E(a)}</b>', E(b), E(c), E(d)) for a, b, c, d in ISCARB]
    clo_rows, last = [], None
    for dom, code, n, text, so, strat, meth in CLOS:
        if dom != last:
            clo_rows.append((SPAN, DOMAINS[dom]))
            last = dom
        clo_rows.append((code, f'{E(text)} <small>(CLO {n})</small>', so, E(strat), E(meth)))
    content_rows = [(str(i + 1), E(t), wk, str(n * 3), E(c), E(a)) for i, (t, wk, n, c, a) in enumerate(CONTENT)]
    content_rows.append(('', '<b>Total</b>', '<b>15 weeks</b>', f'<b>{sum(n for _, _, n, _, _ in CONTENT) * 3}</b>', '', ''))
    assess_rows = [(str(i + 1), E(a), E(w), f'{p}%') for i, (a, w, p) in enumerate(ASSESS)]
    assess_rows.append(('', '<b>Total</b>', '', '<b>100%</b>'))
    mrows = []
    for n in range(1, 12):
        text = next(t for _, _, k, t, _, _, _ in CLOS if k == n)
        short = text if len(text) < 70 else text[:67].rsplit(' ', 1)[0] + '…'
        mrows.append([f'CLO {n} · {E(short)}'] + ['●' if c in MATRIX[n] else '' for c in MATRIX_COLS])

    t_doc = table(['Item', 'Detail'], [
        ('Course (current code)', 'Software Engineering (II) · CPIT-455'),
        ('Course in the revised IT program plan', f'<b>{CODE_NEW}</b> (elective)'),
        ('Program', 'Bachelor of Science in Information Technology'),
        ('Department and faculty', 'Department of Information Technology, Faculty of Computing and Information Technology, King Abdulaziz University'),
        ('Course coordinator and instructor', 'Prof. Adeeb Noor'),
        ('Version and date', f'Version 2.0 · {DATE}'),
        ('Scope', 'The course as delivered in Fall 2026. The approved course specification is held in the department course file.'),
    ])
    t_a = table(['Item', 'Detail'], [
        ('Course title and code', f'Software Engineering (II) · CPIT-455. In the revised IT program plan: {CODE_NEW}'),
        ('Program, department and faculty', 'Bachelor of Science in Information Technology · Department of Information Technology · Faculty of Computing and Information Technology, King Abdulaziz University'),
        ('Credit hours', '3 (theory 3, laboratory 0, practical 1)'),
        ('Course type', 'Department course · elective'),
        ('Pre-requisite and co-requisite', 'CPIT-251 · none'),
        ('Course topics', 'Dependable systems; reliability, safety, security and resilience engineering; software reuse; component-based software engineering; distributed software engineering; systems of systems; code coverage.'),
        ('Teaching mode', 'Traditional classroom instruction on campus: 100% of contact hours. The course website supports study and practice and does not replace classroom instruction.'),
        ('Contact hours per semester', 'Lectures 45 (3 hours × 15 weeks) · practical 22.5 (90 minutes × 15 weeks) · total 67.5'),
    ])
    t_e = table(['Item', 'Resources'], [
        ('Essential reference', 'I. Sommerville, <i>Software Engineering</i>, 10th edition, Pearson (ISBN 9780133943030), the latest edition.'),
        ('Supportive references', 'W. E. Vesely et al., <i>Fault Tree Handbook</i> (NUREG-0492), 1981 · J. H. Saltzer and M. D. Schroeder, “The Protection of Information in Computer Systems,” <i>Proceedings of the IEEE</i>, 1975 · P. Helland and D. Campbell, “Building on Quicksand,” CIDR, 2009 · D. Garlan, R. Allen and J. Ockerbloom, “Architectural Mismatch: Why Reuse Is So Hard,” <i>IEEE Software</i>, 1995 · B. Meyer, “Applying ‘Design by Contract’,” <i>IEEE Computer</i>, 1992 · P. Helland, “Idempotence Is Not a Medical Condition,” <i>ACM Queue</i>, 2012 · M. W. Maier, “Architecting Principles for Systems-of-Systems,” <i>Systems Engineering</i>, 1998'),
        ('Electronic materials', 'The course website: nine lectures, a source ledger for each chapter, nine assessed assignments and offline packages (<a href="course-resources.html">Course &amp; sources</a>); Blackboard for announcements, submissions and grades'),
        ('Other learning materials', 'The original slide packs and the textbook chapters, linked for each chapter'),
        ('Facilities', 'Lecture room; the weekly 90-minute practical session'),
        ('Technology equipment', 'Projector; a current web browser. Python runs within the browser without installation.'),
    ])
    t_f = table(['Assessment area', 'Assessor', 'Assessment method'], [
        ('Effectiveness of teaching', 'Students; course coordinator', 'University course-evaluation survey (indirect); coordination meetings and peer review (direct)'),
        ('Effectiveness of student assessment', 'Faculty', 'Four-level rubrics with calibration examples; commit before STRESS; micro-viva and in-class check of the written work against the student\'s explanation (direct)'),
        ('Quality of learning resources', 'Students; faculty', 'Survey (indirect); review of each chapter\'s source ledger against the textbook and slide pack (direct)'),
        ('Extent to which CLOs are achieved', 'Faculty; program leadership', 'Rubric criteria and examination items mapped to CLOs (section 3), reported in the end-of-semester course report (direct)'),
        ('AI-supported learning', 'Faculty', 'AI-use declarations and the NELC alignment (indirect)'),
    ])
    so_note = ('<p><b>Student outcomes.</b> <b>SO 2</b> · Design, implement, and evaluate a computing-based solution to meet a given '
               'set of computing requirements in the context of the program’s discipline. <b>SO 6 (IT)</b> · Use systemic approaches '
               'to select, develop, apply, integrate, and administer secure computing technologies to accomplish user goals.</p>'
               '<p><b>Values, autonomy and responsibility.</b> The course develops this domain through the iSCARB framework (section 1): '
               'students name the accountable owner of each decision, state its limits, declare any AI assistance, and revise their '
               'decision when new evidence arrives.</p>')

    main = f'''<main class="wrap" id="main"><div class="document-heading"><p class="ey">COURSE SPECIFICATION · ETEC T-104 STRUCTURE · FALL 2026</p>
<h1>Course Specification<br><em>CPIT-455 · {CODE_NEW} in the revised plan</em></h1>
<p class="intro">The course as delivered in Fall 2026, presented in the sections of the course specification template of the Education and Training Evaluation Commission (ETEC, T-104), with the iSCARB teaching and assessment framework mapped to each section.</p></div>
<section class="panel" id="document-control"><h2>Document control <span class="vs-ar-t" lang="ar" dir="rtl">بيانات الوثيقة</span></h2>
{t_doc}</section>
<section class="panel" lang="ar" dir="rtl" id="summary-ar"><h2>نبذة</h2>
<p>تعرض هذه الصفحة مقرر هندسة البرمجيات (2)، ورمزه الحالي CPIT-455، ويقابله في الخطة الدراسية المحدثة لبرنامج تقنية المعلومات المقرر الاختياري <b>IT 456 Dependable Systems</b>. ويُعرض المقرر كما يُدرَّس في الفصل الدراسي الأول 1448هـ وفق أقسام نموذج توصيف المقرر الصادر عن هيئة تقويم التعليم والتدريب (T-104)، مع بيان إسهام إطار iSCARB في طرق التدريس والتقييم ومجالات الإطار الوطني للمؤهلات. أما توصيف المقرر المعتمد فمحفوظ في ملف المقرر بالقسم.</p></section>
<nav aria-label="Contents"><ul class="spec-toc"><li><a href="#iscarb">1 · iSCARB and the specification</a></li><li><a href="#spec">2 · Course specification (A–G)</a></li><li><a href="#matrix">3 · Mapping of CLOs to assessments</a></li><li><a href="#it456">4 · {CODE_NEW}</a></li><li><a href="#attachments">5 · Reference documents</a></li></ul></nav>

<section class="section" id="iscarb"><h2>1 · iSCARB and the course specification <span class="vs-ar-t" lang="ar" dir="rtl">إطار iSCARB وتوصيف المقرر</span></h2>
<p>iSCARB (Interactive System for Case-based Analysis, Reasoning &amp; Boundaries) is the teaching and assessment framework of this course. Class time teaches the engineering mechanism; a separate, bounded assignment asks each student to own, bound and defend a decision with inspectable evidence, and the final sign-off remains human. The table shows which section of the specification each element serves. See also <a href="methodology.html">the iSCARB methodology</a> and <a href="nelc-alignment.html">the Saudi alignment page</a>.</p>
{table(['iSCARB element', 'What students do', 'Specification section', 'Outcomes and NQF domain'], iscarb_rows)}</section>

<section class="section" id="spec"><h2>2 · Course specification, ETEC T-104 structure <span class="vs-ar-t" lang="ar" dir="rtl">توصيف المقرر وفق نموذج الهيئة</span></h2>
<p>The wording of the course learning outcomes is that of the course specification on file.</p>
<h3 class="spec-sub" id="spec-a">A · General information about the course</h3>
{t_a}
<h3 class="spec-sub" id="spec-b">B · Course learning outcomes, teaching strategies and assessment methods</h3>
{table(['Code', 'Course learning outcome', 'Student outcome', 'Teaching strategies', 'Assessment methods'], clo_rows)}
{so_note}
<h3 class="spec-sub" id="spec-c">C · Course content</h3>
{table(['No', 'Topic', 'Weeks', 'Contact hours', 'On the website', 'Assessed in'], content_rows)}
<h3 class="spec-sub" id="spec-d">D · Student assessment activities, Fall 2026</h3>
{table(['No', 'Assessment activity', 'Timing', 'Weight'], assess_rows)}
<p>How assignment points are converted to marks is explained in <a href="assignment-example.html#grading">How the course is graded</a>.</p>
<h3 class="spec-sub" id="spec-e">E · Learning resources and facilities</h3>
{t_e}
<h3 class="spec-sub" id="spec-f">F · Assessment of course quality</h3>
{t_f}
<h3 class="spec-sub" id="spec-g">G · Specification approval data</h3>
<p>The approved course specification is held in the department course file. This page, prepared by the course coordinator on {DATE}, describes the course as delivered in Fall 2026.</p></section>

<section class="section" id="matrix"><h2>3 · Mapping of course learning outcomes to assessments <span class="vs-ar-t" lang="ar" dir="rtl">ربط مخرجات التعلم بأدوات التقييم</span></h2>
<p>● indicates that the outcome is assessed directly in that assessment. Assignment 1 corresponds to Chapter 10, Assignment 2 to Chapter 11, and so on to Assignment 9, which corresponds to Chapter 20.</p>
{table(['Course learning outcome'] + MATRIX_COLS, mrows, 'matrix')}</section>

<section class="section" id="it456"><h2>4 · {CODE_NEW} in the revised IT program plan <span class="vs-ar-t" lang="ar" dir="rtl">المقرر في الخطة المحدثة</span></h2>
<p>In the revised IT program plan, CPIT-455 corresponds to the elective course <b>{CODE_NEW}</b>, which covers dependability, reliability, safety, security and resilience engineering.</p></section>

<section class="section" id="attachments"><h2>5 · Reference documents <span class="vs-ar-t" lang="ar" dir="rtl">الوثائق المرجعية</span></h2>
{table(['Document', 'Note'], [
        (f'<a href="{STD}{TEMPLATES["t104en"]}">ETEC/NCAAA T-104 Course Specification template, V2022 (English, Word)</a>', 'Official template, as distributed by the Deanship of Quality, King Saud University.'),
        (f'<a href="{STD}{TEMPLATES["t104ar"]}">ETEC/NCAAA T-104 توصيف المقرر، إصدار 2022 (عربي، Word)</a>', 'Arabic version of the same template.'),
        ('<a href="methodology.html">iSCARB methodology</a>', 'The teaching and assessment framework of the course.'),
        ('<a href="nelc-alignment.html">Saudi alignment</a>', 'Jaheziah and NELC alignment of every chapter.'),
    ])}</section>
</main>'''

    head = ('<!DOCTYPE html>\n<html data-iscarb-standalone="1" data-theme="dark" lang="en"><head><meta charset="utf-8">'
            '<meta content="width=device-width,initial-scale=1" name="viewport"><meta content="#006b62" name="theme-color">'
            '<meta content="Course specification of CPIT-455 (IT 456 Dependable Systems in the revised IT plan) in the ETEC T-104 structure, with the iSCARB teaching and assessment framework." name="description">'
            '<title>Course specification · CPIT-455 (IT 456) · iSCARB</title>'
            f'<link href="iscarb-hub.css?v={VERSION}" rel="stylesheet"><link rel="stylesheet" href="course-design.css?v={VERSION}">'
            + dependencies() + STYLE + '</head>')
    body = ('<body class="course-page" id="top"><a class="skip" href="#main">Skip to content</a>'
            + header('', 'course-resources.html') + '\n' + main + footer('') + '</body></html>\n')
    PAGE.write_text(head + body, encoding='utf-8')


# ---- Links from the existing pages, and the build registration -------------------------------
LINK_MARK = '<!-- course-specification:link -->'
LINK = (LINK_MARK + '<section class="panel" id="course-specification"><p class="ey">COURSE SPECIFICATION · ETEC T-104</p>'
        '<h2>Course specification</h2><p>CPIT-455 Software Engineering (II), which corresponds to <b>IT 456 Dependable Systems</b> '
        'in the revised IT program plan, presented in the sections of the ETEC course specification template, with the iSCARB '
        'teaching and assessment framework mapped to each section. <a href="course-specification.html"><b>Open the course specification</b></a>.</p>'
        '<p lang="ar" dir="rtl">مقرر هندسة البرمجيات (2) CPIT-455، ويقابله في الخطة المحدثة لبرنامج تقنية المعلومات المقرر '
        'IT 456 Dependable Systems، معروضاً وفق أقسام نموذج توصيف المقرر الصادر عن هيئة تقويم التعليم والتدريب، مع إطار iSCARB. '
        '<a href="course-specification.html">الاطلاع على توصيف المقرر</a>.</p></section>')
# The Saudi alignment page is English only (tools/check-readable-course.cjs): no Arabic line there.
LINK_EN = LINK[:LINK.index('<p lang="ar"')] + '</section>'
GRADE_MARK = '<!-- course-specification:grades -->'
GRADE_LINK = (GRADE_MARK + '<p>The full course specification, in the ETEC T-104 structure: '
              '<a href="course-specification.html">course specification</a>. '
              '<span lang="ar" dir="rtl">توصيف المقرر كاملاً: <a href="course-specification.html">توصيف المقرر</a>.</span></p>')


def put_block(t, block):
    """Replace an earlier version of the marked block in place."""
    mark = block[:block.index('-->') + 3]
    i = t.index(mark)
    close = '</section>' if block.endswith('</section>') else '</p>'
    j = t.index(close, i) + len(close)
    return t[:i] + block + t[j:]


def insert_between(rel, left, right, block):
    """Insert block between two adjacent strings that occur together exactly once; refresh it if already there."""
    p = ROOT / rel
    t = p.read_text(encoding='utf-8')
    if block[:block.index('-->') + 3] in t:
        p.write_text(put_block(t, block), encoding='utf-8')
        return
    assert t.count(left + right) == 1, f'{rel}: anchor found {t.count(left + right)} times'
    p.write_text(t.replace(left + right, left + block + right), encoding='utf-8')


def link_pages():
    insert_between('course-resources.html', '</section>', '<section class="section" id="outcomes">', LINK)
    insert_between('instructor-guide.html', '</div>', '<section class="panel" id="use-iscarb">', LINK)
    t = (ROOT / 'nelc-alignment.html').read_text(encoding='utf-8')
    if LINK_MARK in t:
        t = put_block(t, LINK_EN)
    else:
        a = t.index('<section class="national-hero">')
        b = t.index('</section>', a) + len('</section>')
        t = t[:b] + LINK_EN + t[b:]
    (ROOT / 'nelc-alignment.html').write_text(t, encoding='utf-8')
    for rel in ('student-guide.html', 'assignment-example.html'):
        insert_between(rel, '<!-- lab-credit:end -->', '\n', GRADE_LINK)


def register():
    p = ROOT / 'tools/build_public_site.py'
    t = p.read_text(encoding='utf-8')
    if "'course-specification.html'" not in t:
        t = t.replace("'assignment-example.html',", "'assignment-example.html','course-specification.html',", 1)
    line = "    shutil.copytree(ROOT/'assets/standards',DEST/'assets/standards')  # documents attached to course-specification.html\n"
    anchor = "    shutil.copytree(ROOT/'assets/guide',DEST/'assets/guide')  # pictures for the visual assignment guide\n"
    if line not in t:
        assert anchor in t
        t = t.replace(anchor, anchor + line)
    p.write_text(t, encoding='utf-8')
    p = ROOT / 'tools/audit_classroom.py'
    t = p.read_text(encoding='utf-8')
    if '"course-specification.html"' not in t:
        t = t.replace('"nelc-alignment.html", "download.html",', '"nelc-alignment.html", "course-specification.html", "download.html",', 1)
        p.write_text(t, encoding='utf-8')
    p = ROOT / 'tools/check-site-design.cjs'
    t = p.read_text(encoding='utf-8')
    if "'course-specification.html'" not in t:
        t = t.replace("'nelc-alignment.html','methodology.html',", "'nelc-alignment.html','course-specification.html','methodology.html',", 1)
        p.write_text(t, encoding='utf-8')


def attachments(args):
    """args: key=path pairs for the two ETEC templates (first run only). Withdrawn documents are removed."""
    (ROOT / STD).mkdir(parents=True, exist_ok=True)
    given = dict(a.split('=', 1) for a in args)
    for key, name in TEMPLATES.items():
        dest = ROOT / STD / name
        if key in given:
            shutil.copyfile(given[key], dest)
        assert dest.exists(), f'missing template {name}: pass {key}=<path> on the first run'
    for name in WITHDRAWN:
        (ROOT / STD / name).unlink(missing_ok=True)


# Wording on Course & sources that predates the course specification page.
WORDING = [
    ('course-resources.html', 'Nine published chapters, one source ledger per chapter, and a visible course-level gap.',
     'Nine published chapters, one source ledger per chapter, and the course-outcome map.'),
    ('course-resources.html', 'The course syllabus on file is labelled Fall 2024 and lists 11 course learning outcomes. Its topic allocation guides '
     'the learning-path organization. This website does not declare a replacement syllabus: follow the current LMS for grades, deadlines, '
     'rooms and the official timetable.',
     'The approved course specification lists 11 course learning outcomes, and its topic allocation guides the learning path. The course '
     'as delivered is presented in the <a href="course-specification.html">course specification</a>. Grades, deadlines, rooms and the '
     'official timetable are announced in Blackboard.'),
]


def reword():
    for rel, old, new in WORDING:
        p = ROOT / rel
        t = p.read_text(encoding='utf-8')
        if old in t:
            assert t.count(old) == 1, rel
            p.write_text(t.replace(old, new), encoding='utf-8')
        assert new in p.read_text(encoding='utf-8'), f'{rel}: wording not applied'
    # keep the legacy generator consistent, so a rerun does not bring the old wording back
    g = ROOT / 'tools/build_learning_hub.py'
    t = g.read_text(encoding='utf-8')
    for _, old, new in WORDING:
        t = t.replace(old, new)
    g.write_text(t, encoding='utf-8')


if __name__ == '__main__':
    attachments(sys.argv[1:])
    build_page()
    link_pages()
    reword()
    register()
    print('Course specification page, links and registration applied')
