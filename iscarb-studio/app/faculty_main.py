from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from . import main as engine

FACULTY_VERSION = "3.0.0"
PIPELINE_ID = "faculty-studio-v3-cimt-heritage-iscarb-verified"

app = FastAPI(title="ISCARB Faculty Studio", version=FACULTY_VERSION)

# Reuse the proven engine routes and static mount, but replace its public landing
# page and health endpoint with the adoption-oriented Faculty Studio shell.
for route in engine.app.router.routes:
    path = getattr(route, "path", None)
    if path in {"/", "/api/health"}:
        continue
    app.router.routes.append(route)


@app.get("/")
def faculty_studio():
    html = (engine.APP_ROOT / "static" / "studio_v3.html").read_text(encoding="utf-8")
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
            "public_experience": "ready-lectures + upgrade-my-lecture + ISCARB-verified + starter-kit + reuse",
            "visual_heritage": "CIMT academic canvas + ISCARB visual grammar",
        }
    )
    return data
