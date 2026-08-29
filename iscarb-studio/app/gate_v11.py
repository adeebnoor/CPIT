from __future__ import annotations

"""ISCARB Gate v11 — release-consistent deterministic gate.

v11 preserves all Gate v10 requirements. It corrects one brittle coherence test:
the central-system check evaluates the actual opening engineering crisis, not
later Saudi contextualization/readiness/evidence units that may legitimately
reference other sectors for comparison. No source-fidelity requirement is relaxed.
"""

import re

from .gate_v10 import deterministic_gate as gate_v10
from .models import Blueprint, SourceProfile


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _domain_clusters(text: str) -> set[str]:
    low = " " + _norm(text) + " "
    groups = {
        "healthcare": [" patient ", " clinical ", " hospital ", " healthcare ", " medical record ", " health record "],
        "finance": [" trading ", " equity ", " stock ", " financial ", " banking ", " transaction order "],
        "aviation": [" aircraft ", " aviation ", " air traffic "],
        "automotive": [" vehicle ", " automotive ", " car control "],
        "energy": [" power grid ", " electricity ", " energy system "],
    }
    return {name for name, terms in groups.items() if any(term in low for term in terms)}


def _opening_crisis_text(bp: Blueprint) -> str:
    u1 = bp.units[0]
    # Enrichment and downstream assessment/context units are intentionally not
    # part of this test. The invariant is one central ill-structured opening case.
    return " ".join([
        bp.central_engineering_crisis,
        u1.title,
        u1.engineering_question,
        *u1.core_content,
        *u1.scenario_assumptions,
        u1.student_action,
        u1.takeaway,
    ])


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    checks = gate_v10(bp, profile, source_text)

    # Override the legacy cross-domain composite test with the actual ISCARB
    # definition: one coherent central crisis. Saudi/context/readiness examples
    # later in the lecture may compare other sectors without changing the case.
    checks["one_non_composite_central_system"] = len(_domain_clusters(_opening_crisis_text(bp))) <= 1
    checks["v11_central_crisis_is_single_system"] = checks["one_non_composite_central_system"]

    # Release-consistency sentinels make the intended invariants explicit.
    checks["v11_domain_spine_maps_source"] = checks.get("unit2_maps_major_source_families", False)
    checks["v11_reserved_channels_clean"] = all(checks.get(k, False) for k in [
        "unit15_ai_in_pedagogy_channel",
        "unit19_rubric_method_in_pedagogy_channel",
        "unit20_assurance_method_in_pedagogy_channel",
    ])
    checks["v11_readiness_trace_visible"] = checks.get("unit16_names_etec_readiness_targets", False)
    checks["v11_noncore_technology_source_safe"] = all(checks.get(k, False) for k in [
        "unsupported_noncore_technical_claims_are_framed_as_exercises",
    ])
    return checks
