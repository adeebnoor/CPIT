from __future__ import annotations

"""ISCARB Gate v14 — v13 plus reserved-pedagogy/provenance sentinels.

Gate v14 is intentionally source-agnostic: it does not invent Chapter-specific
facts.  It prevents ISCARB scaffolds from being mislabeled as P1 technical core
and keeps cross-discipline residue out of learner-facing content.
"""

import re

from .gate_v13 import deterministic_gate as gate_v13
from .models import Blueprint, SourceProfile


_RESERVED_SCAFFOLD_TERMS = (
    "counter-evidence",
    "residual uncertainty",
    "ai may assist",
    "human sign-off",
    "hypothetical saudi",
    "capability rubric",
)

_FRAMEWORK_FIRST_TITLE_TERMS = (
    "saudi context:",
    "trend & future:",
    "trend and future:",
    "practitioner wellbeing:",
    "practitioner well-being:",
    "critical ai literacy",
    "iscarb capability rubric",
    "bounded assurance case",
)


def _unsourced_numeric_precision(bp: Blueprint, source_text: str) -> list[str]:
    """Return learner-authored numeric claims that are not traceable to source text.

    Years and unit/page numbers are ignored; the dangerous failure mode here is invented
    percentages/thresholds/multipliers presented as engineering facts.
    """
    source = (source_text or "").lower()
    authored = []
    for u in bp.units:
        blob = " ".join([u.engineering_question, *u.pedagogy_content, *u.enrichment_content, *u.scenario_assumptions, u.student_action, u.takeaway])
        for token in re.findall(r"(?<!\w)(\d+(?:\.\d+)?)\s*(%|percent|x\b)", blob, flags=re.I):
            value, suffix = token
            forms = {f"{value}%", f"{value} %", f"{value} percent", f"{value}x"}
            if not any(form.lower() in source for form in forms):
                authored.append(f"{value}{suffix}")
    return authored


def _core_blob(bp: Blueprint, unit_numbers: tuple[int, ...]) -> str:
    return " ".join(
        x
        for n in unit_numbers
        for x in bp.units[n - 1].core_content
    ).lower()


def _learner_blob(bp: Blueprint) -> str:
    return " ".join(
        x
        for u in bp.units
        for x in [
            u.title,
            u.engineering_question,
            *u.pedagogy_content,
            *u.enrichment_content,
            *u.scenario_assumptions,
            u.student_action,
            u.takeaway,
        ]
    ).lower()


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    checks = gate_v13(bp, profile, source_text)

    # ISCARB-only argumentation/AI/context scaffolds belong in pedagogy or
    # enrichment, not in P1 technical core.  This catches provenance drift
    # without assuming what a particular source chapter teaches.
    reserved_core = _core_blob(bp, (11, 14, 15, 18, 19, 20))
    checks["v14_reserved_iscarb_scaffolds_not_mislabeled_as_p1_core"] = not any(
        term in reserved_core for term in _RESERVED_SCAFFOLD_TERMS
    )

    subject = (profile.lecture_title if profile is not None else bp.lecture_title).lower()
    learner = _learner_blob(bp)
    is_security = "security" in subject or "cyber" in subject
    if is_security:
        checks["v14_no_legacy_security_template_residue"] = True
    else:
        legacy = (
            "security engineering family",
            "security engineering taxonomy",
            "platform protection",
            "application protection",
            "record / asset protection",
        )
        checks["v14_no_legacy_security_template_residue"] = not any(x in learner for x in legacy)

    # Learner-facing titles should teach the source topic, not expose internal ISCARB
    # scaffold labels as the dominant classroom headline.
    titles = [u.title.strip().lower() for u in bp.units]
    checks["v14_source_first_learner_titles"] = not any(
        any(term in title for term in _FRAMEWORK_FIRST_TITLE_TERMS) for title in titles
    )

    # Synthetic activities may use qualitative assumptions, but invented quantitative
    # thresholds must never look like source facts.
    checks["v14_no_unsourced_numeric_precision"] = not _unsourced_numeric_precision(bp, source_text)

    checks["v14_exactly_20_presenter_jobs"] = len(bp.units) == 20
    checks["v14_exactly_90_live_minutes"] = sum(u.planned_minutes for u in bp.units) == 90

    # Renderer text is generated later, but the Blueprint itself should never
    # rely on hard truncation artifacts as authored content.
    authored = " ".join(
        x
        for u in bp.units
        for x in [u.title, u.engineering_question, u.student_action, u.takeaway]
    )
    checks["v14_no_authored_hard_truncation_tokens"] = "..." not in authored and "…" not in authored

    return checks
