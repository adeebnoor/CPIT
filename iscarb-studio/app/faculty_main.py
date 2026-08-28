from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse

from . import main as engine
from .models import Blueprint, JobState, AuditReport, AuditIssue
from .faculty_visual import export_faculty_presenter_pptx, render_faculty_presenter_preview
from .faculty_outputs import export_detailed_pdf, export_instructor_guide, export_student_pack
from .presenter_pdf import export_presenter_pdf

FACULTY_VERSION = "3.6.0"
PIPELINE_ID = "faculty-studio-v3.6-saudi-heritage-visual-provenance"

app = FastAPI(title="ISCARB Faculty Studio", version=FACULTY_VERSION)

# Reuse engine routes while replacing public experience and output routes.
for route in engine.app.router.routes:
    path = getattr(route, "path", None)
    if path in {"/", "/api/health", "/api/jobs/{job_id}/presenter", "/api/jobs/{job_id}/export/{fmt}"}:
        continue
    app.router.routes.append(route)


@app.get("/")
def faculty_studio():
    html = (engine.APP_ROOT / "static" / "studio_v36.html").read_text(encoding="utf-8")
    return HTMLResponse(
        html,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-ISCARB-Version": FACULTY_VERSION,
        },
    )


@app.get("/starter-kit")
def starter_kit():
    html = (engine.APP_ROOT / "static" / "faculty_starter_kit.html").read_text(encoding="utf-8")
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@app.get("/api/health")
def health():
    data = engine.health()
    data.update(
        {
            "version": FACULTY_VERSION,
            "engine_version": engine.SERVICE_VERSION,
            "pipeline": PIPELINE_ID,
            "public_experience": "Saudi heritage academic identity + original source library + output lab + visual provenance",
            "ready_example_source": "https://www.slideshare.net/slideshow/ch14-5148075/5148075",
            "design_language": "Saudi educational heritage — dark academic canvas, sand, magenta, cyan, green and gold; no copied institutional logos",
            "presenter_theme": "visual-first 20-unit presenter with source/visual provenance",
            "output_system": [
                "Visual Presenter Preview + PPTX + Presenter PDF",
                "Faculty Reading Pack PDF",
                "Instructor Guide DOCX",
                "Student Activity Pack DOCX",
                "Blueprint JSON",
            ],
            "local_output_lab": True,
            "visual_provenance": "source-anchored / adapted from P1 / ISCARB visualization",
            "institutional_branding": "context only; no claim of official endorsement",
        }
    )
    return data


@app.post("/api/render-blueprint")
async def render_blueprint(blueprint_file: UploadFile = File(...)):
    """Import a previously generated Blueprint and re-render outputs locally.

    This route intentionally does not call Gemini and can never issue RELEASE or
    ISCARB Verified because source/semantic audits are not repeated.
    """
    if not (blueprint_file.filename or "").lower().endswith(".json"):
        raise HTTPException(400, "Choose an ISCARB Blueprint JSON file.")
    raw = await blueprint_file.read()
    try:
        bp = Blueprint.model_validate_json(raw)
    except Exception as exc:
        raise HTTPException(400, f"Invalid ISCARB Blueprint JSON: {exc}") from exc

    job_id = uuid.uuid4().hex
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
            requirement="Imported Blueprint — audit not repeated",
            problem="Outputs were rendered locally from an existing Blueprint. Source and semantic release audits were not re-run.",
            repair_instruction="Use the original compiled RELEASE job, or re-run the full compiler when audit authority is required.",
        )],
        strengths=["No Gemini call is required to iterate on Visual Presenter, Reading Pack, Instructor, Student, or Blueprint outputs."],
    )
    job = JobState(
        id=job_id,
        status="blocked",
        progress=100,
        message="OUTPUT LAB — Blueprint imported locally. All outputs are available; ISCARB Verified remains disabled because release audit was not repeated.",
        filename=blueprint_file.filename or "imported_blueprint.json",
        model="local-render-only",
        source_manifest=list(bp.source_manifest),
        blueprint=bp,
        audit=audit,
        deterministic_checks={},
    )
    engine.save_job(job)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}/presenter")
def faculty_presenter(job_id: str):
    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    return HTMLResponse(
        render_faculty_presenter_preview(job.blueprint, job.status.upper()),
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@app.get("/api/jobs/{job_id}/export/{fmt}")
def faculty_export(job_id: str, fmt: str):
    fmt = fmt.lower()
    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    if job.status not in {"ready", "blocked", "error"}:
        raise HTTPException(409, "Compilation is still in progress")

    bp = job.blueprint
    base = engine.EXPORTS / f"ISCARB_{job_id}"

    if fmt == "pptx":
        path = export_faculty_presenter_pptx(bp, base.with_name(base.name + "_Visual_Presenter.pptx"))
        media = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif fmt in {"presenter-pdf", "presenter_pdf", "visual-pdf"}:
        path = export_presenter_pdf(bp, base.with_name(base.name + "_Visual_Presenter.pdf"))
        media = "application/pdf"
    elif fmt == "pdf":
        path = export_detailed_pdf(bp, base.with_name(base.name + "_Faculty_Reading_Pack.pdf"))
        media = "application/pdf"
    elif fmt == "docx":
        path = export_instructor_guide(bp, base.with_name(base.name + "_Instructor_Guide.docx"))
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt in {"student", "student-docx", "activity"}:
        path = export_student_pack(bp, base.with_name(base.name + "_Student_Activity_Pack.docx"))
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "json":
        path = base.with_name(base.name + "_Blueprint.json")
        path.write_text(bp.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
        media = "application/json"
    else:
        raise HTTPException(400, "Format must be pptx, presenter-pdf, pdf, docx, student, or json")

    return FileResponse(path, media_type=media, filename=path.name)
