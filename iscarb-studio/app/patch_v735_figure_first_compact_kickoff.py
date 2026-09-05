from __future__ import annotations

"""v7.3.5 — figure-first native prominence + compact kickoff.

This is a presentation/physical-plan layer over the Golden v6.6 curriculum.
It does not rewrite P1 claims or the 20 semantic jobs.

Guarantees:
- genuine source figures keep native/source-backed treatment and receive ~70% of
  the live teaching canvas;
- figure support is capped at two short sentences before any font reduction;
- long titles receive a two-line-safe header instead of colliding with the
  engineering question or footer;
- the task bar keeps a readable font floor;
- kickoff keeps the internal 20-unit blueprint but presents a deliberately
  shorter live sequence: hook, outcomes, course flow, one local case, AI/human
  accountability, assessment, live defense, readiness, close.
"""

from pathlib import Path

from . import start_v440 as base
from . import presenter_v67_prod as presenter
from . import patch_v731_projection_legibility as leg
from . import source_visuals as sv

_PATCHED = False
_ORIG_PHYSICAL_PLAN = None
_ORIG_PPT_HEADER = None
_ORIG_PDF_HEADER = None
_ORIG_PPT_SOURCE_SPLIT = None
_ORIG_PDF_EXPORT = None

# Physical teaching sequence only; the Blueprint remains exactly 20 semantic units.
KICKOFF_LIVE_UNITS = frozenset({1, 3, 6, 8, 15, 16, 17, 20})


def _clean(value) -> str:
    return " ".join(str(value or "").split())


def _words(value, limit: int) -> str:
    words = _clean(value).split()
    return " ".join(words[:limit]) + ("..." if len(words) > limit else "")


def _is_kickoff(bp) -> bool:
    titles = " | ".join(_clean(getattr(u, "title", "")).lower()
                        for u in list(getattr(bp, "units", []) or []))
    families = " | ".join(_clean(x).lower()
                           for x in list(getattr(bp, "source_topic_families", []) or []))
    blob = f"{_clean(getattr(bp, 'lecture_title', '')).lower()} | {titles} | {families}"
    return (
        ("logistics" in blob or "next steps" in blob)
        and "assessment" in blob
        and ("engineering defense" in blob or "kickoff" in blob or "week 1" in blob)
    )


def _compact_physical_plan(bp):
    plan = list(_ORIG_PHYSICAL_PLAN(bp))
    if not _is_kickoff(bp):
        return plan

    compact = []
    for row in plan:
        kind, u, extra = row
        if kind in {"cover", "close"}:
            compact.append(row)
            continue
        if kind == "expansion":
            # Roadmaps/logistics stay authoritative in P1/syllabus and the website;
            # they are deliberately not part of the live kickoff sequence.
            continue
        number = int(getattr(u, "number", 0) or 0)
        if number in KICKOFF_LIVE_UNITS:
            compact.append(row)
    return compact


def _title_for(u) -> str:
    return _clean(presenter.RULE_NAMES.get(getattr(u, "number", 0), getattr(u, "title", "")))


def _ppt_header(slide, u, page_idx, total):
    title = _title_for(u)
    # Short headings keep the established v7.3.2 furniture.
    if len(title) <= 35:
        return _ORIG_PPT_HEADER(slide, u, page_idx, total)

    accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN)
    phase = presenter.PHASE_LABEL.get(u.phase, u.phase)
    presenter._ppt_text(
        slide, .34, .18, 4.8, .25,
        f"{phase}  /  {presenter.RULE_KIND.get(u.number, 'CONCEPT')}",
        8.4, accent, True
    )
    presenter._ppt_text(
        slide, 11.05, .18, 1.95, .25,
        f"U{u.number:02d}/20  ·  {page_idx:02d}/{total:02d}",
        7.3, presenter.MUTED, False, presenter.PP_ALIGN.RIGHT
    )
    # Two-line-safe title box. No decorative badge competes with a long heading.
    presenter._ppt_text(slide, .34, .52, 12.25, .70, title, 19.4, presenter.TEXT, True)
    presenter._ppt_text(
        slide, .34, 1.22, 12.25, .28,
        presenter._short(u.engineering_question, 24), 9.8, presenter.MUTED
    )
    line = slide.shapes.add_shape(
        presenter.MSO_SHAPE.RECTANGLE,
        presenter.Inches(.34), presenter.Inches(1.53),
        presenter.Inches(12.62), presenter.Inches(.018)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = presenter._rgb(presenter.GOLD)
    line.line.fill.background()


def _pdf_header(c, u, page_idx, total):
    title = _title_for(u)
    if len(title) <= 35:
        return _ORIG_PDF_HEADER(c, u, page_idx, total)

    accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN)
    presenter._pdf_text(
        c, 24, 508, 340, 16,
        f"{presenter.PHASE_LABEL.get(u.phase, u.phase)} / {presenter.RULE_KIND.get(u.number, 'CONCEPT')}",
        7.3, accent, True, max_lines=1
    )
    presenter._pdf_text(
        c, 790, 508, 145, 16,
        f"U{u.number:02d}/20 · {page_idx:02d}/{total:02d}",
        6.4, presenter.MUTED, False, "right", 1
    )
    presenter._pdf_text(c, 24, 466, 900, 47, title, 17.8, presenter.TEXT, True, max_lines=2)
    presenter._pdf_text(
        c, 24, 435, 900, 26,
        presenter._short(u.engineering_question, 24), 8.4, presenter.MUTED, max_lines=2
    )
    c.setStrokeColor(presenter.HexColor(presenter.GOLD))
    c.setLineWidth(.8)
    c.line(24, 428, 936, 428)


