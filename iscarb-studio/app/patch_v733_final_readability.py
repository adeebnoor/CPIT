from __future__ import annotations

"""v7.3.3 - final figure-first readability and owner-diagram repair.

Presentation-only patch over the user-approved Golden v6.6 baseline.
It fixes the last classroom readability regression: diagrams must dominate the
slide, support text must stay short, and owner/evidence/sign-off must never
wrap inside tiny circles.
"""

from pathlib import Path

from . import start_v440 as base
from . import presenter_v67_prod as presenter

_PATCHED = False
_ORIG_PPT_SEMANTIC = None
_ORIG_PDF_SEMANTIC = None
_ORIG_PPT_SOURCE_SPLIT = None

FIGURE_UNITS = {6, 7, 9, 10, 12, 13, 14}


def _words(text, n=18):
    words = " ".join(str(text or "").split()).split()
    return " ".join(words[:n]) + ("..." if len(words) > n else "")


def _ppt_source_split(slide, u, asset_path, accent):
    """Figure-first source slide: bigger native figure, less competing text."""
    presenter._ppt_add_image(slide, Path(asset_path), .45, 1.58, 8.15, 5.05)
    presenter._ppt_text(slide, 8.95, 1.70, 3.65, .28, "READ THE SOURCE FIGURE", 9.7, accent, True)
    items = presenter._items(u, 3)
    y = 2.14
    for item in items[:3]:
        presenter._ppt_text(slide, 9.00, y, 3.45, .72, "• " + _words(item, 15), 12.1, presenter.TEXT)
        y += .86
    if getattr(u, "takeaway", ""):
        presenter._ppt_box(slide, 9.00, 5.25, 3.45, .90, "DECISION POINT", _words(u.takeaway, 14), accent,
                           fill=presenter.PANEL2, body_size=9.7, title_size=9.1)


def _ppt_owner_flow(slide):
    # connectors first, then large nodes: prevents arrows crossing labels.
    y = 3.62
    x1, x2, x3 = 2.10, 5.80, 9.50
    for a, b in [(x1 + 1.28, x2 - .10), (x2 + 1.28, x3 - .10)]:
        conn = slide.shapes.add_connector(presenter.MSO_CONNECTOR.STRAIGHT,
                                          presenter.Inches(a), presenter.Inches(y),
                                          presenter.Inches(b), presenter.Inches(y))
        conn.line.color.rgb = presenter._rgb(presenter.TEXT); conn.line.width = presenter.Pt(1.7)
        try:
            conn.line.end_arrowhead = True
        except Exception:
            pass
    data = [
        (x1, "OWNER", "accountable\ndecision", presenter.CYAN),
        (x2, "EVIDENCE", "maintains\nartifact", presenter.GOLD),
        (x3, "SIGN-OFF", "accepts\nresidual risk", presenter.MAGENTA),
    ]
    for x, title, body, col in data:
        sh = slide.shapes.add_shape(presenter.MSO_SHAPE.OVAL, presenter.Inches(x), presenter.Inches(2.48), presenter.Inches(1.55), presenter.Inches(1.55))
        sh.fill.solid(); sh.fill.fore_color.rgb = presenter._rgb(presenter.PANEL2); sh.line.color.rgb = presenter._rgb(col); sh.line.width = presenter.Pt(1.8)
        tf = sh.text_frame; tf.clear(); tf.word_wrap = True; tf.vertical_anchor = presenter.MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.text = title; p.alignment = presenter.PP_ALIGN.CENTER; p.font.name = "Aptos"; p.font.bold = True; p.font.size = presenter.Pt(10.8); p.font.color.rgb = presenter._rgb(col)
        p = tf.add_paragraph(); p.text = body; p.alignment = presenter.PP_ALIGN.CENTER; p.font.name = "Aptos"; p.font.size = presenter.Pt(9.8); p.font.color.rgb = presenter._rgb(presenter.TEXT)
    presenter._ppt_text(slide, 2.3, 5.15, 8.75, .38, "If no one owns the evidence, the assurance claim is not inspectable.",
                        12.4, presenter.TEXT, True, presenter.PP_ALIGN.CENTER)


def _ppt_semantic(slide, bp, u, accent):
    if int(getattr(u, "number", 0) or 0) == 12:
        _ppt_owner_flow(slide)
        return
    return _ORIG_PPT_SEMANTIC(slide, bp, u, accent)


def _pdf_owner_flow(c):
    y = 260
    centers = [(245, presenter.CYAN, "OWNER", "accountable\ndecision"),
               (480, presenter.GOLD, "EVIDENCE", "maintains\nartifact"),
               (715, presenter.MAGENTA, "SIGN-OFF", "accepts\nresidual risk")]
    c.setStrokeColor(presenter.HexColor(presenter.TEXT)); c.setLineWidth(1.5)
    c.line(300, y, 425, y); c.line(535, y, 660, y)
    for cx, col, title, body in centers:
        c.setFillColor(presenter.HexColor(presenter.PANEL2)); c.setStrokeColor(presenter.HexColor(col)); c.setLineWidth(1.6)
        c.circle(cx, y, 55, fill=1, stroke=1)
        presenter._pdf_text(c, cx-48, y+9, 96, 18, title, 8.6, col, True, "center", 1)
        presenter._pdf_text(c, cx-48, y-22, 96, 28, body.replace("\n", " "), 8.1, presenter.TEXT, False, "center", 2)
    presenter._pdf_text(c, 170, 112, 620, 26, "If no one owns the evidence, the assurance claim is not inspectable.",
                        9.8, presenter.TEXT, True, "center", 1)


def _pdf_semantic(c, bp, u, accent):
    if int(getattr(u, "number", 0) or 0) == 12:
        _pdf_owner_flow(c)
        return
    return _ORIG_PDF_SEMANTIC(c, bp, u, accent)


def apply_v733_final_readability_patch(app):
    global _PATCHED, _ORIG_PPT_SEMANTIC, _ORIG_PDF_SEMANTIC, _ORIG_PPT_SOURCE_SPLIT
    if _PATCHED:
        return
    _PATCHED = True
    _ORIG_PPT_SEMANTIC = presenter._ppt_semantic
    _ORIG_PDF_SEMANTIC = presenter._pdf_semantic
    _ORIG_PPT_SOURCE_SPLIT = presenter._ppt_source_split

    presenter._ppt_source_split = _ppt_source_split
    presenter._ppt_semantic = _ppt_semantic
    presenter._pdf_semantic = _pdf_semantic

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "final_readability_version": "v7.3.3",
            "figure_first_slide_policy": "Figure-bearing units allocate the dominant area to native P1 visuals and cap supporting bullets at three.",
            "owner_flow_policy": "Owner/evidence/sign-off is rendered as large nodes with no broken label wrapping.",
            "diagram_collision_policy": "Support text is shortened before reducing figure area or taskbar legibility.",
        })
        return data
    base._health_v440 = health
    base.engine.health = health
