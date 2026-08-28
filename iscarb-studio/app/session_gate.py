from __future__ import annotations

import re

from .models import Blueprint, SourceProfile
from .source_bundle import SourceBundle

# A fixed 90-minute live lecture. The timebox is fixed; coverage is not negotiable.
# If the primary lecture is dense, ISCARB compresses rather than defers primary topics.
UNIT_MINUTES: dict[int, int] = {
    1: 4, 2: 4, 3: 3, 4: 4, 5: 5,          # IFHAM = 20
    6: 6, 7: 7, 8: 6, 9: 6, 10: 5,         # MARIS = 30
    11: 5, 12: 5, 13: 5, 14: 5, 15: 5,     # ATQAN = 25
    16: 4, 17: 3, 18: 3, 19: 3, 20: 2,     # MAYYIZ = 15
}


def apply_90_minute_timebox(bp: Blueprint, profile: SourceProfile, bundle: SourceBundle) -> Blueprint:
    bp.session_minutes = 90
    bp.source_manifest = bundle.manifest_lines()
    # Primary-source deferral is forbidden. Keep the field empty for backward compatibility.
    bp.deferred_topics = []
    for unit in bp.units:
        unit.planned_minutes = UNIT_MINUTES.get(unit.number, 0)
    return bp


def session_scope_gate(bp: Blueprint, profile: SourceProfile, bundle: SourceBundle) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    checks["session_is_exactly_90_minutes"] = bp.session_minutes == 90 and profile.session_minutes == 90
    checks["unit_pacing_totals_90_minutes"] = sum(u.planned_minutes for u in bp.units) == 90
    checks["one_primary_source"] = len([x for x in bundle.items if x.role == "primary"]) == 1
    checks["source_bundle_within_safe_limit"] = 1 <= len(bundle.items) <= 8

    # FULL-COVERAGE CONTRACT: every major P1 topic family stays in scope regardless of density.
    profile_names = {x.name.strip().lower() for x in profile.topic_families if x.name.strip()}
    explicit_scope = {x.strip().lower() for x in profile.in_scope_families if x.strip()}
    bp_topics = {x.strip().lower() for x in bp.source_topic_families if x.strip()}
    coverage_topics = {x.topic_family.strip().lower() for x in bp.topic_coverage if x.topic_family.strip()}

    checks["all_primary_families_are_in_scope"] = bool(profile_names) and (not explicit_scope or explicit_scope == profile_names)
    checks["all_primary_families_appear_in_blueprint"] = bp_topics == profile_names
    checks["all_primary_families_have_coverage_ledger"] = coverage_topics == profile_names
    checks["no_primary_topic_is_deferred"] = not profile.deferred_topics and not bp.deferred_topics
    checks["blueprint_copies_source_manifest"] = bp.source_manifest == bundle.manifest_lines()

    # Each primary family must remain visibly anchored to P1. Supporting sources can enrich it,
    # but they may not replace the primary lecture as the technical authority.
    checks["every_primary_family_has_p1_anchor"] = all(
        "[P1]" in (x.source_anchor or "").upper() for x in bp.topic_coverage
    )

    # With a multi-source bundle, every technical unit must identify the source(s) it uses.
    valid_ids = {x.source_id for x in bundle.items}
    anchors_ok = True
    for unit in bp.units:
        if not unit.core_content:
            continue
        anchor = unit.source_anchor or ""
        ids = set(re.findall(r"\[([PS]\d+)\]", anchor.upper()))
        if not ids or not ids.issubset(valid_ids):
            anchors_ok = False
            break
    checks["technical_anchors_identify_bundle_source"] = anchors_ok

    # A faculty focus may prioritize depth, but never delete primary coverage.
    checks["focus_does_not_narrow_primary_coverage"] = bp_topics == profile_names

    return checks
