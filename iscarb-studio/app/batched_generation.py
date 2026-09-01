"""Small, atomic generation transactions; ledger claims require visible evidence.

Schema validation is not semantic assurance. The existing independent audit and
release gates still run after assembly and after targeted repairs.
"""
from __future__ import annotations

import json
import re

from .models import Blueprint, BlueprintPlan, UnitBatch, CoverageEvidence, LectureUnit
from .prompts import MASTER_PROMPT
from .quality_rules import QUALITY_ADDENDUM
from .readiness import READINESS_CONTEXT
from .readiness_map import READINESS_KLO_MAP_CONTEXT
from .unit_contract import contract_text, role_problems, repair_context, TAG_OWNERS

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


def evidence_problems(bp, profile):
    """Actionable repair reasons from the same rule used by the release gate."""
    problems = {}
    units = {u.number: u for u in bp.units}
    rows = {r.coverage_id: r for r in bp.coverage_ledger}
    problems["batch_coverage_ids_unique"] = "" if len(rows) == len(bp.coverage_ledger) else "Duplicate coverage IDs"
    for item in profile.coverage_items:
        if item.importance != "major":
            continue
        row = rows.get(item.id)
        unit = units.get(row.first_taught_unit) if row else None
        key = f"batch_source_{item.id}_visible_in_unit{row.first_taught_unit:02d}" if row else f"batch_source_{item.id}_assigned"
        reason = ""
        if not unit or not 6 <= unit.number <= 15:
            reason = "Assign a substantive teaching unit numbered 6–15; an introduction or topic map is not source coverage"
        elif not same_source_anchor(row.source_anchor, item.source_anchor):
            reason = f"Ledger points to the wrong source coordinates; expected {item.source_anchor}"
        else:
            visible = " ".join(" ".join(unit.core_content).split()).casefold()
            matches = [ev for ev in unit.coverage_evidence if ev.coverage_id == item.id]
            anchored = [ev for ev in matches if same_source_anchor(ev.source_anchor, item.source_anchor)]
            substantive = [ev for ev in anchored if len(ev.visible_excerpt.split()) >= 4]
            if not matches:
                reason = f"Missing coverage_evidence entry for {item.id} in unit {unit.number}"
            elif not anchored:
                reason = f"Evidence has the wrong source coordinates; expected {item.source_anchor}"
            elif not substantive:
                reason = "Evidence must contain at least four words, not just a heading"
            elif not any(" ".join(ev.visible_excerpt.split()).casefold() in visible for ev in substantive):
                reason = "Evidence excerpt is absent from this unit's core_content; copy an exact passage from its actual teaching content"
        problems[key] = reason
    return problems


def evidence_checks(bp, profile):
    """Structural evidence only; independent semantic review remains mandatory."""
    return {key: not reason for key, reason in evidence_problems(bp, profile).items()}


def validate_plan(plan, profile):
    rows = {r.coverage_id: r for r in plan.coverage_ledger}
    if len(rows) != len(plan.coverage_ledger):
        raise ValueError("Duplicate coverage IDs in lecture plan")
    for item in profile.coverage_items:
        if item.importance == "major":
            row = rows.get(item.id)
            if not row or not 6 <= row.first_taught_unit <= 15 or not same_source_anchor(row.source_anchor, item.source_anchor):
                raise ValueError(f"Missing or displaced mandatory source coverage: {item.id}")


def validate_batch(batch, numbers):
    actual = [u.number for u in batch.units]
    if sorted(actual) != sorted(numbers):
        raise ValueError(f"Expected units {numbers}, received {actual}; batch not committed")
    if any(u.phase != PHASES[u.number - 1] for u in batch.units):
        raise ValueError("Unit phase does not match the fixed 20-unit grammar")


