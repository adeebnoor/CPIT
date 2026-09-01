"""Small, atomic generation transactions; ledger claims require visible evidence.

Schema validation is not semantic assurance. The existing independent audit and
release gates still run after assembly and after targeted repairs.
"""
from __future__ import annotations

import json
import re

from .models import Blueprint, BlueprintPlan, UnitBatch
from .prompts import MASTER_PROMPT
from .quality_rules import QUALITY_ADDENDUM
from .readiness import READINESS_CONTEXT
from .readiness_map import READINESS_KLO_MAP_CONTEXT

BATCH_SIZE = 4
PHASES = ["IFHAM"] * 5 + ["MARIS"] * 5 + ["ATQAN"] * 5 + ["MAYYIZ"] * 5


class GenerationContractError(ValueError):
    """A generated candidate failed quality validation, not an application crash."""


def same_source_anchor(left, right):
    """Compare source coordinates, not the spelling of PAGE versus SLIDE."""
    from .source_visuals import anchor_slides
    left_ids = set(re.findall(r"\b(?:P1|S[1-9]\d*)\b", left.upper()))
    right_ids = set(re.findall(r"\b(?:P1|S[1-9]\d*)\b", right.upper()))
    left_pages, right_pages = set(anchor_slides(left)), set(anchor_slides(right))
    if left_ids and right_ids and left_pages and right_pages:
        return left_ids == right_ids and left_pages == right_pages
    return " ".join(left.split()).casefold() == " ".join(right.split()).casefold()


def evidence_checks(bp, profile):
    """Conservative structural evidence, NOT a claim of semantic equivalence."""
    checks = {}
    units = {u.number: u for u in bp.units}
    rows = {r.coverage_id: r for r in bp.coverage_ledger}
    checks["batch_coverage_ids_unique"] = len(rows) == len(bp.coverage_ledger)
    for item in profile.coverage_items:
        if item.importance != "major":
            continue
        row = rows.get(item.id)
        unit = units.get(row.first_taught_unit) if row else None
        valid = bool(unit and unit.number <= 15 and same_source_anchor(row.source_anchor, item.source_anchor))
        if valid:
            visible = " ".join(" ".join(unit.core_content).split()).casefold()
            valid = any(
                ev.coverage_id == item.id and same_source_anchor(ev.source_anchor, item.source_anchor)
                and len(ev.visible_excerpt.split()) >= 4
                and " ".join(ev.visible_excerpt.split()).casefold() in visible
                for ev in unit.coverage_evidence
            )
        checks[f"batch_source_{item.id}_visible_in_unit{row.first_taught_unit:02d}" if row else f"batch_source_{item.id}_assigned"] = bool(valid)
    return checks


def validate_plan(plan, profile):
    rows = {r.coverage_id: r for r in plan.coverage_ledger}
    if len(rows) != len(plan.coverage_ledger):
        raise ValueError("Duplicate coverage IDs in lecture plan")
    for item in profile.coverage_items:
        if item.importance == "major":
            row = rows.get(item.id)
            if not row or row.first_taught_unit > 15 or not same_source_anchor(row.source_anchor, item.source_anchor):
                raise ValueError(f"Missing or displaced mandatory source coverage: {item.id}")


def validate_batch(batch, numbers):
    actual = [u.number for u in batch.units]
    if sorted(actual) != sorted(numbers):
        raise ValueError(f"Expected units {numbers}, received {actual}; batch not committed")
    if any(u.phase != PHASES[u.number - 1] for u in batch.units):
        raise ValueError("Unit phase does not match the fixed 20-unit grammar")


def context():
    return "\nREADINESS AUTHORITY:\n" + READINESS_CONTEXT + "\nOFFICIAL MAP:\n" + READINESS_KLO_MAP_CONTEXT


def request_validated(service, bundle, schema, prompt, extra, validate):
    # One bounded local-contract repair, scoped to this plan/batch only.
    for attempt in range(2):
        result = service._generate_structured(bundle=bundle, prompt=prompt,
            schema=schema, extra_text=extra, preferred_model=service.model, thinking_level="low")
        try:
            validate(result)
            return result
        except ValueError as exc:
            if attempt:
                raise GenerationContractError(str(exc)) from exc
            extra += "\nLOCAL CONTRACT FAILURE: " + str(exc) + "\nCorrect this output only.\n" + result.model_dump_json(by_alias=True)


