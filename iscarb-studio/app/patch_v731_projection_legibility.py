from __future__ import annotations

"""v7.3.1 - projection legibility + whitespace guard for Golden v6.6.

This patch changes presentation ergonomics only. It does not rewrite P1 content,
change the 20-unit grammar, remove source figures, or add a new theme.

Guarantees:
- learner-visible task text is separated from TIMEBOX and kept short;
- Rule 19 is the two-question peer-review card, never the tiny 6x4 matrix;
- U16-U18 reflow five micro-cards into a readable 3+2 layout;
- SOURCE EXPANSION pages grow sparse cards and add a source-grounded decision bridge;
- long editor/universal gate prose stays in the assessment layer, not on slides.
"""

import re

from . import main as engine
from . import start_v440 as base
from . import presenter_v67_prod as presenter

_PATCHED = False
_ORIGINAL_DRAFT = None
_ORIG_PPT_SEMANTIC = None
_ORIG_PDF_SEMANTIC = None

_TIMEBOX = re.compile(r"^\s*TIMEBOX:\s*(.+?)\s*-\s*(.*)$", re.I | re.S)
_GATE_PREFIXES = ("EDITOR GATE", "UNIVERSAL CHECK", "READINESS GATE", "MANDATORY EDITOR GATES")

MIN_PPT_TASK_PT = 10.2
MIN_PDF_TASK_PT = 8.2


def _clean(v) -> str:
    return " ".join(str(v or "").split())


def _words(text: str, n: int) -> str:
    rows = _clean(text).split()
    return " ".join(rows[:n]) + ("..." if len(rows) > n else "")


def _split_timebox(text: str) -> tuple[str, str]:
    t = _clean(text)
    m = _TIMEBOX.match(t)
    return (_clean(m.group(1)), _clean(m.group(2))) if m else ("", t)


def _clean_visible_gates(bp):
    for u in list(getattr(bp, "units", []) or []):
        ped = []
        for item in list(getattr(u, "pedagogy_content", []) or []):
            s = _clean(item)
            if s.upper().startswith(_GATE_PREFIXES):
                continue
            ped.append(s)
        u.pedagogy_content = ped[:16]
        tb, task = _split_timebox(getattr(u, "student_action", ""))
        task = _words(task, 22)
        u.student_action = f"TIMEBOX: {tb} - {task}" if tb else task
    return bp


def _ppt_footer(slide, u):
    tb, task = _split_timebox(getattr(u, "student_action", ""))
    sh = slide.shapes.add_shape(presenter.MSO_SHAPE.RECTANGLE,
                                presenter.Inches(0), presenter.Inches(6.82),
                                presenter.Inches(presenter.PPT_W), presenter.Inches(.68))
    sh.fill.solid(); sh.fill.fore_color.rgb = presenter._rgb(presenter.PANEL2); sh.line.fill.background()
    if tb:
        presenter._ppt_text(slide, .34, 6.91, 1.85, .26, f"TIMEBOX: {tb}", 9.4, presenter.GOLD, True)
    presenter._ppt_text(slide, .34, 7.20, 1.0, .22, "YOUR TASK", 8.8, presenter.MAGENTA, True)
    presenter._ppt_text(slide, 1.35, 7.14, 11.25, .30, _words(task, 22), MIN_PPT_TASK_PT, presenter.TEXT)


def _pdf_footer(c, u):
    tb, task = _split_timebox(getattr(u, "student_action", ""))
    c.setFillColor(presenter.HexColor(presenter.PANEL2)); c.rect(0, 0, 960, 49, fill=1, stroke=0)
    if tb:
        presenter._pdf_text(c, 24, 28, 155, 14, f"TIMEBOX: {tb}", 7.8, presenter.GOLD, True, max_lines=1)
    presenter._pdf_text(c, 24, 9, 78, 15, "YOUR TASK", 7.5, presenter.MAGENTA, True, max_lines=1)
    presenter._pdf_text(c, 106, 7, 820, 20, _words(task, 22), MIN_PDF_TASK_PT, presenter.TEXT, max_lines=2)


