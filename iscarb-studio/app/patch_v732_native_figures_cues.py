from __future__ import annotations

"""v7.3.2 - native source-figure prominence + visual transition cues.

This layer is deliberately presentation-only. It keeps Golden v6.6, the 20 core
jobs, semantic source expansions, universal meta-gates and the original P1 claims
unchanged.

What changes:
- source figures/pictures are rendered at higher native resolution;
- figure-bearing units prefer a genuine cropped P1 picture over a whole source page;
- source-visual slides give the figure ~58% of the canvas and use larger support text;
- AI and readiness moments carry a small, consistent visual badge;
- the v7.3.1 TIMEBOX parser is corrected so ranges such as 5-7 min stay intact.
"""

import re
from pathlib import Path

from . import start_v440 as base
from . import presenter_v67_prod as presenter
from . import source_visuals as sv
from . import source_visuals_v42 as sv42
from . import patch_v731_projection_legibility as leg

_PATCHED = False
_ORIG_SOURCE_ASSET = None
_ORIG_PDF_EXPORT = None
_ORIG_HTML = None

FIGURE_UNITS = {6, 7, 9, 10, 12, 13, 14}


def _clean(v) -> str:
    return " ".join(str(v or "").split())


def _split_timebox(text: str) -> tuple[str, str]:
    """Split only on the deliberate task separator: space-hyphen-space.

    A range such as ``5-7 min`` is part of the duration and must never be
    interpreted as the separator.
    """
    t = _clean(text)
    if not t.upper().startswith("TIMEBOX:"):
        return "", t
    rest = t.split(":", 1)[1].strip()
    parts = re.split(r"\s+-\s+", rest, maxsplit=1)
    return (_clean(parts[0]), _clean(parts[1])) if len(parts) == 2 else (_clean(rest), "")


def _source_asset_for_unit(bp, u, registry):
    if registry is None or not sv._looks_source_backed(presenter._anchor(u)):
        return None
    anchors = set(sv.anchor_slides(presenter._anchor(u)))
    pool = [a for a in registry.assets if not anchors or a.slide_number in anchors]
    if not pool:
        return None

    # On figure-bearing teaching units, a genuine cropped P1 picture/figure gets
    # first refusal. Whole-page renders remain fallback only.
    if int(getattr(u, "number", 0) or 0) in FIGURE_UNITS:
        visual = [a for a in pool if getattr(a, "source_kind", "") in {sv.FIGURE_KIND, sv.PICTURE_KIND}]
        visual.sort(key=lambda a: sv42._quality_score(a, u, anchors), reverse=True)
        for asset in visual:
            if sv42._quality_score(asset, u, anchors) >= 6 and sv42._is_presentable(asset):
                path = sv.local_asset(asset)
                if path and Path(path).exists():
                    return asset, path

    ranked = sorted(pool, key=lambda a: sv42._quality_score(a, u, anchors), reverse=True)
    ranked = sv42._prefer_source_picture(ranked, u, anchors)
    for asset in ranked:
        if sv42._quality_score(asset, u, anchors) >= 10 and not sv42._looks_like_title_only(asset) and sv42._is_presentable(asset):
            path = sv.local_asset(asset)
            if path and Path(path).exists():
                return asset, path
    return None


def _ppt_source_split(slide, u, asset_path, accent):
    # Figure-first layout: enlarge the actual P1 surface and keep commentary terse.
    presenter._ppt_add_image(slide, asset_path, .34, 1.52, 7.52, 5.10)
    items = presenter._items(u, 4)
    presenter._ppt_text(slide, 8.04, 1.60, 4.65, .28, "FROM THE PRIMARY SOURCE", 9.8, accent, True)
    y = 1.98
    for item in items[:4]:
        presenter._ppt_text(slide, 8.05, y, 4.48, .82, "• " + presenter._short(item, 19), 12.0, presenter.TEXT)
        y += .88
    if u.takeaway:
        presenter._ppt_box(slide, 8.05, 5.38, 4.45, .96, "ENGINEERING TAKEAWAY",
                           presenter._short(u.takeaway, 17), accent, fill=presenter.PANEL2,
                           body_size=9.6, title_size=9.2)


