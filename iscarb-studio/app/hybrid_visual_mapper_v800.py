from __future__ import annotations

"""Final v8 mapping policy: 3-5 distinct source visuals, not image wallpaper."""

from typing import Any

from .hybrid_visual_engine import build_hybrid_visual_map as _raw_map


def build_hybrid_visual_map(job: Any, max_critical: int = 5) -> dict[str, Any]:
    data = _raw_map(job, max_critical=max_critical)
    units = data.get("units") or {}
    ranked = sorted(
        units.items(),
        key=lambda item: float((item[1] or {}).get("mapping_score", 0.0)),
        reverse=True,
    )
    distinct: dict[str, dict[str, Any]] = {}
    used_pages: set[int] = set()
    for unit_key, visual in ranked:
        try:
            page = int(visual.get("page"))
        except Exception:
            continue
        if page in used_pages:
            continue
        distinct[str(unit_key)] = visual
        used_pages.add(page)
        if len(distinct) >= max_critical:
            break
    data["units"] = distinct
    data["mapped_visual_count"] = len(distinct)
    data["mapping_policy"] = "At most five distinct P1 visuals are mapped to learner Units; repeated decorative reuse is suppressed."
    return data