def _ppt_peer_review(slide):
    presenter._ppt_box(slide, .72, 2.0, 11.85, 1.35,
                       "1  IS THE EVIDENCE INDEPENDENTLY INSPECTABLE?",
                       "Could another team verify the claim without trusting your explanation or the AI/tool that prepared it?",
                       presenter.CYAN, fill=presenter.PANEL2, body_size=11.2, title_size=11.2)
    presenter._ppt_box(slide, .72, 3.65, 11.85, 1.35,
                       "2  WHAT WOULD MAKE THE CLAIM FAIL?",
                       "Name the variable, counter-example, missing evidence, or failure condition that would reverse the verdict.",
                       presenter.MAGENTA, fill=presenter.PANEL2, body_size=11.2, title_size=11.2)
    presenter._ppt_box(slide, 2.0, 5.35, 9.3, .75,
                       "FAST PEER REVIEW", "Inspectability + falsifiability before formal scoring.",
                       presenter.GOLD, fill=presenter.PANEL2, body_size=10.2, title_size=9.6)


def _pdf_peer_review(c):
    presenter._pdf_box(c, 55, 300, 850, 100,
                       "1  IS THE EVIDENCE INDEPENDENTLY INSPECTABLE?",
                       "Could another team verify the claim without trusting your explanation or the AI/tool that prepared it?",
                       presenter.CYAN, fill=presenter.PANEL2, body_size=10.2, title_size=9.2)
    presenter._pdf_box(c, 55, 180, 850, 100,
                       "2  WHAT WOULD MAKE THE CLAIM FAIL?",
                       "Name the variable, counter-example, missing evidence, or failure condition that would reverse the verdict.",
                       presenter.MAGENTA, fill=presenter.PANEL2, body_size=10.2, title_size=9.2)
    presenter._pdf_box(c, 190, 105, 580, 48, "FAST PEER REVIEW",
                       "Inspectability + falsifiability before formal scoring.",
                       presenter.GOLD, fill=presenter.PANEL2, body_size=8.8, title_size=8.0)


def _ppt_reflow_five(slide, bodies, labels, colors, takeaway=""):
    pos = [(0.62, 2.00), (4.45, 2.00), (8.28, 2.00), (2.50, 4.15), (6.55, 4.15)]
    sizes = [(3.45, 1.65)] * 3 + [(3.75, 1.55)] * 2
    for i, (lab, body, col) in enumerate(zip(labels, bodies, colors)):
        x, y = pos[i]; w, h = sizes[i]
        presenter._ppt_box(slide, x, y, w, h, lab, body, col,
                           fill=presenter.PANEL2, body_size=10.4, title_size=9.5)
    if takeaway:
        presenter._ppt_text(slide, 1.2, 5.95, 10.9, .35, _words(takeaway, 18),
                            10.2, presenter.GOLD, True, presenter.PP_ALIGN.CENTER)


def _pdf_reflow_five(c, bodies, labels, colors, takeaway=""):
    pos = [(35, 285), (335, 285), (635, 285), (180, 150), (485, 150)]
    sizes = [(270, 110)] * 3 + [(295, 100)] * 2
    for i, (lab, body, col) in enumerate(zip(labels, bodies, colors)):
        x, y = pos[i]; w, h = sizes[i]
        presenter._pdf_box(c, x, y, w, h, lab, body, col,
                           fill=presenter.PANEL2, body_size=8.8, title_size=8.2)
    if takeaway:
        presenter._pdf_text(c, 110, 105, 740, 25, _words(takeaway, 18),
                            8.5, presenter.GOLD, True, "center", 2)


def _ppt_semantic(slide, bp, u, accent):
    n = int(getattr(u, "number", 0) or 0)
    if n == 16:
        _ppt_reflow_five(slide,
            ["Name the bounded system and decision context.",
             "Name the source-backed mechanism controlling the decision.",
             "State what the option buys, costs, or leaves uncertain.",
             "Point to an inspectable source, test, calculation, or artifact.",
             "Name the next test or monitor that could change the verdict."],
            ["SYSTEM", "MECHANISM", "TRADE-OFF", "EVIDENCE", "READINESS PROBE"],
            [presenter.CYAN, presenter.GOLD, presenter.MAGENTA, presenter.BLUE, presenter.GREEN],
            "Output: one inspectable decision artifact, not five disconnected notes.")
        return
    if n == 17:
        _ppt_reflow_five(slide,
            ["Change exactly one decision-sensitive variable.",
             "Apply the same mechanism under the new condition.",
             "State what fails first and why.",
             "Have a peer challenge the evidence, not the style.",
             "Revise only where the evidence requires it."],
            ["1 PICK CONSTRAINT", "2 RE-RUN MECHANISM", "3 RECORD BREAK", "4 PEER CRITIQUE", "5 REDESIGN"],
            [presenter.CYAN, presenter.GOLD, presenter.MAGENTA, presenter.BLUE, presenter.GREEN],
            "A strong decision survives mutation - or explains exactly why it changes.")
        return
    if n == 18:
        vals = presenter._labeled(u, ["claim", "evidence", "warrant", "counter-evidence", "residual uncertainty"])
        _ppt_reflow_five(slide,
            [vals.get("claim", "State the bounded claim you defend."),
             vals.get("evidence", "Point to the inspectable evidence."),
             vals.get("warrant", "Explain why that evidence supports the claim."),
             vals.get("counter-evidence", "Name the strongest result that could defeat the claim."),
             vals.get("residual uncertainty", "State what remains unverified and how it will be monitored.")],
            ["CLAIM", "EVIDENCE", "WARRANT", "COUNTER-EVIDENCE", "RESIDUAL UNCERTAINTY"],
            [presenter.CYAN, presenter.GOLD, presenter.BLUE, presenter.MAGENTA, presenter.GREEN],
            "Counter-evidence and uncertainty answer different questions; keep both visible.")
        return
    if n == 19:
        _ppt_peer_review(slide); return
    return _ORIG_PPT_SEMANTIC(slide, bp, u, accent)


