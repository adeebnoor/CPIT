from __future__ import annotations

"""ISCARB v4.2 post-generation sanity layer.

This layer never rewrites P1 core_content.  It only bounds model-generated
instructional language, makes unsupported Saudi context explicitly hypothetical,
and keeps the reserved AI-literacy contract visible.  Its purpose is to stop a
sound source-grounded lecture from being weakened by absolute or cross-domain
wording introduced during instructional transformation.
"""

import re

from .models import Blueprint, SourceProfile

HYP_BASIS = "HYPOTHETICAL — no external factual claim; design exploration only."


def _bounded(text: str) -> str:
    if not text:
        return text
    replacements = [
        (r"\bmathematically\s+eliminate(?:s|d|ing)?\s+errors?\b", "use mathematical specification and analysis to expose and reduce error risk"),
        (r"\beliminate(?:s|d|ing)?\s+(?:all\s+)?errors?\b", "identify and reduce errors"),
        (r"\bprevent(?:s|ed|ing)?\s+common[- ]mode\s+failures?\b", "reduce exposure to common-mode failures"),
        (r"\bguarantee(?:s|d|ing)?\b", "support"),
        (r"\bensure(?:s|d|ing)?\s+zero\s+risk\b", "reduce risk within stated bounds"),
        (r"\bensure(?:s|d|ing)?\s+that\s+no\s+failure\s+can\s+occur\b", "reduce the likelihood of failure within stated assumptions"),
        (r"\bfully\s+prevent(?:s|ed|ing)?\b", "reduce"),
        (r"\bprove\s+secure\b", "support a bounded security claim"),
        (r"\bimpossible\s+to\s+(?:fail|breach)\b", "designed to resist failure within stated assumptions"),
    ]
    out = text
    for pattern, replacement in replacements:
        out = re.sub(pattern, replacement, out, flags=re.I)
    return re.sub(r"\s+", " ", out).strip()


def _supporting_source_present(bp: Blueprint) -> bool:
    return any(re.search(r"\[S\d+\]", line or "", flags=re.I) for line in bp.source_manifest)


def _make_unit11_hypothetical(bp: Blueprint) -> None:
    if _supporting_source_present(bp):
        return
    u = bp.units[10]
    blob = " ".join([u.title, u.engineering_question, *u.enrichment_content, *u.scenario_assumptions]).lower()
    if "hypothetical" not in blob and "assume" not in blob:
        u.engineering_question = "In a hypothetical Saudi operating scenario, " + u.engineering_question[:1].lower() + u.engineering_question[1:]
    if not u.scenario_assumptions:
        u.scenario_assumptions = ["HYPOTHETICAL SAUDI SCENARIO — apply only source-taught mechanisms; no national mandate or technical capability is asserted as fact."]
    elif not any("hypothetical" in x.lower() or "assume" in x.lower() for x in u.scenario_assumptions):
        u.scenario_assumptions[0] = "HYPOTHETICAL SAUDI SCENARIO — " + u.scenario_assumptions[0]
    if u.enrichment_content and HYP_BASIS not in u.enrichment_basis:
        u.enrichment_basis = [HYP_BASIS]
        u.contextual_enrichment = True


def _fix_ai_contract(bp: Blueprint) -> None:
    u = bp.units[14]
    blob = " ".join(u.pedagogy_content).upper()
    if "AI MAY ASSIST" not in blob:
        u.pedagogy_content.append("AI MAY ASSIST — draft, compare, or propose checks; every technical statement must still be traced to P1 or learner evidence.")
    blob = " ".join(u.pedagogy_content).upper()
    if "AI MUST NOT BE TRUSTED AUTONOMOUSLY" not in blob:
        u.pedagogy_content.append("AI MUST NOT BE TRUSTED AUTONOMOUSLY — a human engineer owns source checking, testing, failure search, and final sign-off.")
    u.pedagogy_content = u.pedagogy_content[:8]


def normalize_cimt_sanity_v42(
    bp: Blueprint,
    source_text: str = "",
    profile: SourceProfile | None = None,
) -> Blueprint:
    # Never touch source-locked core_content.
    for clo in bp.clOs:
        clo.statement = _bounded(clo.statement)
        clo.evidence_expected = _bounded(clo.evidence_expected)

    bp.engineering_thesis = _bounded(bp.engineering_thesis)
    bp.central_engineering_crisis = _bounded(bp.central_engineering_crisis)
    bp.named_ethical_purpose = _bounded(bp.named_ethical_purpose)

    for u in bp.units:
        u.title = _bounded(u.title)
        u.engineering_question = _bounded(u.engineering_question)
        u.pedagogy_content = [_bounded(x) for x in u.pedagogy_content]
        u.enrichment_content = [_bounded(x) for x in u.enrichment_content]
        u.scenario_assumptions = [_bounded(x) for x in u.scenario_assumptions]
        u.student_action = _bounded(u.student_action)
        u.takeaway = _bounded(u.takeaway)
        u.evidence = _bounded(u.evidence)
        if u.visual_plan is not None:
            u.visual_plan.teaching_purpose = _bounded(u.visual_plan.teaching_purpose)
            u.visual_plan.annotation_plan = [_bounded(x) for x in u.visual_plan.annotation_plan]

    for criterion in bp.rubric_criteria:
        criterion.criterion = _bounded(criterion.criterion)
        criterion.distinguished = _bounded(criterion.distinguished)
        criterion.ready = _bounded(criterion.ready)
        criterion.developing = _bounded(criterion.developing)
        criterion.not_yet_ready = _bounded(criterion.not_yet_ready)

    _make_unit11_hypothetical(bp)
    _fix_ai_contract(bp)

    note = "v4.2 computing sanity applied: source core preserved; generated absolutism bounded; unsupported Saudi context made explicitly hypothetical; AI human-sign-off contract restored."
    if note not in bp.release_notes:
        bp.release_notes.append(note)
    return bp


def bounded_language_ok(bp: Blueprint) -> bool:
    generated = [bp.engineering_thesis, bp.central_engineering_crisis, bp.named_ethical_purpose]
    generated.extend(x.statement for x in bp.clOs)
    generated.extend(x.evidence_expected for x in bp.clOs)
    for u in bp.units:
        generated.extend([u.title, u.engineering_question, *u.pedagogy_content, *u.enrichment_content, *u.scenario_assumptions, u.student_action, u.takeaway, u.evidence])
    blob = " ".join(generated).lower()
    forbidden = [
        "mathematically eliminate errors", "eliminate all errors", "eliminate errors",
        "prevent common-mode failures", "prevent common mode failures", "ensure zero risk",
        "fully prevent", "prove secure", "impossible to breach", "impossible to fail",
    ]
    return not any(x in blob for x in forbidden)
