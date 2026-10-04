"""Shorten the administrative text students must read before the task (Assignments 3–9).

Nothing assessed is removed: the lecture-connection section and the scope/edition notes are folded into
<details>, and "Before you start" becomes three short points, one of which announces the two-minute
ownership check (micro-viva). Idempotent:  python3 tools/apply_assignment_concise.py
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = 'data-concise="v1"'
START = ('<section class="card" ' + MARK + '><h2>Before you start</h2><ul>'
         '<li><b>Save often.</b> Use <b>Save draft</b> while working and download a backup before leaving a shared device.</li>'
         '<li><b>Commit, then the new evidence.</b> Part A becomes read-only when you commit, and the new evidence opens on this page straight away. Complete Part B, export the PDF and upload it in Blackboard.</li>'
         '<li><b>Ownership check.</b> Your instructor may ask you to explain your Part A and REFIT in a two-minute conversation. Your written work and your explanation should agree. AI may help you practise; the reasoning you submit must be your own.</li>'
         '</ul><p class="hint">The sequence preserves your first judgment; it is not a secure examination system.</p></section>')


def visible_before_task(s: str) -> int:
    head = s[:s.index('id="assessed-scenario"')]
    head = re.sub(r'<details[^>]*>.*?</details>', lambda m: (re.search(r'<summary>(.*?)</summary>', m.group(0), re.S) or [''])[0], head, flags=re.S)
    head = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', head, flags=re.S)
    body = head[head.index('<body'):] if '<body' in head else head
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body)).strip())


def patch(path: Path) -> tuple[int, int] | None:
    s = path.read_text(encoding='utf-8')
    if MARK in s:
        return None
    before = visible_before_task(s)
    # 1. Before you start
    m = re.search(r'<section class="card"><h2>Before you start</h2>.*?</section>', s, re.S)
    if not m: raise SystemExit(f'{path.name}: "Before you start" not found')
    s = s[:m.start()] + START + s[m.end():]
    # 2. lecture connection folded
    a = s.index('<section class="card" id="classroom-assignment-alignment">'); b = s.index('</section>', a)
    inner = s[a + len('<section class="card" id="classroom-assignment-alignment">'):b]
    s = (s[:a] + '<details class="card" id="classroom-assignment-alignment"><summary><b>How this assignment connects to the lecture and the five objectives</b></summary>'
         + inner + '</details>' + s[b + len('</section>'):])
    # 3. scope and earlier-edition notes folded
    a = s.index('id="requiredPreparation"'); b = s.index('</section>', a)
    sec = s[a:b]
    p1 = re.search(r'<p>One assigned source application.*?</p>', sec, re.S)
    p2 = re.search(r'<p><b>Already started the previous edition\?</b>.*?</p>', sec, re.S)
    if not p1 or not p2: raise SystemExit(f'{path.name}: scope notes not found')
    folded = '<details><summary>Scope notes and earlier editions</summary>' + p1.group(0) + p2.group(0) + '</details>'
    sec = sec.replace(p1.group(0), '').replace(p2.group(0), folded)
    s = s[:a] + sec + s[b:]
    path.write_text(s, encoding='utf-8')
    return before, visible_before_task(s)


def fold_levels(path: Path) -> tuple[int, int] | None:
    """Rubric: the full-credit description stays visible; the partial-credit levels fold under it."""
    s = path.read_text(encoding='utf-8')
    if 'class="levels"' in s:
        return None
    before = visible_before_task(s)
    i = s.index('<table class="rubric">'); j = s.index('</table>', i)
    table = re.sub(r'(<td><b>1:</b>.*?)<br/>(<b>0\.75:</b>.*?)</td>',
                   lambda m: m.group(1) + '<details class="levels"><summary>Partial credit: 0.75 · 0.5 · 0</summary>' + m.group(2) + '</details></td>',
                   s[i:j], flags=re.S)
    if table.count('class="levels"') != 5: raise SystemExit(f'{path.name}: expected five rubric rows')
    s = s[:i] + table + s[j:]
    path.write_text(s, encoding='utf-8')
    return before, visible_before_task(s)


def fold_prep(path: Path) -> tuple[int, int] | None:
    """Warm-up and preparation: keep the question and the reading; fold the scope sentences (v2)."""
    s = path.read_text(encoding='utf-8')
    if 'data-concise="v2"' in s:
        return None
    before = visible_before_task(s)
    s = s.replace('<p class="hint">No written warm-up response is required.</p>', '', 1)
    a = s.index('id="requiredPreparation"'); b = s.index('</section>', a); sec = s[a:b]
    m = re.search(r'(Complete the <a [^>]*>five-objective preparation check</a> after the <a [^>]*>assigned reading</a>), before starting this task and before the next chapter discussion\. (Blackboard supplies the calendar deadline\. All five chapter objectives, the classroom concepts and named reading are in assessment scope\. Optional toolkit activities are enrichment unless assigned\.)', sec)
    if not m: raise SystemExit(f'{path.name}: preparation paragraph not found')
    sec = sec.replace(m.group(0), m.group(1) + ' before you start.').replace('<details><summary>Scope notes and earlier editions</summary>', '<details><summary>Scope notes and earlier editions</summary><p>' + m.group(2) + '</p>', 1)
    s = s[:a] + sec.replace('id="requiredPreparation"', 'id="requiredPreparation" data-concise="v2"', 1) + s[b:]
    path.write_text(s, encoding='utf-8')
    return before, visible_before_task(s)


def main() -> int:
    pub = json.loads((ROOT / 'curriculum/publication.json').read_text(encoding='utf-8'))
    for a in pub['assignments']:
        if a['chapter'] < 12: continue
        r = patch(ROOT / a['path'])
        if r: print(f"Chapter {a['chapter']}: visible text before the task {r[0]} → {r[1]} characters ({100 - round(100 * r[1] / r[0])}% less)")
        r = fold_levels(ROOT / a['path'])
        if r: print(f"Chapter {a['chapter']}: rubric levels folded {r[0]} → {r[1]} characters")
        r = fold_prep(ROOT / a['path'])
        if r: print(f"Chapter {a['chapter']}: preparation folded {r[0]} → {r[1]} characters")
    return 0


if __name__ == '__main__':
    sys.exit(main())