def _ppt_badge(slide, u):
    n = int(getattr(u, "number", 0) or 0)
    if n == 15:
        presenter._ppt_box(slide, 10.40, .54, 2.25, .72, "AI MOMENT", "assist, not assurance",
                           presenter.CYAN, fill=presenter.PANEL2, body_size=8.6, title_size=9.0)
    elif n == 16:
        presenter._ppt_box(slide, 10.08, .54, 2.58, .72, "READINESS CHECK", "next test / next monitor",
                           presenter.GREEN, fill=presenter.PANEL2, body_size=8.4, title_size=8.8)


def _ppt_header(slide, u, page_idx, total):
    # Reuse the established v6.6 header, then add a bounded transition marker.
    accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN)
    phase = presenter.PHASE_LABEL.get(u.phase, u.phase)
    presenter._ppt_text(slide, .34, .18, 4.8, .25, f"{phase}  /  {presenter.RULE_KIND.get(u.number,'CONCEPT')}", 8.4, accent, True)
    presenter._ppt_text(slide, 11.05, .18, 1.95, .25, f"U{u.number:02d}/20  ·  {page_idx:02d}/{total:02d}", 7.3, presenter.MUTED, False, presenter.PP_ALIGN.RIGHT)
    presenter._ppt_text(slide, .34, .54, 9.55 if u.number in {15,16} else 12.4, .44,
                        presenter.RULE_NAMES.get(u.number, u.title), 21.5, presenter.TEXT, True)
    presenter._ppt_text(slide, .34, 1.03, 12.25, .34, presenter._short(u.engineering_question, 28), 10.0, presenter.MUTED)
    line = slide.shapes.add_shape(presenter.MSO_SHAPE.RECTANGLE, presenter.Inches(.34), presenter.Inches(1.43), presenter.Inches(12.62), presenter.Inches(.018))
    line.fill.solid(); line.fill.fore_color.rgb = presenter._rgb(presenter.GOLD); line.line.fill.background()
    _ppt_badge(slide, u)


def _pdf_badge(c, u):
    n = int(getattr(u, "number", 0) or 0)
    if n == 15:
        presenter._pdf_box(c, 742, 455, 185, 45, "AI MOMENT", "assist, not assurance",
                           presenter.CYAN, fill=presenter.PANEL2, body_size=6.5, title_size=7.0)
    elif n == 16:
        presenter._pdf_box(c, 720, 455, 207, 45, "READINESS CHECK", "next test / monitor",
                           presenter.GREEN, fill=presenter.PANEL2, body_size=6.4, title_size=6.8)


def _pdf_header(c, u, page_idx, total):
    accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN)
    presenter._pdf_text(c,24,508,340,16,f"{presenter.PHASE_LABEL.get(u.phase,u.phase)} / {presenter.RULE_KIND.get(u.number,'CONCEPT')}",7.3,accent,True,max_lines=1)
    presenter._pdf_text(c,790,508,145,16,f"U{u.number:02d}/20 · {page_idx:02d}/{total:02d}",6.4,presenter.MUTED,False,"right",1)
    presenter._pdf_text(c,24,465,690 if u.number in {15,16} else 900,40,presenter.RULE_NAMES.get(u.number,u.title),20,presenter.TEXT,True,max_lines=1)
    presenter._pdf_text(c,24,439,900,25,presenter._short(u.engineering_question,28),8.6,presenter.MUTED,max_lines=2)
    c.setStrokeColor(presenter.HexColor(presenter.GOLD)); c.setLineWidth(.8); c.line(24,432,936,432)
    _pdf_badge(c, u)


