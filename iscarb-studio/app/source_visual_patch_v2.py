from __future__ import annotations

"""Hardening patch for Visual Lecture Engine v2.

Explicit source anchors are authoritative. Semantic ranking is allowed only
when a source-backed unit does not name a specific P1 slide/page.
"""

import re

from . import source_visuals as sv

_parse_explicit_coordinates = sv.anchor_slides


def robust_anchor_slides(anchor: str) -> list[int]:
    # Share the parser used outside application bootstrap too. Source IDs,
    # chapter numbers and coverage IDs are not page coordinates.
    return _parse_explicit_coordinates(anchor)


def robust_plan_for_unit(bp, unit, registry=None):
    visual_type = sv.VISUAL_TYPES.get(unit.number, "concept-visual")
    purpose = sv.TEACHING_PURPOSE.get(unit.number, "Make the engineering decision visible.")
    anchor = (unit.source_anchor or "").strip()
    source_backed = sv._looks_source_backed(anchor)

    if registry and unit.number in sv.SOURCE_VISUAL_PRIORITY and source_backed:
        anchors = robust_anchor_slides(anchor)
        if anchors:
            by_number = {asset.slide_number: asset for asset in registry.assets}
            for slide_number in anchors:
                asset = by_number.get(slide_number)
                if asset is not None:
                    return sv.VisualPlan(
                        visual_type=visual_type,
                        teaching_purpose=purpose,
                        reuse_mode="USE",
                        citation=f"Source visual: [P1] Slide/Page {asset.slide_number} · {registry.source_title}",
                        source_visual_available=True,
                        source_slide=asset.slide_number,
                        asset=asset,
                        focal_elements=(unit.takeaway, unit.student_action),
                    )
            # An explicit anchor that is outside the available file must NOT be
            # silently replaced by a semantically similar slide.
            return sv.VisualPlan(
                visual_type, purpose, "REDRAW",
                f"{anchor} · explicit source visual unavailable; ISCARB redraw only",
                False, None, None, (unit.takeaway, unit.student_action),
            )

        ranked = sorted(registry.assets, key=lambda a: sv._asset_score(a, unit, set()), reverse=True)
        if ranked and sv._asset_score(ranked[0], unit, set()) >= 8.0:
            best = ranked[0]
            return sv.VisualPlan(
                visual_type, purpose, "USE",
                f"Source visual: [P1] Slide/Page {best.slide_number} · {registry.source_title}",
                True, best.slide_number, best, (unit.takeaway, unit.student_action),
            )

    if source_backed:
        return sv.VisualPlan(visual_type, purpose, "REDRAW", anchor or "[P1] source-anchored redraw", False, None, None,
                             (unit.takeaway, unit.student_action))
    return sv.VisualPlan(visual_type, purpose, "NEW", "ISCARB pedagogy — original teaching visualization", False, None, None,
                         (unit.takeaway, unit.student_action))


sv.anchor_slides = robust_anchor_slides
sv.plan_for_unit = robust_plan_for_unit
