"""FCIT Generative AI Policy on the course pages (idempotent).

The course follows the FCIT Generative AI Policy Guide for Course Syllabus (Faculty of Computing and Information
Technology) and adopts its Option C, Mixed Approach. The syllabus statement and the AI level of every assessment are
in the course specification, section D.1 (tools/apply_course_specification.py); the assignment pages state the level
of each step (tools/apply_ai_integrity.py) and the flipped-lecture page states its own (tools/apply_flip.py).

This tool adds a short panel that points to D.1 on Course & sources, the instructor guide and the Saudi alignment page
(English only there), lists the guide among the alignment sources, and adds one line to the student guide.

Run after tools/apply_course_specification.py.  Idempotent:  python3 tools/apply_ai_policy.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = '<!-- ai-policy:link -->'
SPEC_MARK = '<!-- course-specification:link -->'
GUIDE = 'FCIT Generative AI Policy Guide for Course Syllabus'
EN = ('<section class="panel" id="ai-policy"><p class="ey">USE OF GENERATIVE AI · FCIT POLICY</p>'
      '<h2>Use of Generative AI</h2><p>The course follows the <b>' + GUIDE + '</b> of the Faculty of Computing and '
      'Information Technology and adopts its <b>Option C, Mixed Approach</b>. Each assessment has its own permitted level: '
      'the examinations and the in-class check are AI-Free; Part A of Assignments 6–9 is AI-Free; the Python build and the '
      'work after commitment are AI-Assisted, as stated on each assignment page; no assessment is AI-Integrated. Students '
      'declare any AI use, and use beyond the permitted level may be treated as academic misconduct. '
      '<a href="course-specification.html#ai-policy"><b>The AI level of every assessment</b></a>.</p>')
AR = ('<p lang="ar" dir="rtl">يتبع المقرر دليل سياسة الذكاء الاصطناعي التوليدي في كلية الحاسبات وتقنية المعلومات، ويطبّق '
      'الخيار C (النهج المختلط): لكل تقييم مستوى مسموح. الاختبارات والتحقق في المحاضرة بدون ذكاء اصطناعي، والجزء A في الواجبات '
      '6–9 بدون ذكاء اصطناعي، والبناء في بايثون والعمل بعد التثبيت بمساعدة الذكاء الاصطناعي كما هو مكتوب في صفحة كل واجب. '
      'ويصرّح الطالب بأي استخدام، والاستخدام بما يتجاوز المستوى المسموح قد يُعامل مخالفةً أكاديمية. '
      '<a href="course-specification.html#ai-policy">مستوى الذكاء الاصطناعي في كل تقييم</a>.</p>')
PANEL = MARK + EN + AR + '</section>'
PANEL_EN = MARK + EN + '</section>'  # The Saudi alignment page is English only (tools/check-readable-course.cjs).

SOURCE = ('<li>' + GUIDE + ', Faculty of Computing and Information Technology — The course adopts Option C (Mixed '
          'Approach). The syllabus statement and the AI level of every assessment are in the '
          '<a href="course-specification.html#ai-policy">course specification (D.1)</a>; the acknowledgment wording on the '
          'assignment pages follows the appendix of the guide.</li>')
SOURCE_ANCHOR = '<li><a href="https://zenodo.org/records/22964248"'

SG_OLD = ('<li><b>Declare, export, upload.</b> Name any AI tool, what you used it for, and what you checked, or write '
          '“No AI used.” Export the PDF, read it, and upload it to Blackboard before the deadline.</li>')
SG_NEW = ('<li><b>Declare, export, upload.</b> Name any AI tool, what you used it for, and what you checked, or write '
          '“No AI used.” Each step has its permitted AI level under the FCIT Generative AI Policy (Option C): see the AI '
          'rules on the assignment page and <a href="course-specification.html#ai-policy">the level of every assessment</a>. '
          'Export the PDF, read it, and upload it to Blackboard before the deadline.</li>')


def put_panel(rel: str, panel: str) -> None:
    p = ROOT / rel
    t = p.read_text(encoding='utf-8')
    if MARK in t:
        a = t.index(MARK)
        b = t.index('</section>', a) + len('</section>')
        t = t[:a] + panel + t[b:]
    else:
        assert t.count(SPEC_MARK) == 1, f'{rel}: run tools/apply_course_specification.py first'
        a = t.index('</section>', t.index(SPEC_MARK)) + len('</section>')
        t = t[:a] + panel + t[a:]
    p.write_text(t, encoding='utf-8')


def main() -> None:
    put_panel('course-resources.html', PANEL)
    put_panel('instructor-guide.html', PANEL)
    put_panel('nelc-alignment.html', PANEL_EN)
    p = ROOT / 'nelc-alignment.html'
    t = p.read_text(encoding='utf-8')
    if SOURCE not in t:
        assert t.count(SOURCE_ANCHOR) == 1, 'nelc-alignment.html: sources list changed'
        t = t.replace(SOURCE_ANCHOR, SOURCE + SOURCE_ANCHOR)
    p.write_text(t, encoding='utf-8')
    p = ROOT / 'student-guide.html'
    t = p.read_text(encoding='utf-8')
    if SG_NEW not in t:
        assert t.count(SG_OLD) == 1, 'student-guide.html: declaration step changed'
        t = t.replace(SG_OLD, SG_NEW)
    p.write_text(t, encoding='utf-8')
    print('FCIT Generative AI Policy panel, alignment source and student-guide line applied')


if __name__ == '__main__':
    main()
