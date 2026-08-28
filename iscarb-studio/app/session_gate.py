from __future__ import annotations

import re

from .models import Blueprint, SourceProfile
from .source_bundle import SourceBundle

# A 90-minute live lecture. Units 16-20 brief/launch the portfolio, evidence,
# rubric and assurance work; they are not intended to consume the full take-home task in class.
UNIT_MINUTES: dict[int, int] = {
    1: 4, 2: 4, 3: 3, 4: 4, 5: 5,          # IFHAM = 20
    6: 6, 7: 7, 8: 6, 9: 6, 10: 5,         # MARIS = 30
    11: 5, 12: 5, 13: 5, 14: 5, 15: 5,     # ATQAN = 25
    16: 4, 17: 3, 18: 3, 19: 3, 20: 2,     # MAYYIZ = 15
}


def apply_90_minute_timebox(bp: Blueprint, profile: SourceProfile, bundle: SourceBundle) -> Blueprint:
    bp.session_minutes = 90
    bp.source_manifest = bundle.manifest_lines()
    bp.deferred_topics = list(profile.deferred_topics)
    for unit in bp.units:
        unit.planned_minutes = UNIT_MINUTES.get(unit.number, 0)
    return bp


def session_scope_gate(bp: Blueprint, profile: SourceProfile, bundle: SourceBundle) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    checks["session_is_exactly_90_minutes"] = bp.session_minutes == 90 and profile.session_minutes == 90
    checks["unit_pacing_totals_90_minutes"] = sum(u.planned_minutes for u in bp.units) == 90
    checks["one_primary_source"] = len([x for x in bundle.items if x.role == "primary"]) == 1
    checks["source_bundle_within_safe_limit"] = 1 <= len(bundle.items) <= 8
    checks["scope_not_mixed_across_multiple_lectures"] = profile.scope_fit != "MIXED"
    checks["lecture_scope_is_teachable_in_90_minutes"] = 1 <= len(profile.topic_families) <= 6

    profile_names = {x.name.strip().lower() for x in profile.topic_families}
    explicit_scope = {x.strip().lower() for x in profile.in_scope_families if x.strip()}
    checks["in_scope_family_list_matches_profile"] = not explicit_scope or explicit_scope == profile_names

    deferred = {x.strip().lower() for x in profile.deferred_topics if x.strip()}
    bp_topics = {x.strip().lower() for x in bp.source_topic_families if x.strip()}
    checks["deferred_topics_not_promoted_to_weekly_scope"] = not bool(deferred & bp_topics)
    checks["blueprint_copies_deferred_topics"] = {x.lower() for x in bp.deferred_topics} == deferred
    checks["blueprint_copies_source_manifest"] = bp.source_manifest == bundle.manifest_lines()

    # With a multi-source bundle, every technical anchor should identify its source ID.
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

    return checks
