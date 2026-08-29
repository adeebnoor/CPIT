from __future__ import annotations

"""ISCARB Faculty Studio v4.0.4 production bootstrap.

Release goals:
- Gate v11 + v10 source-safe normalization before deterministic release checks.
- No Audit-PASS / deterministic-BLOCKED contradiction: deterministic failures
  are explicitly reflected in the audit report.
- Preserve the approved Saudi-heritage Faculty Studio and Visual Lecture Engine v2.
"""

from fastapi.responses import HTMLResponse

from . import start as legacy
from .gate_v11 import deterministic_gate as gate_v11
from .gate_v10 import normalize_blueprint_for_gate as normalize_v10
from .normalizer_v404 import normalize_source_backed_v404, normalize_output_lab_v404
from .models import AuditIssue
from .gemini_service import GeminiService

engine = legacy.engine
app = legacy.app

PUBLIC_VERSION = "4.0.4"
PIPELINE_ID = "faculty-studio-v4.0.4-gate-v11-release-consistency"


# --- Source-backed normalization -------------------------------------------------
def _timebox_v404(bp, profile, bundle):
    # Use the unwrapped base 90-minute timebox captured by v4.0.3, then apply the
    # complete v4.0.4 source-safe normalization exactly once.
    bp = legacy._original_timebox(bp, profile, bundle)
    try:
        source_text = bundle.combined_local_text()
    except Exception:
        source_text = ""
    return normalize_source_backed_v404(bp, source_text=source_text, profile=profile)


# --- Audit/deterministic consistency --------------------------------------------
_original_audit = GeminiService.audit


def _audit_v404(self, bundle, blueprint, deterministic_failures=None):
    failures = list(deterministic_failures or [])
    report = _original_audit(self, bundle, blueprint, failures)
    if not failures:
        return report

    # A semantic reviewer may judge the content sound while deterministic
    # invariants still fail. RELEASE requires both; therefore the audit summary
    # must not visually claim an overall PASS when hard deterministic gates fail.
    report.overall_pass = False

    low = " ".join(failures).lower()
    if any(x in low for x in ["source", "anchor", "primary", "topic_coverage", "technical_anchors"]):
        report.source_fidelity_pass = False
    if any(x in low for x in ["unit5", "unit8", "unit9", "unit10", "one_non_composite", "bounded_assurance", "first_taught"]):
        report.engineering_rigor_pass = False
    if any(x in low for x in ["unit2", "unit3", "unit4", "unit11", "unit12", "unit13", "unit14", "unit15", "unit16", "unit18", "unit19", "unit20", "phase", "coverage_"]):
        report.cumulative_fidelity_pass = False
    if any(x in low for x in ["readiness", "etec"]):
        report.readiness_alignment_pass = False
    if any(x in low for x in ["provenance", "enrichment", "pedagogy", "unsourced", "channel"]):
        report.provenance_separation_pass = False

    failed_text = ", ".join(failures[:24])
    report.issues.append(AuditIssue(
        severity="major",
        unit_numbers=[],
        requirement="Deterministic release invariants",
        problem="Semantic review cannot override unresolved deterministic gates: " + failed_text,
        repair_instruction=(
            "Repair the named structural/provenance/readiness invariants while preserving P1 technical content; "
            "then rerun both deterministic and semantic audit before RELEASE."
        ),
    ))
    return report


# Activate v4.0.4 runtime behavior before any new compile request.
engine.deterministic_gate = gate_v11
engine.apply_90_minute_timebox = _timebox_v404
legacy.normalize_output_lab_v38 = normalize_output_lab_v404
GeminiService.audit = _audit_v404


def _health_v404():
    data = legacy._original_health()
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v11-release-consistency-on-v10-v9-fidelity",
        "faculty_experience": "v4.0.4-approved-saudi-heritage",
        "visual_output": "visual-lecture-engine-v2-source-aware-pdf-first",
        "source_visual_policy": "explicit-anchor-first-local-pdf-then-best-effort-public-then-redraw",
        "local_pre_gate_normalizer": True,
        "normalizer": "v4.0.4-source-safe-release-normalizer",
        "audit_deterministic_consistency": True,
        "session_minutes": 90,
        "full_primary_coverage": True,
        "primary_topic_deferral_allowed": False,
        "capacity_retry_attempts_per_model": 3,
        "capacity_failover": True,
        "no_blueprint_exports": "hidden",
        "no_blueprint_gate_state": "NOT RUN",
        "visual_lecture_engine": "v2",
        "source_library_verified": True,
        "verified_source_count": 8,
        "release_contract": "semantic audit PASS AND every deterministic gate PASS",
        "release_repairs": [
            "authoritative P1 Domain Spine map",
            "explicit [P1] technical anchors",
            "reserved-unit pedagogy/core channel separation",
            "source-safe noncore technology handling",
            "minimum-sufficient ETEC target visibility",
            "single opening ill-structured central system",
        ],
    })
    return data


engine.health = _health_v404


# Replace only the two public version-bearing routes; all compile/output routes
# remain the same tested FastAPI endpoints.
app.router.routes[:] = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {"/", "/api/health"}
]


@app.get("/")
def faculty_studio_v404():
    response = legacy.final_faculty_studio()
    body = bytes(response.body).decode("utf-8")
    body = body.replace("4.0.3", "4.0.4")
    body = body.replace("v403", "v404")
    body = body.replace(
        "Capacity-Safe Visual Lecture Engine v2",
        "Gate v11 · Visual Lecture Engine v2",
    )
    return HTMLResponse(body, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-ISCARB-Version": PUBLIC_VERSION,
    })


@app.get("/api/health")
def health_v404():
    data = legacy.public_health()
    data.update(_health_v404())
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v11-release-consistency-on-v10-v9-fidelity",
        "audit_deterministic_consistency": True,
    })
    return data
