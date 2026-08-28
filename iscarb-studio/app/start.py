from __future__ import annotations

"""ISCARB process bootstrap for Faculty Studio v3.7.

Gate v9 patches the compiler before the Faculty Studio app is imported. Output
Lab repairs are intentionally presentation-safe and never pretend to re-run a
source-dependent release audit without the original lecture bundle.
"""

import uuid

from fastapi import HTTPException

from . import main as engine
from .gate_v9 import (
    deterministic_gate as gate_v9,
    normalize_blueprint_for_gate,
    normalize_blueprint_for_output_lab,
)
from .models import AuditIssue, AuditReport, JobState


_original_timebox = engine.apply_90_minute_timebox
_original_health = engine.health


def _timebox_v9(bp, profile, bundle):
    bp = _original_timebox(bp, profile, bundle)
    try:
        source_text = bundle.combined_local_text()
    except Exception:
        source_text = ""
    return normalize_blueprint_for_gate(bp, source_text=source_text, profile=profile)


def _health_v9():
    data = _original_health()
    data.update({
        "deterministic_gate": "v9-claim-level-fidelity",
        "visual_output": "v7-approved-saudi-heritage",
        "local_pre_gate_normalizer": True,
        "local_gate_repair": True,
        "output_lab_audit_mode": "render-and-presentation-repair-only",
        "local_normalizer_scope": [
            "enrichment-state consistency",
            "visible Unit 5 first-principles scaffold",
            "provenance channel cleanup",
            "Unit 10 information ledger",
            "Unit 20 bounded assurance",
            "unsourced precision labeled synthetic",
            "unsupported authority claims bounded as hypothetical",
            "human-factors kept outside P1 core unless source-supported",
            "Units 16-17 readiness orientation reference",
            "exact readiness mapping when original source is available",
        ],
    })
    return data


engine.deterministic_gate = gate_v9
engine.apply_90_minute_timebox = _timebox_v9
engine.health = _health_v9

from . import faculty_main as faculty  # noqa: E402

app = faculty.app


@app.post("/api/jobs/{job_id}/local-repair")
def local_gate_repair(job_id: str):
    """Apply source-independent Blueprint repairs without Gemini.

    This endpoint is deliberately NOT a release audit. Imported Blueprint JSON
    does not include the raw P1 source text needed for source fidelity, exact
    ETEC atomicity, or semantic release authority. Those states are therefore
    reported as NOT RE-AUDITED rather than false FAIL results.
    """
    try:
        old = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if old.blueprint is None:
        raise HTTPException(409, "No Blueprint is available to repair")

    repaired = normalize_blueprint_for_output_lab(old.blueprint)

    new_id = uuid.uuid4().hex
    audit = AuditReport(
        overall_pass=False,
        source_fidelity_pass=False,
        engineering_rigor_pass=False,
        cumulative_fidelity_pass=False,
        readiness_alignment_pass=False,
        provenance_separation_pass=False,
        issues=[AuditIssue(
            severity="major",
            unit_numbers=[],
            requirement="Output Lab — release audit not repeated",
            problem=(
                "Presentation-safe deterministic repairs were applied with 0 Gemini calls. "
                "Source fidelity, ETEC source atomicity, semantic engineering audit, and release authority "
                "cannot be re-evaluated from Blueprint JSON alone."
            ),
            repair_instruction=(
                "Use the repaired outputs for faculty review. Re-run Generate New Lecture with the original "
                "lecture source when ISCARB Verified release authority is required."
            ),
        )],
        strengths=[
            "Enrichment-state consistency repaired locally.",
            "Unit 5 first-principles sequence made explicit locally.",
            "Visual/document outputs can be iterated with zero model calls.",
        ],
    )
    job = JobState(
        id=new_id,
        status="blocked",
        progress=100,
        message=(
            "OUTPUT LAB REPAIR COMPLETE — presentation-safe local normalization applied with 0 Gemini calls. "
            "Source-dependent gates are NOT RE-AUDITED; full compile is required for ISCARB Verified."
        ),
        filename=old.filename,
        model="local-output-repair-v3.7",
        source_manifest=list(old.source_manifest),
        lecture_focus=old.lecture_focus,
        source_profile=old.source_profile,
        blueprint=repaired,
        audit=audit,
        deterministic_checks={},
        error=None,
    )
    engine.save_job(job)
    return {"job_id": new_id, "audit_state": "not_reaudited"}
