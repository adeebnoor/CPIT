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


def _looks_like_title_only(asset: base.VisualAsset) -> bool:
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
    if _looks_like_title_only(asset):
        return -100.0
    score = base._asset_score(asset, unit, anchors)
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
