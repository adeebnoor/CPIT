from __future__ import annotations

import re

from .models import Blueprint
from .prompts import IDR, EER


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


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def deterministic_gate(bp: Blueprint) -> dict[str, bool]:
    checks: dict[str, bool] = {}

    # Structural contract.
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

    # Weekly-source provenance must stay separate from enrichment.
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

    # CIMT and inherited/elite requirements.
    lenses = {lens for u in bp.units for lens in u.cimtlens}
    for lens in ["C", "I", "M", "T"]:
        checks[f"cimt_{lens}_present"] = lens in lenses
    idr_tags = {tag for u in bp.units for tag in u.inherited_requirements}
    eer_tags = {tag for u in bp.units for tag in u.elite_requirements}
    for tag in IDR:
        checks[f"coverage_{tag}"] = tag in idr_tags
    for tag in EER:
        checks[f"coverage_{tag}"] = tag in eer_tags

    # Problem framing: Unit 1 cannot give away the diagnosis.
    u1 = _text(bp.units[0])
    diagnosis_leaks = [
        "the core issue is", "the root cause is", "the actual problem is",
        "the problem is a failure", "engineers must frame the challenge as",
        "engineers must frame the problem as", "the diagnosis is",
    ]
    checks["unit1_does_not_reveal_diagnosis"] = not any(p in u1 for p in diagnosis_leaks)

    # Major technical topic coverage must be complete before the MAYYIZ assessment phase.
    source_topics = {_norm(x) for x in bp.source_topic_families}
    coverage_topics = {_norm(x.topic_family) for x in bp.topic_coverage}
    checks["topic_coverage_matches_source_profile"] = source_topics == coverage_topics
    checks["no_major_topic_first_taught_after_unit15"] = all(x.first_taught_unit <= 15 for x in bp.topic_coverage)
    checks["topic_coverage_has_source_anchors"] = all(bool(x.source_anchor.strip()) for x in bp.topic_coverage)

    # Elite engineering semantics with simple hard checks; semantic auditor handles the rest.
    combined_5_10 = " ".join(_text(u) for u in bp.units[4:10])
    checks["uncertainty_is_operationalized"] = (
        "unknown" in combined_5_10
        and any(k in combined_5_10 for k in ["monitor", "telemetry", "observe", "measure after", "post-deployment"])
    )
    u8 = _text(bp.units[7])
    checks["unit8_has_alternatives_and_tradeoff"] = (
        any(k in u8 for k in ["alternative", "option a", "design a", "approach a"])
        and any(k in u8 for k in ["trade-off", "tradeoff", "sacrifice", "cost", "versus", "vs."])
    )
    u9 = _text(bp.units[8])
    checks["unit9_has_falsification"] = any(k in u9 for k in ["falsif", "prove us wrong", "abandon", "disconfirm", "counter-evidence"])
    checks["unit17_constraint_mutation"] = any(k in _text(bp.units[16]) for k in ["constraint", "mutation", "keep", "change", "remove", "add", "redesign"])

    # Unit 15 AI permissibility gate must be explicit, not implied.
    u15 = _text(bp.units[14])
    checks["unit15_ai_may_assist"] = "ai may assist" in u15
    checks["unit15_ai_must_not_autonomously"] = (
        "ai must not" in u15 and any(k in u15 for k in ["autonomous", "autonomously", "trusted"])
    )

    # Unit 18 is evidence policy, not a late content lecture.
    u18 = _text(bp.units[17])
    checks["unit18_full_evidence_protocol"] = all(k in u18 for k in ["claim", "evidence", "warrant", "counter-evidence", "residual uncertainty"])

    # Four-level rubric must be a real matrix, not four vague bullets.
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

    # ETEC readiness: GKU/SKU/SLO/KLO → CLO → evidence; EKUs are forbidden for standardized readiness.
    checks["readiness_alignment_present"] = len(bp.readiness_alignment) >= 1
    checks["readiness_no_eku_targets"] = all(
        "eku" not in (r.gku + " " + r.sku + " " + " ".join(r.slo_refs)).lower()
        for r in bp.readiness_alignment
    )
    checks["readiness_refs_structured"] = all(
        r.gku.upper().startswith("GKU")
        and r.sku.upper().startswith("SKU")
        and all(x.upper().startswith("SLO") for x in r.slo_refs)
        and all(x.upper().startswith("KLO") for x in r.klo_refs)
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
        "etec" in u16_all and any(r.sku.lower() in u16_all or any(s.lower() in u16_all for s in r.slo_refs) for r in bp.readiness_alignment)
    )
    checks["gulf_is_orientation_not_authority"] = not any(
        "gulf" in r.standard.lower() or "gulf.edu" in r.standard.lower() for r in bp.readiness_alignment
    )

    # Assurance must be bounded and evidence-based.
    u20 = _text(bp.units[19])
    checks["unit20_assurance_language"] = all(k in u20 for k in ["claim", "evidence", "warrant", "residual uncertainty"])
    checks["unit20_avoids_false_certainty"] = not any(k in u20 for k in ["undeniable", "proves security", "proven secure", "guarantees security", "zero uncertainty"])

    return checks


def all_required_pass(checks: dict[str, bool]) -> bool:
    return all(checks.values())


def failed_check_names(checks: dict[str, bool]) -> list[str]:
    return [k for k, v in checks.items() if not v]