def _pdf_semantic(c, bp, u, accent):
    n = int(getattr(u, "number", 0) or 0)
    if n == 16:
        _pdf_reflow_five(c,
            ["Name the bounded system and decision context.",
             "Name the source-backed mechanism controlling the decision.",
             "State what the option buys, costs, or leaves uncertain.",
             "Point to an inspectable source, test, calculation, or artifact.",
             "Name the next test or monitor that could change the verdict."],
            ["SYSTEM", "MECHANISM", "TRADE-OFF", "EVIDENCE", "READINESS PROBE"],
            [presenter.CYAN, presenter.GOLD, presenter.MAGENTA, presenter.BLUE, presenter.GREEN],
            "Output: one inspectable decision artifact, not five disconnected notes.")
        return
    if n == 17:
        _pdf_reflow_five(c,
            ["Change exactly one decision-sensitive variable.",
             "Apply the same mechanism under the new condition.",
             "State what fails first and why.",
             "Have a peer challenge the evidence, not the style.",
             "Revise only where the evidence requires it."],
            ["1 PICK CONSTRAINT", "2 RE-RUN MECHANISM", "3 RECORD BREAK", "4 PEER CRITIQUE", "5 REDESIGN"],
            [presenter.CYAN, presenter.GOLD, presenter.MAGENTA, presenter.BLUE, presenter.GREEN],
            "A strong decision survives mutation - or explains exactly why it changes.")
        return
    if n == 18:
        vals = presenter._labeled(u, ["claim", "evidence", "warrant", "counter-evidence", "residual uncertainty"])
        _pdf_reflow_five(c,
            [vals.get("claim", "State the bounded claim you defend."),
             vals.get("evidence", "Point to the inspectable evidence."),
             vals.get("warrant", "Explain why that evidence supports the claim."),
             vals.get("counter-evidence", "Name the strongest result that could defeat the claim."),
             vals.get("residual uncertainty", "State what remains unverified and how it will be monitored.")],
            ["CLAIM", "EVIDENCE", "WARRANT", "COUNTER-EVIDENCE", "RESIDUAL UNCERTAINTY"],
            [presenter.CYAN, presenter.GOLD, presenter.BLUE, presenter.MAGENTA, presenter.GREEN],
            "Counter-evidence and uncertainty answer different questions; keep both visible.")
        return
    if n == 19:
        _pdf_peer_review(c); return
    return _ORIG_PDF_SEMANTIC(c, bp, u, accent)


def _ppt_expansion(slide, u, idx, chunk, page_idx, total):
    presenter._ppt_bg(slide); accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN)
    presenter._ppt_text(slide, .34, .18, 5.8, .25, "SOURCE EXPANSION", 8.8, accent, True)
    presenter._ppt_text(slide, 11.0, .18, 1.95, .25, f"X{idx:02d} - {page_idx:02d}/{total:02d}", 7.6,
                        presenter.MUTED, False, presenter.PP_ALIGN.RIGHT)
    title = "Domain spine - continued" if u.number == 2 else f"{u.title} - source detail"
    presenter._ppt_text(slide, .34, .55, 12.2, .55, title, 21.5, presenter.TEXT, True)
    presenter._ppt_text(slide, .34, 1.10, 12.2, .34,
                        "Keep source propositions readable; use each one to change evidence or a decision.",
                        10.2, presenter.MUTED)
    rows = list(chunk or [])[:6]; count = max(1, len(rows))
    if count <= 2: cols, card_h, y0, gap_y = 2, 2.55, 1.85, 0
    elif count <= 4: cols, card_h, y0, gap_y = 2, 1.85, 1.78, 2.05
    else: cols, card_h, y0, gap_y = 2, 1.30, 1.70, 1.50
    for i, item in enumerate(rows):
        r, c = divmod(i, cols)
        presenter._ppt_box(slide, .55 + c * 6.15, y0 + r * gap_y, 5.85, card_h,
                           f"P1 - {i+1}", _words(item, 26), accent,
                           fill=presenter.PANEL, body_size=10.6, title_size=8.6)
    if count <= 4:
        presenter._ppt_box(slide, 2.0, 5.55, 9.3, .72, "DECISION BRIDGE",
                           "Which source statement changes the evidence request, trade-off, or verdict?",
                           presenter.GOLD, fill=presenter.PANEL2, body_size=10.0, title_size=9.0)
    _ppt_footer(slide, u)


