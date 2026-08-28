from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from . import main as engine
from .faculty_visual import export_faculty_presenter_pptx, render_faculty_presenter_preview
from .faculty_outputs import export_detailed_pdf, export_instructor_guide, export_student_pack

FACULTY_VERSION = "3.4.0"
PIPELINE_ID = "faculty-studio-v3.4-output-v4-original-identity"

app = FastAPI(title="ISCARB Faculty Studio", version=FACULTY_VERSION)

# Reuse the proven engine routes, but replace public landing, health, presenter
# preview and export routes with the faculty-oriented experience/output system.
for route in engine.app.router.routes:
    path = getattr(route, "path", None)
    if path in {"/", "/api/health", "/api/jobs/{job_id}/presenter", "/api/jobs/{job_id}/export/{fmt}"}:
        continue
    app.router.routes.append(route)


@app.get("/")
def faculty_studio():
    html = (engine.APP_ROOT / "static" / "studio_v33.html").read_text(encoding="utf-8")
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
            "public_experience": "original-source-library + upgrade-my-lecture + ISCARB-verified + starter-kit",
            "ready_example_source": "https://www.slideshare.net/slideshow/ch14-5148075/5148075",
            "design_language": "ISCARB Original Identity — Saudi academic engineering; no third-party logos or copied design assets",
            "presenter_theme": "deep green + technical purple + warm gold + visual-first text budget",
            "output_system": [
                "Presenter Preview + PPTX — sparse visual teaching surface",
                "Detailed Deck PDF — source/evidence/readiness reference",
                "Instructor Guide DOCX — 90-minute run of show",
                "Student Activity Pack DOCX — activities without instructor answers",
                "Blueprint JSON — auditable structured source of truth",
            ],
            "institutional_branding": "context links only; no claim of official KAU or Vision 2030 endorsement",
        }
    )
    return data


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
        path = export_faculty_presenter_pptx(bp, base.with_name(base.name + "_Presenter.pptx"))
        media = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif fmt == "pdf":
        path = export_detailed_pdf(bp, base.with_name(base.name + "_Detailed_Deck.pdf"))
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
        raise HTTPException(400, "Format must be pptx, pdf, docx, student, or json")

    return FileResponse(path, media_type=media, filename=path.name)
