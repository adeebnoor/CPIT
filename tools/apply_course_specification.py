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

# ---- 1. Reference requirements ------------------------------------------------------------
CODE_NOW = 'CPIT-455 Software Engineering (II)'
CODE_NEW = 'IT 456 Dependable Systems'
SOURCES = [
    ('Education and Training Evaluation Commission (ETEC), NCAAA', 'T-104 Course Specification template, version 2022',
     'Sections A to G: general information, teaching mode and contact hours; course learning outcomes in the three '
     'domains of the National Qualifications Framework (knowledge and understanding; skills; values, autonomy and '
     'responsibility), aligned with program outcomes and each linked to teaching strategies and assessment methods; '
     'course content with contact hours; assessment activities with timing and weight; learning resources and '
     'facilities; assessment of course quality; specification approval data.',
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["t104en"]}">English template</a> · '
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["t104ar"]}">Arabic template</a>'),
    ('Department of Information Technology, FCIT', 'CPIT-455 course specifications (course file), Fall 2024, last articulated 12 October 2023',
     'Eleven course learning outcomes and their student outcomes (SO 2 and SO 6); topic allocation by week; grade '
     'distribution; textbook; credit of three hours (theory 3, practical 1); a weekly 90-minute laboratory or tutorial session.',
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["spec"]}">Specification on file (PDF)</a>'),
    ('Course coordinator, Department of Information Technology', 'CPIT-455 Articulation Matrix, template version 5.0, Spring 2025',
     'Weekly teaching schedule (weeks 1 to 15); learning-outcome domain and student outcome for each CLO; teaching '
     'activities and assessment weeks for each CLO; grade distribution: homework 10% (week 7), examination 30% (week 8), '
     'graded laboratory work 10% and group project 20% (week 15), final examination 30% (week 16).',
     'Internal course document; summarised in this report'),
    ('Head of the Department of Information Technology', 'First Semester Guidelines, 1448 H, issued 27 August 2026',
     'A unified grading policy, syllabus and weekly schedule in accordance with the Articulation Matrix; the same grade '
     'distribution in all sections; the syllabus made available to students in the first week; students kept informed '
     'of their assessment grades; office hours scheduled and posted; at least three coordination meetings; completion '
     'of the previous end-of-semester report.',
     'Internal circular; summarised in this report'),
    ("Bachelor's Curriculum Development Committee", 'Course specification review and professional certification alignment, 22 October 2026',
     'Review and update of course specifications, including the latest editions of textbooks and references; for each '
     'proposed certification, the issuing organization, the course topics covered and not covered, an estimated '
     'coverage percentage and a recommendation on equivalency. In the revised IT program plan, CPIT-455 corresponds '
     f'to the elective course {CODE_NEW}.',
     'Internal correspondence; summarised in this report'),
    ('Technical and Vocational Training Corporation (TVTC) and Human Resources Development Fund (HRDF)',
     'Supported Professional Certifications Guide for the ICT Sector, 2025, second edition',
     'The supported professional certifications by field, with the issuing organization and the maximum HRDF compensation.',
     f'<a href="{STD}{SCRATCH_ATTACHMENTS["cert"]}">Guide (PDF, 6.5 MB)</a>'),
]

