from __future__ import annotations

"""ISCARB v7.2.1 pedagogy + AI-era dependability layer.

This layer does not widen P1's factual scope. It changes *how* the twenty fixed
ISCARB jobs are enacted in class, and adds clearly labelled contemporary
extensions only when the lecture context makes them pedagogically relevant.
"""

import re

from . import main as engine
from . import start_v440 as base

_PATCHED = False

# Intentionally conservative. Generic words such as failure/risk/model are NOT
# enough to inject an AI-era extension into an unrelated database/networking
# lecture. The extension activates for dependability/assurance-critical or
# explicitly AI/ML contexts.
_AI_CONTEXT = re.compile(
    r"\b(?:dependab\w*|reliab\w*|safety(?:-critical)?|security|assurance|formal methods?|"
    r"fault[- ]toler\w*|mission[- ]critical|safety[- ]critical|artificial intelligence|"
    r"machine learning|generative ai|\bai\b|\bllm\b|neural network|foundation model)\b",
    re.I,
)

_TPS_UNITS = {5, 8, 10, 14, 15}
_CORE_CASE_UNITS = {11, 12}
_POST_CLASS_UNITS = {16, 17, 18, 19}


def _text_blob(bp) -> str:
    parts = [
        getattr(bp, "lecture_title", ""),
        getattr(bp, "engineering_thesis", ""),
        getattr(bp, "central_engineering_crisis", ""),
        *list(getattr(bp, "source_topic_families", []) or []),
    ]
    for unit in getattr(bp, "units", []) or []:
        parts.extend([getattr(unit, "title", ""), *list(getattr(unit, "core_content", []) or [])])
    return " ".join(str(x) for x in parts if str(x).strip())


def _replace_prefixed(items, prefix: str, value: str) -> list[str]:
    out = [str(x) for x in (items or []) if not str(x).upper().startswith(prefix.upper())]
    out.append(value)
    return out


def _set_activity_budget(bp) -> None:
    for u in list(getattr(bp, "units", []) or []):
        n = int(getattr(u, "number", 0) or 0)
        if n in _TPS_UNITS:
            u.student_action = "THINK–PAIR–SHARE · 1 MIN — make one choice, compare with a partner, then state the evidence that would change it."
            if getattr(u, "planned_minutes", 0) > 0:
                u.planned_minutes = max(2, int(u.planned_minutes))
        elif n in _CORE_CASE_UNITS:
            u.student_action = "CORE IN-CLASS CASE · 5–7 MIN — analyse the case as a team, defend one decision, and identify the evidence that would reverse it."
            u.planned_minutes = max(6, int(getattr(u, "planned_minutes", 0) or 0))
        elif n in _POST_CLASS_UNITS:
            u.student_action = "POST-CLASS ARTIFACT — complete or review the evidence artifact individually after class; submit a traceable decision and reversal condition."
            if getattr(u, "planned_minutes", 0) > 2:
                u.planned_minutes = 2
        else:
            u.student_action = "CHECKPOINT — follow the reasoning; respond only if the lecturer calls for a quick check."


def _add_case_scaffold(bp) -> None:
    units = list(getattr(bp, "units", []) or [])
    if len(units) < 11:
        return
    u = units[10]
    micro = (
        "MICRO-EXAMPLE — Before the full local case, trace one small change: a platform, library, device or service update invalidates a previously safe technical assumption. "
        "Check the affected requirement, independent evidence, decision, and reversal condition."
    )
    u.pedagogy_content = _replace_prefixed(u.pedagogy_content, "MICRO-EXAMPLE", micro)
    u.pedagogy_content = _replace_prefixed(
        u.pedagogy_content,
        "TRANSFER STEP",
        "TRANSFER STEP — Apply the same sequence to the full case: observed change → affected requirement → independent evidence → decision → reversal condition.",
    )


def _add_decision_boxes(bp) -> None:
    for u in list(getattr(bp, "units", []) or [])[5:15]:
        u.pedagogy_content = _replace_prefixed(
            u.pedagogy_content,
            "DECISION BOX",
            "DECISION BOX — What engineering decision does this source rule support, and what evidence would make you change that decision?",
        )


def _add_peer_review_card(bp) -> None:
    units = list(getattr(bp, "units", []) or [])
    if len(units) < 19:
        return
    u = units[18]
    u.pedagogy_content = _replace_prefixed(
        u.pedagogy_content,
        "PEER-REVIEW CARD",
        "PEER-REVIEW CARD — (1) Can another person independently inspect the evidence? (2) What variable or edge case would invalidate the claim?",
    )
    u.student_action = "POST-CLASS ARTIFACT — use the full 6×4 rubric after class; in class use only the two-question peer-review card."


