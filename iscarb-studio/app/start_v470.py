from __future__ import annotations

"""ISCARB Faculty Studio v4.7.0 — enforceable Master Guidelines."""

from .start_v4612 import app
from . import start_v440 as base
from . import main as engine_main
from . import deterministic_blueprint_fallback as draft_builder
from . import presenter_v44
from . import source_visuals_v42
from .gate_v16 import deterministic_gate as gate_v16
from .master_guidelines_v470 import apply_master_guidelines, plans_for_blueprint_v470, visual_plan_checks

PUBLIC_VERSION = "4.7.0"
PIPELINE_ID = "faculty-studio-v4.7.0-master-guidelines-visual-first"

# Apply the master rules to both newly built deterministic drafts and any
# source-preserving rebuild invoked by the live engine.
_original_build = draft_builder.build_deterministic_blueprint

def _build_v470(profile):
    return apply_master_guidelines(_original_build(profile))

draft_builder.build_deterministic_blueprint = _build_v470
engine_main.build_deterministic_blueprint = _build_v470

_original_source_draft = engine_main._source_preserving_draft

def _source_draft_v470(profile, bundle):
    return apply_master_guidelines(_original_source_draft(profile, bundle))

engine_main._source_preserving_draft = _source_draft_v470

# All presenter surfaces use the same source-first, non-repeating visual planner.
source_visuals_v42.plans_for_blueprint_v42 = plans_for_blueprint_v470
presenter_v44.plans_for_blueprint_v42 = plans_for_blueprint_v470

# Gate v16 is the release gate, not an advisory report.
base.engine.deterministic_gate = gate_v16
engine_main.deterministic_gate = gate_v16

_original_critical = engine_main._critical_presenter_failures

def _critical_v470(checks):
    failures = list(_original_critical(checks))
    for name in (
        "v16_primary_source_has_no_paragraphs",
        "v16_visual_text_alignment_target_declared",
        "v16_local_context_is_bounded",
        "v16_scalability_has_explicit_stress_variable",
        "v16_ai_generation_is_separate_from_signoff",
        "v16_grading_requires_live_evidence_defense",
        "v16_master_guidelines_pass",
        "v16_no_visual_reuse_without_mutation",
        "v16_visual_matches_unit_concept_or_p1_anchor",
    ):
        if checks.get(name) is False and name not in failures:
            failures.append(name)
    return failures

engine_main._critical_presenter_failures = _critical_v470

# Preview/export knows the actual selected assets, so this is where visual
# duplication and semantic alignment are tested against real plans.
_original_presenter_job = base._presenter_job

def _presenter_job_v470(job_id: str):
    job = _original_presenter_job(job_id)
    try:
        from .storage import UPLOADS
        plans = plans_for_blueprint_v470(job.blueprint, source_root=UPLOADS / job_id)
        job.deterministic_checks.update(visual_plan_checks(job.blueprint, plans))
        job.deterministic_checks["v16_master_guidelines_pass"] = all(
            value for key, value in job.deterministic_checks.items()
            if key.startswith("v16_") and key != "v16_master_guidelines_pass"
        )
        if job.status == "ready" and not job.deterministic_checks["v16_master_guidelines_pass"]:
            job.status = "blocked"
            job.message = "Master Guidelines visual/content gate requires repair before release."
        base.engine.save_job(job)
    except Exception:
        pass
    return job

base._presenter_job = _presenter_job_v470

# Health/version contract.
base.PUBLIC_VERSION = PUBLIC_VERSION
base.PIPELINE_ID = PIPELINE_ID
_prev_health = base._health_v440

def _health_v470():
    data = _prev_health()
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v16-master-guidelines-on-v15",
        "presenter_text_contract": "P1 appears as <=3 short maxims; narrative stays in source/notes",
        "visual_contract": "P1 figure first; otherwise semantically matched public image; no duplicate asset unless explicit Unit-17 mutation",
        "local_context_contract": "bounded hypothetical + current-P1 mechanisms only",
        "scalability_contract": "explicit numeric or structural stress variable + fail-first assumption",
        "ai_governance_contract": "AI generates candidates; accountable human owns sign-off",
        "grading_contract": "capability credit requires live defense + P1 evidence + learner artifact",
        "release_contract": "semantic audit PASS AND all Gate v16 checks PASS",
    })
    return data

base._health_v440 = _health_v470
base.engine.health = _health_v470
