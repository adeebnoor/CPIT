from __future__ import annotations

import re

from .models import Blueprint, SourceProfile
from .source_bundle import SourceBundle

UNIT_MINUTES: dict[int, int] = {
    1: 4, 2: 4, 3: 3, 4: 4, 5: 5,
    6: 6, 7: 7, 8: 6, 9: 6, 10: 5,
    11: 5, 12: 5, 13: 5, 14: 5, 15: 5,
    16: 4, 17: 3, 18: 3, 19: 3, 20: 2,
}


def _txt(unit) -> str:
    return " ".join([
        unit.title,
        unit.engineering_question,
        *unit.core_content,
        *unit.pedagogy_content,
        *unit.enrichment_content,
        *unit.scenario_assumptions,
        unit.student_action,
        unit.takeaway,
        unit.evidence,
    ]).lower()


def _noncore_txt(unit) -> str:
    return " ".join([
        *unit.pedagogy_content,
        *unit.scenario_assumptions,
        unit.student_action,
        unit.takeaway,
        unit.evidence,
    ]).lower()


def apply_90_minute_timebox(bp: Blueprint, profile: SourceProfile, bundle: SourceBundle) -> Blueprint:
    bp.session_minutes = 90
    bp.source_manifest = bundle.manifest_lines()
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

    profile_names = {x.name.strip().lower() for x in profile.topic_families if x.name.strip()}
    explicit_scope = {x.strip().lower() for x in profile.in_scope_families if x.strip()}
    bp_topics = {x.strip().lower() for x in bp.source_topic_families if x.strip()}
    coverage_topics = {x.topic_family.strip().lower() for x in bp.topic_coverage if x.topic_family.strip()}

    checks["all_primary_families_are_in_scope"] = bool(profile_names) and (not explicit_scope or explicit_scope == profile_names)
    checks["all_primary_families_appear_in_blueprint"] = bp_topics == profile_names
    checks["all_primary_families_have_coverage_ledger"] = coverage_topics == profile_names
    checks["no_primary_topic_is_deferred"] = not profile.deferred_topics and not bp.deferred_topics
    checks["blueprint_copies_source_manifest"] = bp.source_manifest == bundle.manifest_lines()
    checks["every_primary_family_has_p1_anchor"] = all("[P1]" in (x.source_anchor or "").upper() for x in bp.topic_coverage)

    valid_ids = {x.source_id for x in bundle.items}
    anchors_ok = True
    for unit in bp.units:
        if not unit.core_content:
            continue
        ids = set(re.findall(r"\[([PS]\d+)\]", (unit.source_anchor or "").upper()))
        if not ids or not ids.issubset(valid_ids):
            anchors_ok = False
            break
    checks["technical_anchors_identify_bundle_source"] = anchors_ok
    checks["focus_does_not_narrow_primary_coverage"] = bp_topics == profile_names

    # v1.9: learner-visible order. A PREDICT tag hidden after explanation is not prediction-before-explanation.
    u5 = bp.units[4]
    q5 = u5.engineering_question.lower()
    checks["unit5_prediction_is_visible_before_explanation"] = "predict" in q5 and any(
        marker in q5 for marker in ["before", "without", "given only", "from the evidence", "from these constraints"]
    )

    # ATQAN functions are integrated pedagogy, while learner-facing titles remain source/topic-first.
    # Keep the historical check names for API compatibility; the semantics are now "present and integrated",
    # not "must dominate the title". Gate v14 separately rejects framework-first titles.
    u11, u12, u13, u14, u15 = bp.units[10:15]
    t11, t12, t13, t14, t15 = (_txt(u) for u in (u11, u12, u13, u14, u15))
    checks["unit11_saudi_context_is_dominant"] = any(k in t11 for k in ["saudi", "kingdom", "ksa", "gulf", "hypothetical"])
    checks["unit12_accountability_is_dominant"] = any(k in t12 for k in ["accountab", "role", "responsib", "ethical", "ethics", "amanah", "pre-condition", "post-condition"])
    checks["unit13_trend_is_dominant"] = any(k in t13 for k in ["trend", "future", "next", "evolv", "improv", "measurement", "change"])
    checks["unit14_wellbeing_is_dominant"] = any(k in t14 for k in ["wellbeing", "well-being", "practitioner", "workload", "sustainable", "refactor", "visibility", "process friction"])
    checks["unit15_ai_literacy_is_dominant"] = any(k in t15 for k in ["ai may assist", "human sign-off", "source check", "maturity", "capability", "audit"])

    # Pedagogy/non-core fields may not smuggle in technical mechanisms absent from the lecture bundle.
    source_text = bundle.combined_local_text().lower()
    watched = [
        "row-level encryption", "immutable logging", "penetration test", "penetration testing",
        "intrusion detection system", " ids ", "zero trust", "proxy gateway", "token-based",
        "container image", "infrastructure-as-code", "configuration drift", "cryptographic",
    ]
    leakage = []
    for unit in bp.units:
        noncore = " " + _noncore_txt(unit) + " "
        for term in watched:
            if term in noncore and term.strip() not in source_text:
                leakage.append((unit.number, term.strip()))
    checks["no_unsourced_technology_hidden_in_pedagogy"] = not leakage

    # Enrichment must have a traceable or explicitly hypothetical/exploratory basis.
    basis_ok = True
    acceptable_basis_markers = ["hypothetical", "scenario", "future exploration", "illustrative", "[s", "http://", "https://"]
    vague_only = ["standard literature", "industry best practice", "modern practice", "common practice"]
    for unit in bp.units:
        if not unit.enrichment_content:
            continue
        joined_basis = " ".join(unit.enrichment_basis).lower()
        if not joined_basis or any(v in joined_basis for v in vague_only):
            basis_ok = False
            break
        if not any(m in joined_basis for m in acceptable_basis_markers):
            basis_ok = False
            break
    checks["enrichment_basis_is_release_quality"] = basis_ok

    # Rubric must measure ISCARB engineering capability, not merely list weekly content topics.
    rubric_names = " ".join(r.criterion.lower() for r in bp.rubric_criteria)
    rubric_dimensions = [
        ["technical", "source fidelity", "correctness"],
        ["first principles", "mechanism", "derivation"],
        ["trade-off", "tradeoff", "engineering judgment", "alternatives"],
        ["evidence", "falsification", "verification"],
        ["constraint", "adapt", "redesign"],
        ["readiness", "etec", "professional accountability"],
    ]
    checks["rubric_has_explicit_iscarb_capability_dimensions"] = all(any(alias in rubric_names for alias in group) for group in rubric_dimensions)

    # Bounded assurance means no absolute security promises in Unit 20 pedagogy/subclaims.
    u20 = " " + " ".join([*bp.units[19].pedagogy_content, bp.units[19].takeaway, bp.units[19].evidence]).lower() + " "
    absolute_terms = [" guarantee", " guarantees", " guaranteed", " eliminate", " eliminates", " prevent", " prevents", " zero risk", " prove secure", " proves secure", " impossible to breach", " always secure"]
    checks["unit20_uses_bounded_assurance_language"] = not any(term in u20 for term in absolute_terms)

    return checks
