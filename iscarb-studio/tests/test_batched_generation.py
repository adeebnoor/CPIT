"""Transport-free contract tests. These do not certify model output quality."""
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.batched_generation import generate, repair, evidence_checks, validate_batch, validate_plan, GenerationContractError
from app.models import BlueprintPlan, UnitBatch, CoverageEvidence, AuditReport, AuditIssue
from tests.test_v44_release import source, LECTURE


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
    from app.models import LectureUnit
    assert [LectureUnit.model_validate(u.model_dump()).model_dump() for u in service.partial_blueprint.units[:4]] == [u.model_dump() for u in bp.units[:4]]


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


def test_rejected_model_content_is_review_required_not_an_application_crash(source):
    from app import main
    from app.models import JobState
    from app.source_bundle import SourceBundle, SourceItem
    profile, _ = source
    job = JobState(id="contract-test", status="queued",progress=0,message="")
    bundle = SourceBundle(items=[SourceItem("primary","P1",LECTURE.name,LECTURE,LECTURE.name)],lecture_focus="",session_minutes=90)
    service = Mock()
    service.profile_source.return_value = profile
    service.generate_blueprint.side_effect = GenerationContractError("Missing learner-visible source evidence: unit01")
    with patch.object(main,"load_job",return_value=job), patch.object(main,"save_job"), patch.object(main,"prune_expired"), patch.object(main,"GeminiService",return_value=service):
        main._compile(job.id,bundle,"auto",0)
    assert job.status == "blocked"
    assert job.error is None and job.blueprint is not None
    assert job.audit.overall_pass is False
    assert any("unit01" in i.problem for i in job.audit.issues)


def test_source_evidence_compares_coordinates_not_page_label_spelling():
    from app.batched_generation import same_source_anchor
    assert same_source_anchor("[P1] PAGE 7", "[P1] SLIDE 7")
    assert not same_source_anchor("[P1] PAGE 7", "[P1] PAGE 8")
    assert not same_source_anchor("[P1] PAGE 7", "[S1] PAGE 7")


def test_new_generation_schema_requires_explicit_source_evidence():
    schema = UnitBatch.model_json_schema()
    assert "source_passages" in schema["$defs"]["BatchLectureUnit"]["required"]
    assert set(schema["$defs"]["SourcePassage"]["required"]) == {"coverage_ids", "text"}


def test_repair_diagnostic_distinguishes_missing_quote_from_missing_id(source):
    from app.batched_generation import evidence_problems
    profile, bp = prepared(source)
    row = next(r for r in bp.coverage_ledger if any(x.id==r.coverage_id and x.importance=="major" for x in profile.coverage_items))
    unit = bp.units[row.first_taught_unit-1]
    ev = next(x for x in unit.coverage_evidence if x.coverage_id==row.coverage_id)
    ev.visible_excerpt = "This passage is not actually taught in this unit."
    assert any("absent from" in reason for reason in evidence_problems(bp,profile).values())
    unit.coverage_evidence = [x for x in unit.coverage_evidence if x.coverage_id != row.coverage_id]
    assert any("Missing coverage_evidence" in reason for reason in evidence_problems(bp,profile).values())


def test_domain_spine_is_not_a_substitute_for_teaching_source_details(source):
    profile, bp = prepared(source)
    plan = BlueprintPlan.model_validate(bp.model_dump())
    row = next(r for r in plan.coverage_ledger if any(x.id==r.coverage_id and x.importance=="major" for x in profile.coverage_items))
    row.first_taught_unit = 2
    with pytest.raises(ValueError, match="mandatory source coverage"):
        validate_plan(plan, profile)


def test_cross_phase_batch_gets_canonical_labels_without_a_model_retry(source):
    from app.batched_generation import request_validated
    _, bp = source
    batch = UnitBatch(units=bp.units[4:8])
    for unit in batch.units:
        unit.phase = "MARIS"
    service = SimpleNamespace(model="auto", _generate_structured=Mock(return_value=batch))
    result = request_validated(service, None, UnitBatch, "", "", lambda b: validate_batch(b, [5,6,7,8]))
    assert [u.phase for u in result.units] == ["IFHAM","MARIS","MARIS","MARIS"]
    assert service._generate_structured.call_count == 1


def test_source_passage_builds_visible_text_and_evidence_from_one_value(source):
    from app.batched_generation import materialize_source_passages
    profile, bp = prepared(source)
    batch = UnitBatch(units=[bp.units[5]])
    unit = batch.units[0]
    assert unit.source_passages
    unit.core_content = []
    unit.coverage_evidence = []
    materialize_source_passages(batch, bp.coverage_ledger)
    assert all(e.visible_excerpt in unit.core_content for e in unit.coverage_evidence)
    bp.units[5] = unit
    assert all(evidence_checks(bp, profile).values())


def test_source_passages_cannot_invent_coverage_ids(source):
    from app.batched_generation import materialize_source_passages
    _, bp = prepared(source)
    batch = UnitBatch(units=[bp.units[5]])
    batch.units[0].source_passages[0].coverage_ids = ["NOT-IN-THE-SOURCE"]
    with pytest.raises(ValueError, match="Unknown source coverage ID"):
        materialize_source_passages(batch, bp.coverage_ledger)
