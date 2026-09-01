from __future__ import annotations

"""ISCARB Gate v15 - learner-visible 20-unit grammar and detail retention.

Gate v14 proved that a Blueprint had twenty records and broad coverage.  It did
not prove that each record performed the cognitive job advertised on the public
site, nor that the technical span retained enough source detail to teach.  Gate
v15 makes those promises executable release conditions.
"""

import re

from .gate_v14 import deterministic_gate as gate_v14
from .models import Blueprint, LectureUnit, SourceProfile


EXPECTED_PHASES = ["IFHAM"] * 5 + ["MARIS"] * 5 + ["ATQAN"] * 5 + ["MAYYIZ"] * 5
HSTACK_LABELS = (
    "analytical reasoning",
    "engineering judgment",
    "evidence-based reasoning",
    "socio-technical thinking",
    "risk-aware design",
    "ethical responsibility",
)


def _blob(unit: LectureUnit, *, include_core: bool = True) -> str:
    values = [
        unit.title,
        unit.engineering_question,
        *(unit.core_content if include_core else []),
        *unit.pedagogy_content,
        *unit.scenario_assumptions,
        unit.student_action,
        unit.takeaway,
        unit.evidence,
    ]
    return " ".join(str(x or "") for x in values).lower()


def _contains(blob: str, *families: tuple[str, ...] | str) -> bool:
    """Each argument is one required synonym family."""
    for family in families:
        terms = (family,) if isinstance(family, str) else family
        if not any(term.lower() in blob for term in terms):
            return False
    return True


def _unit3_contract(unit: LectureUnit) -> bool:
    pedagogy = " ".join(unit.pedagogy_content).upper()
    return not unit.core_content and len(unit.pedagogy_content) == 5 and all(f"CLO{i}" in pedagogy for i in range(1, 6))


def _unit4_contract(unit: LectureUnit) -> bool:
    pedagogy = " ".join(unit.pedagogy_content).lower()
    return not unit.core_content and all(label in pedagogy for label in HSTACK_LABELS) and len(unit.pedagogy_content) == 6


def _unit5_contract(unit: LectureUnit) -> bool:
    return all(
        _substantive_segment(unit.pedagogy_content, label)
        for label in ("predict", "constrain(?:t)?", "derive", "name"))


def _substantive_segment(values, label: str) -> bool:
    """A heading alone is not performance of a cognitive job."""
    pattern = re.compile(rf"^\s*(?:{label})\s*[:—–-]\s*(.+)", re.I)
    return any(match and len(match.group(1).split()) >= 4
               for value in values for match in [pattern.match(str(value))])


def _teaching_contract(unit: LectureUnit) -> bool:
    blob = _blob(unit)
    source_backed = "p1" in (unit.source_anchor or "").lower()
    has_source = bool(unit.core_content) and source_backed
    if unit.number == 6:
        return has_source and len(unit.core_content) + len(unit.pedagogy_content) >= 3
    if unit.number == 7:
        return has_source and bool(unit.student_action.strip())
    if unit.number == 8:
        return has_source and all(_substantive_segment([*unit.core_content,*unit.pedagogy_content], label)
                                  for label in ("(?:alternative|option) A", "(?:alternative|option) B", "trade-off|tradeoff"))
    if unit.number == 9:
        return has_source and all(_substantive_segment([*unit.core_content,*unit.pedagogy_content], label)
                                  for label in ("measure|metric", "falsifier|falsification"))
    if unit.number == 10:
        # The review is pedagogical, not a new primary-source factual claim.
        return all(_substantive_segment(unit.pedagogy_content, label)
                                  for label in ("known", "unknown", "decision-sensitive(?: unknown)?", "(?:what we )?monitor"))
    if unit.number == 11:
        return has_source and _contains(blob, ("apply", "application", "concrete"), ("saudi", "gulf"), ("constraint", "condition", "context"))
    if unit.number == 12:
        return has_source and _contains(blob, ("responsib", "owner", "sign-off", "accountab"))
    if unit.number == 13:
        return has_source and _contains(blob, ("change", "future", "scale", "improv", "evol"))
    if unit.number == 14:
        return has_source and _contains(blob, ("operat", "consequence", "practitioner", "workload", "burden", "misunderstood"))
    if unit.number == 15:
        return has_source and _contains(blob, "ai may assist", "ai must not be trusted autonomously", "sign-off")
    return True


