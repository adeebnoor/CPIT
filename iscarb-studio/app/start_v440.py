from __future__ import annotations

"""ISCARB Faculty Studio v4.4.0 - executable grammar and source-detail release."""

from fastapi import HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pathlib import Path

from . import start_v430 as prev
from .gate_v15 import deterministic_gate as gate_v15
from .presenter_v44 import export_presenter_pdf, export_presenter_pptx, render_presenter_preview
from .presenter_v44 import PresenterLayoutError
from .storage import UPLOADS, JOB_MISSING_MESSAGE

engine = prev.engine
app = prev.app


async def _layout_rejected(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc), "code": "presenter_layout_requires_repair"})


app.add_exception_handler(PresenterLayoutError, _layout_rejected)

PUBLIC_VERSION = "4.5.3"
PIPELINE_ID = "faculty-studio-v4.5.3-single-source-passages"

# Gate v15 is the active compiler release gate. Presenter rendering remains on
# the CIMT-native surface, now hardened for exact source-page selection and
# atomic source-detail retention.
engine.deterministic_gate = gate_v15


def _health_v440():
    data = prev._health_v430()
    data.update({
        "version": PUBLIC_VERSION,
        "model_request_timeout_seconds": 150,
        "model_job_budget_seconds": 600,
        "source_only_mode": True,
        "draft_downloads_during_audit": True,
        "generation_batch_size": 4,
        "targeted_unit_repair": True,
        "coverage_evidence_required": True,
        "presenter_overflow_preflight": True,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v15-executable-unit-grammar-on-v14",
        "presenter_renderer": "cimt-native-v4.4-source-detail-preserving",
        "presenter_text_contract": "atomic source statements; 35-80 visible technical words or an information-bearing source visual",
        "source_visual_contract": "explicit PAGE/SLIDE coordinates only; cover-slide reuse is forbidden; multi-page anchors are preserved",
        "unit_grammar_contract": "twenty learner-visible cognitive jobs, each independently gate-checked",
        "hollow_draft_policy": "unresolved grammar/density drafts are replaced by the source-complete review draft",
        "release_contract": "semantic audit PASS AND every Gate v15 deterministic check PASS",
        "public_experience": "ISCARB Faculty Studio v4.4 with executable 20-unit grammar, chapter completeness proof, and coverage-visible Output Lab",
    })
    return data


engine.health = _health_v440

app.router.routes[:] = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {"/", "/api/health", "/api/jobs/{job_id}/presenter", "/api/jobs/{job_id}/export/{fmt}"}
]


@app.get("/")
def faculty_studio_v440():
    body = (Path(__file__).with_name("static") / "index_v440.html").read_text(encoding="utf-8")
    return HTMLResponse(body, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-ISCARB-Version": PUBLIC_VERSION,
    })


@app.get("/api/health")
def health_v440():
    data = prev.health_v430()
    data.update(_health_v440())
    return data


def _presenter_job(job_id):
    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, JOB_MISSING_MESSAGE)
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    return job


@app.get("/api/jobs/{job_id}/presenter")
def presenter_v440(job_id: str):
    job = _presenter_job(job_id)
    return HTMLResponse(render_presenter_preview(job.blueprint, job.status.upper(), source_root=UPLOADS / job_id),
                        headers={"Cache-Control": "no-store"})


@app.get("/api/jobs/{job_id}/export/{fmt}")
def export_v440(job_id: str, fmt: str):
    fmt = fmt.lower()
    if fmt == "source-pdf":
        from .source_visuals import _find_local_primary_pdf
        _presenter_job(job_id)
        source = _find_local_primary_pdf(UPLOADS / job_id)
        if source is None:
            raise HTTPException(404, "This job has no original PDF. Use the original uploaded document.")
        return FileResponse(source, media_type="application/pdf", filename=f"ISCARB_{job_id}_Original_Source.pdf")
    if fmt not in {"pptx", "presenter-pdf", "presenter_pdf", "visual-pdf"}:
        return prev.export_v430(job_id, fmt)
    job = _presenter_job(job_id)
    # Snapshots during audit are explicitly marked REVIEW DRAFT, never READY.
    engine.EXPORTS.mkdir(parents=True, exist_ok=True)
    suffix = "pptx" if fmt == "pptx" else "pdf"
    import uuid
    from starlette.background import BackgroundTask
    path = engine.EXPORTS / f"ISCARB_{job_id}_{uuid.uuid4().hex}_Visual_Presenter.{suffix}"
    exporter = export_presenter_pptx if suffix == "pptx" else export_presenter_pdf
    exporter(job.blueprint, path, source_root=UPLOADS / job_id, release_state=job.status)
    media = "application/vnd.openxmlformats-officedocument.presentationml.presentation" if suffix == "pptx" else "application/pdf"
    return FileResponse(path, media_type=media, filename=f"ISCARB_{job_id}_Visual_Presenter.{suffix}",
                        background=BackgroundTask(path.unlink, missing_ok=True))
