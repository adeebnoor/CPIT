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



def _meaningful_tokens(text: str) -> set[str]:
    stop = {"the","and","for","with","from","that","this","into","using","what","how","why","system","software","engineering","source","primary"}
    return {t for t in re.findall(r"[a-z0-9]+", str(text or "").lower()) if len(t) >= 4 and t not in stop}


def _major_items_are_actually_taught(bp: Blueprint, profile: SourceProfile | None) -> bool:
    if profile is None:
        return True
    major = [x for x in profile.coverage_items if x.importance == "major"]
    if not major:
        return False
    ledger = {x.coverage_id: x for x in bp.coverage_ledger}
    for item in major:
        row = ledger.get(item.id)
        if row is None or not (1 <= row.first_taught_unit <= 15):
            return False
        unit = bp.units[row.first_taught_unit - 1]
        visible = " ".join([unit.title, *unit.core_content, unit.takeaway])
        source_tokens = _meaningful_tokens(item.label + " " + item.why_important)
        visible_tokens = _meaningful_tokens(visible)
        # At least two meaningful source tokens (or all tokens for a very short label)
        # must be learner-visible; a ledger-only row is not chapter coverage.
        needed = 1 if len(source_tokens) <= 2 else 2
        if len(source_tokens & visible_tokens) < needed:
            return False
    return True


def _readiness_has_real_evidence_units(bp: Blueprint) -> bool:
    if not bp.readiness_alignment:
        return False
    for alignment in bp.readiness_alignment:
        if not alignment.evidence_units:
            return False
        for n in alignment.evidence_units:
            if not 1 <= n <= len(bp.units):
                return False
            u = bp.units[n - 1]
            if not str(u.evidence or "").strip() or not str(u.student_action or "").strip():
                return False
    return True


# A slide carrying one sentence in a large box is not a taught minute, whether or
# not a source image sits beside it. A source visual raises the floor it must
# clear; it never removes the floor.
MIN_TEACHING_WORDS_WITH_SOURCE_VISUAL = 24
MIN_TEACHING_WORDS_WITHOUT_VISUAL = 35
# Two boxes holding one sentence each is what a reviewer calls an empty slide.
MIN_TEACHING_ITEMS = 3

# A 90-minute lecture needs material to teach. Measured across eleven real
# uploads, every genuine chapter gave the ten teaching units at least four
# distinct source checkpoints; a two-page course-syllabus header gave one and
# still produced a full twenty-unit deck built from that single page. Three is
# the floor, one below the thinnest real lecture seen.
MIN_DISTINCT_TEACHING_ANCHORS = 3


def _teaching_payload_words(u) -> int:
    """Words a learner actually reads: source content plus its scaffolding."""
    return sum(len(str(x).split()) for x in (*u.core_content, *u.pedagogy_content))


def _visible_item_count(u) -> int:
    """Distinct blocks the slide will draw.

    Word count alone does not measure a slide: one long sentence clears any word
    floor and still renders as a single oversized box. What a learner sees is the
    number of separate points, so that is counted separately.
    """
    return len([x for x in (*u.core_content, *u.pedagogy_content) if str(x).strip()])


def _technical_density_ok(bp: Blueprint, profile: SourceProfile | None) -> bool:
    major_count = len([x for x in (profile.coverage_items if profile else []) if x.importance == "major"])
    if major_count < 6:
        return True
    for u in bp.units[5:15]:
        words = _teaching_payload_words(u)
        source_visual = bool(u.visual_plan and u.visual_plan.source_visual_available)
        floor = MIN_TEACHING_WORDS_WITH_SOURCE_VISUAL if source_visual else MIN_TEACHING_WORDS_WITHOUT_VISUAL
        if words < floor:
            return False
        # A source figure carries its own structure, so the text beside it may be
        # briefer; without one the slide must stand on its points alone.
        if not source_visual and _visible_item_count(u) < MIN_TEACHING_ITEMS:
            return False
    return True


def _source_supports_ten_teaching_units(bp) -> bool:
    """Does the source carry enough distinct material for the teaching units?

    Without this, a source too thin to teach still produced twenty units: the
    same checkpoint recycled under ten headings, reported only as a scatter of
    generic coverage-rubric misses that no reader can trace back to the real
    cause. The failure now has a name faculty can act on.
    """
    anchors = {
        str(u.source_anchor or "").strip()
        for u in bp.units[5:15]
        if str(u.source_anchor or "").strip()
    }
    return len(anchors) >= MIN_DISTINCT_TEACHING_ANCHORS


def _presenter_density_ok(bp: Blueprint) -> bool:
    """No unit in the deck may be a near-empty slide.

    _technical_density_ok guards the source-teaching span. This guards the whole
    deck: the synthesis and assessment units carry pedagogy rather than source
    content, and a learner staring at two boxes with one sentence each has been
    given a blank minute regardless of which phase the unit sits in.
    """
    for u in bp.units:
        floor = 24 if u.number != 19 else 20
        if _teaching_payload_words(u) < floor:
            return False
        visible_items = len([x for x in (*u.core_content, *u.pedagogy_content) if str(x).strip()])
        if u.number != 19 and visible_items < 3:
            return False
        if not str(u.student_action or "").strip() or not str(u.takeaway or "").strip():
            return False
    return True

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

    # Chapter completeness is stronger than metadata completeness: each major
    # profile checkpoint must be visible in the Unit that claims to teach it.
    checks["v14_major_chapter_items_are_actually_taught"] = _major_items_are_actually_taught(bp, profile)
    checks["v14_technical_units_have_teaching_density"] = _technical_density_ok(bp, profile)
    checks["v14_no_unit_is_a_near_empty_slide"] = _presenter_density_ok(bp)
    checks["v14_source_supports_ten_teaching_units"] = _source_supports_ten_teaching_units(bp)

    # Replace the historical Unit-16 readiness badge requirement with an
    # evidence-trail requirement.  Readiness may appear wherever the artifact is
    # actually produced, and Unit 19 can index it later.
    readiness_evidence = _readiness_has_real_evidence_units(bp)
    checks["v14_readiness_is_evidence_backed"] = readiness_evidence
    checks["unit16_names_etec_readiness_targets"] = readiness_evidence
    checks["v11_readiness_trace_visible"] = readiness_evidence

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
