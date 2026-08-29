from __future__ import annotations

"""CIMT-native Presenter renderer for ISCARB Faculty Studio v4.3.

Design objective: the learner-facing deck should feel like the author's CIMT
lectures — white canvas, large green serif headings, thin gold rules, generous
white space, readable diagrams/tables, and source visuals that dominate the
slide when they are useful.  ISCARB pedagogy remains in the learning sequence;
it is not expressed as a dashboard UI.
"""

import html
import re
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .models import Blueprint, LectureUnit
from .source_visuals import asset_data_uri, local_asset
from .source_visuals_v42 import plans_for_blueprint_v42


# CIMT visual DNA taken from the archived CPIT-455 lecture deck: restrained,
# high-contrast, presentation-first.  No university logos are reproduced.
GREEN = RGBColor(0, 112, 68)
GREEN_DARK = RGBColor(0, 86, 52)
GOLD = RGBColor(196, 154, 39)
RED = RGBColor(197, 45, 45)
INK = RGBColor(24, 28, 25)
MUTED = RGBColor(91, 99, 93)
WHITE = RGBColor(255, 255, 255)
PALE = RGBColor(246, 248, 244)
PALE_GREEN = RGBColor(233, 244, 237)
PALE_GOLD = RGBColor(249, 244, 228)
LINE = RGBColor(215, 220, 214)

R_GREEN = colors.HexColor('#007044')
R_GREEN_DARK = colors.HexColor('#005634')
R_GOLD = colors.HexColor('#C49A27')
R_RED = colors.HexColor('#C52D2D')
R_INK = colors.HexColor('#181C19')
R_MUTED = colors.HexColor('#5B635D')
R_WHITE = colors.white
R_PALE = colors.HexColor('#F6F8F4')
R_PALE_GREEN = colors.HexColor('#E9F4ED')
R_PALE_GOLD = colors.HexColor('#F9F4E4')
R_LINE = colors.HexColor('#D7DCD6')

PPT_W = 13.333
PPT_H = 7.5
PDF_W = 960
PDF_H = 540