def _ppt_source_split(slide, u, asset_path, accent):
    """Native-figure prominence: the source visual dominates; commentary is secondary."""
    # The image box ends at 6.55; the fixed task bar starts at 6.82.
    presenter._ppt_add_image(slide, Path(asset_path), .34, 1.66, 9.18, 4.89)

    presenter._ppt_text(
        slide, 9.78, 1.78, 3.02, .28,
        "READ THE SOURCE FIGURE", 9.6, accent, True
    )
    items = presenter._items(u, 2)
    y = 2.22
    for item in items[:2]:
        presenter._ppt_text(
            slide, 9.80, y, 2.92, 1.22,
            "• " + _words(item, 15), 11.7, presenter.TEXT
        )
        y += 1.48

    # One small prompt replaces a third paragraph/takeaway box.
    presenter._ppt_text(
        slide, 9.80, 5.30, 2.92, .72,
        "Use the figure to justify the decision; do not paraphrase the whole source.",
        10.0, presenter.GOLD, True
    )


def _source_is_visual(source) -> bool:
    if not source:
        return False
    try:
        asset = source[0]
        return getattr(asset, "source_kind", "") in {sv.FIGURE_KIND, sv.PICTURE_KIND}
    except Exception:
        return False


def _pdf_export(bp, out, source_root=None, release_state="REVIEW"):
    """PDF companion with the same figure-first geometry as PPTX."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    c = presenter.rl_canvas.Canvas(str(out), pagesize=(presenter.PDF_W, presenter.PDF_H))
    plan = presenter._physical_plan(bp)
    assets = presenter._source_assets(bp, source_root)
    total = len(plan)

    for page_idx, (kind, u, extra) in enumerate(plan, 1):
        c.setFillColor(presenter.HexColor(presenter.BG))
        c.rect(0, 0, 960, 540, fill=1, stroke=0)

        if kind == "cover":
            presenter._pdf_cover(c, bp, total)
        elif kind == "close":
            presenter._pdf_close(c, bp, total)
        elif kind == "expansion":
            idx, chunk = extra
            presenter._pdf_expansion(c, u, idx, chunk, page_idx, total)
        else:
            presenter._pdf_header(c, u, page_idx, total)
            accent = presenter.PHASE_ACCENT.get(u.phase, presenter.CYAN)
            source = assets.get(u.number)

            if source and _source_is_visual(source):
                # 70%+ canvas prominence with native P1 asset; support is exactly two cues.
                presenter._pdf_image(c, source[1], 24, 78, 680, 344)
                presenter._pdf_text(
                    c, 724, 390, 212, 18,
                    "READ THE SOURCE FIGURE", 8.0, accent, True, max_lines=1
                )
                y = 346
                for item in presenter._items(u, 2)[:2]:
                    presenter._pdf_text(
                        c, 724, y, 212, 78,
                        "• " + _words(item, 15), 9.4, presenter.TEXT, max_lines=4
                    )
                    y -= 100
                presenter._pdf_text(
                    c, 724, 105, 212, 54,
                    "Use the figure to justify the decision; do not paraphrase the whole source.",
                    7.8, presenter.GOLD, True, max_lines=3
                )
            else:
                presenter._pdf_semantic(c, bp, u, accent)

            presenter._pdf_footer(c, u)
        c.showPage()

    c.save()
    return out


def apply_v735_figure_first_compact_kickoff_patch(app):
    global _PATCHED, _ORIG_PHYSICAL_PLAN, _ORIG_PPT_HEADER, _ORIG_PDF_HEADER
    global _ORIG_PPT_SOURCE_SPLIT, _ORIG_PDF_EXPORT
    if _PATCHED:
        return
    _PATCHED = True

    _ORIG_PHYSICAL_PLAN = presenter._physical_plan
    _ORIG_PPT_HEADER = presenter._ppt_header
    _ORIG_PDF_HEADER = presenter._pdf_header
    _ORIG_PPT_SOURCE_SPLIT = presenter._ppt_source_split
    _ORIG_PDF_EXPORT = presenter.export_presenter_pdf

    # Native/source-first quality. Genuine embedded source figures remain preferred;
    # higher raster density is only for cases that require a source-page crop.
    sv.PDF_RENDER_ZOOM = max(float(getattr(sv, "PDF_RENDER_ZOOM", 3.4)), 4.0)
    sv.MAX_FIGURE_ZOOM = max(float(getattr(sv, "MAX_FIGURE_ZOOM", 8.0)), 10.0)

    # Footer is a fixed classroom affordance; never solve density by making it tiny.
    leg.MIN_PPT_TASK_PT = max(float(getattr(leg, "MIN_PPT_TASK_PT", 10.2)), 11.0)
    leg.MIN_PDF_TASK_PT = max(float(getattr(leg, "MIN_PDF_TASK_PT", 8.2)), 9.0)

    presenter._physical_plan = _compact_physical_plan
    presenter._ppt_header = _ppt_header
    presenter._pdf_header = _pdf_header
    presenter._ppt_source_split = _ppt_source_split
    presenter.export_presenter_pdf = _pdf_export

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "figure_first_compact_kickoff_version": "v7.3.5",
            "native_figure_canvas": "PPTX 9.18in (~69% width); PDF 680/960px (~71% width) for genuine P1 figures/pictures.",
            "figure_support_cap": "Two short source-grounded cues; support is shortened before figure area or taskbar text.",
            "projection_font_floor": "Taskbar >=11pt PPTX and >=9pt PDF; long titles use a two-line-safe header.",
            "collision_guard": "Content stops above fixed footer; long-title header reserves its own vertical band.",
            "kickoff_live_units": sorted(KICKOFF_LIVE_UNITS),
            "kickoff_live_sequence": "cover + 8 essential teaching units + close (10 physical slides unless a non-kickoff plan applies).",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