def _pdf_export(bp, out, source_root=None, release_state="REVIEW"):
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    c = presenter.rl_canvas.Canvas(str(out), pagesize=(presenter.PDF_W, presenter.PDF_H))
    plan = presenter._physical_plan(bp); assets = presenter._source_assets(bp, source_root); total = len(plan)
    for page_idx, (kind, u, extra) in enumerate(plan, 1):
        c.setFillColor(presenter.HexColor(presenter.BG)); c.rect(0,0,960,540,fill=1,stroke=0)
        if kind == "cover": presenter._pdf_cover(c, bp, total)
        elif kind == "close": presenter._pdf_close(c, bp, total)
        elif kind == "expansion":
            idx, chunk = extra; presenter._pdf_expansion(c, u, idx, chunk, page_idx, total)
        else:
            _pdf_header(c, u, page_idx, total)
            accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN); source = assets.get(u.number)
            if source and u.number in FIGURE_UNITS:
                presenter._pdf_image(c, source[1], 24, 82, 550, 340)
                presenter._pdf_text(c, 600, 390, 320, 18, "FROM THE PRIMARY SOURCE", 8.2, accent, True, max_lines=1)
                y = 350
                for item in presenter._items(u, 4):
                    presenter._pdf_text(c, 600, y, 320, 58, "• " + presenter._short(item, 19), 10.0, presenter.TEXT, max_lines=3)
                    y -= 67
                if u.takeaway:
                    presenter._pdf_box(c, 600, 94, 320, 62, "ENGINEERING TAKEAWAY", presenter._short(u.takeaway, 17), accent,
                                       fill=presenter.PANEL2, body_size=7.3, title_size=7.0)
            else:
                presenter._pdf_semantic(c, bp, u, accent)
            presenter._pdf_footer(c, u)
        c.showPage()
    c.save(); return out


def _html_preview(bp, release_state="REVIEW", source_root=None):
    html = _ORIG_HTML(bp, release_state=release_state, source_root=source_root)
    html = html.replace("</style>", ".sourceBody{grid-template-columns:1.65fr .85fr}.momentBadge{position:absolute;right:4%;top:15%;border:1px solid #2CDCFF;border-radius:12px;padding:7px 10px;background:#11192a;font-size:12px;font-weight:800;color:#2CDCFF;z-index:5}</style>")
    # Mark source split bodies so the image receives more canvas.
    html = re.sub(r"<div class='body'>(<div><img class='img')", r"<div class='body sourceBody'>\1", html)
    # Lightweight visual state markers for the two transition moments.
    html = html.replace("AI assist, human sign-off</div>", "AI assist, human sign-off</div><div class='momentBadge'>AI MOMENT · assist, not assurance</div>")
    html = html.replace("Build the decision artifact</div>", "Build the decision artifact</div><div class='momentBadge' style='border-color:#34D399;color:#34D399'>READINESS CHECK · next test / monitor</div>")
    return html


def apply_v732_native_figures_cues_patch(app):
    global _PATCHED, _ORIG_SOURCE_ASSET, _ORIG_PDF_EXPORT, _ORIG_HTML
    if _PATCHED:
        return
    _PATCHED = True

    # Higher-density P1 rasterization; changing PDF_RENDER_ZOOM also invalidates
    # the source-visual cache key so old softer crops are not silently reused.
    sv.PDF_RENDER_ZOOM = 3.4
    sv.MAX_FIGURE_ZOOM = 8.0
    sv.MIN_PRESENTABLE_ASSET_WIDTH = 1450
    sv42.PICTURE_PREFERENCE_SHARE = .35

    # Repair the v7.3.1 timebox split without rewriting that patch.
    leg._split_timebox = _split_timebox

    _ORIG_SOURCE_ASSET = presenter._source_asset_for_unit
    _ORIG_PDF_EXPORT = presenter.export_presenter_pdf
    _ORIG_HTML = presenter.render_presenter_preview

    presenter._source_asset_for_unit = _source_asset_for_unit
    presenter._ppt_source_split = _ppt_source_split
    presenter._ppt_header = _ppt_header
    presenter._pdf_header = _pdf_header
    presenter.export_presenter_pdf = _pdf_export
    presenter.render_presenter_preview = _html_preview

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "native_figure_prominence_version": "v7.3.2",
            "native_figure_policy": "Prefer genuine cropped P1 figure/picture; render at 3.4x/8x; figure gets majority canvas; no redraw when usable P1 exists.",
            "source_figure_canvas": "PPTX ~58% width; PDF ~57% width with enlarged support text.",
            "visual_transition_cues": "AI MOMENT on U15; READINESS CHECK on U16; same meaning in PPTX/PDF/HTML.",
            "timebox_range_parser": "Ranges such as 5-7 min and 60-90 sec are preserved intact.",
        })
        return data
    base._health_v440 = health
    base.engine.health = health