def presenter_text(text: str, limit: int = 116) -> str:
    """Shorten semantically without visible ellipsis/hard-cut artifacts."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    t = t.replace("…", "").replace("...", "")
    if len(t) <= limit:
        return t
    # Prefer a complete sentence.
    sentences = re.split(r"(?<=[.!?])\s+", t)
    if sentences and 18 <= len(sentences[0]) <= limit:
        return sentences[0].strip()
    # Then a complete clause.
    for sep in (";", ":", " — ", " – ", ","):
        part = t.split(sep, 1)[0].strip()
        if 18 <= len(part) <= limit:
            return part
    words = t.split()
    out: list[str] = []
    for w in words:
        trial = " ".join(out + [w])
        if len(trial) > limit:
            break
        out.append(w)
    return " ".join(out).rstrip(" ,;:-") or t[:limit].rstrip(" ,;:-")


def _subject(bp: Blueprint) -> str:
    t = re.sub(r"^\s*chapter\s*\d+\s*[-:–—]?\s*", "", bp.lecture_title or "", flags=re.I).strip()
    return t or bp.lecture_title or "Computing Systems"


def _source_label(u: LectureUnit) -> str:
    return presenter_text(u.source_anchor or "ISCARB pedagogy", 64)


def _core(u: LectureUnit, n: int = 6) -> list[str]:
    return [presenter_text(x, 104) for x in u.core_content[:n] if str(x).strip()]


def _ped(u: LectureUnit, n: int = 6) -> list[str]:
    return [presenter_text(x, 104) for x in u.pedagogy_content[:n] if str(x).strip()]


def _pick(values: list[str], i: int, fallback: str) -> str:
    return values[i] if i < len(values) and values[i].strip() else fallback


def _spec(bp: Blueprint, u: LectureUnit) -> tuple[str, list[tuple[str, str]]]:
    """Return a simple lecture-native visual grammar, never a dashboard."""
    core = _core(u, 8)
    ped = _ped(u, 8)
    if u.number == 1:
        return "crisis", [
            ("ENGINEERING CRISIS", presenter_text(bp.central_engineering_crisis, 180)),
            ("EVIDENCE", " • ".join(core[:3]) or presenter_text(u.takeaway, 130)),
            ("DECISION", "What evidence would change your first diagnosis?"),
        ]
    if u.number == 2:
        return "map", [(f"{i+1:02d}", presenter_text(x, 72)) for i, x in enumerate(bp.source_topic_families[:8])]
    if u.number == 3:
        return "rows", [(c.id, presenter_text(c.statement, 105)) for c in bp.clOs[:5]]
    if u.number == 4:
        labels = ["ANALYTICAL", "JUDGMENT", "EVIDENCE", "SOCIO-TECH", "RISK-AWARE", "ETHICAL"]
        defaults = [
            "Reason from mechanisms", "Choose under constraints", "Link claims to proof",
            "Trace people and process", "Expose failure and uncertainty", "Own consequences",
        ]
        return "grid", [(x, _pick(ped, i, defaults[i])) for i, x in enumerate(labels)]
    if u.number == 5:
        return "flow", [
            ("PREDICT", presenter_text(u.student_action, 88)),
            ("CONSTRAIN", _pick(core, 0, "Identify what cannot be violated")),
            ("DERIVE", _pick(core, 1, _pick(ped, 0, u.takeaway))),
            ("NAME", _pick(core, 2, u.takeaway)),
        ]
    if 6 <= u.number <= 10:
        k = (u.knowledge_types[0] if u.knowledge_types else "CONCEPT").replace("_", " ")
        vals = core[:4] or ped[:4] or [presenter_text(u.takeaway, 100)]
        if u.knowledge_types and u.knowledge_types[0] == "TRADE_OFF" and len(vals) >= 2:
            return "compare", [("ALTERNATIVE A", vals[0]), ("ALTERNATIVE B", vals[1]), ("DECISION CRITERIA", " • ".join(vals[2:4]) or u.takeaway)]
        return "flow", [(k if i == 0 else f"{k} {i+1}", x) for i, x in enumerate(vals)]
    if u.number == 11:
        return "flow", [
            ("HYPOTHETICAL SAUDI CONDITION", presenter_text(_pick(list(u.scenario_assumptions), 0, u.engineering_question), 105)),
            ("SOURCE MECHANISM", _pick(core, 0, "Apply only a mechanism taught by P1")),
            ("DESIGN CONSEQUENCE", presenter_text(u.takeaway, 105)),
        ]
    if u.number == 12:
        return "flow", [
            ("SOURCE DECISION", _pick(core, 0, u.takeaway)),
            ("EVIDENCE", presenter_text(u.evidence or _pick(core, 1, "Observable evidence"), 95)),
            ("OWNER", _pick(ped, 0, "Name the responsible engineering role")),
            ("CONSEQUENCE", presenter_text(u.student_action, 95)),
        ]
    if u.number == 13:
        return "flow", [
            ("ENDURING", _pick(core, 0, "Source principle")),
            ("CURRENT", _pick(core, 1, u.takeaway)),
            ("NEXT", presenter_text(_pick(list(u.enrichment_content), 0, u.student_action), 105)),
        ]
    if u.number == 14:
        return "flow", [
            ("DESIGN FRICTION", _pick(core, 0, "Source-grounded operational pressure")),
            ("HUMAN LOAD", _pick(ped, 0, "Identify avoidable cognitive burden")),
            ("DESIGN RESPONSE", presenter_text(u.student_action, 95)),
            ("RESIDUAL BURDEN", presenter_text(u.takeaway, 95)),
        ]
    if u.number == 15:
        return "flow", [
            ("AI MAY ASSIST", "Draft, compare, or propose candidate checks"),
            ("SOURCE CHECK", _pick(core, 0, "Trace the technical claim to P1")),
            ("TEST", presenter_text(u.student_action, 95)),
            ("HUMAN SIGN-OFF", "The engineer owns the bounded decision"),
        ]
    if u.number == 16:
        return "grid", [
            ("PROBLEM", presenter_text(bp.central_engineering_crisis, 95)),
            ("MECHANISM", _pick(core, 0, "P1 mechanism")),
            ("DESIGN", presenter_text(u.student_action, 90)),
            ("TRADE-OFF", presenter_text(bp.units[7].takeaway, 90)),
            ("EVIDENCE", presenter_text(u.evidence or "Evidence artifact", 90)),
            ("ASSURANCE", presenter_text(u.takeaway, 90)),
        ]
    if u.number == 17:
        return "flow", [
            ("BEFORE", _pick(core, 0, presenter_text(bp.units[15].takeaway, 88))),
            ("MUTATION", presenter_text(_pick(list(u.scenario_assumptions), 0, u.engineering_question), 88)),
            ("REDESIGN", presenter_text(u.student_action, 88)),
            ("CRITIQUE", _pick(ped, 0, "Peer challenges the revised decision")),
        ]
    if u.number == 18:
        vals = ped or []
        return "flow", [
            ("CLAIM", _pick(vals, 0, u.takeaway)),
            ("EVIDENCE", presenter_text(u.evidence or _pick(vals, 1, "Observed evidence"), 85)),
            ("WARRANT", _pick(vals, 2, "Explain why the evidence supports the claim")),
            ("COUNTER-EVIDENCE", _pick(vals, 3, "State what would weaken the claim")),
            ("UNCERTAINTY", _pick(vals, 4, "Keep the residual bound visible")),
        ]
    if u.number == 19:
        return "grid", [(presenter_text(c.criterion, 38), presenter_text(c.ready, 82)) for c in bp.rubric_criteria[:6]]
    if u.number == 20:
        return "assurance", [
            ("TOP CLAIM", presenter_text(u.takeaway, 150)),
            ("EVIDENCE", presenter_text(u.evidence or "Trace to CLO evidence and source bounds", 125)),
            ("RESIDUAL UNCERTAINTY", _pick(ped, 0, "State what remains unknown")),
            ("VERDICT", "APPROVE  |  CONDITIONAL  |  REDESIGN  |  REJECT"),
        ]
    vals = core[:4] or ped[:4] or [u.takeaway]
    return "grid", [(f"{i+1:02d}", x) for i, x in enumerate(vals)]


# ---------------------------------------------------------------------------
# PowerPoint
# ---------------------------------------------------------------------------

def _ppt_text(slide, x, y, w, h, text, size=16, color=INK, bold=False, font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = sh.text_frame; tf.clear(); tf.word_wrap = True; tf.vertical_anchor = valign
    p = tf.paragraphs[0]; p.text = str(text or ""); p.alignment = align
    p.font.name = font; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = color
    return sh


def _ppt_line(slide, y, color=GOLD, width=1.2):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.42), Inches(y), Inches(12.48), Inches(.018))
    sh.fill.solid(); sh.fill.fore_color.rgb = color; sh.line.fill.background()


def _ppt_base(slide, u: LectureUnit):
    bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = WHITE
    _ppt_line(slide, .23, GOLD)
    _ppt_text(slide, .52, .38, 10.6, .64, u.title, 29, GREEN_DARK, False, "Georgia")
    _ppt_text(slide, 10.85, .48, 1.95, .30, f"UNIT {u.number:02d} · {u.phase} · {u.planned_minutes} MIN", 8.5, MUTED, True, "Aptos", PP_ALIGN.RIGHT)
    _ppt_text(slide, .55, 1.10, 11.85, .50, presenter_text(u.engineering_question, 180), 13.2, INK, True)
    _ppt_line(slide, 6.90, GOLD)
    _ppt_text(slide, .55, 7.00, 1.05, .22, "YOU TRY", 8.5, GREEN, True)
    _ppt_text(slide, 1.48, 6.98, 8.65, .30, presenter_text(u.student_action, 125), 9.5, INK, True)
    _ppt_text(slide, 10.18, 7.00, 2.62, .24, _source_label(u), 7.3, MUTED, False, "Aptos", PP_ALIGN.RIGHT)


def _ppt_box(slide, x, y, w, h, title, body, fill=WHITE, line=GREEN, title_color=GREEN_DARK, body_color=INK, title_size=12, body_size=13):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill; sh.line.color.rgb = line; sh.line.width = Pt(1.1)
    tf = sh.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = Inches(.16); tf.margin_right = Inches(.16); tf.margin_top = Inches(.12); tf.margin_bottom = Inches(.08)
    p = tf.paragraphs[0]; p.text = presenter_text(title, 46); p.font.name = "Aptos"; p.font.size = Pt(title_size); p.font.bold = True; p.font.color.rgb = title_color
    if body:
        p = tf.add_paragraph(); p.text = presenter_text(body, 112); p.font.name = "Aptos"; p.font.size = Pt(body_size); p.font.color.rgb = body_color; p.space_before = Pt(7)
    return sh


def _ppt_flow(slide, items: list[tuple[str, str]]):
    n = max(1, len(items)); gap = .20; left = .58; total = 12.14
    w = (total - gap * (n - 1)) / n; y = 2.03; h = 3.80
    for i, (title, body) in enumerate(items):
        fill = PALE_GREEN if i % 2 == 0 else WHITE
        _ppt_box(slide, left + i * (w + gap), y, w, h, title, body, fill, GREEN, body_size=12.3 if n >= 5 else 13.4)
        if i < n - 1:
            _ppt_text(slide, left + (i + 1) * w + i * gap + .01, 3.50, gap - .02, .35, "→", 18, GOLD, True, align=PP_ALIGN.CENTER)


def _ppt_grid(slide, items: list[tuple[str, str]], cols=3):
    cols = max(1, min(cols, len(items))); rows = (len(items) + cols - 1) // cols
    gx = .24; gy = .20; left = .64; top = 2.0; total_w = 12.00; total_h = 3.95
    w = (total_w - gx * (cols - 1)) / cols; h = (total_h - gy * (rows - 1)) / rows
    for i, (title, body) in enumerate(items):
        r, c = divmod(i, cols)
        _ppt_box(slide, left + c * (w + gx), top + r * (h + gy), w, h, title, body, PALE if i % 2 else WHITE, LINE if i % 2 else GREEN, body_size=12.5)


def _ppt_compare(slide, items: list[tuple[str, str]]):
    a, b = items[0], items[1]
    _ppt_box(slide, .72, 2.10, 4.35, 3.55, a[0], a[1], PALE_GREEN, GREEN, body_size=14)
    _ppt_text(slide, 5.28, 3.18, 2.72, .65, "↔", 38, GOLD, True, "Georgia", PP_ALIGN.CENTER)
    if len(items) > 2:
        _ppt_text(slide, 5.15, 3.90, 2.95, .75, presenter_text(items[2][1], 70), 11.2, MUTED, True, align=PP_ALIGN.CENTER)
    _ppt_box(slide, 8.20, 2.10, 4.35, 3.55, b[0], b[1], PALE_GOLD, GOLD, body_size=14)


def _ppt_source(slide, u: LectureUnit, plan) -> bool:
    if not plan.asset:
        return False
    path = local_asset(plan.asset)
    if not path or not path.exists():
        return False
    x, y, box_w, box_h = .78, 1.78, 11.78, 4.80
    try:
        with Image.open(path) as im:
            iw, ih = im.size
        scale = min(box_w / iw, box_h / ih)
        w, h = iw * scale, ih * scale
        slide.shapes.add_picture(str(path), Inches(x + (box_w-w)/2), Inches(y + (box_h-h)/2), width=Inches(w), height=Inches(h))
    except Exception:
        slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(box_w), height=Inches(box_h))
    _ppt_text(slide, 9.30, 6.52, 3.20, .22, f"SOURCE VISUAL · P1 SLIDE {plan.source_slide}", 7.4, GREEN, True, align=PP_ALIGN.RIGHT)
    return True


def _ppt_redraw(slide, bp: Blueprint, u: LectureUnit):
    kind, items = _spec(bp, u)
    if kind == "compare":
        _ppt_compare(slide, items)
    elif kind == "rows":
        _ppt_grid(slide, items, 1)
    elif kind == "map":
        subject = presenter_text(_subject(bp), 38)
        _ppt_text(slide, 5.08, 3.17, 3.10, .75, subject, 20, WHITE, True, "Georgia", PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        hub = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.00), Inches(3.05), Inches(3.25), Inches(.95))
        hub.fill.solid(); hub.fill.fore_color.rgb = GREEN; hub.line.fill.background(); slide.shapes._spTree.remove(hub._element); slide.shapes._spTree.insert(2, hub._element)
        positions = [(.75,2.05),(.75,3.38),(.75,4.71),(9.25,2.05),(9.25,3.38),(9.25,4.71)]
        for i, (t, body) in enumerate(items[:6]):
            px, py = positions[i]; _ppt_box(slide, px, py, 3.20, .90, t, body, WHITE, GREEN, body_size=11.2)
    elif kind == "crisis":
        _ppt_box(slide, .72, 2.0, 5.10, 3.92, items[0][0], items[0][1], PALE_GOLD, RED, RED, body_size=14)
        _ppt_box(slide, 6.12, 2.0, 6.00, 1.75, items[1][0], items[1][1], WHITE, GREEN, body_size=12.5)
        _ppt_box(slide, 6.12, 4.02, 6.00, 1.90, items[2][0], items[2][1], PALE_GREEN, GREEN, body_size=14)
    elif kind == "assurance":
        _ppt_box(slide, 1.05, 1.90, 11.20, 1.35, items[0][0], items[0][1], PALE_GREEN, GREEN, body_size=14)
        _ppt_grid(slide, items[1:3], 2)
        _ppt_text(slide, 1.10, 5.62, 11.10, .48, items[3][1], 16, GREEN_DARK, True, "Aptos", PP_ALIGN.CENTER)
    elif kind == "grid":
        _ppt_grid(slide, items, 3 if len(items) >= 5 else 2)
    else:
        _ppt_flow(slide, items)


def export_cimt_presenter_pptx_v43(bp: Blueprint, out: Path) -> Path:
    out = Path(out)
    prs = Presentation(); prs.slide_width = Inches(PPT_W); prs.slide_height = Inches(PPT_H)
    plans = plans_for_blueprint_v42(bp)
    for u, plan in zip(bp.units, plans):
        slide = prs.slides.add_slide(prs.slide_layouts[6]); _ppt_base(slide, u)
        if plan.reuse_mode == "USE" and _ppt_source(slide, u, plan):
            continue
        _ppt_redraw(slide, bp, u)
        tag = "ADAPTED FROM P1" if u.source_anchor else "ISCARB VISUALIZATION"
        _ppt_text(slide, .58, 6.52, 2.20, .22, tag, 7.3, GREEN if u.source_anchor else MUTED, True)
    prs.save(str(out)); return out


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def _r_wrap(c, text, x, y, width, size=12, color=R_INK, bold=False, max_lines=4, align="left"):
    font = "Helvetica-Bold" if bold else "Helvetica"
    words = str(text or "").split(); lines: list[str] = []; line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if c.stringWidth(trial, font, size) <= width:
            line = trial
        else:
            if line: lines.append(line)
            line = word
            if len(lines) >= max_lines - 1: break
    if line and len(lines) < max_lines: lines.append(line)
    c.setFont(font, size); c.setFillColor(color)
    for i, ln in enumerate(lines):
        yy = y - i * size * 1.26
        if align == "center": c.drawCentredString(x + width/2, yy, ln)
        elif align == "right": c.drawRightString(x + width, yy, ln)
        else: c.drawString(x, yy, ln)


def _r_base(c, u: LectureUnit):
    c.setFillColor(R_WHITE); c.rect(0, 0, PDF_W, PDF_H, fill=1, stroke=0)
    c.setFillColor(R_GOLD); c.rect(30, 518, 900, 1.5, fill=1, stroke=0); c.rect(30, 43, 900, 1.5, fill=1, stroke=0)
    c.setFillColor(R_GREEN_DARK); c.setFont("Times-Roman", 24); c.drawString(40, 485, presenter_text(u.title, 78))
    c.setFillColor(R_MUTED); c.setFont("Helvetica-Bold", 7.3); c.drawRightString(918, 490, f"UNIT {u.number:02d} · {u.phase} · {u.planned_minutes} MIN")
    _r_wrap(c, presenter_text(u.engineering_question, 170), 42, 454, 850, 11.2, R_INK, True, 2)
    c.setFillColor(R_GREEN); c.setFont("Helvetica-Bold", 7.5); c.drawString(40, 22, "YOU TRY")
    _r_wrap(c, presenter_text(u.student_action, 125), 92, 22, 610, 8.2, R_INK, True, 1)
    c.setFillColor(R_MUTED); c.setFont("Helvetica", 6.4); c.drawRightString(920, 22, _source_label(u))


def _r_box(c, x, y, w, h, title, body, fill=R_WHITE, stroke=R_GREEN, title_color=R_GREEN_DARK, body_size=11.2):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(1.1); c.roundRect(x, y, w, h, 10, fill=1, stroke=1)
    c.setFillColor(title_color); c.setFont("Helvetica-Bold", 9.4); c.drawString(x+12, y+h-22, presenter_text(title, 44))
    _r_wrap(c, presenter_text(body, 110), x+12, y+h-46, w-24, body_size, R_INK, False, 5)


def _r_source(c, plan) -> bool:
    if not plan.asset: return False
    path = local_asset(plan.asset)
    if not path or not path.exists(): return False
    try:
        img = ImageReader(str(path)); iw, ih = img.getSize(); box=(55,75,850,350); scale=min(box[2]/iw, box[3]/ih); dw,dh=iw*scale,ih*scale
        c.drawImage(img, box[0]+(box[2]-dw)/2, box[1]+(box[3]-dh)/2, width=dw, height=dh, preserveAspectRatio=True, mask='auto')
        c.setFillColor(R_GREEN); c.setFont("Helvetica-Bold", 6.5); c.drawRightString(905, 57, f"SOURCE VISUAL · P1 SLIDE {plan.source_slide}")
        return True
    except Exception:
        return False


def _r_redraw(c, bp: Blueprint, u: LectureUnit):
    kind, items = _spec(bp, u)
    if kind == "compare":
        _r_box(c, 65, 130, 320, 250, items[0][0], items[0][1], R_PALE_GREEN, R_GREEN, body_size=12)
        c.setFillColor(R_GOLD); c.setFont("Times-Bold", 28); c.drawCentredString(480, 265, "<->")
        if len(items)>2: _r_wrap(c, items[2][1], 402, 215, 156, 9.5, R_MUTED, True, 4, "center")
        _r_box(c, 575, 130, 320, 250, items[1][0], items[1][1], R_PALE_GOLD, R_GOLD, body_size=12)
        return
    if kind == "crisis":
        _r_box(c, 55, 125, 385, 275, items[0][0], items[0][1], R_PALE_GOLD, R_RED, R_RED, 12)
        _r_box(c, 470, 260, 430, 140, items[1][0], items[1][1], R_WHITE, R_GREEN, body_size=10.5)
        _r_box(c, 470, 125, 430, 110, items[2][0], items[2][1], R_PALE_GREEN, R_GREEN, body_size=12)
        return
    if kind == "assurance":
        _r_box(c, 90, 320, 780, 90, items[0][0], items[0][1], R_PALE_GREEN, R_GREEN, body_size=11.5)
        _r_box(c, 90, 185, 375, 105, items[1][0], items[1][1], R_WHITE, R_GREEN, body_size=10.5)
        _r_box(c, 495, 185, 375, 105, items[2][0], items[2][1], R_WHITE, R_GREEN, body_size=10.5)
        c.setFillColor(R_GREEN_DARK); c.setFont("Helvetica-Bold", 12); c.drawCentredString(480, 130, items[3][1])
        return
    cols = 1 if kind == "rows" else (3 if kind in {"grid","map"} and len(items)>=5 else len(items))
    cols = max(1, min(cols, 5)); rows=(len(items)+cols-1)//cols; gx=12; gy=12; left=50; top=405; total_w=860; total_h=285
    w=(total_w-gx*(cols-1))/cols; h=(total_h-gy*(rows-1))/rows
    for i,(title,body) in enumerate(items):
        r,cc=divmod(i,cols); y=top-(r+1)*h-r*gy
        _r_box(c,left+cc*(w+gx),y,w,h,title,body,R_PALE if i%2 else R_WHITE,R_GREEN,body_size=9.5 if cols>=4 else 11)


def export_cimt_presenter_pdf_v43(bp: Blueprint, out: Path) -> Path:
    out=Path(out); c=canvas.Canvas(str(out), pagesize=(PDF_W,PDF_H), pageCompression=1)
    c.setTitle(bp.lecture_title); c.setAuthor("ISCARB Faculty Studio")
    plans=plans_for_blueprint_v42(bp)
    for u,plan in zip(bp.units,plans):
        _r_base(c,u)
        if not (plan.reuse_mode=="USE" and _r_source(c,plan)):
            _r_redraw(c,bp,u)
        c.showPage()
    c.save(); return out


# ---------------------------------------------------------------------------
# Browser preview
# ---------------------------------------------------------------------------

def _h(s: str) -> str:
    return html.escape(str(s or ""))


def _html_redraw(bp: Blueprint, u: LectureUnit) -> str:
    kind, items = _spec(bp,u)
    if kind == "compare":
        return f'<div class="compare"><article><b>{_h(items[0][0])}</b><span>{_h(items[0][1])}</span></article><div class="vs">↔<small>{_h(items[2][1] if len(items)>2 else "trade-off")}</small></div><article class="gold"><b>{_h(items[1][0])}</b><span>{_h(items[1][1])}</span></article></div>'
    if kind == "crisis":
        return '<div class="crisis">' + ''.join(f'<article class="c{i}"><b>{_h(t)}</b><span>{_h(b)}</span></article>' for i,(t,b) in enumerate(items)) + '</div>'
    if kind == "assurance":
        return f'<div class="assurance"><article><b>{_h(items[0][0])}</b><span>{_h(items[0][1])}</span></article><div class="twocol"><article><b>{_h(items[1][0])}</b><span>{_h(items[1][1])}</span></article><article><b>{_h(items[2][0])}</b><span>{_h(items[2][1])}</span></article></div><strong>{_h(items[3][1])}</strong></div>'
    cls = "rows" if kind=="rows" else ("grid" if kind in {"grid","map"} else "flow")
    return f'<div class="{cls}">' + ''.join(f'<article><b>{_h(t)}</b><span>{_h(b)}</span></article>' for t,b in items) + '</div>'


def render_cimt_presenter_preview_v43(bp: Blueprint, release_state: str="BLOCKED") -> str:
    plans=plans_for_blueprint_v42(bp); slides=[]; thumbs=[]
    for i,(u,plan) in enumerate(zip(bp.units,plans)):
        visual=""
        if plan.reuse_mode=="USE" and plan.asset:
            uri=asset_data_uri(plan.asset)
            if uri:
                visual=f'<div class="source"><img src="{uri}" alt="P1 source visual"><small>SOURCE VISUAL · P1 SLIDE {plan.source_slide}</small></div>'
        if not visual: visual=_html_redraw(bp,u)
        slides.append(f'''<section class="slide{' show' if i==0 else ''}" data-i="{i}">
          <div class="toprule"></div><div class="head"><h2>{_h(u.title)}</h2><em>UNIT {u.number:02d} · {_h(u.phase)} · {u.planned_minutes} MIN</em></div>
          <p class="q">{_h(presenter_text(u.engineering_question,180))}</p>
          <div class="visual">{visual}</div>
          <div class="bottomrule"></div><div class="foot"><b>YOU TRY</b><span>{_h(presenter_text(u.student_action,125))}</span><em>{_h(_source_label(u))}</em></div>
        </section>''')
        thumbs.append(f'<button class="thumb{" active" if i==0 else ""}" data-i="{i}"><b>{u.number:02d}</b><span>{_h(presenter_text(u.title,46))}</span></button>')
    css='''
    *{box-sizing:border-box}body{margin:0;font-family:Inter,Aptos,Arial,sans-serif;background:#e9ece7;color:#181c19}.deck{height:100vh;display:grid;grid-template-columns:230px 1fr}.rail{background:#f7f7f2;border-right:1px solid #d4d9d2;padding:18px;overflow:auto}.brand{font-family:Georgia,serif;color:#005634;font-size:19px}.state{font-size:9px;color:#6b736d;margin:6px 0 16px}.thumb{width:100%;display:grid;grid-template-columns:28px 1fr;gap:6px;text-align:left;background:transparent;border:0;border-bottom:1px solid #dde2db;padding:8px 4px;color:#4d5650;cursor:pointer}.thumb b{color:#007044}.thumb span{font-size:10px}.thumb.active{background:#e9f4ed;color:#181c19}.stage{display:grid;place-items:center;padding:24px}.slide{display:none;width:min(1190px,calc(100vw - 285px));aspect-ratio:16/9;background:#fff;box-shadow:0 22px 55px #22312727;padding:22px 34px 16px;position:relative;overflow:hidden;grid-template-rows:2px auto auto 1fr 2px auto}.slide.show{display:grid}.toprule,.bottomrule{height:2px;background:#c49a27}.head{display:flex;justify-content:space-between;align-items:start;padding-top:8px;gap:18px}.head h2{margin:0;font-family:Georgia,serif;font-weight:400;font-size:clamp(25px,2.5vw,38px);color:#005634;letter-spacing:-.02em}.head em{font-style:normal;font-size:8px;font-weight:850;color:#6b736d;white-space:nowrap;padding-top:9px}.q{font-size:13px;font-weight:720;margin:8px 0 0;max-width:1000px}.visual{min-height:0;display:grid;align-items:center;padding:15px 8px}.foot{display:grid;grid-template-columns:70px 1fr 230px;gap:9px;align-items:center;padding-top:7px;font-size:9px}.foot b{color:#007044}.foot span{font-weight:700}.foot em{font-style:normal;text-align:right;color:#6b736d;font-size:7px}.flow{display:flex;align-items:stretch;gap:12px}.flow article,.grid article,.rows article{border:1.5px solid #007044;border-radius:9px;padding:15px;background:#fff;display:flex;flex-direction:column;gap:9px;min-width:0}.flow article{flex:1}.flow article:nth-child(odd){background:#e9f4ed}.flow b,.grid b,.rows b,.compare b,.crisis b,.assurance b{font-size:10px;color:#005634;letter-spacing:.04em}.flow span,.grid span,.rows span,.compare span,.crisis span,.assurance span{font-size:13px;line-height:1.35;font-weight:650}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.rows{display:grid;gap:8px}.rows article{display:grid;grid-template-columns:90px 1fr;align-items:center;padding:10px 14px}.compare{display:grid;grid-template-columns:1fr 160px 1fr;align-items:stretch;gap:18px}.compare article{border:1.5px solid #007044;background:#e9f4ed;border-radius:10px;padding:24px}.compare article.gold{border-color:#c49a27;background:#f9f4e4}.vs{display:grid;place-items:center;font-family:Georgia,serif;font-size:42px;color:#c49a27;text-align:center}.vs small{display:block;font-family:Inter,sans-serif;color:#6b736d;font-size:10px}.crisis{display:grid;grid-template-columns:1.15fr 1fr;grid-template-rows:1fr 1fr;gap:13px}.crisis article{border-radius:10px;padding:20px;border:1.5px solid #007044}.crisis .c0{grid-row:1/3;border-color:#c52d2d;background:#f9f4e4}.crisis .c2{background:#e9f4ed}.assurance{display:grid;gap:12px}.assurance>article,.assurance .twocol article{border:1.5px solid #007044;border-radius:9px;padding:14px}.assurance>article{background:#e9f4ed}.assurance .twocol{display:grid;grid-template-columns:1fr 1fr;gap:12px}.assurance>strong{text-align:center;color:#005634;font-size:14px}.source{height:100%;display:grid;place-items:center;position:relative}.source img{max-width:100%;max-height:100%;object-fit:contain}.source small{position:absolute;right:0;bottom:0;background:#fff;color:#007044;font-size:7px;font-weight:850;padding:4px 7px}
    @media(max-width:850px){.deck{grid-template-columns:1fr}.rail{display:none}.slide{width:96vw}.grid{grid-template-columns:repeat(2,1fr)}}
    '''
    js='''<script>(function(){const s=[...document.querySelectorAll('.slide')],b=[...document.querySelectorAll('.thumb')];function go(i){s.forEach((x,j)=>x.classList.toggle('show',j===i));b.forEach((x,j)=>x.classList.toggle('active',j===i));}b.forEach((x,i)=>x.onclick=()=>go(i));document.onkeydown=e=>{let i=s.findIndex(x=>x.classList.contains('show'));if(e.key==='ArrowRight')go(Math.min(s.length-1,i+1));if(e.key==='ArrowLeft')go(Math.max(0,i-1));};})();</script>'''
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{_h(bp.lecture_title)} · ISCARB Presenter</title><style>{css}</style></head><body><div class="deck"><aside class="rail"><div class="brand">ISCARB · CIMT-native Presenter</div><div class="state">{_h(release_state)} · 20 units · 90 minutes</div>{"".join(thumbs)}</aside><main class="stage">{"".join(slides)}</main></div>{js}</body></html>'
