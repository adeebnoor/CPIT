"""Regression cases from the live 4.5.3 class-2 rejection, not model approval."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.batched_generation import generate, repair, GenerationContractError
from app.gate import deterministic_gate as base_gate
from app.gate_v15 import deterministic_gate, unit_role_checks
from app.gemini_service import GeminiService
from app.models import AuditIssue, AuditReport, BlueprintPlan, UnitBatch
from app.unit_contract import contract_text, role_problems
from tests.test_batched_generation import prepared
from tests.test_v44_release import source


def audit_for(numbers=(), requirement="Deterministic release invariants", instruction="Repair the defects"):
    return AuditReport(overall_pass=False, source_fidelity_pass=False,
        engineering_rigor_pass=False, cumulative_fidelity_pass=False,
        readiness_alignment_pass=True, provenance_separation_pass=False,
        issues=[AuditIssue(severity="major", unit_numbers=list(numbers),
            requirement=requirement, problem="A real defect", repair_instruction=instruction)])


def test_local_checks_are_the_final_role_checks(source):
    profile, bp = source
    bp = bp.model_copy(deep=True)
    bp.units[7].pedagogy_content = ["Alternatives", "Trade-off"]
    local = unit_role_checks(bp, [8])
    final = deterministic_gate(bp, profile)
    assert local and all(final[k] == v for k, v in local.items())
    assert "v15_unit08_job_is_visible" in role_problems(bp, [8])


def test_outcomes_and_hstack_are_not_source_knowledge(source):
    _, bp = source
    bp = bp.model_copy(deep=True)
    bp.units[2].core_content = ["Dependability includes availability and reliability."]
    bp.units[3].core_content = ["Evidence-based reasoning is a capability."]
    assert not unit_role_checks(bp)["v15_unit03_five_clos_only"]
    assert not unit_role_checks(bp)["v15_unit04_hstack_is_exact"]
    bp.units[2].core_content = []
    bp.units[2].pedagogy_content.append("Extra outcome that should not be accepted.")
    assert not unit_role_checks(bp)["v15_unit03_five_clos_only"]


def test_batch_rejects_malformed_roles_before_committing(source):
    profile, bp = prepared(source)
    bad = UnitBatch(units=bp.units[:4])
    bad.units[2].core_content = ["A misplaced source fact about dependability."]
    service = SimpleNamespace(model="auto", _generate_structured=Mock(side_effect=[
        BlueprintPlan.model_validate(bp.model_dump()), bad, bad.model_copy(deep=True)]), on_batch=Mock())
    with pytest.raises(GenerationContractError, match="unit03_five_clos_only"):
        generate(service, None, profile)
    service.on_batch.assert_not_called()


def test_p1_ai_topic_is_allowed_but_instructional_ai_rules_are_not_core(source):
    profile, bp = source
    bp = bp.model_copy(deep=True)
    bp.units[14].core_content = ["AI can improve redundancy and diversity."]
    bp.units[14].source_anchor = "[P1] PAGE 12"
    assert base_gate(bp, profile, "Dependable systems in the AI era")["unit15_ai_in_pedagogy_channel"]
    assert not base_gate(bp, profile, "Software processes")["unit15_ai_in_pedagogy_channel"]
    bp.units[14].core_content.append("AI MAY ASSIST: Generate learner test cases under supervision.")
    assert not base_gate(bp, profile, "Dependable systems in the AI era")["unit15_ai_in_pedagogy_channel"]


def test_auditor_receives_the_same_channel_contract(source):
    _, bp = source
    service = object.__new__(GeminiService)
    service._generate_structured = Mock(return_value=audit_for())
    service.audit(SimpleNamespace(manifest_text=lambda: "[P1] source"), bp, ["unit18_evidence_method_in_pedagogy_channel"])
    extra = service._generate_structured.call_args.kwargs["extra_text"]
    assert contract_text() in extra
    assert "U18 evidence-method instructions stay in pedagogy" in extra
    assert "never infer its meaning from a check name alone" in extra


def test_global_gate_summary_does_not_regenerate_coverage_plan(source):
    _, bp = prepared(source)
    service = SimpleNamespace(model="auto", _generate_structured=Mock(return_value=UnitBatch(units=[bp.units[4]])))
    result = repair(service, None, bp, audit_for(), ["v15_unit05_predict_constraint_derive_name", "v15_complete_20_unit_grammar"])
    assert service._generate_structured.call_count == 1
    assert service._generate_structured.call_args.kwargs["schema"] is UnitBatch
    assert result.coverage_ledger == bp.coverage_ledger


def test_repair_cannot_drop_locked_source_evidence(source):
    _, bp = prepared(source)
    bad = UnitBatch(units=[bp.units[5]])
    bad.units[0].source_passages = []
    service = SimpleNamespace(model="auto", _generate_structured=Mock(side_effect=[bad, bad.model_copy(deep=True)]))
    with pytest.raises(GenerationContractError, match="Missing coverage_evidence"):
        repair(service, None, bp, audit_for([6]), ["v15_unit06_job_is_visible"])


def test_advice_cannot_override_role_contract_in_repair_prompt(source):
    _, bp = prepared(source)
    service = SimpleNamespace(model="auto", _generate_structured=Mock(return_value=UnitBatch(units=[bp.units[17]])))
    wrong_advice = "Move warrant and residual uncertainty into core_content."
    repair(service, None, bp, audit_for([18], instruction=wrong_advice), ["unit18_evidence_method_in_pedagogy_channel"])
    text = service._generate_structured.call_args.kwargs["extra_text"]
    assert text.index(wrong_advice) < text.index("AUTHORITATIVE CORRECTION TARGETS")
    assert "Evidence protocol lives in pedagogy_content, NOT core_content" in text


def test_unreadable_slide_is_localized_for_targeted_repair(source):
    profile, bp = source
    bp = bp.model_copy(deep=True)
    bp.units[6].pedagogy_content = ["Repeated long instructional passage " * 250]
    checks = deterministic_gate(bp, profile)
    assert not checks["presenter_unit07_readable"]
    assert not checks["v15_presenter_fits_readable_canvas"]


def test_missing_obligation_targets_its_unit_not_the_plan(source):
    _, bp = prepared(source)
    service = SimpleNamespace(model="auto", _generate_structured=Mock(return_value=UnitBatch(units=[bp.units[8]])))
    repair(service, None, bp, audit_for(), ["coverage_EER-7"])
    assert service._generate_structured.call_count == 1
    call = service._generate_structured.call_args.kwargs
    assert call["schema"] is UnitBatch
    assert "estimate before measurement" in call["extra_text"]


def test_metadata_repair_cannot_reallocate_the_source(source):
    _, bp = prepared(source)
    plan = BlueprintPlan.model_validate(bp.model_dump())
    plan.coverage_ledger[0].first_taught_unit = 15
    plan.topic_coverage[0].first_taught_unit = 15
    service = SimpleNamespace(model="auto", _generate_structured=Mock(return_value=plan))
    result = repair(service, None, bp, audit_for(requirement="Readiness alignment"), ["readiness_alignment_present"])
    assert result.coverage_ledger == bp.coverage_ledger
    assert result.topic_coverage == bp.topic_coverage
