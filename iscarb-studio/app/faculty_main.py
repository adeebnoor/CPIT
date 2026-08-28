from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from . import main as engine
from .faculty_visual import export_faculty_presenter_pptx, render_faculty_presenter_preview

FACULTY_VERSION = "3.3.0"
PIPELINE_ID = "faculty-studio-v3.3-original-identity-source-library"

app = FastAPI(title="ISCARB Faculty Studio", version=FACULTY_VERSION)

# Reuse the proven engine routes and static mount, but replace public landing,
# health, presenter preview and presenter PPTX with the faculty-oriented shell/theme.
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
            "presenter_theme": "deep green + technical purple + warm gold + hexagonal decision geometry",
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
    if fmt != "pptx":
        return engine.export_job(job_id, fmt)

    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    if job.status not in {"ready", "blocked", "error"}:
        raise HTTPException(409, "Compilation is still in progress")

    path = engine.EXPORTS / f"ISCARB_{job_id}_Presenter.pptx"
    path = export_faculty_presenter_pptx(job.blueprint, path)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=path.name,
    )