def materialize_source_passages(batch, ledger):
    """Build evidence from the exact visible text, never from a second LLM copy.

    This guarantees structural traceability only. Semantic fidelity still needs
    the independent audit against the original source bundle.
    """
    rows = {row.coverage_id: row for row in ledger}
    for unit in batch.units:
        core = list(unit.core_content)
        evidence = []
        for passage in unit.source_passages:
            for coverage_id in dict.fromkeys(passage.coverage_ids):
                if coverage_id not in rows:
                    raise ValueError(f"Unknown source coverage ID {coverage_id} in unit {unit.number}")
                evidence.append(CoverageEvidence(coverage_id=coverage_id,
                    source_anchor=rows[coverage_id].source_anchor, visible_excerpt=passage.text))
            if passage.text not in core:
                core.append(passage.text)
        unit.core_content = core
        unit.coverage_evidence = evidence
        # Assignment must not circumvent the original unit's length limits.
        LectureUnit.model_validate(unit.model_dump())


def context():
    return "\nREADINESS AUTHORITY:\n" + READINESS_CONTEXT + "\nOFFICIAL MAP:\n" + READINESS_KLO_MAP_CONTEXT


def request_validated(service, bundle, schema, prompt, extra, validate):
    # One bounded local-contract repair, scoped to this plan/batch only.
    for attempt in range(2):
        result = service._generate_structured(bundle=bundle, prompt=prompt,
            schema=schema, extra_text=extra, preferred_model=service.model, thinking_level="low")
        if isinstance(result, UnitBatch):
            # Phase is fixed routing metadata, not an LLM judgment. A batch can
            # straddle phases (unit 5 is IFHAM; 6–8 are MARIS). Canonicalizing
            # labels does not establish or waive the learner-visible role gate.
            for unit in result.units:
                unit.phase = PHASES[unit.number - 1]
        try:
            validate(result)
            return result
        except ValueError as exc:
            if attempt:
                raise GenerationContractError(str(exc)) from exc
            extra += "\nLOCAL CONTRACT FAILURE: " + str(exc) + "\nCorrect this output only.\n" + result.model_dump_json(by_alias=True)


