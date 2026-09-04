from __future__ import annotations

"""ISCARB v6.9.3: repair Balanced30 against the current LectureUnit schema."""

from . import presenter_v67_prod as presenter
from . import start_v440 as base

PUBLIC_VERSION = "6.9.3"
PIPELINE_ID = "faculty-studio-v6.9.3-balanced30-compatible"
_PATCHED = False


def _clean_rows(values):
    return [str(v).strip() for v in (values or []) if str(v).strip()]


def _source_expansion_for(unit):
    """Return genuine source overflow without relying on a removed model field.

    Older presenter code expected ``overflow_content``.  The current LectureUnit
    schema stores source-backed material in ``core_content`` instead.  Keep the
    first six source points on the core unit and use only the remainder as
    expansion material.  Never manufacture expansion from pedagogy/enrichment.
    """
    explicit = getattr(unit, "overflow_content", None)
    if explicit:
        return _clean_rows(explicit)

    core = _clean_rows(getattr(unit, "core_content", None))
    source_anchor = str(getattr(unit, "source_anchor", "") or "").strip()
    if not source_anchor or len(core) <= 6:
        return []
    return core[6:]


def balanced30_plan_v693(bp):
    """Cover + 20 core units + up to 8 source-only expansions + close."""
    plan = [("cover", None, None)]
    budget = 8
    expansion_no = 0

    for unit in list(getattr(bp, "units", []) or []):
        plan.append(("unit", unit, None))
        if budget <= 0:
            continue

        # Domain Spine must remain one curated map, never expansion-list pages.
        if int(getattr(unit, "number", 0) or 0) == 2:
            continue

        extra = _source_expansion_for(unit)
        for i in range(0, len(extra), 6):
            if budget <= 0:
                break
            chunk = extra[i:i + 6]
            if not chunk:
                continue
            expansion_no += 1
            plan.append(("expansion", unit, (expansion_no, chunk)))
            budget -= 1

    plan.append(("close", None, None))
    return plan


def apply_v693_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    # Last-write wins: replace the v6.8 plan that still dereferenced the removed
    # LectureUnit.overflow_content attribute and caused /presenter to return 500.
    presenter._physical_plan = balanced30_plan_v693

    base.PUBLIC_VERSION = PUBLIC_VERSION
    base.PIPELINE_ID = PIPELINE_ID

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "version": PUBLIC_VERSION,
            "pipeline": PIPELINE_ID,
            "balanced30": "current LectureUnit schema; source core overflow only; max 8 expansion pages",
            "presenter_preview_500_fix": True,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
