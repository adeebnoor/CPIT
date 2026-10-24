"""Consistency fixes from the site audit of 24 October 2026 (idempotent).

- Assignment pages (current edition): the learning-outcome line names the course specification, matches the
  CLO-to-assessment map in course-specification.html (Assignment 1: CLO 1, 2; Assignment 2: CLO 1, 2, 3) and, for
  Assignments 3-9, names CLO 11 for the Python build. Assignment 1 gets the line it was missing.
- evidence.html: the mutation test is part of every build from Assignment 3, not 4.
- imam.html and cimt.html: a notice that the archived lectures are earlier teaching cycles; their dates, tasks, grading
  and figures do not describe the current course. The banner on each archived slide deck is added by
  build_public_site.py, so the archived sources stay unchanged in the repository.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CLO = {10: '1 and 2', 11: '1, 2 and 3', 12: '4', 13: '2 and 5', 14: '6', 15: '7', 16: '8', 17: '9', 20: '10'}
NOTE = ('It is course-written practice, not an official national readiness assessment or an approved item-weight mapping.')


def alignment(n):
    build = ' The Python build, its tests and the coverage step also support CLO 11.' if n >= 12 else ''
    return (f'<details><summary>Learning-outcome alignment</summary><p>This task supports CLO {CLO[n]} of the course specification '
            f'(section B).{build} {NOTE}</p></details>')


def fix_assignments():
    for n in CLO:
        p = ROOT / f'lectures/iscarb/Ch{n}-FBR-Student-Assignment.html'
        t = p.read_text(encoding='utf-8')
        block = re.compile(r'<details><summary>Learning-outcome alignment</summary><p>.*?</p></details>', re.S)
        if block.search(t):
            t = block.sub(lambda m: alignment(n), t, count=1)
        else:
            anchor = '<details id="qualityExample">'
            assert t.count(anchor) == 1, f'Ch{n}: anchor found {t.count(anchor)} times'
            t = t.replace(anchor, alignment(n) + anchor)
        assert t.count('Learning-outcome alignment') == 1 and 'supplied syllabus' not in t, f'Ch{n}'
        p.write_text(t, encoding='utf-8')


def fix_evidence():
    p = ROOT / 'evidence.html'
    t = p.read_text(encoding='utf-8')
    t = t.replace('known bugs caught (mutation test, Assignments 4–9)', 'known bugs caught (mutation test, Assignments 3–9)')
    t = t.replace('if the share of bugs caught rises from A4 to A9', 'if the share of bugs caught rises from A3 to A9')
    p.write_text(t, encoding='utf-8')


ARCHIVE = ('Archived teaching cycle. These lectures are preserved as they were taught in an earlier cycle. Their dates, tasks, '
           'grading, contact details and illustrative figures do not describe the current course; for the current course use the '
           '<a href="iscarb.html">learning path</a> and the <a href="course-specification.html">course specification</a>.')


def fix_archives():
    edits = [
        ('imam.html', 'Historical source pages are preserved as instructional artifacts; this archive uses IMAM as the current framework name.</p>',
         'Historical source pages are preserved as instructional artifacts; this archive uses IMAM as the current framework name.</p>'
         f'<p class="archive-note"><b>{ARCHIVE.split(". ", 1)[0]}.</b> {ARCHIVE.split(". ", 1)[1]}</p>'),
        ('cimt.html', '<b>Provenance note.</b> The source decks are preserved in this public archive to document the CIMT teaching lineage. Lecture reuse requires attribution.</div>',
         '<b>Provenance note.</b> The source decks are preserved in this public archive to document the CIMT teaching lineage. Lecture reuse requires attribution. '
         + ARCHIVE.split('. ', 1)[1] + '</div>'),
    ]
    for rel, old, new in edits:
        p = ROOT / rel
        t = p.read_text(encoding='utf-8')
        if new not in t:
            assert t.count(old) == 1, f'{rel}: anchor found {t.count(old)} times'
            p.write_text(t.replace(old, new), encoding='utf-8')


if __name__ == '__main__':
    fix_assignments()
    fix_evidence()
    fix_archives()
    print('Audit fixes applied: assignment outcome lines, evidence wording, archive notices')