# ---- 2. Gap analysis: (requirement, source, finding, action taken on the website, status) -----
GAPS = [
    ('Course code in the revised IT program plan', 'Curriculum Development Committee',
     f'The website identified the course only as CPIT-455.',
     f'This report identifies the course as CPIT-455 (current code) and {CODE_NEW} (code in the revised plan, elective).', MET),
    ('Course specification in the ETEC T-104 structure, available to students', 'ETEC T-104; department guidelines (syllabus in the first week)',
     'The website contained a course-outcome map only; the specification itself was not published.',
     'Section 3 presents the specification in sections A to G, and the specification on file is attached.', MET),
    ('Course learning outcomes classified in the three NQF domains', 'ETEC T-104, section B',
     'The Articulation Matrix classifies CLOs 1–6 and 11 as cognitive skills and CLOs 7–10 as knowledge, using the earlier '
     'five-domain NCAAA framework. No CLO is in the domain of values, autonomy and responsibility.',
     'Each CLO is placed in the current three-domain structure (section 3B). A values outcome is proposed for the next '
     'specification; the website already collects its evidence.', PART),
    ('Each CLO linked to teaching strategies and assessment methods', 'ETEC T-104, section B; Articulation Matrix',
     'The website indicated where each CLO is taught but not how it is assessed.',
     'Teaching strategies and assessment methods are stated for each CLO (section 3B), with a CLO-to-assessment map (section 4).', MET),
    ('Course learning outcomes aligned with program outcomes', 'ETEC T-104, section B; Articulation Matrix',
     'Student outcomes were not shown on the website.',
     'SO 2 and SO 6 are shown for each CLO, with their wording from the Articulation Matrix. The outcome codes of the '
     'revised program have not yet been received.', PART),
    ('Number and wording of course learning outcomes', 'ETEC guidance on measurable outcomes',
     'CLO 7 and CLO 8 overlap (both describe reuse by composition of standardized components); CLO 10 contains a typing error ("systes").',
     'Recommended for the next specification: merge CLO 7 and CLO 8, and correct CLO 10 (recommendation 2).', OPEN),
    ('Course content and weekly schedule with contact hours', 'ETEC T-104, section C; Articulation Matrix',
     'Topic weeks and contact hours were not shown on the website.',
     'Section 3C lists each topic with its weeks in the Articulation Matrix, its contact hours, and the chapter and assignment on the website.', MET),
    ('Code Coverage (weeks 14 and 15 in the Articulation Matrix)', 'Specification on file; Articulation Matrix',
     'Since 15 October 2026, Code Coverage has been taught within the Python builds of Assignments 3–9 rather than in two lecture weeks.',
     'Recorded in section 3C as a change in delivery, to be reported in the end-of-semester course report.', PART),
    ('Assessment activities, timing and weights consistent with the Articulation Matrix in all sections', 'ETEC T-104, section D; department guidelines',
     'The website publishes assignments 30%, midterm examination 30%, final examination 30% and participation 10%. The '
     'specification on file and the Articulation Matrix (Spring 2025) specify homework 10%, examination 30%, graded '
     'laboratory work 10%, group project 20% and final examination 30%.',
     'Both schemes are presented in section 3D. Weights are not changed during the semester; the weights for Fall 2026 '
     'are to be confirmed in the current Articulation Matrix and the coordination record.', OPEN),
    ('Latest textbook edition and references', 'Curriculum Development Committee',
     'The website used Sommerville, 10th edition.',
     'Verified on 23 October 2026: the 10th edition is the latest (Pearson eText 2021, © 2016); no 11th edition was found. '
     'The seven primary sources used in the assignments are listed as supportive references (section 3E).', MET),
    ('Catalog description consistent with the course content', 'ETEC T-104, section A',
     'The description on file refers to topics no longer taught (team management, cost estimation, quality management, '
     'process and re-engineering) and omits dependability, safety, security and resilience.',
     'A revised description is proposed (recommendation 1), subject to department approval.', OPEN),
    ('Learning resources, facilities and equipment', 'ETEC T-104, section E',
     'Not stated on the website.', 'Stated in section 3E, including the in-browser Python environment, which requires no installation.', MET),
    ('Plan for the assessment of course quality', 'ETEC T-104, section F',
     'Not stated on the website.', 'Assessment areas, assessors and direct or indirect methods are stated in section 3F.', MET),
    ('Alignment with professional certifications', 'Curriculum Development Committee; TVTC/HRDF guide',
     'Not addressed on the website.',
     'Section 5 assesses six certifications from the guide (issuer, topics covered and not covered, estimated coverage and '
     'recommendation). None supports equivalency.', MET),
    (f'Content of {CODE_NEW} in the revised plan', 'Curriculum Development Committee',
     'No comparison was available on the website.',
     f'Section 6 records the correspondence. A clause-by-clause comparison will follow receipt of the {CODE_NEW} specification.', PART),
    ('Office hours scheduled and posted', 'Department guidelines', 'Not shown on the website.',
     'To be added once the office hours for Fall 2026 are confirmed.', OPEN),
    ('Students informed of their assessment grades', 'Department guidelines',
     'Grades are released in Blackboard; the website explains how assignment points are converted to marks.', 'No change required.', MET),
    ('At least three coordination meetings; Articulation Matrix updated after each', 'Department guidelines',
     'A coordination record maintained by the course coordinator; not a website item.', 'Listed in the course-file checklist (section 7).', OPEN),
    ('AI-supported learning design', 'NELC framework, September 2026',
     'Addressed on the Saudi alignment page since 28 September 2026.', 'No change required.', MET),
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
VALUES_PROPOSED = ('3.1', 'Proposed: take responsibility for engineering decisions by identifying the accountable owner, '
                   'disclosing any use of AI assistance and revising the decision when new evidence becomes available.',
                   'Named owner in ACT; AI-use declaration; commit before STRESS, then REFIT',
                   'ACT and REFIT rubric rows; AI-use declaration; in-class check (Assignments 6–9). Not a separate CLO on file.')

CONTENT = [  # (topic, weeks in the Articulation Matrix, number of weeks, chapter on the website, assessment)
    ('Dependable systems', '1–2', 2, 'Chapter 10', 'Assignment 1'),
    ('Reliability engineering', '3–4', 2, 'Chapter 11', 'Assignment 2'),
    ('Safety engineering', '5', 1, 'Chapter 12', 'Assignment 3'),
    ('Security engineering', '6–7', 2, 'Chapter 13', 'Assignment 4'),
    ('Resilience engineering', '8–9', 2, 'Chapter 14', 'Assignment 5'),
    ('Software reuse', '10', 1, 'Chapter 15', 'Assignment 6'),
    ('Distributed software engineering', '11', 1, 'Chapter 17', 'Assignment 8'),
    ('Component-based software engineering', '12', 1, 'Chapter 16', 'Assignment 7'),
    ('Systems of systems', '13', 1, 'Chapter 20', 'Assignment 9'),
    ('Code coverage (testing strategies and levels, coverage tools)', '14–15', 2, 'Within every Python build, Assignments 3–9', 'Coverage step, Assignments 3–9'),
]
ASSESS_FILE = [('Homework assignments', '7', 10), ('Examination', '8', 30), ('Graded laboratory work', '15', 10),
               ('Group project', '15', 20), ('Final examination', '16', 30)]
ASSESS_NOW = [('Assignments 1–9 (written analysis and, from Assignment 3, a Python build)', 'After each chapter, weeks 2–14', 30),
              ('Midterm examination (written test)', 'Week 8 (20 October 2026)', 30),
              ('Final examination (written test)', 'Final examination period', 30),
              ('Participation (preparation, in-class activities and questions)', 'Weeks 1–15', 10)]

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
     'Official template, as distributed by the Deanship of Quality, King Saud University.'),
    (SCRATCH_ATTACHMENTS['t104ar'], 'ETEC/NCAAA T-104 توصيف المقرر، إصدار 2022 (عربي، Word)',
     'Arabic version of the same template.'),
    (SCRATCH_ATTACHMENTS['spec'], 'CPIT-455 course specifications on file, Fall 2024 (PDF)',
     'Department course file, last articulated 12 October 2023. It remains the reference for the course learning outcomes until a revised specification is approved.'),
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

    content_rows = [(str(i + 1), E(t), wk, str(n * 3), E(c), E(a)) for i, (t, wk, n, c, a) in enumerate(CONTENT)]
    content_rows.append(('', '<b>Total</b>', '<b>15 weeks</b>', f'<b>{sum(n for _, _, n, _, _ in CONTENT) * 3}</b>', '', ''))
    file_rows = [(str(i + 1), E(a), w, f'{p}%') for i, (a, w, p) in enumerate(ASSESS_FILE)]
    file_rows.append(('', '<b>Total</b>', '', '<b>100%</b>'))
    now_rows = [(str(i + 1), E(a), E(w), f'{p}%') for i, (a, w, p) in enumerate(ASSESS_NOW)]
    now_rows.append(('', '<b>Total</b>', '', '<b>100%</b>'))

    mrows = []
    for n in range(1, 12):
        text = next(t for _, _, k, t, _, _, _ in CLOS if k == n)
        short = text if len(text) < 70 else text[:67].rsplit(' ', 1)[0] + '…'
        mrows.append([f'CLO {n} · {E(short)}'] + ['●' if c in MATRIX[n] else '' for c in MATRIX_COLS])
    cert_rows = [(f'<b>{E(c)}</b>', E(i), f'SAR {m}', E(cov), E(unc), pct, 'Insufficient for equivalency; suitable as a subsequent professional credential')
                 for c, i, m, cov, unc, pct in CERTS]
    att_rows = [(f'<a href="{STD}{f}">{E(t)}</a>', E(d)) for f, t, d in ATTACH]

    t_doc = table(['Item', 'Detail'], [
        ('Course (current code)', 'Software Engineering (II) · CPIT-455'),
        ('Course in the revised IT program plan', f'<b>{CODE_NEW}</b> (elective)'),
        ('Program', 'Bachelor of Science in Information Technology'),
        ('Department and faculty', 'Department of Information Technology, Faculty of Computing and Information Technology, King Abdulaziz University'),
        ('Prepared by', 'Prof. Adeeb Noor, course instructor'),
        ('Version and date', f'Version 1.1 · {DATE}'),
        ('Status', 'Working document for departmental review. Not approved by the department council.'),
    ])
    t_a = table(['Item', 'Detail'], [
        ('Course title and code', f'Software Engineering (II) · CPIT-455. In the revised IT program plan: {CODE_NEW}'),
        ('Program, department and faculty', 'Bachelor of Science in Information Technology · Department of Information Technology · Faculty of Computing and Information Technology, King Abdulaziz University'),
        ('Credit hours', '3 (theory 3, laboratory 0, practical 1)'),
        ('Course type', 'Department course · elective'),
        ('Level', 'As specified in the program study plan (not stated in the specification on file)'),
        ('Pre-requisite and co-requisite', 'CPIT-251 · none'),
        ('Catalog description on file', 'Advanced software engineering principles and techniques used in the specification, design and testing of software systems. This description no longer reflects the course content; a revision is proposed in recommendation 1.'),
        ('Main objective (proposed wording)', 'To enable students to make and justify engineering decisions on dependable, safe, secure and resilient software systems, on the basis of evidence, testing and stated limitations.'),
        ('Teaching mode', 'Traditional classroom instruction on campus: 100% of contact hours. The course website supports study and practice and does not replace classroom instruction.'),
        ('Contact hours per semester', 'Lectures 45 (3 hours × 15 weeks) · practical 22.5 (90 minutes × 15 weeks) · total 67.5'),
    ])
    t_e = table(['Item', 'Resources'], [
        ('Essential reference', f'I. Sommerville, <i>Software Engineering</i>, 10th edition, Pearson (ISBN 9780133943030). Verified on {DATE} as the latest edition; no 11th edition was found.'),
        ('Supportive references', 'W. E. Vesely et al., <i>Fault Tree Handbook</i> (NUREG-0492), 1981 · J. H. Saltzer and M. D. Schroeder, “The Protection of Information in Computer Systems,” <i>Proceedings of the IEEE</i>, 1975 · P. Helland and D. Campbell, “Building on Quicksand,” CIDR, 2009 · D. Garlan, R. Allen and J. Ockerbloom, “Architectural Mismatch: Why Reuse Is So Hard,” <i>IEEE Software</i>, 1995 · B. Meyer, “Applying ‘Design by Contract’,” <i>IEEE Computer</i>, 1992 · P. Helland, “Idempotence Is Not a Medical Condition,” <i>ACM Queue</i>, 2012 · M. W. Maier, “Architecting Principles for Systems-of-Systems,” <i>Systems Engineering</i>, 1998'),
        ('Electronic materials', 'The course website: nine lectures, a source ledger for each chapter, nine assessed assignments and offline packages (<a href="course-resources.html">Course &amp; sources</a>); Blackboard for announcements, submissions and grades'),
        ('Other learning materials', 'The original slide packs and the textbook chapters, linked for each chapter'),
        ('Facilities', 'Lecture room; the weekly 90-minute practical session'),
        ('Technology equipment', 'Projector; a current web browser. Python runs within the browser without installation; a copy of the Python environment is hosted on the course website in case the external download is unavailable.'),
    ])
    t_f = table(['Assessment area', 'Assessor', 'Assessment method'], [
        ('Effectiveness of teaching', 'Students; course coordinator', 'University course-evaluation survey (indirect); coordination meetings and peer review (direct)'),
        ('Effectiveness of student assessment', 'Faculty', 'Four-level rubrics with calibration examples; second marking of a sample; in-class verification of the written work against the student\'s explanation (direct)'),
        ('Quality of learning resources', 'Students; faculty', 'Survey (indirect); review of each chapter\'s source ledger against the textbook and slide pack (direct)'),
        ('Extent to which CLOs are achieved', 'Faculty; program leadership', 'Rubric criteria and examination items mapped to CLOs (section 4), reported in the end-of-semester course report (direct)'),
        ('AI-supported learning', 'Faculty', 'Review of AI-use declarations and of the NELC alignment (indirect)'),
    ])
    t_g = table(['Item', 'Status'], [
        ('Specification on file', 'CPIT-455 course file, Fall 2024; last articulated 12 October 2023; coordinator Dr. Mounira Taileb'),
        ('Articulation Matrix on file', 'CPIT-455 Articulation Matrix, template version 5.0, Spring 2025'),
        ('This report', f'Prepared by the course instructor, {DATE}. Not approved by the department council. Proposed changes are submitted for the next specification review.'),
    ])
    so_note = ('<p><b>Student outcomes</b> (wording from the Articulation Matrix): <b>SO 2</b> · Design, implement, and evaluate a '
               'computing-based solution to meet a given set of computing requirements in the context of the program’s discipline. '
               '<b>SO 6 (IT)</b> · Use systemic approaches to select, develop, apply, integrate, and administer secure computing '
               'technologies to accomplish user goals.</p>')
    main = f'''<main class="wrap" id="main"><div class="document-heading"><p class="ey">COURSE SPECIFICATION AND ALIGNMENT REPORT · {DATE.upper()}</p>
<h1>Course Specification and Gap Analysis<br><em>CPIT-455 · {CODE_NEW} in the revised plan</em></h1>
<p class="intro">This report reviews the course website against the requirements of the Department of Information Technology, the Faculty of Computing and Information Technology and the Education and Training Evaluation Commission (ETEC). It presents the course specification in the ETEC T-104 structure, records the changes made to the website and identifies the items that require a departmental decision.</p></div>
<section class="panel" id="document-control"><h2>Document control <span class="vs-ar-t" lang="ar" dir="rtl">بيانات الوثيقة</span></h2>
{t_doc}</section>
<section class="panel" lang="ar" dir="rtl" id="summary-ar"><h2>الملخص التنفيذي</h2>
<p>يراجع هذا التقرير موقع مقرر هندسة البرمجيات (2)، ورمزه الحالي CPIT-455، ويقابله في الخطة الدراسية المحدثة لبرنامج تقنية المعلومات المقرر الاختياري <b>IT 456 Dependable Systems</b>. وتشمل المراجعة المتطلبات التالية: توصيف المقرر المعتمد في ملف المقرر، ومصفوفة المواءمة (Articulation Matrix)، وتوجيهات رئيس القسم للفصل الدراسي الأول 1448هـ، وطلب لجنة تطوير الخطط الدراسية، ونموذج توصيف المقرر الصادر عن هيئة تقويم التعليم والتدريب (T-104، إصدار 2022)، ودليل الشهادات المهنية الاحترافية المدعومة الصادر عن المؤسسة العامة للتدريب التقني والمهني وصندوق تنمية الموارد البشرية (2025).</p>
<ul><li><b>المتطلبات المستوفاة ({counts[MET]}):</b> تحديد رمز المقرر في الخطة المحدثة، ونشر التوصيف وفق أقسام نموذج الهيئة (أ–ز)، وربط كل مخرج تعلم بطرق التدريس والتقييم، وعرض محتوى المقرر وجدوله الأسبوعي وساعاته، والتحقق من حداثة المرجع الأساسي، وبيان المرافق وخطة تقييم جودة المقرر، ودراسة مواءمة الشهادات المهنية.</li>
<li><b>المتطلبات المستوفاة جزئياً ({counts[PART]}):</b> تصنيف مخرجات التعلم وفق مجالات الإطار الوطني للمؤهلات، وربطها بمخرجات البرنامج، وتدريس تغطية الشيفرة ضمن البناء البرمجي، ومقارنة محتوى المقرر IT 456، وكلها مرهونة بوثائق أو اعتمادات من خارج الموقع.</li>
<li><b>المتطلبات المفتوحة ({counts[OPEN]}):</b> توحيد توزيع الدرجات وفق مصفوفة المواءمة للفصل الحالي، وتحديث وصف المقرر، ودمج المخرجين السابع والثامن، ونشر الساعات المكتبية، واستكمال سجل اجتماعات التنسيق.</li></ul>
<p>لم تُعدَّل أوزان الدرجات خلال الفصل الدراسي. والوثائق المرجعية مرفقة في القسم الثامن.</p></section>
<nav aria-label="Contents of this report"><ul class="spec-toc"><li><a href="#sources">1 · Reference requirements</a></li><li><a href="#gaps">2 · Gap analysis</a></li><li><a href="#spec">3 · Course specification (A–G)</a></li><li><a href="#matrix">4 · Mapping of CLOs to assessments</a></li><li><a href="#certifications">5 · Professional certifications</a></li><li><a href="#it456">6 · {CODE_NEW}</a></li><li><a href="#recommendations">7 · Recommendations</a></li><li><a href="#attachments">8 · Reference documents</a></li></ul></nav>

<section class="section" id="sources"><h2>1 · Reference requirements <span class="vs-ar-t" lang="ar" dir="rtl">المتطلبات المرجعية</span></h2>
{table(['Issuing body', 'Document', 'Requirements', 'Copy'], src_rows)}</section>

<section class="section" id="gaps"><h2>2 · Gap analysis <span class="vs-ar-t" lang="ar" dir="rtl">تحليل الفجوات</span></h2>
<p>Status as of {DATE}. <b>Met</b>: the requirement is satisfied on the website. <b>Partly met</b>: the requirement is satisfied in part, and the remainder depends on a document or an approval outside the website. <b>Open</b>: the requirement needs a departmental decision or further information from the instructor.</p>
<div class="spec-counts">{pill(MET)} <b>{counts[MET]}</b> {pill(PART)} <b>{counts[PART]}</b> {pill(OPEN)} <b>{counts[OPEN]}</b></div>
{table(['Requirement', 'Source', 'Finding', 'Action taken', 'Status'], gap_rows, 'stack gaps')}</section>

<section class="section" id="spec"><h2>3 · Course specification, ETEC T-104 structure <span class="vs-ar-t" lang="ar" dir="rtl">توصيف المقرر وفق نموذج الهيئة</span></h2>
<p>The course as delivered in Fall 2026, presented in the sections of the ETEC template. The wording of the course learning outcomes is taken from the specification on file; additions are marked <i>proposed</i>.</p>
<h3 class="spec-sub" id="spec-a">A · General information about the course</h3>
{t_a}
<h3 class="spec-sub" id="spec-b">B · Course learning outcomes, teaching strategies and assessment methods</h3>
{table(['Code', 'Course learning outcome', 'Student outcome', 'Teaching strategies', 'Assessment methods'], clo_rows)}
{so_note}
<h3 class="spec-sub" id="spec-c">C · Course content</h3>
{table(['No', 'Topic', 'Weeks (Articulation Matrix)', 'Contact hours', 'On the website', 'Assessed in'], content_rows)}
<p>Change in delivery: Code Coverage, scheduled for weeks 14 and 15, is taught as the coverage step of every Python build (Assignments 3–9) in the weekly practical session. Chapters 16 and 17 are taught in chapter order. Both changes are to be reported in the end-of-semester course report.</p>
<h3 class="spec-sub" id="spec-d">D · Student assessment activities</h3>
<p><b>Specification on file and Articulation Matrix (Spring 2025):</b></p>
{table(['No', 'Assessment activity', 'Week', 'Weight'], file_rows)}
<p><b>Fall 2026, as published to students on the website:</b></p>
{table(['No', 'Assessment activity', 'Timing', 'Weight'], now_rows)}
<p>The two schemes differ. The weights of the written examinations are the same (examination and midterm 30%; final examination 30%). The remaining 40% is allocated on file to homework, graded laboratory work and a group project, and on the website to nine assignments with Python builds and to participation. The department sets the weights for all sections in the Articulation Matrix; the weights for Fall 2026 are to be confirmed there and are not changed during the semester.</p>
<h3 class="spec-sub" id="spec-e">E · Learning resources and facilities</h3>
{t_e}
<h3 class="spec-sub" id="spec-f">F · Assessment of course quality</h3>
{t_f}
<h3 class="spec-sub" id="spec-g">G · Specification approval data</h3>
{t_g}</section>

<section class="section" id="matrix"><h2>4 · Mapping of course learning outcomes to assessments <span class="vs-ar-t" lang="ar" dir="rtl">ربط مخرجات التعلم بأدوات التقييم</span></h2>
<p>● indicates that the outcome is assessed directly in that assessment. Assignment 1 corresponds to Chapter 10, Assignment 2 to Chapter 11, and so on to Assignment 9, which corresponds to Chapter 20.</p>
{table(['Course learning outcome'] + MATRIX_COLS, mrows, 'matrix')}</section>

<section class="section" id="certifications"><h2>5 · Alignment with professional certifications <span class="vs-ar-t" lang="ar" dir="rtl">مواءمة الشهادات المهنية</span></h2>
<p>The certifications in the TVTC/HRDF guide that relate to topics of this course, reported in the fields requested by the Curriculum Development Committee. Coverage is the instructor's estimate of the proportion of course content addressed by the certification. Maximum compensation is as stated in the guide.</p>
{table(['Certification', 'Issuing organization', 'Maximum HRDF compensation', 'Course topics covered', 'Course topics not covered', 'Estimated coverage', 'Recommendation'], cert_rows)}
<p><b>Conclusion.</b> No certification in the guide addresses dependability, reliability specification, safety engineering, software reuse and component-based engineering, or systems of systems. None supports full or partial equivalency with CPIT-455 or {CODE_NEW}. The certifications may serve as subsequent professional credentials: ISTQB CTFL builds on CLO 11, CompTIA Security+ on CLO 5, and AWS Solutions Architect – Associate on CLOs 6 and 9.</p></section>

<section class="section" id="it456"><h2>6 · {CODE_NEW} in the revised IT program plan <span class="vs-ar-t" lang="ar" dir="rtl">المقرر في الخطة المحدثة</span></h2>
<p>In the revised IT program plan, CPIT-455 corresponds to the elective course <b>{CODE_NEW}</b>. Its specification covers dependability, reliability, safety, security and resilience engineering and lists Sommerville as a reference. These topics correspond to Chapters 10–14 and CLOs 1–6 of the current course.</p>
<p>Pending: the {CODE_NEW} specification is held in the committee's shared folder and was not available for this review. A clause-by-clause comparison will be added on receipt, in particular to establish whether Chapters 15, 16, 17 and 20 (CLOs 7–10) and Code Coverage remain within {CODE_NEW}.</p></section>

<section class="section" id="recommendations"><h2>7 · Recommendations and course-file checklist <span class="vs-ar-t" lang="ar" dir="rtl">التوصيات وقائمة ملف المقرر</span></h2>
<ol>
<li><b>Catalog description (proposed).</b> Engineering of dependable software systems: dependability properties; reliability specification and metrics; safety and hazard analysis; security engineering; resilience engineering; software reuse and component-based software engineering; distributed software engineering; systems of systems; test design, mutation testing and code coverage as evidence for engineering decisions.</li>
<li><b>Course learning outcomes.</b> Merge CLO 7 and CLO 8 into a single outcome on software reuse; correct the typing error in CLO 10; add the proposed outcome 3.1 in the domain of values, autonomy and responsibility; classify all outcomes in the three domains of the current National Qualifications Framework.</li>
<li><b>Grade distribution.</b> Record the weights for all sections in the Articulation Matrix for Fall 2026, and present the same table in the specification and on the website.</li>
<li><b>Code Coverage.</b> Record Code Coverage as practised within the builds of Assignments 3–9 rather than as two separate lecture weeks.</li>
<li><b>Articulation Matrix.</b> Correct the week-13 entry (systems of systems), which contains text from Chapter 25 on configuration management.</li>
<li><b>References.</b> Retain Sommerville, 10th edition, as the essential reference and add the seven primary sources in section 3E as supportive references.</li>
<li><b>Course code.</b> Record {CODE_NEW} as the corresponding course in the revised plan in the next version of the specification.</li>
</ol>
<p><b>Course-file checklist (department guidelines, 1448 H).</b> Syllabus available to students in the first week: met (this report and the attached specification) · same grade distribution in all sections: recommendation 3 · at least three coordination meetings with minutes: course coordinator · Articulation Matrix updated after each meeting: course coordinator · office hours posted: open · previous end-of-semester report completed: course instructor.</p></section>

<section class="section" id="attachments"><h2>8 · Reference documents <span class="vs-ar-t" lang="ar" dir="rtl">الوثائق المرجعية</span></h2>
{table(['Document', 'Note'], att_rows)}
<p>Internal documents (the department guidelines, the Articulation Matrix and the committee correspondence) are summarised in section 1 and are not published. The certification alignment sheet and the specifications of other courses are likewise not published.</p></section>
</main>'''

    head = (f'<!DOCTYPE html>\n<html data-iscarb-standalone="1" data-theme="dark" lang="en"><head><meta charset="utf-8">'
            '<meta content="width=device-width,initial-scale=1" name="viewport"><meta content="#006b62" name="theme-color">'
            '<meta content="Course specification of CPIT-455 (IT 456 Dependable Systems in the revised IT plan) in the ETEC T-104 structure, with a gap analysis against departmental, faculty and ETEC requirements and an alignment with professional certifications." name="description">'
            '<title>Course specification and gap analysis · CPIT-455 (IT 456) · iSCARB</title>'
            f'<link href="iscarb-hub.css?v={VERSION}" rel="stylesheet"><link rel="stylesheet" href="course-design.css?v={VERSION}">'
            + dependencies() + STYLE + '</head>')
    body = ('<body class="course-page" id="top"><a class="skip" href="#main">Skip to content</a>'
            + header('', 'course-resources.html') + '\n' + main + footer('') + '</body></html>\n')
    PAGE.write_text(head + body, encoding='utf-8')


