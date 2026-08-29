from __future__ import annotations

"""ISCARB Gate v13 — computing-wide renderer/sanity release sentinels."""

import re

from .gate_v12 import deterministic_gate as gate_v12
from .models import Blueprint, SourceProfile
from .cimt_sanity_v42 import bounded_language_ok


def _has_supporting(bp: Blueprint) -> bool:
    return any(re.search(r"\[S\d+\]", x or "", flags=re.I) for x in bp.source_manifest)


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    checks = gate_v12(bp, profile, source_text)
    checks["v13_generated_language_is_bounded"] = bounded_language_ok(bp)

    u11 = bp.units[10]
    u11_blob = " ".join([u11.title, u11.engineering_question, *u11.scenario_assumptions, *u11.enrichment_content]).lower()
    checks["v13_unsourced_saudi_context_is_explicitly_hypothetical"] = (
        _has_supporting(bp) or "hypothetical" in u11_blob or "assume" in u11_blob
    )

    u15_blob = " ".join(bp.units[14].pedagogy_content).upper()
    checks["v13_ai_human_signoff_contract_visible"] = (
        "AI MAY ASSIST" in u15_blob and "AI MUST NOT BE TRUSTED AUTONOMOUSLY" in u15_blob
    )

    subject = (profile.lecture_title if profile is not None else bp.lecture_title).lower()
    is_security = "security" in subject or "cyber" in subject
    # Cross-discipline residue is checked in the actual learner-facing Blueprint
    # fields. Renderer regression tests separately guard hard-coded labels.
    if is_security:
        checks["v13_no_cross_discipline_security_residue"] = True
    else:
        noncore = " ".join(
            [u.title, u.engineering_question, *u.pedagogy_content, u.student_action, u.takeaway]
            for u in []
        ) if False else " ".join(
            x for u in bp.units for x in [u.title, u.engineering_question, *u.pedagogy_content, u.student_action, u.takeaway]
        ).lower()
        suspicious = ["security claims · sign-off", "platform protection", "application protection", "record / asset protection"]
        checks["v13_no_cross_discipline_security_residue"] = not any(x in noncore for x in suspicious)

    return checks
