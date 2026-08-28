from __future__ import annotations

import math
import re

from .models import Blueprint, SourceProfile
from .prompts import IDR, EER
from .readiness import ETEC_IT_READINESS
from .readiness_map import SLO_KLO_MAP, expected_klos


def _text(unit) -> str:
    return " ".join([
        unit.title,
        unit.engineering_question,
        *unit.core_content,
        *unit.enrichment_content,
        *unit.scenario_assumptions,
        unit.student_action,
        unit.takeaway,
        unit.evidence,
    ]).lower()


def _core_text(unit) -> str:
    return " ".join(unit.core_content).lower()


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _profile_text(profile: SourceProfile | None) -> str:
    if profile is None:
        return ""
    return " ".join([
        profile.lecture_title,
        profile.weekly_focus,
        *[x.name + " " + x.why_important for x in profile.topic_families],
        *profile.technical_boundaries,
        *profile.source_warnings,
    ]).lower()


def deterministic_gate(bp: Blueprint, profile: SourceProfile | None = None) -> dict[str, bool]:
    checks: dict[str, bool] = {}

    checks["exactly_20_units"] = len(bp.units) == 20
    checks["exactly_5_clos"] = len(bp.clOs) == 5
    checks["unit_numbers_1_to_20"] = [u.number for u in bp.units] == list(range(1, 21))
    checks["phase_sequence"] = all(
        u.phase == ("IFHAM" if u.number <= 5 else "MARIS" if u.number <= 10 else "ATQAN" if u.number <= 15 else "MAYYIZ")
        for u in bp.units
    )
    checks["clo_ids_unique"] = sorted(c.id for c in bp.clOs) == ["CLO1", "CLO2", "CLO3", "CLO4", "CLO5"]
    checks["all_units_have_source_anchor"] = all(bool(u.source_anchor.strip()) for u in bp.units)
    checks["all_units_have_action"] = all(bool(u.student_action.strip()) for u in bp.units)
    checks["all_units_have_question"] = all(bool(u.engineering_question.strip()) for u in bp.units)

    # Exact semantic function contract for the first four reserved units.
    u2 = _text(bp.units[1])
    checks["unit2_is_domain_spine"] = any(k in u2 for k in ["domain spine", "system map", "topic map", "domain map"])
    if profile is not None and profile.topic_families:
        u2n = _norm(u2)
        family_hits = sum(1 for fam in profile.topic_families if _norm(fam.name) in u2n)
        required_hits = max(1, math.ceil(len(profile.topic_families) * 0.7))
        checks["unit2_maps_major_source_families"] = family_hits >= required_hits
    else:
        checks["unit2_maps_major_source_families"] = True

    u3 = bp.units[2]
    u3_text = _text(u3)
    checks["unit3_is_exactly_five_clos"] = (
        len(u3.core_content) == 5
        and all(f"clo{i}" in u3_text for i in range(1, 6))
    )

    u4 = _text(bp.units[3])
    hstack_terms = [
        "analytical reasoning",
        "engineering judgment",
        "evidence-based reasoning",
        "socio-technical thinking",
        "risk-aware design",
        "ethical responsibility",
    ]
    checks["unit4_has_all_six_hstack_competencies"] = all(term in u4 for term in hstack_terms)

    # Provenance split.
    checks["no_unresolved_verify_flags"] = not any(u.verify_before_release for u in bp.units)
    checks["enrichment_flag_consistency"] = all(
        (not u.enrichment_content and not u.contextual_enrichment)
        or (bool(u.enrichment_content) and u.contextual_enrichment and bool(u.enrichment_basis))
        for u in bp.units
    )
    checks["weekly_source_anchor_not_external"] = all(
        not any(marker in u.source_anchor.lower() for marker in ["http://", "https://", "etec", "gulf.edu", "nca.gov"])
        for u in bp.units
    )

    risky_claim_terms = [" require", " requires", " mandate", " mandates", " regulation", " regulations", " national rule", " market rule"]
    hypothetical_language_ok = True
    for u in bp.units:
        has_hyp_basis = any("hypothetical" in b.lower() for b in u.enrichment_basis)
        if not has_hyp_basis:
            continue
        for bullet in u.enrichment_content:
            low = " " + bullet.lower()
            if any(term in low for term in risky_claim_terms):
                if not any(marker in low for marker in ["assume", "in this scenario", "in this hypothetical", "scenario requires"]):
                    hypothetical_language_ok = False
    checks["hypothetical_enrichment_not_stated_as_fact"] = hypothetical_language_ok

    lenses = {lens for u in bp.units for lens in u.cimtlens}
    for lens in ["C", "I", "M", "T"]:
        checks[f"cimt_{lens}_present"] = lens in lenses
    idr_tags = {tag for u in bp.units for tag in u.inherited_requirements}
    eer_tags = {tag for u in bp.units for tag in u.elite_requirements}
    for tag in IDR:
        checks[f"coverage_{tag}"] = tag in idr_tags
    for tag in EER:
        checks[f"coverage_{tag}"] = tag in eer_tags

    u1 = _text(bp.units[0])
    diagnosis_leaks = [
        "the core issue is", "the root cause is", "the actual problem is",
        "the problem is a failure", "engineers must frame the challenge as",
        "engineers must frame the problem as", "the diagnosis is",
    ]
    checks["unit1_does_not_reveal_diagnosis"] = not any(p in u1 for p in diagnosis_leaks)

    declared_topics = {_norm(x) for x in bp.source_topic_families}
    coverage_topics = {_norm(x.topic_family) for x in bp.topic_coverage}
    if profile is not None:
        authoritative_topics = {_norm(x.name) for x in profile.topic_families}
        checks["source_topic_list_matches_source_profile"] = declared_topics == authoritative_topics
        checks["topic_coverage_matches_source_profile"] = coverage_topics == authoritative_topics
    else:
        checks["topic_coverage_matches_source_profile"] = declared_topics == coverage_topics
    checks["no_major_topic_first_taught_after_unit15"] = all(x.first_taught_unit <= 15 for x in bp.topic_coverage)
    checks["topic_coverage_has_source_anchors"] = all(bool(x.source_anchor.strip()) for x in bp.topic_coverage)

    u5 = _text(bp.units[4])
    checks["unit5_prediction_before_explanation"] = "predict" in u5
    checks["unit5_visible_first_principles_derivation"] = (
        "constraint" in u5 and "deriv" in u5 and "principle" in u5
    )

    combined_5_10 = " ".join(_text(u) for u in bp.units[4:10])
    checks["uncertainty_is_operationalized"] = (
        "unknown" in combined_5_10
        and any(k in combined_5_10 for k in ["monitor", "telemetry", "observe", "measure after", "post-deployment"])
    )
    u10 = _text(bp.units[9])
    checks["unit10_known_unknown_monitoring"] = (
        "known" in u10 and "unknown" in u10 and any(k in u10 for k in ["monitor", "telemetry", "observe"])
    )

    u8 = _text(bp.units[7])
    alternatives_present = (
        any(k in u8 for k in ["alternative", "option a", "design a", "approach a"])
        or " versus " in u8
        or " vs. " in u8
        or " vs " in u8
    )
    tradeoff_present = any(k in u8 for k in ["trade-off", "tradeoff", "sacrifice", "cost", "versus", " vs "])
    checks["unit8_has_alternatives_and_tradeoff"] = alternatives_present and tradeoff_present

    u9 = _text(bp.units[8])
    checks["unit9_has_falsification"] = any(k in u9 for k in ["falsif", "prove us wrong", "abandon", "disconfirm", "counter-evidence"])
    checks["unit17_constraint_mutation"] = any(k in _text(bp.units[16]) for k in ["constraint", "mutation", "keep", "change", "remove", "add", "redesign"])

    u15 = _text(bp.units[14])
    checks["unit15_ai_may_assist"] = "ai may assist" in u15
    checks["unit15_ai_must_not_autonomously"] = (
        "ai must not" in u15 and any(k in u15 for k in ["autonomous", "autonomously", "trusted"])
    )

    u18 = _text(bp.units[17])
    checks["unit18_full_evidence_protocol"] = all(k in u18 for k in ["claim", "evidence", "warrant", "counter-evidence", "residual uncertainty"])

    source_profile_text = _profile_text(profile)
    source_mentions_ai = bool(re.search(r"\bai\b|artificial intelligence", source_profile_text))
    checks["unit15_ai_not_misrepresented_as_source"] = source_mentions_ai or not bool(re.search(r"\bai\b|artificial intelligence", _core_text(bp.units[14])))
    checks["unit14_wellbeing_not_misrepresented_as_source"] = not any(
        term in _core_text(bp.units[13]) for term in ["cognitive load", "operator fatigue", "burnout", "alert fatigue", "wellbeing"]
    )
    checks["unit18_evidence_method_not_misrepresented_as_source"] = not any(
        term in _core_text(bp.units[17]) for term in ["warrant", "counter-evidence", "residual uncertainty", "evidence policy framework"]
    )
    checks["unit19_rubric_method_not_misrepresented_as_source"] = not any(
        term in _core_text(bp.units[18]) for term in ["distinguished", "not yet ready", "rubric calibration", "four-tier rubric"]
    )

    checks["rubric_has_at_least_6_criteria"] = len(bp.rubric_criteria) >= 6
    rubric_names = " ".join(_norm(r.criterion) for r in bp.rubric_criteria)
    checks["rubric_covers_core_engineering_dimensions"] = all(
        any(alias in rubric_names for alias in aliases)
        for aliases in [
            ["technical", "correctness"],
            ["first principles", "mechanism", "derivation"],
            ["trade off", "tradeoff", "engineering judgment"],
            ["evidence", "falsification", "verification"],
            ["adapt", "constraint", "redesign"],
            ["readiness", "etec", "slo", "klo"],
        ]
    )
    checks["rubric_all_four_descriptors_present"] = all(
        all(bool(v.strip()) for v in [r.distinguished, r.ready, r.developing, r.not_yet_ready])
        for r in bp.rubric_criteria
    )

    checks["readiness_alignment_present"] = len(bp.readiness_alignment) >= 1
    valid_skus = ETEC_IT_READINESS["skus"]
    valid_klos = ETEC_IT_READINESS["klo"]
    checks["readiness_no_eku_targets"] = all(
        "eku" not in (r.gku + " " + r.sku + " " + " ".join(r.slo_refs)).lower()
        for r in bp.readiness_alignment
    )
    checks["readiness_refs_exist_in_etec_profile"] = all(
        r.sku in valid_skus
        and r.gku == valid_skus[r.sku]["gku"]
        and all(s in valid_skus[r.sku]["slos"] for s in r.slo_refs)
        and all(k in valid_klos for k in r.klo_refs)
        and set(r.standard_source_pages).issubset(set(valid_skus[r.sku]["source_pages"]))
        for r in bp.readiness_alignment
    )
    checks["readiness_exact_official_slo_klo_map"] = all(
        r.sku in SLO_KLO_MAP
        and all(s in SLO_KLO_MAP[r.sku] for s in r.slo_refs)
        and set(r.klo_refs) == set(expected_klos(r.sku, r.slo_refs))
        for r in bp.readiness_alignment
    )
    checks["readiness_has_clo_and_evidence_trace"] = all(
        bool(r.clo_ids)
        and bool(r.evidence_units)
        and all(1 <= n <= 20 for n in r.evidence_units)
        and bool(r.standard_source_pages)
        for r in bp.readiness_alignment
    )
    u16_all = _text(bp.units[15])
    checks["unit16_names_etec_readiness_targets"] = (
        "etec" in u16_all
        and any(r.sku.lower() in u16_all or any(s.lower() in u16_all for s in r.slo_refs) for r in bp.readiness_alignment)
    )
    checks["gulf_is_orientation_not_authority"] = not any(
        "gulf" in r.standard.lower() or "gulf.edu" in r.standard.lower() for r in bp.readiness_alignment
    )

    u20 = _text(bp.units[19])
    checks["unit20_assurance_language"] = all(k in u20 for k in ["claim", "evidence", "warrant", "residual uncertainty"])
    checks["unit20_avoids_false_certainty"] = not any(k in u20 for k in [
        "undeniable", "proves security", "proven secure", "guarantees security", "zero uncertainty",
        "proving security", "proving critical service", "prove the system is secure",
    ])

    return checks


def all_required_pass(checks: dict[str, bool]) -> bool:
    return all(checks.values())


def failed_check_names(checks: dict[str, bool]) -> list[str]:
    return [k for k, v in checks.items() if not v]