# ---- Links from the existing pages, and the build registration -------------------------------
LINK_MARK = '<!-- course-specification:link -->'
LINK = (LINK_MARK + '<section class="panel" id="course-specification"><p class="ey">COURSE SPECIFICATION · ETEC/NCAAA</p>'
        '<h2>Course specification and gap analysis</h2><p>CPIT-455 Software Engineering (II), which corresponds to '
        '<b>IT 456 Dependable Systems</b> in the revised IT program plan. The report presents the course specification in the '
        'ETEC T-104 structure, a gap analysis against the requirements of the department, the faculty and ETEC, and an '
        'assessment of alignment with professional certifications, together with the reference documents. '
        '<a href="course-specification.html"><b>Open the report</b></a>.</p>'
        '<p lang="ar" dir="rtl">مقرر هندسة البرمجيات (2) CPIT-455، ويقابله في الخطة المحدثة لبرنامج تقنية المعلومات المقرر '
        'IT 456 Dependable Systems. يتضمن التقرير توصيف المقرر وفق نموذج هيئة تقويم التعليم والتدريب، وتحليل الفجوات مع '
        'متطلبات القسم والكلية والهيئة، ومواءمة الشهادات المهنية، مع الوثائق المرجعية. <a href="course-specification.html">الاطلاع على التقرير</a>.</p></section>')
# The Saudi alignment page is English only (tools/check-readable-course.cjs): no Arabic line there.
LINK_EN = LINK[:LINK.index('<p lang="ar"')] + '</section>'
GRADE_MARK = '<!-- course-specification:grades -->'
GRADE_LINK = (GRADE_MARK + '<p>The relationship between these weights, the course specification and the department\'s Articulation Matrix is set out in '
              '<a href="{p}course-specification.html#spec-d">section 3D of the course specification report</a>. '
              '<span lang="ar" dir="rtl">العلاقة بين هذه الأوزان وتوصيف المقرر ومصفوفة المواءمة موضحة في <a href="{p}course-specification.html#spec-d">القسم 3د من تقرير توصيف المقرر</a>.</span></p>')


def put_block(t, block):
    """Insert-or-refresh helper: replace an earlier version of the marked block in place."""
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