def generate(service, bundle, profile):
    plan = request_validated(service, bundle, BlueprintPlan,
        MASTER_PROMPT + QUALITY_ADDENDUM + "\nSTAGE: PLAN ONLY. Return metadata, five CLOs, rubric and complete source allocation, NOT units. Copy every major coverage ID and source_anchor exactly. Allocate its first teaching to units 1–15.",
        profile.model_dump_json() + context(), lambda p: validate_plan(p, profile))
    # Unfinished slots remain explicitly review-only source drafts, never empty.
    from .deterministic_blueprint_fallback import build_deterministic_blueprint
    draft = build_deterministic_blueprint(profile)
    working = Blueprint(**plan.model_dump(), units=draft.units, generation_mode="batched-partial")
    completed = []
    for start in range(1, 21, BATCH_SIZE):
        numbers = list(range(start, min(21, start + BATCH_SIZE)))
        assigned = [r.model_dump() for r in plan.coverage_ledger if r.first_taught_unit in numbers]
        extra = ("\nLOCKED PLAN:\n" + plan.model_dump_json(by_alias=True)
            + "\nGENERATE ONLY UNIT NUMBERS: " + json.dumps(numbers)
            + "\nMANDATORY SOURCE ITEMS FOR THESE UNITS:\n" + json.dumps(assigned)
            + "\nALREADY COMPLETED OUTLINE:\n" + json.dumps(completed))
        def validate_candidate(batch):
            validate_batch(batch, numbers)
            replacements = {u.number: u for u in batch.units}
            candidate = working.model_copy(update={"units": [replacements.get(u.number, u) for u in working.units]})
            ids = {row["coverage_id"] for row in assigned}
            scoped_profile = profile.model_copy(update={"coverage_items": [x for x in profile.coverage_items if x.id in ids]})
            failed = [k for k, ok in evidence_checks(candidate, scoped_profile).items() if not ok]
            if failed:
                raise ValueError("Missing learner-visible source evidence: " + ", ".join(failed))
        batch = request_validated(service, bundle, UnitBatch,
            MASTER_PROMPT + QUALITY_ADDENDUM + "\nBATCH OUTPUT: only the requested units. Each assigned coverage item needs coverage_evidence with its exact ID/anchor and an exact visible_excerpt of AT LEAST FOUR WORDS and 20 characters copied from this unit's core_content. Teach the actual mechanism/example, not just its title. Evidence in notes or a ledger does not count. Preserve complete source figures in visual_plan where relevant. Never put a newly invented scenario detail in core_content: keep source statements general and put hypothetical applications in scenario_assumptions/pedagogy_content with explicit HYPOTHETICAL labeling.",
            extra, validate_candidate)
        replacement = {u.number: u for u in batch.units}
        working.units = [replacement.get(u.number, u) for u in working.units]
        completed.extend({"number": u.number, "title": u.title, "takeaway": u.takeaway} for u in batch.units)
        service.partial_blueprint = working.model_copy(deep=True)
        callback = getattr(service, "on_batch", None)
        if callback:
            callback(service.partial_blueprint, len(completed))
    working.generation_mode = "batched"
    return working


def repair(service, bundle, blueprint, audit, failures):
    numbers = {n for issue in audit.issues for n in issue.unit_numbers if 1 <= n <= 20}
    for failure in failures:
        numbers.update(int(n) for n in re.findall(r"(?:unit|\bU)[_ -]?0?([1-9]|1[0-9]|20)(?!\d)", failure, re.I))
    numbers = sorted(numbers)
    working = blueprint.model_copy(deep=True)
    # Unlocalized failures do not authorize speculative replacement of all units.
    # Repair only global metadata separately; all gates are re-run by the caller.
    global_issues = [i.model_dump() for i in audit.issues if not i.unit_numbers]
    global_failures = [f for f in failures if not re.search(r"unit[_ -]?\d", f, re.I)]
    if global_issues or global_failures:
        plan = service._generate_structured(bundle=bundle, schema=BlueprintPlan,
            prompt="Repair only lecture metadata. Never claim new source coverage unless it is already taught in the supplied units. Do not output units. " + QUALITY_ADDENDUM,
            extra_text=blueprint.model_dump_json(by_alias=True) + context() + json.dumps({"issues": global_issues, "failures": global_failures}),
            preferred_model=service.model, thinking_level="low")
        working = Blueprint(**plan.model_dump(), units=working.units, generation_mode=working.generation_mode)
    for offset in range(0, len(numbers), BATCH_SIZE):
        selected = numbers[offset:offset + BATCH_SIZE]
        batch = request_validated(service, bundle, UnitBatch,
            MASTER_PROMPT + QUALITY_ADDENDUM + "\nTARGETED REPAIR: return ONLY requested units. Keep supported content and coverage evidence; correct the listed defects. Other units are immutable.",
            working.model_dump_json(by_alias=True) + "\nREQUESTED UNITS: " + json.dumps(selected)
            + "\nAUDIT: " + audit.model_dump_json() + "\nFAILURES: " + json.dumps(failures),
            lambda b: validate_batch(b, selected))
        replacements = {u.number: u for u in batch.units}
        working.units = [replacements.get(u.number, u) for u in working.units]
    return working
