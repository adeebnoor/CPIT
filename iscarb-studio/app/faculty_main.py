from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from . import main as engine
from .heritage_pptx import export_cimt_heritage_pptx

FACULTY_VERSION = "3.1.0"
PIPELINE_ID = "faculty-studio-v3.1-clean-source-first-cimt-heritage"

app = FastAPI(title="ISCARB Faculty Studio", version=FACULTY_VERSION)

# Reuse the proven engine routes and static mount, but replace its public landing,
# health endpoint and presenter-PPTX export with the adoption-oriented Faculty Studio shell.
for route in engine.app.router.routes:
    path = getattr(route, "path", None)
    if path in {"/", "/api/health", "/api/jobs/{job_id}/export/{fmt}"}:
        continue
    app.router.routes.append(route)


@app.get("/")
def faculty_studio():
    html = (engine.APP_ROOT / "static" / "studio_v31.html").read_text(encoding="utf-8")
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
            "public_experience": "one-clear-cta + real-source-example + upgrade-my-lecture + verified-output + starter-kit",
            "ready_example_source": "https://www.slideshare.net/slideshow/ch14-5148075/5148075",
            "visual_heritage": "CIMT academic canvas + ISCARB visual grammar",
        }
    )
    return data


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

    path = engine.EXPORTS / f"ISCARB_{job_id}_Presenter_CIMT_Heritage.pptx"
    path = export_cimt_heritage_pptx(job.blueprint, path)
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=path.name,
    )
