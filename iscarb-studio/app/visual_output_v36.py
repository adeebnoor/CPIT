from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from .models import Blueprint
from .visual_provenance import classify_visual
from .faculty_visual import export_faculty_presenter_pptx as _export_pptx
from .faculty_visual import render_faculty_presenter_preview as _render_preview
from . import presenter_pdf as pp


MAGENTA = RGBColor(210, 11, 109)
TEAL = RGBColor(10, 53, 62)
WHITE = RGBColor(255, 255, 255)
SAND = RGBColor(215, 180, 135)


def _ppt_provenance(slide, label: str, citation: str) -> None:
    # Compact visual-provenance badge; sits between phase marker and minute pill.
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.42), Inches(.30), Inches(3.08), Inches(.36))
    sh.fill.solid(); sh.fill.fore_color.rgb = TEAL
    sh.line.color.rgb = MAGENTA; sh.line.width = Pt(.7)
    tf = sh.text_frame; tf.clear(); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = label
    p.font.name = "Aptos"; p.font.size = Pt(7.2); p.font.bold = True; p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    tx = slide.shapes.add_textbox(Inches(8.38), Inches(6.80), Inches(4.35), Inches(.22))
    tf = tx.text_frame; tf.clear(); tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = citation[:92]
    p.font.name = "Aptos"; p.font.size = Pt(5.8); p.font.color.rgb = SAND
    p.alignment = PP_ALIGN.RIGHT


def export_presenter_pptx(bp: Blueprint, out: Path) -> Path:
    out = _export_pptx(bp, Path(out))
    prs = Presentation(str(out))
    for slide, unit in zip(prs.slides, bp.units):
        prov = classify_visual(unit)
        _ppt_provenance(slide, prov.label, prov.citation)
    prs.save(str(out))
    return out


def render_presenter_preview(bp: Blueprint, release_state: str = "BLOCKED") -> str:
    html = _render_preview(bp, release_state)
    prov = [classify_visual(u).__dict__ for u in bp.units]
    payload = json.dumps(prov, ensure_ascii=False).replace("</", "<\\/")
    inject = f'''
    <style>
      .vprov{{position:absolute;right:34px;top:22px;z-index:5;background:#0a353e;color:#fff;border:1px solid #d20b6d;border-radius:999px;padding:5px 9px;font-size:7px;font-weight:900;letter-spacing:.04em}}
      .vprov small{{display:block;color:#d7b487;font-size:5.8px;font-weight:650;margin-top:2px;max-width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
      .slide{{position:relative}}
    </style>
    <script>
      (function(){{const p={payload};document.querySelectorAll('.slide').forEach((s,i)=>{{if(!p[i])return;const b=document.createElement('div');b.className='vprov';b.textContent=p[i].label;const sm=document.createElement('small');sm.textContent=p[i].citation;b.appendChild(sm);s.appendChild(b);}});}})();
    </script>
    '''
    return html.replace("</body>", inject + "</body>")


def export_presenter_pdf(bp: Blueprint, out: Path) -> Path:
    original_base = pp._base

    def _base_with_provenance(c, unit):
        original_base(c, unit)
        prov = classify_visual(unit)
        c.setFillColor(pp.TEAL)
        c.roundRect(650, 493, 188, 22, 11, fill=1, stroke=0)
        c.setFillColor(pp.WHITE); c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(744, 500, prov.label)
        c.setFillColor(pp.GOLD); c.setFont("Helvetica", 5.6)
        c.drawRightString(920, 38, prov.citation[:95])

    pp._base = _base_with_provenance
    try:
        return pp.export_presenter_pdf(bp, Path(out))
    finally:
        pp._base = original_base
