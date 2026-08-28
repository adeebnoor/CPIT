from __future__ import annotations

"""ISCARB process bootstrap for Faculty Studio v4.0 Final Candidate.

Gate v9 remains the source-backed release gate. v4.0 keeps Output Lab in
REVIEW MODE and never manufactures source-dependent PASS/FAIL results without
the original P1 bundle.
"""

import uuid

from fastapi import HTTPException

from . import main as engine
from .gate_v9 import deterministic_gate as gate_v9
from .normalizer_v38 import normalize_source_backed_v38, normalize_output_lab_v38
from .models import AuditIssue, AuditReport, JobState


_original_timebox = engine.apply_90_minute_timebox
_original_health = engine.health


def _timebox_v40(bp, profile, bundle):
    bp = _original_timebox(bp, profile, bundle)
    try:
        source_text = bundle.combined_local_text()
    except Exception:
        source_text = ""
    return normalize_source_backed_v38(bp, source_text=source_text, profile=profile)


def _health_v40():
    data = _original_health()
    data.update({
        "deterministic_gate": "v9-claim-level-fidelity",
        "faculty_experience": "v4.0-final-candidate-reference-matched-heritage",
        "visual_output": "visual-first-presenter-with-provenance",
        "local_pre_gate_normalizer": True,
        "local_gate_repair": True,
        "output_lab_audit_mode": "review-mode-not-reaudited-no-false-fails",
        "local_normalizer_scope": [
            "Unit 3 exactly five CLOs in pedagogy channel",
            "hypothetical enrichment bounded as scenario assumptions",
            "IDR-7 progression metadata",
            "EER-7 estimate-before-precision scaffold",
            "enrichment-state consistency",
            "visible Unit 5 first-principles scaffold",
            "Unit 10 information ledger",
            "Unit 20 bounded assurance",
            "unsourced precision labeled synthetic",
            "human-factors provenance",
            "readiness orientation references",
        ],
    })
    return data


engine.deterministic_gate = gate_v9
engine.apply_90_minute_timebox = _timebox_v40
engine.health = _health_v40

from . import faculty_main as faculty  # noqa: E402

app = faculty.app


@app.post("/api/jobs/{job_id}/local-repair")
def local_gate_repair(job_id: str):
    """Apply source-independent Blueprint repairs without Gemini.

    This endpoint is deliberately NOT a release audit. Imported Blueprint JSON
    does not contain the raw P1 source text required for source fidelity and
    source-dependent ETEC validation. The UI therefore reports NOT RE-AUDITED.
    """
    try:
        old = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if old.blueprint is None:
        raise HTTPException(409, "No Blueprint is available to repair")

    repaired = normalize_output_lab_v38(old.blueprint)

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
                "Presentation-safe structural repairs were applied with 0 Gemini calls. Source fidelity, source-dependent "
                "ETEC checks, semantic engineering audit, and release authority were not re-evaluated because P1 is absent."
            ),
            repair_instruction=(
                "Use the repaired outputs for design/faculty review. Run Analyze Source with the original lecture source "
                "when ISCARB Verified release authority is required."
            ),
        )],
        strengths=[
            "Unit 3 CLO channel repaired locally.",
            "Hypothetical enrichment framing repaired locally.",
            "IDR-7/EER-7 pedagogy metadata and estimation scaffold repaired locally.",
            "Visual/document outputs can be iterated with zero model calls.",
        ],
    )
    job = JobState(
        id=new_id,
        status="blocked",
        progress=100,
        message=(
            "OUTPUT LAB REPAIR COMPLETE — presentation-safe v4.0 normalization applied with 0 Gemini calls. "
            "Source-dependent gates are NOT RE-AUDITED; full source-backed compile is required for ISCARB Verified."
        ),
        filename=old.filename,
        model="local-output-repair-v4.0",
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
