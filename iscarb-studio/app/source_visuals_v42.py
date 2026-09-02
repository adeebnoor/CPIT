from __future__ import annotations

"""ISCARB v4.2 source-visual quality planner.

Explicit P1 anchors remain authoritative for provenance, but an anchored title
slide is not automatically a useful teaching visual.  This planner prefers the
most information-bearing slide inside the anchored range and falls back to an
ISCARB redraw when the source image would merely enlarge a heading.
"""

import re
from pathlib import Path

from . import source_visuals as base
from .models import Blueprint, LectureUnit


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9+/#_.-]*", text or ""))


# A book page whose only content is running prose cannot fill a slide: enlarged
# to the canvas it is a wall of 10pt text, and the chapter's own figures are
# cropped separately anyway. A dense lecture slide is a different thing - it was
# authored to be projected - so the rule applies only to portrait pages, which
# is what separates a printed page from a 16:9 or 4:3 slide.
MAX_WORDS_FOR_A_PAGE_VISUAL = 220


def _is_portrait(asset) -> bool:
    size = _asset_pixel_size(asset)
    return bool(size and size[1] > size[0])


def _is_text_wall(asset: base.VisualAsset) -> bool:
    return (
        asset.source_kind != base.FIGURE_KIND
        and asset.visual_area_ratio < .05
        and _word_count(asset.alt_text or "") > MAX_WORDS_FOR_A_PAGE_VISUAL
        and _is_portrait(asset)
    )


def _looks_like_title_only(asset: base.VisualAsset) -> bool:
    # A cropped, captioned figure is information-bearing by construction; its
    # alt text is the caption plus its labels, which a word count would call thin.
    if asset.source_kind == base.FIGURE_KIND:
        return False
    if asset.slide_number != 1 and asset.visual_area_ratio >= .25:
        # A diagram-only page can contain little extractable text. Its actual
        # image content, not an OCR word count, makes it information-bearing.
        return False
    text = " ".join((asset.alt_text or "").split())
    wc = _word_count(text)
    if wc < 11:
        return True
    low = text.lower()
    # Typical source-slide furniture should not make a two-word title look rich.
    furniture = [
        "chapter", "software engineering", "ian sommerville", "©", "copyright",
        "department", "faculty", "university", "semester", "fall", "spring",
        "professor", "phd", "course", "class",
    ]
    stripped = low
    for token in furniture:
        stripped = stripped.replace(token, " ")
    meaningful = [w for w in re.findall(r"[a-z][a-z0-9-]{2,}", stripped) if w not in {"page", "slide", "edition"}]
    technical_cues = {
        "definition", "example", "process", "model", "architecture", "system",
        "failure", "risk", "cost", "requirements", "properties", "activities",
        "algorithm", "equation", "protocol", "metric", "trade", "advantages",
    }
    # Cover slides often contain enough author/course furniture to clear a raw
    # word-count rule.  Unless a first page also carries real explanatory cues,
    # it is not teaching material and must never fill a Unit's main canvas.
    if asset.slide_number == 1 and not (technical_cues & set(meaningful)):
        return True
    return len(set(meaningful)) < 7


def _quality_score(asset: base.VisualAsset, unit: LectureUnit, anchors: set[int]) -> float:
    if _looks_like_title_only(asset) or _is_text_wall(asset):
        return -100.0
    score = base._asset_score(asset, unit, anchors)
    if asset.source_kind == base.FIGURE_KIND:
        # The chapter's own diagram beats a rendering of the page it sits on.
        score += 14.0
    if asset.source_kind == base.PICTURE_KIND:
        # The picture the lecturer pasted onto the page beats a rendering of the
        # page it was pasted on, which is the same picture inside a title bar.
        score += 6.0
    if asset.visual_area_ratio >= .25:
        score += 12.0
    wc = _word_count(asset.alt_text)
    if 18 <= wc <= 120:
        score += 8.0
    elif 121 <= wc <= 220:
        score += 4.0
    elif wc > 300:
        score -= 4.0
    # Reward visual/content cues that commonly indicate a meaningful source slide.
    low = (asset.alt_text or "").lower()
    for cue in ("cost", "process", "activities", "requirements", "model", "figure", "diagram", "advantages", "disadvantages", "failure", "redundancy", "diversity", "formal", "regulation", "compliance"):
        if cue in low:
            score += 1.5
    return score


