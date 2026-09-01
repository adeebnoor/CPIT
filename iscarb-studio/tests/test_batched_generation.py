"""Transport-free contract tests. These do not certify model output quality."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.batched_generation import generate, repair, evidence_checks, validate_batch, validate_plan
from app.models import BlueprintPlan, UnitBatch, CoverageEvidence, AuditReport, AuditIssue
from tests.test_v44_release import source


def prepared(source):
    profile, original = source
    bp = original.model_copy(deep=True)
    for row in bp.coverage_ledger:
        u = bp.units[row.first_taught_unit - 1]
        excerpt = f"Visible teaching evidence for source item {row.coverage_id}."
        u.core_content.append(excerpt)
        u.coverage_evidence.append(CoverageEvidence(coverage_id=row.coverage_id,
            source_anchor=row.source_anchor, visible_excerpt=excerpt))
    return profile, bp


def test_generation_requests_plan_then_five_atomic_batches(source):
    profile, bp = prepared(source)
    results = [BlueprintPlan.model_validate(bp.model_dump())]
    results += [UnitBatch(units=bp.units[i:i+4]) for i in range(0,20,4)]
    service = SimpleNamespace(model="auto", _generate_structured=Mock(side_effect=results), on_batch=Mock())
    actual = generate(service, None, profile)
    assert actual.generation_mode == "batched"
    assert [u.number for u in actual.units] == list(range(1,21))
    assert service._generate_structured.call_count == 6
    assert [call.args[1] for call in service.on_batch.call_args_list] == [4,8,12,16,20]
    assert all(evidence_checks(actual, profile).values())


def test_duplicate_or_wrong_phase_batch_is_never_committed(source):
    _, bp = source
    with pytest.raises(ValueError, match="Expected units"):
        validate_batch(UnitBatch(units=[bp.units[0]] * 4), [1,2,3,4])
    bad = bp.units[0].model_copy(update={"phase":"MARIS"})
    with pytest.raises(ValueError, match="phase"):
        validate_batch(UnitBatch(units=[bad]), [1])


def test_ledger_alone_and_pedagogy_only_do_not_prove_source_coverage(source):
    profile, bp = prepared(source)
    assert all(evidence_checks(bp, profile).values())
    row = next(r for r in bp.coverage_ledger if any(x.id==r.coverage_id and x.importance=="major" for x in profile.coverage_items))
    u = bp.units[row.first_taught_unit-1]
    u.pedagogy_content += u.core_content
    u.core_content = []
    assert not all(evidence_checks(bp, profile).values())


def test_plan_cannot_drop_or_defer_mandatory_source_items(source):
    profile, bp = prepared(source)
    plan = BlueprintPlan.model_validate(bp.model_dump())
    validate_plan(plan, profile)
    plan.coverage_ledger = []
    with pytest.raises(ValueError, match="mandatory"):
        validate_plan(plan, profile)


def test_timeout_preserves_last_completed_batch_without_claiming_completion(source):
    profile, bp = prepared(source)
    service = SimpleNamespace(model="auto", _generate_structured=Mock(side_effect=[
        BlueprintPlan.model_validate(bp.model_dump()), UnitBatch(units=bp.units[:4]), TimeoutError("upstream")]))
    with pytest.raises(TimeoutError):
        generate(service, None, profile)
    assert service.partial_blueprint.generation_mode == "batched-partial"
    assert service.partial_blueprint.units[:4] == bp.units[:4]


def test_targeted_repair_does_not_rewrite_nineteen_good_units(source):
    _, bp = prepared(source)
    changed = bp.units[4].model_copy(update={"title":"Repaired prediction"})
    service = SimpleNamespace(model="auto", _generate_structured=Mock(return_value=UnitBatch(units=[changed])))
    audit = AuditReport(overall_pass=False, source_fidelity_pass=True,
        engineering_rigor_pass=False, cumulative_fidelity_pass=True,
        readiness_alignment_pass=True, provenance_separation_pass=True,
        issues=[AuditIssue(severity="major",unit_numbers=[5],requirement="prediction",
            problem="Missing prediction",repair_instruction="Repair prediction")])
    result = repair(service,None,bp,audit,["v15_unit05_predict_constraint_derive_name"])
    assert result.units[4].title == "Repaired prediction"
    assert all(result.units[i] == bp.units[i] for i in range(20) if i != 4)
    assert bp.units[4].title != "Repaired prediction"
    assert service._generate_structured.call_count == 1
