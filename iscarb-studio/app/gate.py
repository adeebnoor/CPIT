from __future__ import annotations

from .models import Blueprint
from .prompts import IDR, EER


def deterministic_gate(bp: Blueprint) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    checks["exactly_20_units"] = len(bp.units) == 20
    checks["exactly_5_clos"] = len(bp.clOs) == 5
    checks["unit_numbers_1_to_20"] = [u.number for u in bp.units] == list(range(1, 21))

    phase_ok = True
    for u in bp.units:
        expected = "IFHAM" if u.number <= 5 else "MARIS" if u.number <= 10 else "ATQAN" if u.number <= 15 else "MAYYIZ"
        phase_ok = phase_ok and u.phase == expected
    checks["phase_sequence"] = phase_ok

    clo_ids = [c.id for c in bp.clOs]
    checks["clo_ids_unique"] = sorted(clo_ids) == ["CLO1", "CLO2", "CLO3", "CLO4", "CLO5"]
    checks["all_units_have_source_anchor"] = all(bool(u.source_anchor.strip()) for u in bp.units)
    checks["all_units_have_action"] = all(bool(u.student_action.strip()) for u in bp.units)
    checks["all_units_have_question"] = all(bool(u.engineering_question.strip()) for u in bp.units)

    lenses = {lens for u in bp.units for lens in u.cimtlens}
    checks["cimt_C_present"] = "C" in lenses
    checks["cimt_I_present"] = "I" in lenses
    checks["cimt_M_present"] = "M" in lenses
    checks["cimt_T_present"] = "T" in lenses

    idr_tags = {tag for u in bp.units for tag in u.inherited_requirements}
    eer_tags = {tag for u in bp.units for tag in u.elite_requirements}
    for tag in IDR:
        checks[f"coverage_{tag}"] = tag in idr_tags
    for tag in EER:
        checks[f"coverage_{tag}"] = tag in eer_tags

    checks["unit20_assurance_language"] = any(
        k in (bp.units[19].title + " " + " ".join(bp.units[19].core_content)).lower()
        for k in ["assurance", "claim", "evidence", "uncertainty"]
    )
    checks["unit17_constraint_mutation"] = any(
        k in (bp.units[16].title + " " + bp.units[16].engineering_question + " " + " ".join(bp.units[16].core_content)).lower()
        for k in ["constraint", "change", "mutation", "redesign"]
    )
    checks["unit15_ai"] = "ai" in (bp.units[14].title + " " + " ".join(bp.units[14].core_content)).lower()
    checks["unit14_wellbeing"] = any(
        k in (bp.units[13].title + " " + " ".join(bp.units[13].core_content)).lower()
        for k in ["wellbeing", "well-being", "workload", "fatigue", "burnout", "on-call", "cognitive"]
    )
    return checks


def all_required_pass(checks: dict[str, bool]) -> bool:
    return all(checks.values())


def failed_check_names(checks: dict[str, bool]) -> list[str]:
    return [k for k, v in checks.items() if not v]
