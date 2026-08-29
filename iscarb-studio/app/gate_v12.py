from __future__ import annotations

"""ISCARB Gate v12 — CIMT+ computing-wide coverage and visual integrity.

v12 preserves every v11 source/provenance/readiness invariant and adds:
- atomic major P1 coverage ledger completeness,
- source-native computing knowledge typing,
- one dominant visual plan per Unit,
- safe source-visual provenance,
- representation diversity so all computing subjects are not rendered as the
  same boxes/arrows template.
"""

from .gate_v11 import deterministic_gate as gate_v11
from .models import Blueprint, SourceProfile


def _major_profile_items(profile: SourceProfile | None):
    if profile is None:
        return []
    return [x for x in profile.coverage_items if x.importance == "major"]


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    checks = gate_v11(bp, profile, source_text)

    major = _major_profile_items(profile)
    profile_ids = {x.id for x in major}
    ledger_by_id = {x.coverage_id: x for x in bp.coverage_ledger}

    checks["v12_atomic_computing_profile_exists"] = bool(major)
    checks["v12_every_major_p1_element_in_coverage_ledger"] = bool(major) and profile_ids.issubset(ledger_by_id)

    exact_labels = True
    p1_anchors = True
    first_taught = True
    knowledge_types_match = True
    for item in major:
        row = ledger_by_id.get(item.id)
        if row is None:
            exact_labels = p1_anchors = first_taught = knowledge_types_match = False
            continue
        if row.label.strip() != item.label.strip():
            exact_labels = False
        if "[P1]" not in (item.source_anchor or "").upper() or "[P1]" not in (row.source_anchor or "").upper():
            p1_anchors = False
        if row.first_taught_unit > 15:
            first_taught = False
        if row.knowledge_type != item.knowledge_type:
            knowledge_types_match = False

    checks["v12_coverage_labels_preserve_p1"] = bool(major) and exact_labels
    checks["v12_major_coverage_has_p1_provenance"] = bool(major) and p1_anchors
    checks["v12_every_major_element_first_taught_by_unit15"] = bool(major) and first_taught
    checks["v12_knowledge_types_preserve_profile"] = bool(major) and knowledge_types_match

    checks["v12_every_unit_has_knowledge_type"] = all(bool(u.knowledge_types) for u in bp.units)
    checks["v12_every_unit_has_visual_plan"] = all(u.visual_plan is not None for u in bp.units)
    checks["v12_visual_plan_has_teaching_purpose"] = all(
        u.visual_plan is not None and bool(u.visual_plan.teaching_purpose.strip()) for u in bp.units
    )
    checks["v12_visual_plan_has_citation"] = all(
        u.visual_plan is not None and bool(u.visual_plan.citation.strip()) for u in bp.units
    )
    checks["v12_no_unverifiable_source_visual_claim"] = all(
        u.visual_plan is not None and (
            not u.visual_plan.source_visual_available
            or bool(u.visual_plan.source_page_or_slide.strip())
            or "[P1]" in (u.source_anchor or "").upper()
        )
        for u in bp.units
    )

    visual_types = {
        (u.visual_plan.visual_type or "").strip().lower()
        for u in bp.units
        if u.visual_plan is not None and (u.visual_plan.visual_type or "").strip()
    }
    checks["v12_visual_grammar_is_not_one_repeated_template"] = len(visual_types) >= 6

    # Computing representation sentinel: source-native technical Units 6-10 may
    # not all collapse into generic concept-map/card visuals.
    generic = {"concept-map", "causal-concept-map", "cards", "generic", "generic-boxes", "infographic"}
    technical_units = bp.units[5:10]
    native_specialized = [
        u for u in technical_units
        if any(k != "CONCEPT" for k in u.knowledge_types)
    ]
    checks["v12_source_native_computing_representation"] = (
        not native_specialized
        or any(
            u.visual_plan is not None and u.visual_plan.visual_type.strip().lower() not in generic
            for u in native_specialized
        )
    )
    return checks