def _pdf_expansion(c, u, idx, chunk, page_idx, total):
    c.setFillColor(presenter.HexColor(presenter.BG)); c.rect(0, 0, 960, 540, fill=1, stroke=0)
    accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN)
    presenter._pdf_text(c, 24, 508, 300, 16, "SOURCE EXPANSION", 7.8, accent, True, max_lines=1)
    presenter._pdf_text(c, 800, 508, 135, 16, f"X{idx:02d} - {page_idx:02d}/{total:02d}", 6.8, presenter.MUTED, False, "right", 1)
    title = "Domain spine - continued" if u.number == 2 else f"{u.title} - source detail"
    presenter._pdf_text(c, 24, 465, 900, 40, title, 19.5, presenter.TEXT, True, max_lines=1)
    presenter._pdf_text(c, 24, 439, 900, 24,
                        "Keep source propositions readable; use each one to change evidence or a decision.",
                        8.8, presenter.MUTED, max_lines=2)
    rows = list(chunk or [])[:6]; count = max(1, len(rows))
    if count <= 2: positions, h = [(45, 205), (505, 205)], 190
    elif count <= 4: positions, h = [(45, 285), (505, 285), (45, 155), (505, 155)], 105
    else: positions, h = [(45, 320), (505, 320), (45, 220), (505, 220), (45, 120), (505, 120)], 82
    for i, item in enumerate(rows):
        x, y = positions[i]
        presenter._pdf_box(c, x, y, 410, h, f"P1 - {i+1}", _words(item, 26), accent, body_size=8.8, title_size=7.5)
    if count <= 4:
        presenter._pdf_box(c, 180, 85, 600, 50, "DECISION BRIDGE",
                           "Which source statement changes the evidence request, trade-off, or verdict?",
                           presenter.GOLD, fill=presenter.PANEL2, body_size=8.4, title_size=7.6)
    _pdf_footer(c, u)


def apply_v731_projection_legibility_patch(app):
    global _PATCHED, _ORIGINAL_DRAFT, _ORIG_PPT_SEMANTIC, _ORIG_PDF_SEMANTIC
    if _PATCHED: return
    _PATCHED = True
    _ORIGINAL_DRAFT = engine._source_preserving_draft
    _ORIG_PPT_SEMANTIC = presenter._ppt_semantic
    _ORIG_PDF_SEMANTIC = presenter._pdf_semantic

    def clean_draft(profile, bundle):
        return _clean_visible_gates(_ORIGINAL_DRAFT(profile, bundle))

    engine._source_preserving_draft = clean_draft
    base.engine._source_preserving_draft = clean_draft
    presenter._ppt_footer = _ppt_footer
    presenter._pdf_footer = _pdf_footer
    presenter._ppt_semantic = _ppt_semantic
    presenter._pdf_semantic = _pdf_semantic
    presenter._ppt_expansion = _ppt_expansion
    presenter._pdf_expansion = _pdf_expansion

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "projection_legibility_version": "v7.3.1",
            "projection_min_ppt_task_pt": MIN_PPT_TASK_PT,
            "projection_min_pdf_task_pt": MIN_PDF_TASK_PT,
            "projection_rule19": "two-question peer-review card; no 6x4 matrix on learner slide",
            "projection_five_card_reflow": "U16-U18 use 3+2 card layout; no five-column microtype",
            "projection_expansion_fill": "SOURCE EXPANSION cards expand adaptively; sparse pages receive a source-grounded decision bridge",
            "projection_gate_visibility": "full editor/universal gates remain in assessment layer; long gate prose is not dumped on learner slides",
        })
        return data
    base._health_v440 = health
    base.engine.health = health