def _add_ai_era_dependability(bp) -> None:
    if not _AI_CONTEXT.search(_text_blob(bp)):
        return
    units = list(getattr(bp, "units", []) or [])
    if len(units) < 15:
        return

    u12 = units[11]
    ai_accountability = (
        "AI-ERA ASSURANCE — AI may prepare code, tests, summaries or evidence, but assurance ownership remains human. "
        "Sign-off requires independently inspectable evidence, explicit edge cases, and a named reversal condition."
    )
    if ai_accountability not in u12.enrichment_content:
        u12.enrichment_content.append(ai_accountability)
        u12.enrichment_basis.append("ISCARB contemporary extension — not asserted as P1 content")
    u12.contextual_enrichment = True

    u13 = units[12]
    contemporary = [
        "AI-ERA SYSTEM BEHAVIOR — deterministic software assumptions are insufficient for probabilistic model components; test distributions and failure envelopes, not only nominal inputs.",
        "AI-ERA FAILURE MODES — include hallucination, data bias, distribution shift, prompt/context sensitivity and silent model/version change in the assurance argument when an AI component is present.",
        "AI-GENERATED CODE — treat generated code as untrusted implementation until static analysis, tests, review and—where justified—formal verification establish the required property.",
    ]
    for item in contemporary:
        if item not in u13.enrichment_content:
            u13.enrichment_content.append(item)
            u13.enrichment_basis.append("ISCARB contemporary extension — not asserted as P1 content")
    u13.contextual_enrichment = True

    u15 = units[14]
    u15.pedagogy_content = _replace_prefixed(
        u15.pedagogy_content,
        "AI ASSURANCE LENS",
        "AI ASSURANCE LENS — Separate model performance from system assurance: robustness, distribution shift, guardrails, auditability, provenance and human sign-off must each have evidence.",
    )
    u15.pedagogy_content = _replace_prefixed(
        u15.pedagogy_content,
        "BLACK-BOX TEST",
        "BLACK-BOX TEST — If a model decision cannot be explained directly, what observable evidence would still make the behavior auditable to an independent reviewer or regulator?",
    )


def _clean_visual_metadata(bp) -> None:
    for u in list(getattr(bp, "units", []) or []):
        plan = getattr(u, "visual_plan", None)
        if plan is None:
            continue
        role = str(getattr(plan, "visual_evidence_role", "") or "")
        if "faculty review required before release" in role.lower():
            plan.visual_evidence_role = "Draft visualization; inspect source alignment before any verified release."


def _enhance(bp):
    if not getattr(bp, "units", None) or len(bp.units) != 20:
        return bp
    _set_activity_budget(bp)
    _add_case_scaffold(bp)
    _add_decision_boxes(bp)
    _add_peer_review_card(bp)
    _add_ai_era_dependability(bp)
    _clean_visual_metadata(bp)
    return bp


def apply_v721_pedagogy_ai_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    previous_timebox = engine.apply_90_minute_timebox
    def timebox_v721(blueprint, profile, bundle):
        return _enhance(previous_timebox(blueprint, profile, bundle))
    engine.apply_90_minute_timebox = timebox_v721
    base.engine.apply_90_minute_timebox = timebox_v721

    previous_draft = engine._source_preserving_draft
    def draft_v721(profile, bundle):
        return _enhance(previous_draft(profile, bundle))
    engine._source_preserving_draft = draft_v721
    base.engine._source_preserving_draft = draft_v721

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        # Retired implementation/history fields do not belong in the production
        # faculty contract. Keep history in git, not in the live product surface.
        for key in (
            "cimt_reference_archive", "ready_example_source", "source_library_verified",
            "verified_source_count", "public_experience", "design_language",
            "fixed_task_footer", "hero_live_release", "faculty_experience",
        ):
            data.pop(key, None)
        data.update({
            "version": "7.2.1",
            "release_ui": "7.2.1",
            "pipeline": "iscarb-v7.2.1-clean-it-wide-cognitive-budget-ai-era",
            "cognitive_budget": "5 one-minute Think-Pair-Share + 2 core in-class cases + post-class artifact build/review",
            "learner_action_labels": ["CHECKPOINT", "THINK-PAIR-SHARE", "CORE IN-CLASS CASE", "POST-CLASS ARTIFACT"],
            "micro_example_before_context_case": True,
            "source_expansion_decision_box": True,
            "peer_review_quick_card": "2 questions",
            "ai_era_dependability": True,
            "ai_extension_provenance": "enrichment-only unless supported by P1",
            "approved_hero_asset": "hero_user_original.png",
            "approved_hero_web_derivative": "hero_user_web.jpg",
            "public_web_image_fallback": False,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