def _asset_pixel_size(asset):
    """(width, height) in pixels, or None when the asset cannot be measured."""
    path = base.local_asset(asset)
    if not path or not Path(path).exists():
        return None
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def _asset_pixel_width(asset) -> int | None:
    """Pixel width of a source asset, or None when it cannot be measured."""
    path = base.local_asset(asset)
    if not path or not Path(path).exists():
        return None
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size[0]
    except Exception:
        return None


def _is_presentable(asset) -> bool:
    """Whether this asset can fill the teaching canvas without visible softening.

    A source figure earns the main canvas by being readable there. One that has
    to be enlarged past its own resolution teaches less than a clean redraw of
    the same mechanism, so it is not eligible for USE. An asset we cannot
    measure keeps the previous behaviour rather than being rejected on a guess.
    """
    width = _asset_pixel_width(asset)
    return width is None or width >= base.MIN_PRESENTABLE_ASSET_WIDTH


# A page of prose wins a keyword count against a picture every time - the
# picture has almost no words to match on - which is how a "Chapter Summary"
# slide kept beating the diagram two pages before it. Inside a unit's own
# anchor range a picture the lecturer chose to project is at least as good a
# teaching surface as a paragraph, so it takes the canvas whenever it is nearly
# as relevant. It never reaches outside the range, so provenance is unchanged.
PICTURE_PREFERENCE_SHARE = .6


def _prefer_source_picture(ranked, unit, anchors):
    if not ranked or ranked[0].source_kind == base.PICTURE_KIND:
        return ranked
    top = _quality_score(ranked[0], unit, anchors)
    for asset in ranked:
        if asset.source_kind == base.PICTURE_KIND and _quality_score(asset, unit, anchors) >= top * PICTURE_PREFERENCE_SHARE:
            return [asset, *(a for a in ranked if a is not asset)]
    return ranked


def _visual_type(unit: LectureUnit) -> str:
    if unit.visual_plan is not None and unit.visual_plan.visual_type.strip():
        return unit.visual_plan.visual_type.strip()
    return base.VISUAL_TYPES.get(unit.number, "concept-visual")


def plan_for_unit_v42(bp: Blueprint, unit: LectureUnit, registry: base.VisualRegistry | None = None) -> base.VisualPlan:
    purpose = (unit.visual_plan.teaching_purpose if unit.visual_plan is not None else "") or base.TEACHING_PURPOSE.get(unit.number, "Make the engineering decision visible.")
    anchor = (unit.source_anchor or "").strip()
    source_backed = base._looks_source_backed(anchor)
    visual_type = _visual_type(unit)

    if registry and unit.number in base.SOURCE_VISUAL_PRIORITY and source_backed:
        anchors = set(base.anchor_slides(anchor))
        pool = [a for a in registry.assets if not anchors or a.slide_number in anchors]
        # An unavailable explicit page is not permission to substitute another
        # page. Leave the pool empty and produce a provenance-safe redraw.
        ranked = sorted(pool, key=lambda a: _quality_score(a, unit, anchors), reverse=True)
        ranked = _prefer_source_picture(ranked, unit, anchors)
        if ranked:
            best = ranked[0]
            score = _quality_score(best, unit, anchors)
            # A source visual must carry real explanatory information.  Low-info
            # title pages are REDRAW even when the anchor names them explicitly.
            if score >= 10.0 and not _looks_like_title_only(best) and _is_presentable(best):
                return base.VisualPlan(
                    visual_type,
                    purpose,
                    "USE",
                    f"Source visual: [P1] Slide/Page {best.slide_number} · {registry.source_title}",
                    True,
                    best.slide_number,
                    best,
                    (unit.takeaway, unit.student_action),
                )

    if source_backed:
        return base.VisualPlan(
            visual_type,
            purpose,
            "REDRAW",
            anchor or "[P1] source-anchored redraw",
            False,
            None,
            None,
            (unit.takeaway, unit.student_action),
        )
    return base.VisualPlan(
        visual_type,
        purpose,
        "NEW",
        "ISCARB pedagogy — original teaching visualization",
        False,
        None,
        None,
        (unit.takeaway, unit.student_action),
    )


def plans_for_blueprint_v42(bp: Blueprint, source_root=None) -> list[base.VisualPlan]:
    registry = base.load_registry(bp, source_root=source_root)
    return [plan_for_unit_v42(bp, unit, registry) for unit in bp.units]
