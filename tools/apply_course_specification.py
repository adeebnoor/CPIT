"""Course specification and alignment page (idempotent).

Writes course-specification.html: a gap analysis of the CPIT-455 site against the college and
department requirements and the ETEC/NCAAA course specification template (T-104, V2022), the
course specification in the T-104 structure (sections A–G) as taught in Fall 2026, a CLO-by-
assessment matrix, and the professional-certification alignment with the TVTC/HRDF guide (2025).
It links the page from the existing site pages, copies the attachments to assets/standards/ and
registers the page in the public build and the site checks.

Sources (23 October 2026):
- CPIT-455 course file, course specifications (syllabus), Fall 2024, last articulated 12 Oct 2023.
- Head of the IT Department, First Semester Guidelines 1448 H (27 Aug 2026).
- Bachelor's Curriculum Development Committee, course specification review and professional
  certification alignment (22 Oct 2026); revised IT plan: CPIT-455 corresponds to IT 456.
- ETEC/NCAAA T-104 Course Specification, V2022 (English and Arabic templates).
- TVTC and HRDF, Supported Professional Certifications Guide, 2025, second edition.
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
DATE = '23 October 2026'
SCRATCH_ATTACHMENTS = {  # source path given on the command line → published name
    'cert': 'TVTC-HRDF-Supported-Professional-Certifications-Guide-2025.pdf',
    'spec': 'CPIT-455-Course-Specification-on-file-Fall-2024.pdf',
    't104en': 'ETEC-NCAAA-T-104-Course-Specification-V2022-EN.docx',
    't104ar': 'ETEC-NCAAA-T-104-Course-Specification-V2022-AR.docx',
}

MET, PART, OPEN = 'met', 'partly', 'open'
LABEL = {MET: 'Met', PART: 'Partly met', OPEN: 'Open'}
LABEL_AR = {MET: 'مستوفى', PART: 'مستوفى جزئياً', OPEN: 'مفتوح'}

# ---- 1. The requirements used --------------------------------------------------------------
SOURCES = [
    ('ETEC / NCAAA', 'T-104 Course Specification template, version 2022',
     'Sections A–G: general information, teaching mode and contact hours; CLOs in three domains '
     '(knowledge and understanding; skills; values, autonomy and responsibility) aligned with program '
     'outcomes, each with teaching strategies and assessment methods; course content with contact hours; '
     'assessment activities with week and weight; learning resources and facilities; assessment of course '
     'quality; approval data.',
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["t104en"]}">English template</a> · '
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["t104ar"]}">Arabic template</a>'),
    ('IT Department, FCIT', 'CPIT-455 course specifications (course file), Fall 2024, last articulated 12 October 2023',
     'The 11 CLOs and their student outcomes (2 and 6), the topic weeks, the grade distribution, the textbook, '
     'credit (3: theory 3, practical 1) and the weekly 90-minute lab/tutorial.',
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["spec"]}">Specification on file (PDF)</a>'),
    ('Head of the IT Department', 'First Semester Guidelines 1448 H, 27 August 2026',
     'One grading policy, syllabus and weekly schedule per the Articulation Matrix, the same grade distribution '
     'in all sections, the syllabus available to students in the first week, students kept informed of their '
     'grades, posted office hours, at least three coordination meetings, and the previous end-of-semester report.',
     'Summarised here (internal email)'),
    ('Bachelor\'s Curriculum Development Committee', 'Course specification review and certification alignment, 22 October 2026',
     'Update course specifications, including the latest textbook editions and references, and record for each '
     'certification its issuer, the course topics it covers and does not cover, a coverage percentage and a '
     'recommendation. In the revised IT plan CPIT-455 corresponds to the elective IT 456 Dependable Systems.',
     'Summarised here (internal email)'),
    ('TVTC and HRDF', 'Supported Professional Certifications Guide for the ICT sector, 2025, second edition',
     'The supported certifications by field, each with its issuer and the maximum HRDF compensation.',
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["cert"]}">Guide (PDF, 6.5 MB)</a>'),
]

# ---- 2. Gap analysis: (requirement, source, finding before, action on the site, status) ------
GAPS = [
    ('Course specification in the ETEC T-104 structure, visible to students', 'ETEC T-104; department: syllabus in week 1',
     'The site had a CLO map only. The specification itself was not on the site.',
     'Sections A–G below for CPIT-455 as taught in Fall 2026, with the specification on file attached.', MET),
    ('CLOs classified into the three NQF domains', 'ETEC T-104 section B',
     'The specification on file lists 11 CLOs without domains. No CLO is in the values, autonomy and responsibility domain.',
     'Each CLO is placed in its domain (B). A values CLO is proposed for the revised specification; the site already '
     'produces its evidence (named owner, AI-use declaration, REFIT, in-class check).', PART),
    ('Each CLO linked to teaching strategies and assessment methods', 'ETEC T-104 section B',
     'The site showed where each CLO is taught, not how it is assessed.',
     'Strategies and methods per CLO (B) and a CLO-by-assessment matrix (section 4).', MET),
    ('CLOs aligned with program outcomes', 'ETEC T-104 section B; specification on file',
     'Student outcomes 2 and 6 were not shown on the site.',
     'Shown for every CLO as recorded in the specification on file. The revised plan\'s outcome codes are not available here.', PART),
    ('Number and wording of CLOs', 'ETEC guidance on measurable CLOs',
     'CLO 7 and CLO 8 overlap (both describe reuse by composing standardized components); CLO 10 has a typing error ("systes").',
     'Recommendation 2 below: merge CLO 7 and 8 and correct CLO 10 in the next specification.', OPEN),
    ('Course content with contact hours', 'ETEC T-104 section C; specification on file',
     'The site did not show topic weeks or contact hours.',
     'Topics, weeks and contact hours (C), with the site chapter and assignment for each topic.', MET),
    ('Code Coverage topic (2 weeks in the specification)', 'Specification on file',
     'Taught inside the builds of Assignments 3–9 since 15 October 2026, not as two lecture weeks.',
     'Recorded in C as a delivery change, to be reported in the end-of-semester course report.', PART),
    ('Assessment activities, timing and weights the same as the Articulation Matrix and in all sections', 'ETEC T-104 section D; department guidelines',
     'The site publishes assignments 30, midterm 30, final 30, participation 10. The specification on file lists homework 10, '
     'exam 1 30, group project 20, graded lab work 10, final exam 30.',
     'Both are shown side by side in D. Weights are not changed mid-semester; the coordinator confirms the weights in this '
     'semester\'s Articulation Matrix and the coordination record.', OPEN),
    ('Latest textbook edition and references', 'Curriculum Development Committee',
     'The site used Sommerville, 10th edition.',
     'Checked: the 10th edition is the latest (Pearson eText 2021, © 2016); no 11th edition found. The seven primary '
     'sources used in the assignments are listed as supportive references (E).', MET),
    ('Catalog description matches the course', 'ETEC T-104 section A',
     'The description on file names topics the course no longer teaches (team management, cost estimation, quality '
     'management, process and re-engineering) and omits dependability, safety, security and resilience.',
     'A replacement description is proposed (recommendation 1). It needs department approval.', OPEN),
    ('Learning resources, facilities and equipment', 'ETEC T-104 section E',
     'Not stated on the site.', 'Listed in E, including the in-browser Python runner that needs no installation.', MET),
    ('Plan to assess course quality', 'ETEC T-104 section F',
     'Not stated on the site.', 'Areas, assessors and direct or indirect methods in F.', MET),
    ('Professional certification alignment', 'Curriculum Development Committee; TVTC/HRDF guide',
     'Not on the site.',
     'Section 5: six certifications from the guide with issuer, covered and uncovered topics, coverage estimate and '
     'recommendation. None supports course equivalency.', MET),
    ('Correspondence with IT 456 Dependable Systems in the revised plan', 'Curriculum Development Committee',
     'Not on the site.',
     'Section 6 records the correspondence. A clause-by-clause crosswalk waits for the IT 456 specification file.', PART),
    ('Office hours posted', 'Department guidelines', 'Not on the site.', 'To be added with the instructor\'s hours.', OPEN),
    ('Students kept informed of their grades', 'Department guidelines',
     'Grades are released in Blackboard; the site explains how assignment points become marks.', 'No change needed.', MET),
    ('At least three coordination meetings; Articulation Matrix updated', 'Department guidelines',
     'A coordinator and committee record, not a website item.', 'Listed in the course-file checklist (section 7).', OPEN),
    ('AI-supported learning design', 'NELC framework, September 2026 (already on the site)',
     'Aligned on the Saudi alignment page since 28 September 2026.', 'No change.', MET),
]

# ---- 3. Course specification, T-104 structure ------------------------------------------------
CLOS = [  # (domain code, ETEC code, CLO no. on file, CLO text on file, SO, strategies, assessment)
    ('1', '1.1', 7, 'Identify the elements involved in the re-use of code and describe an approach to software reuse '
     'based on the composition of standardized, reusable components', '6',
     'Story-led lecture with a real case; reuse-strategy station; primary source (Garlan, Allen and Ockerbloom 1995)',
     'Assignment 6 rubric (FIT with the AI-draft critique, COMPARE, BOUND); final exam items'),
    ('1', '1.2', 8, 'Describe an approach to software reuse based on the composition of standardized and reusable components', '6',
     'Lecture; interface-contract station; primary source (Meyer 1992)',
     'Assignment 7 rubric (contract, BOUND, build); final exam items'),
    ('1', '1.3', 9, 'Explain distributed systems engineering and distributed systems architectures', '6',
     'Lecture; remote-failure station; primary source (Helland 2012)',
     'Assignment 8 rubric (remote-failure reasoning, build with a retry test); final exam items'),
    ('1', '1.4', 10, 'Explain the idea of a system of systems and discuss the challenges of building complex systems of software systems', '6',
     'Lecture; staged-acceptance station; primary source (Maier 1998)',
     'Assignment 9 rubric (governance, BOUND, build); final exam items'),
    ('2', '2.1', 1, 'Design dependability in systems by using redundancy and diversity', '2',
     'Lecture with a real failure case; redundancy and common-cause station',
     'Assignment 1 rubric (FIT, BOUND, ACT + EVIDENCE); midterm items'),
    ('2', '2.2', 2, 'Write functional and non-functional dependability and security requirements', '2',
     'Lecture; requirement-writing station with write-before-reveal',
     'Assignments 1, 2 and 4 (requirement and evidence rows); midterm items'),
    ('2', '2.3', 3, 'Apply metrics for reliability specification to specify measurable reliability requirements', '2',
     'Worked calculation (POFOD, ROCOF, MTTF, AVAIL) and operational-profile station',
     'Assignment 2 MEASURE row; midterm calculation items'),
    ('2', '2.4', 4, 'Design safety in safety-critical systems', '2',
     'Lecture; hazard-trace station; primary source (Vesely et al., Fault Tree Handbook, 1981)',
     'Assignment 3 TRACE row and fault-tree build; midterm items'),
    ('2', '2.5', 5, 'Design and test secure systems', '2',
     'Lecture; misuse-case station; primary source (Saltzer and Schroeder 1975)',
     'Assignment 4 build (complete mediation, fail-safe defaults) and negative tests; midterm items'),
    ('2', '2.6', 6, 'Design systems to support resilience', '2',
     'Lecture; recovery station; primary source (Helland and Campbell 2009)',
     'Assignment 5 RECOVER row and merge build; midterm items'),
    ('2', '2.7', 11, 'Design and implementation of test cases in the different testing strategies', '2',
     'Weekly 90-minute practical session: Python build with at least three tests, a mutation test and a coverage step',
     'Build and TESTS RUN rows in Assignments 3–9; micro-viva; in-class check (Assignments 6–9); final exam items'),
]
DOMAINS = {'1': '1.0 · Knowledge and understanding · المعرفة والفهم', '2': '2.0 · Skills · المهارات',
           '3': '3.0 · Values, autonomy and responsibility · القيم والاستقلالية والمسؤولية'}
VALUES_PROPOSED = ('3.1', 'Proposed: take responsibility for an engineering decision by naming the accountable owner, '
                   'disclosing any AI assistance and revising the decision when new evidence arrives.',
                   'Named owner in ACT; AI-use declaration; commit before STRESS, then REFIT',
                   'ACT and REFIT rubric rows; AI-use declaration; in-class check (Assignments 6–9). Not a separate CLO on file.')

CONTENT = [  # (topic, weeks on file, chapter on the site, assignment)
    ('Dependable systems', 2, 'Chapter 10', 'Assignment 1'),
    ('Reliability engineering', 2, 'Chapter 11', 'Assignment 2'),
    ('Safety engineering', 1, 'Chapter 12', 'Assignment 3'),
    ('Security engineering', 2, 'Chapter 13', 'Assignment 4'),
    ('Resilience engineering', 2, 'Chapter 14', 'Assignment 5'),
    ('Software reuse', 1, 'Chapter 15', 'Assignment 6'),
    ('Component-based software engineering', 1, 'Chapter 16', 'Assignment 7'),
    ('Distributed software engineering', 1, 'Chapter 17', 'Assignment 8'),
    ('Systems of systems', 1, 'Chapter 20', 'Assignment 9'),
    ('Code coverage', 2, 'Inside every build, Assignments 3–9', 'Coverage step in Assignments 3–9'),
]
ASSESS_FILE = [('Homework assignments', '7', 10), ('Exam 1', '8', 30), ('Group project', '15', 20),
               ('Graded lab work', '15', 10), ('Final exam', '16', 30)]
ASSESS_NOW = [('Assignments 1–9 (written work and, from Assignment 3, the Python build)', 'After each chapter, weeks 2–14', 30),
              ('Midterm exam (written test)', 'Week 8 (20 October 2026)', 30),
              ('Final exam (written test)', 'Final examination period', 30),
              ('Participation (preparation, stations and explain-it questions)', 'Weeks 1–15', 10)]

MATRIX_COLS = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'Midterm', 'Final']
MATRIX = {1: {'A1', 'Midterm', 'Final'}, 2: {'A1', 'A2', 'A4', 'Midterm', 'Final'}, 3: {'A2', 'Midterm', 'Final'},
          4: {'A3', 'Midterm', 'Final'}, 5: {'A4', 'Midterm', 'Final'}, 6: {'A5', 'Midterm', 'Final'},
          7: {'A6', 'Final'}, 8: {'A7', 'Final'}, 9: {'A8', 'Final'}, 10: {'A9', 'Final'},
          11: {'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'Final'}}

# ---- 5. Certifications from the TVTC/HRDF guide (instructor estimate of CPIT-455 content covered) ----
CERTS = [
    ('ISTQB Certified Tester Foundation Level (CTFL) v4.0', 'ISTQB', '7,000',
     'Test levels and types, test design techniques, coverage, test planning (CLO 11)',
     'Dependability, reliability metrics, safety, security and resilience engineering, reuse, CBSE, distributed systems, systems of systems',
     '10%'),
    ('CompTIA Security+', 'CompTIA', '11,525',
     'Threats, vulnerabilities and attacks, access control, secure design principles, incident response (CLO 2 in part, CLO 5)',
     'Dependability, reliability metrics, safety, resilience, reuse, CBSE, distributed systems, systems of systems, test design',
     '15%'),
    ('BCS Certificate in Information Security Management Principles (CISMP)', 'BCS', '10,000',
     'Security policy, risk and controls (CLO 2 and CLO 5 in part)',
     'All engineering topics outside information-security management; no design or testing of systems',
     '5–10%'),
    ('ISO/IEC 27001', 'PECB', '7,000',
     'Information-security controls and risk treatment (CLO 2 in part)',
     'Everything except security management controls',
     '5%'),
    ('ISACA CRISC', 'ISACA', '7,250',
     'Risk identification, assessment and response (safety and security risk, CLO 4 and CLO 5 in part)',
     'Design, metrics, testing, reuse, distributed systems, systems of systems',
     '5%'),
    ('AWS Certified Solutions Architect – Associate', 'AWS', '5,900',
     'Resilient and highly available architectures, redundancy, fault isolation in the cloud (CLO 1, CLO 6 and CLO 9 in part)',
     'Reliability metrics, safety, security requirements, reuse and CBSE, systems of systems, test design',
     '10–15%'),
]

ATTACH = [
    (SCRATCH_ATTACHMENTS['t104en'], 'ETEC/NCAAA T-104 Course Specification template, V2022 (English, Word)',
     'Copy of the official template as distributed by the KSU Deanship of Quality.'),
    (SCRATCH_ATTACHMENTS['t104ar'], 'ETEC/NCAAA T-104 توصيف المقرر، إصدار 2022 (عربي، Word)',
     'Arabic version of the same template.'),
    (SCRATCH_ATTACHMENTS['spec'], 'CPIT-455 course specifications on file, Fall 2024 (PDF)',
     'Department course file, last articulated 12 October 2023. The authority for CLOs until a revised specification is approved.'),
    (SCRATCH_ATTACHMENTS['cert'], 'TVTC and HRDF Supported Professional Certifications Guide, 2025 (PDF, 6.5 MB)',
     'دليل الشهادات المهنية الاحترافية المدعومة في قطاع الاتصالات وتقنية المعلومات، النسخة الثانية 2025.'),
]


SPAN = object()  # a row that spans the whole table, used for the domain headings


def pill(s):
    return f'<span class="st st-{s}">{LABEL[s]} · <span lang="ar" dir="rtl">{LABEL_AR[s]}</span></span>'


def table(head, rows, cls='stack'):
    h = ''.join(f'<th scope="col">{c}</th>' for c in head)
    b = ''.join(f'<tr><td class="dom" colspan="{len(head)}">{r[1]}</td></tr>' if r[0] == SPAN else
                '<tr>' + ''.join(f'<td data-label="{E(h_)}">{c}</td>' for h_, c in zip(head, r)) + '</tr>' for r in rows)
    return f'<div class="table-scroll"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


STYLE = '''<style>
.st{display:inline-block;white-space:nowrap;font-size:.8rem;font-weight:700;padding:2px 8px;border-radius:999px;border:1px solid currentColor}
.st-met{color:var(--green)}.st-partly{color:var(--gold)}.st-open{color:var(--red)}
.spec-counts{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 0}
.spec-toc{display:flex;flex-wrap:wrap;gap:6px 14px;margin:10px 0 0;padding:0;list-style:none}
.gaps td:first-child{min-width:12rem}.gaps td:nth-child(3),.gaps td:nth-child(4){min-width:16rem}
.matrix td,.matrix th{text-align:center}.matrix td:first-child,.matrix th:first-child{text-align:left}
.spec-sub{margin-top:1.4rem}
.dom{background:color-mix(in srgb,var(--accent) 10%,transparent);font-weight:700}
.prop{font-style:italic}
@media (max-width:700px){.table-scroll table.stack{min-width:0}.stack thead{display:none}.stack,.stack tbody,.stack tr,.stack td{display:block;width:100%;box-sizing:border-box}
.stack tr{padding:10px 0;border-bottom:1px solid var(--line)}.stack td{border:0;padding:4px 12px;min-width:0!important}
.stack td:empty{display:none}.stack td[data-label]::before{content:attr(data-label);display:block;font-size:.75rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.stack td.dom::before{content:none}}
</style>'''


def build_page():
    counts = {s: sum(1 for g in GAPS if g[4] == s) for s in (MET, PART, OPEN)}
    gap_rows = [(f'<b>{E(r)}</b>', E(src), E(f), E(a), pill(s)) for r, src, f, a, s in GAPS]
    src_rows = [(f'<b>{E(o)}</b>', E(t), E(w), att) for o, t, w, att in SOURCES]

    clo_rows, last = [], None
    for dom, code, n, text, so, strat, meth in CLOS:
        if dom != last:
            clo_rows.append((SPAN, DOMAINS[dom]))
            last = dom
        clo_rows.append((code, f'{E(text)} <small>(CLO {n} on file)</small>', so, E(strat), E(meth)))
    clo_rows.append((SPAN, DOMAINS['3']))
    code, text, strat, meth = VALUES_PROPOSED
    clo_rows.append((code, f'<span class="prop">{E(text)}</span>', '—', E(strat), E(meth)))

    content_rows = [(str(i + 1), E(t), str(w), str(w * 3), E(c), E(a)) for i, (t, w, c, a) in enumerate(CONTENT)]
    content_rows.append(('', '<b>Total</b>', '<b>15</b>', f'<b>{sum(w for _, w, _, _ in CONTENT) * 3}</b>', '', ''))
    file_rows = [(str(i + 1), E(a), w, f'{p}%') for i, (a, w, p) in enumerate(ASSESS_FILE)]
    file_rows.append(('', '<b>Total</b>', '', '<b>100%</b>'))
    now_rows = [(str(i + 1), E(a), E(w), f'{p}%') for i, (a, w, p) in enumerate(ASSESS_NOW)]
    now_rows.append(('', '<b>Total</b>', '', '<b>100%</b>'))

    mrows = []
    for n in range(1, 12):
        text = next(t for _, _, k, t, _, _, _ in CLOS if k == n)
        short = text if len(text) < 70 else text[:67].rsplit(' ', 1)[0] + '…'
        mrows.append([f'CLO {n} · {E(short)}'] + ['●' if c in MATRIX[n] else '' for c in MATRIX_COLS])
    cert_rows = [(f'<b>{E(c)}</b>', E(i), f'{m} SAR', E(cov), E(unc), pct, 'Insufficient alignment for equivalency; useful as a follow-on credential')
                 for c, i, m, cov, unc, pct in CERTS]
    att_rows = [(f'<a href="{STD}{f}">{E(t)}</a>', E(d)) for f, t, d in ATTACH]

    t_a = table(['Item', 'CPIT-455'], [
        ('Course title and code', 'Software Engineering (II) · CPIT-455'),
        ('Program · department · college', 'BSc Information Technology · Department of Information Technology · Faculty of Computing and Information Technology, King Abdulaziz University'),
        ('Credit hours', '3 (theory 3, lab 0, practical 1)'),
        ('Course type', 'Department · elective'),
        ('Level', 'As in the program plan (not stated in the specification on file)'),
        ('Pre-requisite · co-requisite', 'CPIT-251 · none'),
        ('Catalog description on file', 'Advanced software engineering principles and techniques used in the specification, design and testing of software systems. See recommendation 1: the description no longer matches the topics.'),
        ('Main objective (proposed wording)', 'Make and defend engineering decisions about dependable, safe, secure and resilient software systems, using evidence, tests and stated limits.'),
        ('Teaching mode', 'Traditional classroom on campus, 100% of contact hours. The course website supports study and practice; it does not replace class.'),
        ('Contact hours per semester', 'Lectures 45 (3 hours × 15 weeks) · practical 22.5 (90 minutes × 15 weeks) · total 67.5'),
    ])
    t_e = table(['Item', 'Resources'], [
        ('Essential reference', 'I. Sommerville, <i>Software Engineering</i>, 10th edition, Pearson (ISBN 9780133943030). Checked {DATE}: the latest edition; no 11th edition was found.'.format(DATE=DATE)),
        ('Supportive references', 'Vesely et al., <i>Fault Tree Handbook</i> (NUREG-0492), 1981 · Saltzer and Schroeder, “The Protection of Information in Computer Systems,” <i>Proc. IEEE</i>, 1975 · Helland and Campbell, “Building on Quicksand,” CIDR, 2009 · Garlan, Allen and Ockerbloom, “Architectural Mismatch,” <i>IEEE Software</i>, 1995 · Meyer, “Applying Design by Contract,” <i>IEEE Computer</i>, 1992 · Helland, “Idempotence Is Not a Medical Condition,” <i>ACM Queue</i>, 2012 · Maier, “Architecting Principles for Systems-of-Systems,” <i>Systems Engineering</i>, 1998'),
        ('Electronic materials', 'This course website: nine lectures, a source ledger per chapter, nine assessed assignments and offline packages (<a href="course-resources.html">Course &amp; sources</a>); Blackboard for announcements, submissions and grades'),
        ('Other learning materials', 'The original slide packs and textbook chapter PDFs, linked per chapter'),
        ('Facilities', 'Lecture room; the weekly 90-minute practical session'),
        ('Technology', 'Projector; a current web browser. Python runs inside the browser, with nothing to install, and a copy of Python is kept on this site in case the download fails.'),
    ])
    t_f = table(['Assessment area', 'Assessor', 'Method'], [
        ('Effectiveness of teaching', 'Students; course coordinator', 'University course-evaluation survey (indirect); coordination meetings and peer review (direct)'),
        ('Effectiveness of student assessment', 'Faculty', 'Four-level rubrics with calibration anchors; second marking of a sample; in-class check comparing the written work with the student\'s explanation (direct)'),
        ('Quality of learning resources', 'Students; faculty', 'Survey (indirect); each chapter\'s source ledger checked against the textbook and slide pack (direct)'),
        ('Extent to which CLOs are achieved', 'Faculty; program leaders', 'Rubric rows and exam items tagged to CLOs (section 4), reported in the end-of-semester course report (direct)'),
        ('AI-supported learning', 'Faculty', 'AI-use declarations and the NELC alignment review (indirect)'),
    ])
    t_g = table(['Item', 'Status'], [
        ('Specification on file', 'CPIT-455 course file, Fall 2024; last articulated 12 October 2023; coordinator Dr. Mounira Taileb'),
        ('This page', f'Instructor\'s alignment, {DATE}. Not approved by the department council. Proposed changes are for the next specification review.'),
    ])
    main = f'''<main class="wrap" id="main"><div class="document-heading"><p class="ey">COURSE SPECIFICATION · ETEC/NCAAA · COLLEGE · {DATE.upper()}</p>
<h1>What the course must meet.<br><em>Where the site stands.</em></h1>
<p class="intro">A gap analysis of the CPIT-455 site against the college and department requirements and the ETEC course specification template, the changes made on the site, and what is still open.</p></div>
<section class="panel" lang="ar" dir="rtl" id="summary-ar"><h2>الملخص</h2>
<p>قارنّا موقع المقرر بمتطلبات القسم والكلية (توصيف المقرر المعتمد في ملف المقرر، وتوجيهات رئيس القسم للفصل الأول 1448هـ، وطلب لجنة تطوير الخطط) وبنموذج توصيف المقرر من هيئة تقويم التعليم والتدريب (T-104، إصدار 2022)، وبدليل الشهادات المهنية المدعومة من المؤسسة العامة للتدريب التقني والمهني وصندوق هدف (2025).</p>
<ul><li><b>مستوفى ({counts[MET]}):</b> التوصيف بهيكل الهيئة (أ–ز) منشور في هذه الصفحة، وطرق التدريس والتقييم لكل مخرج، ومحتوى المقرر بالساعات، والمراجع (الطبعة العاشرة هي الأحدث)، والمرافق، وخطة تقييم جودة المقرر، ومواءمة الشهادات المهنية.</li>
<li><b>مستوفى جزئياً ({counts[PART]}):</b> تصنيف المخرجات في مجالات الإطار الوطني (لا يوجد مخرج في مجال القيم؛ اقترحنا واحداً)، وربط المخرجات بمخرجات البرنامج، وتغطية الكود، ومقابلة المقرر IT 456 في الخطة الجديدة.</li>
<li><b>مفتوح ({counts[OPEN]}):</b> توزيع الدرجات المنشور يختلف عن التوصيف الموجود في الملف ويحتاج تأكيداً في مصفوفة المواءمة (Articulation Matrix)، ووصف المقرر في الملف قديم، ودمج المخرجين 7 و8، والساعات المكتبية، وسجل اجتماعات التنسيق.</li></ul>
<p>لم نغيّر أوزان الدرجات في منتصف الفصل. الوثائق المرفقة في القسم 8.</p></section>
<nav aria-label="On this page"><ul class="spec-toc"><li><a href="#sources">1 · Requirements used</a></li><li><a href="#gaps">2 · Gap analysis</a></li><li><a href="#spec">3 · Course specification (A–G)</a></li><li><a href="#matrix">4 · CLO-by-assessment matrix</a></li><li><a href="#certifications">5 · Professional certifications</a></li><li><a href="#it456">6 · Revised plan: IT 456</a></li><li><a href="#recommendations">7 · Recommendations and course file</a></li><li><a href="#attachments">8 · Attachments</a></li></ul></nav>

<section class="section" id="sources"><h2>1 · Requirements used <span class="vs-ar-t" lang="ar" dir="rtl">المتطلبات المعتمدة في التحليل</span></h2>
{table(['Issued by', 'Document', 'What it requires', 'Copy'], src_rows)}</section>

<section class="section" id="gaps"><h2>2 · Gap analysis <span class="vs-ar-t" lang="ar" dir="rtl">تحليل الفجوات</span></h2>
<p>Status after the changes made on {DATE}. <b>Met</b>: the site now shows or does it. <b>Partly met</b>: shown, but part depends on a document or approval outside the site. <b>Open</b>: needs a department decision or the instructor's input.</p>
<div class="spec-counts">{pill(MET)} <b>{counts[MET]}</b> {pill(PART)} <b>{counts[PART]}</b> {pill(OPEN)} <b>{counts[OPEN]}</b></div>
{table(['Requirement', 'Source', 'Finding before', 'Action on the site', 'Status'], gap_rows, 'stack gaps')}</section>

<section class="section" id="spec"><h2>3 · Course specification, ETEC T-104 structure <span class="vs-ar-t" lang="ar" dir="rtl">توصيف المقرر بهيكل نموذج الهيئة</span></h2>
<p>CPIT-455 as taught in Fall 2026, written in the sections of the ETEC template. CLO wording is copied from the specification on file; anything new is marked <i>proposed</i>.</p>
<h3 class="spec-sub" id="spec-a">A · General information</h3>
{t_a}
<h3 class="spec-sub" id="spec-b">B · Course learning outcomes, teaching strategies and assessment methods</h3>
<p>Program alignment uses the student-outcome numbers recorded in the specification on file (SO 2 and SO 6).</p>
{table(['Code', 'Course learning outcome', 'Student outcome', 'Teaching strategies', 'Assessment methods'], clo_rows)}
<h3 class="spec-sub" id="spec-c">C · Course content</h3>
{table(['No', 'Topic', 'Weeks on file', 'Contact hours', 'On the site', 'Assessed in'], content_rows)}
<p>Delivery change: the two weeks of Code Coverage are taught as the coverage step of every Python build (Assignments 3–9) in the weekly practical session. To be reported in the end-of-semester course report.</p>
<h3 class="spec-sub" id="spec-d">D · Student assessment activities</h3>
<p><b>Specification on file (Fall 2024):</b></p>
{table(['No', 'Assessment activity', 'Week', 'Weight'], file_rows)}
<p><b>This semester, as published to students on the site:</b></p>
{table(['No', 'Assessment activity', 'Timing', 'Weight'], now_rows)}
<p>The two schemes differ. The written-test weights match (exam 1 and midterm 30, final 30). Homework, the group project and graded lab work (40 together) correspond to the nine assignments with their Python builds and to participation (40 together). The weights for all sections are set in the course Articulation Matrix. The coordinator confirms them there, and they are not changed mid-semester.</p>
<h3 class="spec-sub" id="spec-e">E · Learning resources and facilities</h3>
{t_e}
<h3 class="spec-sub" id="spec-f">F · Assessment of course quality</h3>
{t_f}
<h3 class="spec-sub" id="spec-g">G · Specification approval data</h3>
{t_g}</section>

<section class="section" id="matrix"><h2>4 · CLO-by-assessment matrix <span class="vs-ar-t" lang="ar" dir="rtl">مصفوفة المخرجات والتقييم</span></h2>
<p>● marks where each CLO is assessed directly. Assignment 1 covers Chapter 10, Assignment 2 Chapter 11, and so on to Assignment 9, Chapter 20.</p>
{table(['Course learning outcome'] + MATRIX_COLS, mrows, 'matrix')}</section>

<section class="section" id="certifications"><h2>5 · Professional certifications <span class="vs-ar-t" lang="ar" dir="rtl">مواءمة الشهادات المهنية</span></h2>
<p>The certifications in the TVTC/HRDF guide that touch CPIT-455 topics, using the committee's fields. Coverage is the instructor's estimate of the share of CPIT-455 content the certification covers. Maximum compensation is as stated in the guide.</p>
{table(['Certification', 'Issuer', 'Max HRDF compensation', 'Course topics covered', 'Course topics not covered', 'Coverage', 'Recommendation'], cert_rows)}
<p><b>Conclusion:</b> no certification in the guide covers dependability, reliability specification, safety engineering, reuse and component-based engineering, or systems of systems. None supports full or partial equivalency for CPIT-455 or IT 456. Students may take them after the course: CTFL builds on CLO 11, Security+ on CLO 5, AWS Solutions Architect on CLO 6 and 9.</p></section>

<section class="section" id="it456"><h2>6 · Revised plan: IT 456 Dependable Systems <span class="vs-ar-t" lang="ar" dir="rtl">الخطة المحدثة: IT 456</span></h2>
<p>In the revised IT program plan, CPIT-455 corresponds to the elective <b>IT 456 Dependable Systems</b>. Its specification covers dependability, reliability, safety, security and resilience engineering and uses Sommerville as a reference. These match Chapters 10–14 and CLOs 1–6 here.</p>
<p>Open: the IT 456 specification file is in the committee's shared folder and was not available for this review. A clause-by-clause crosswalk will be added when it is compared. Check in particular whether Chapters 15, 16, 17 and 20 (CLOs 7–10) and Code Coverage stay in IT 456.</p></section>

<section class="section" id="recommendations"><h2>7 · Recommendations and course file <span class="vs-ar-t" lang="ar" dir="rtl">التوصيات وملف المقرر</span></h2>
<ol>
<li><b>Catalog description (proposed):</b> Engineering of dependable software systems: dependability properties; reliability specification and metrics; safety and hazard analysis; security engineering; resilience; software reuse and component-based software engineering; distributed software engineering; systems of systems; test design, mutation testing and code coverage as evidence for engineering decisions.</li>
<li><b>CLOs:</b> merge CLO 7 and CLO 8 into one reuse outcome; correct “systes” in CLO 10; add the values outcome 3.1 in section B.</li>
<li><b>Grade distribution:</b> record the weights for all sections in the Articulation Matrix. Then make the specification and the site show the same table.</li>
<li><b>Code Coverage:</b> record it as practised in the builds of Assignments 3–9, not as two separate lecture weeks.</li>
<li><b>References:</b> keep Sommerville 10th edition as essential. Add the seven primary sources in section E as supportive references.</li>
</ol>
<p><b>Course-file checklist from the department guidelines:</b> syllabus available to students in week 1 (this page and the attached specification) · same grading in all sections (recommendation 3) · at least three coordination meetings, with minutes (coordinator) · Articulation Matrix updated after each meeting (coordinator) · office hours posted (open) · previous end-of-semester report completed (instructor).</p></section>

<section class="section" id="attachments"><h2>8 · Attachments <span class="vs-ar-t" lang="ar" dir="rtl">المرفقات</span></h2>
{table(['Document', 'Note'], att_rows)}
<p>The internal emails (department guidelines and the committee request) are summarised in section 1 and are not attached. The certification alignment sheet and other colleagues' course specifications are internal and are not published.</p></section>
</main>'''

    head = (f'<!DOCTYPE html>\n<html data-iscarb-standalone="1" data-theme="dark" lang="en"><head><meta charset="utf-8">'
            '<meta content="width=device-width,initial-scale=1" name="viewport"><meta content="#006b62" name="theme-color">'
            '<meta content="CPIT-455 course specification in the ETEC T-104 structure, gap analysis against college and ETEC requirements, and professional certification alignment." name="description">'
            '<title>Course specification and alignment · iSCARB CPIT-455</title>'
            f'<link href="iscarb-hub.css?v={VERSION}" rel="stylesheet"><link rel="stylesheet" href="course-design.css?v={VERSION}">'
            + dependencies() + STYLE + '</head>')
    body = ('<body class="course-page" id="top"><a class="skip" href="#main">Skip to content</a>'
            + header('', 'course-resources.html') + '\n' + main + footer('') + '</body></html>\n')
    PAGE.write_text(head + body, encoding='utf-8')


# ---- Links from the existing pages, and the build registration -------------------------------
LINK_MARK = '<!-- course-specification:link -->'
LINK = (LINK_MARK + '<section class="panel" id="course-specification"><p class="ey">COURSE SPECIFICATION · ETEC/NCAAA</p>'
        '<h2>Course specification and alignment</h2><p>The CPIT-455 specification in the ETEC T-104 structure, a gap analysis '
        'against the college, department and ETEC requirements, and the professional-certification alignment, with the source '
        'documents attached. <a href="course-specification.html"><b>Open the course specification</b></a>.</p>'
        '<p lang="ar" dir="rtl">توصيف المقرر بهيكل نموذج هيئة تقويم التعليم والتدريب، وتحليل الفجوات مع متطلبات الكلية والقسم والهيئة، '
        'ومواءمة الشهادات المهنية، مع الوثائق المرجعية. <a href="course-specification.html">افتح توصيف المقرر</a>.</p></section>')
# The Saudi alignment page is English only (tools/check-readable-course.cjs): no Arabic line there.
LINK_EN = LINK[:LINK.index('<p lang="ar"')] + '</section>'
GRADE_MARK = '<!-- course-specification:grades -->'
GRADE_LINK = (GRADE_MARK + '<p>How these weights relate to the course specification and the department\'s Articulation Matrix: '
              '<a href="{p}course-specification.html#spec-d">course specification, section D</a>. '
              '<span lang="ar" dir="rtl">علاقة هذه الأوزان بتوصيف المقرر: <a href="{p}course-specification.html#spec-d">القسم د في توصيف المقرر</a>.</span></p>')


def insert_between(rel, left, right, block):
    """Insert block between two adjacent strings that occur together exactly once (skipped if already there)."""
    p = ROOT / rel
    t = p.read_text(encoding='utf-8')
    if block[:block.index('-->') + 3] in t:
        return
    assert t.count(left + right) == 1, f'{rel}: anchor found {t.count(left + right)} times'
    p.write_text(t.replace(left + right, left + block + right), encoding='utf-8')


def link_pages():
    insert_between('course-resources.html', '</section>', '<section class="section" id="outcomes">', LINK)
    insert_between('instructor-guide.html', '</div>', '<section class="panel" id="use-iscarb">', LINK)
    t = (ROOT / 'nelc-alignment.html').read_text(encoding='utf-8')
    t = t.replace(LINK, LINK_EN)
    if LINK_MARK not in t:
        a = t.index('<section class="national-hero">')
        b = t.index('</section>', a) + len('</section>')
        t = t[:b] + LINK_EN + t[b:]
    (ROOT / 'nelc-alignment.html').write_text(t, encoding='utf-8')
    for rel in ('student-guide.html', 'assignment-example.html'):
        insert_between(rel, '<!-- lab-credit:end -->', '\n', GRADE_LINK.format(p=''))


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


def copy_attachments(args):
    """args: key=path pairs for the four source documents (first run only)."""
    (ROOT / STD).mkdir(parents=True, exist_ok=True)
    given = dict(a.split('=', 1) for a in args)
    for key, name in SCRATCH_ATTACHMENTS.items():
        dest = ROOT / STD / name
        if key in given:
            shutil.copyfile(given[key], dest)
        assert dest.exists(), f'missing attachment {name}: pass {key}=<path> on the first run'


if __name__ == '__main__':
    copy_attachments(sys.argv[1:])
    build_page()
    link_pages()
    register()
    print('Course specification page, links and registration applied')