def generate(service, bundle, profile):
    plan = request_validated(service, bundle, BlueprintPlan,
        MASTER_PROMPT + QUALITY_ADDENDUM + "\nSTAGE: PLAN ONLY. Return metadata, five CLOs, rubric and complete source allocation, NOT units. Copy every major coverage ID and source_anchor exactly. Allocate mandatory source coverage to substantive teaching units 6–15 ONLY. Units 1–5 introduce, map, set outcomes and activate prediction; they must not substitute for teaching source details. Units 16–20 assess and synthesize. Distribute source items coherently across the teaching units, preserving examples and figures.",
        profile.model_dump_json() + context() + contract_text(), lambda p: validate_plan(p, profile))
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
            + "\nALREADY COMPLETED OUTLINE:\n" + json.dumps(completed) + contract_text(numbers))
        def validate_candidate(batch):
            materialize_source_passages(batch, plan.coverage_ledger)
            validate_batch(batch, numbers)
            replacements = {u.number: u for u in batch.units}
            candidate = working.model_copy(update={"units": [replacements.get(u.number, u) for u in working.units]})
            ids = {row["coverage_id"] for row in assigned}
            scoped_profile = profile.model_copy(update={"coverage_items": [x for x in profile.coverage_items if x.id in ids]})
            failed = [f"{k}: {reason}" for k, reason in evidence_problems(candidate, scoped_profile).items() if reason]
            failed += [f"{k}: {reason}" for k, reason in role_problems(candidate, numbers).items()]
            if failed:
                raise ValueError("Source/role contract failed: " + ", ".join(failed) + contract_text(numbers))
        batch = request_validated(service, bundle, UnitBatch,
            MASTER_PROMPT + QUALITY_ADDENDUM + "\nBATCH OUTPUT: only the requested units. Put assigned source teaching in source_passages: each passage has coverage_ids and substantive source-grounded text of at least four words and 20 characters. Every assigned ID must occur. The program uses this exact text as visible core_content and derives coverage_evidence; do NOT repeat it in either of those fields. Teach the actual mechanism/example, not just its title. Metadata-only coverage does not count. Preserve complete source figures in visual_plan where relevant. Never put a newly invented scenario detail in source_passages or core_content: keep source statements general and put hypothetical applications in scenario_assumptions/pedagogy_content with explicit HYPOTHETICAL labeling.",
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
        if failure.startswith("coverage_") and failure.removeprefix("coverage_") in TAG_OWNERS:
            numbers.add(TAG_OWNERS[failure.removeprefix("coverage_")])
    numbers = sorted(numbers)
    working = blueprint.model_copy(deep=True)
    # Unlocalized failures do not authorize speculative replacement of all units.
    # Repair only global metadata separately; all gates are re-run by the caller.
    # Generic gate summaries are not metadata defects. Previously almost every
    # repair regenerated the plan, silently moving source allocations away from
    # the already-generated evidence. Keep the ledger locked for unit repairs.
    metadata_keys = ("clo_ids", "exactly_5_clos", "source_topic_list", "topic_coverage_matches",
                     "rubric_", "readiness_")
    global_issues = [i.model_dump() for i in audit.issues if not i.unit_numbers
                     and any(k in i.requirement.lower() for k in ("metadata", "rubric", "readiness alignment"))]
    global_failures = [f for f in failures if f.startswith(metadata_keys)]
    if global_issues or global_failures:
        plan = service._generate_structured(bundle=bundle, schema=BlueprintPlan,
            prompt="Repair only lecture metadata. Never claim new source coverage unless it is already taught in the supplied units. Do not output units. " + QUALITY_ADDENDUM,
            extra_text=blueprint.model_dump_json(by_alias=True) + context() + json.dumps({"issues": global_issues, "failures": global_failures}),
            preferred_model=service.model, thinking_level="low")
        working = Blueprint(**plan.model_dump(), units=working.units, generation_mode=working.generation_mode)
        working.coverage_ledger = blueprint.model_copy(deep=True).coverage_ledger
        working.topic_coverage = blueprint.model_copy(deep=True).topic_coverage
    for offset in range(0, len(numbers), BATCH_SIZE):
        selected = numbers[offset:offset + BATCH_SIZE]
        def validate_repair(batch):
            materialize_source_passages(batch, working.coverage_ledger)
            validate_batch(batch, selected)
            replacements = {u.number: u for u in batch.units}
            candidate = working.model_copy(update={"units": [replacements.get(u.number, u) for u in working.units]})
            problems = role_problems(candidate, selected)
            # Repairs must retain every locked assignment, not just valid IDs.
            from types import SimpleNamespace
            scoped = SimpleNamespace(coverage_items=[SimpleNamespace(id=r.coverage_id,
                importance="major", source_anchor=r.source_anchor)
                for r in working.coverage_ledger if r.first_taught_unit in selected])
            problems.update({k: v for k, v in evidence_problems(candidate, scoped).items() if v})
            if problems:
                raise ValueError(json.dumps(problems) + contract_text(selected))
        batch = request_validated(service, bundle, UnitBatch,
            MASTER_PROMPT + QUALITY_ADDENDUM + "\nTARGETED REPAIR: return ONLY requested units. Put supported source teaching in source_passages with its coverage_ids and exact student-visible text; the program derives core and evidence from this one value. Keep existing source coverage and correct the listed defects. Other units are immutable.",
            working.model_dump_json(by_alias=True) + "\nREQUESTED UNITS: " + json.dumps(selected)
            + "\nAUDIT (advice cannot override the following contract): " + audit.model_dump_json()
            + "\nFAILURES: " + json.dumps(failures) + repair_context(working, selected),
            validate_repair)
        replacements = {u.number: u for u in batch.units}
        working.units = [replacements.get(u.number, u) for u in working.units]
    return working
