from __future__ import annotations

"""ISCARB process bootstrap for Faculty Studio v3.6.

Gate v9 patches the compiler before the Faculty Studio app is imported. The v3.6
public UI is native, so runtime HTML string-patching is no longer required.
"""

import uuid

from fastapi import HTTPException

from . import main as engine
from .gate import failed_check_names
from .gate_v9 import deterministic_gate as gate_v9, normalize_blueprint_for_gate
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
        "visual_output": "v6-saudi-heritage-visual-provenance",
        "local_pre_gate_normalizer": True,
        "local_gate_repair": True,
        "local_normalizer_scope": [
            "provenance channel cleanup",
            "Unit 10 information ledger",
            "Unit 20 bounded assurance",
            "unsourced precision labeled synthetic",
            "unsupported authority claims bounded as hypothetical",
            "human-factors kept outside P1 core unless source-supported",
            "Units 16-17 readiness orientation reference",
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
    """Deterministically repair a generated Blueprint without Gemini.

    Local repair is review-only and never grants RELEASE/ISCARB Verified.
    """
    try:
        old = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if old.blueprint is None:
        raise HTTPException(409, "No Blueprint is available to repair")

    repaired = normalize_blueprint_for_gate(old.blueprint, source_text="", profile=old.source_profile)
    checks = gate_v9(repaired, old.source_profile, "")
    failures = failed_check_names(checks)

    new_id = uuid.uuid4().hex
    audit = AuditReport(
        overall_pass=False,
        source_fidelity_pass=(checks.get("no_obvious_unsourced_terms_in_core", False) and checks.get("human_factors_not_misattributed_to_p1_core", False)),
        engineering_rigor_pass=(checks.get("unit10_known_unknown_monitoring", False) and checks.get("unit20_assurance_language", checks.get("unit20_uses_bounded_assurance_language", False)) and checks.get("no_unsourced_precision_in_noncore", False)),
        cumulative_fidelity_pass=not any(name.startswith(("unit2_","unit3_","unit4_","unit11_","unit12_","unit13_","unit14_","unit15_","unit16_","unit17_","unit18_","unit19_")) for name in failures),
        readiness_alignment_pass=not any("readiness" in name or "etec" in name for name in failures),
        provenance_separation_pass=not any(any(k in name for k in ["provenance","enrichment","unsourced","source_anchor","pedagogy_channel","external_authority","human_factors"]) for name in failures),
        issues=[AuditIssue(
            severity="major",
            unit_numbers=[],
            requirement="Local deterministic repair — semantic audit not repeated",
            problem=("Gate v9 local normalization was applied without Gemini. " + ("Remaining deterministic checks: " + ", ".join(failures[:24]) if failures else "No locally repairable Gate v9 failures remain.")),
            repair_instruction="Use these outputs for faculty review. Re-run the full compiler/audit before assigning ISCARB Verified.",
        )],
        strengths=["Gate v9 claim-level provenance controls applied locally.","Visual outputs can be iterated with zero model calls."],
    )
    job = JobState(
        id=new_id,
        status="blocked",
        progress=100,
        message="LOCAL REPAIR COMPLETE — Gate v9 normalization applied with 0 Gemini calls. v3.6 visual outputs are ready for faculty review; RELEASE audit was not repeated.",
        filename=old.filename,
        model="local-gate-v9-repair",
        source_manifest=list(old.source_manifest),
        lecture_focus=old.lecture_focus,
        source_profile=old.source_profile,
        blueprint=repaired,
        audit=audit,
        deterministic_checks=checks,
        error=None,
    )
    engine.save_job(job)
    return {"job_id": new_id, "remaining_failures": failures}