def _bookend_contract(unit: LectureUnit, bp: Blueprint) -> bool:
    blob = _blob(unit)
    if unit.number == 1:
        # The presenter draws these two locked-plan fields on slide 1. They
        # need not be duplicated in the unit just to satisfy a keyword check.
        visible = " ".join([blob, bp.central_engineering_crisis, bp.named_ethical_purpose]).lower()
        return bool(bp.central_engineering_crisis.strip()) and _contains(visible, ("evidence", "unknown", "missing"), ("decision", "decide"))
    if unit.number == 2:
        return len(unit.core_content) >= 2 and "p1" in (unit.source_anchor or "").lower()
    if unit.number == 16:
        return bool(unit.evidence.strip()) and _contains(blob, ("artifact", "design"), "trade", "evidence")
    if unit.number == 17:
        return bool(unit.evidence.strip()) and _contains(blob, "constraint", "peer", ("redesign", "revised", "rerun"))
    if unit.number == 18:
        return _contains(blob, "claim", "evidence", "warrant", "counter-evidence", "residual uncertainty")
    if unit.number == 19:
        return len(bp.rubric_criteria) == 6 and all(
            len(str(level).split()) >= 2 for row in bp.rubric_criteria
            for level in (row.distinguished,row.ready,row.developing,row.not_yet_ready))
    if unit.number == 20:
        return _contains(blob, "approve", "conditionally approve", "redesign", "reject", "residual uncertainty")
    return True


def _source_detail_retained(bp: Blueprint, profile: SourceProfile | None) -> bool:
    major = [x for x in (profile.coverage_items if profile else []) if x.importance == "major"]
    if len(major) < 6:
        return True
    for unit in bp.units[5:15]:
        if unit.number == 10 and not unit.core_content:
            continue
        words = sum(len(str(x).split()) for x in unit.core_content)
        if words < 12:
            return False
        if not unit.core_content or "p1" not in (unit.source_anchor or "").lower():
            return False
    return True


def _no_fragment_endings(bp: Blueprint) -> bool:
    dangling = re.compile(r"\b(of|for|to|the|a|an|and|or|in|on|at|by|with|from|that|is|are)$", re.I)
    for unit in bp.units:
        for text in [unit.title, unit.engineering_question, *unit.core_content, unit.student_action, unit.takeaway]:
            clean = str(text or "").strip().rstrip("?.!;:")
            if clean and dangling.search(clean):
                return False
    return True


def unit_role_checks(bp: Blueprint, numbers=None) -> dict[str, bool]:
    selected = set(numbers if numbers is not None else range(1, 21))
    checks = {}
    for unit in bp.units:
        if unit.number not in selected:
            continue
        if unit.number == 3:
            checks["v15_unit03_five_clos_only"] = _unit3_contract(unit)
        elif unit.number == 4:
            checks["v15_unit04_hstack_is_exact"] = _unit4_contract(unit)
        elif unit.number == 5:
            checks["v15_unit05_predict_constraint_derive_name"] = _unit5_contract(unit)
        elif 6 <= unit.number <= 15:
            checks[f"v15_unit{unit.number:02d}_job_is_visible"] = _teaching_contract(unit)
        else:
            checks[f"v15_unit{unit.number:02d}_job_is_visible"] = _bookend_contract(unit, bp)
    return checks


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    checks = gate_v14(bp, profile, source_text)
    if bp.generation_mode.startswith("batched"):
        from .batched_generation import evidence_checks
        checks["batch_all_units_generated"] = bp.generation_mode == "batched"
        checks["batch_source_profile_available"] = profile is not None
        if profile is not None:
            checks.update(evidence_checks(bp, profile))
    checks["v15_unit_numbers_are_exact"] = [u.number for u in bp.units] == list(range(1, 21))
    if len(bp.units) != 20:
        checks["v15_complete_20_unit_grammar"] = False
        return checks
    checks["v15_phase_sequence_is_exact"] = [u.phase for u in bp.units] == EXPECTED_PHASES
    checks.update(unit_role_checks(bp))

    role_checks = [value for key, value in checks.items() if key.startswith("v15_unit")]
    checks["v15_complete_20_unit_grammar"] = all(role_checks)
    checks["v15_technical_units_retain_source_detail"] = _source_detail_retained(bp, profile)
    checks["v15_no_source_fragment_ends_mid_thought"] = _no_fragment_endings(bp)
    from .presenter_v44 import readability_problems
    readability = readability_problems(bp)
    checks["v15_presenter_fits_readable_canvas"] = not readability
    # A global fit failure alone previously sent repair down the metadata path.
    # Localize the affected units without relaxing any font/fit threshold.
    for unit in bp.units:
        checks[f"presenter_unit{unit.number:02d}_readable"] = unit.number not in readability
    return checks
