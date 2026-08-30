from __future__ import annotations

"""ISCARB Faculty Studio v4.3.0 — CIMT-native Presenter release candidate.

v4.3 keeps the tested v4.2 source/generation pipeline but replaces the
learner-facing Presenter with the visual language of the archived CIMT lecture
collection: white canvas, large green serif headings, gold rules, source-native
figures, readable diagrams, and no dashboard-style visual chrome.
"""

import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from . import start_v410 as prev
from .gate_v14 import deterministic_gate as gate_v14
from .cimt_native_v43 import (
    export_cimt_presenter_pptx_v43,
    export_cimt_presenter_pdf_v43,
    render_cimt_presenter_preview_v43,
)
from .cimt_presenter_copy_v431 import install_presenter_copy_v431
from .faculty_outputs import export_detailed_pdf, export_instructor_guide, export_student_pack

engine = prev.engine
app = prev.app

PUBLIC_VERSION = "4.3.0"
PIPELINE_ID = "faculty-studio-v4.3.0-cimt-native-presenter-gate-v14"
CIMT_REFERENCE_ARCHIVE = "https://adeebnoor.github.io/CPIT/cimt.html"

# Generation, source lock, normalization, semantic audit and timebox stay on
# the tested v4.2 path. Gate v14 adds provenance/presenter safety sentinels.
engine.deterministic_gate = gate_v14

# Keep the detailed Blueprint intact for audit/export, but let the learner deck
# prefer concise source-safe visual annotations over verbose metadata prose.
install_presenter_copy_v431()


def _deployed_build() -> dict[str, str]:
    """Identify the code actually serving this request.

    PUBLIC_VERSION is pinned in render.yaml, so it stays 4.3.0 across every
    commit and cannot tell a fresh deploy from a stale one. Two live validation
    runs were read as evidence about changes that had not deployed yet before
    this was added. Render injects the deployed commit; locally there is none,
    and saying so is better than implying a deploy.
    """
    commit = (os.getenv("RENDER_GIT_COMMIT") or "").strip()
    return {
        "build_commit": commit[:12] if commit else "unknown-not-a-render-deploy",
        "build_branch": (os.getenv("RENDER_GIT_BRANCH") or "").strip() or "unknown",
    }


def _health_v430():
    data = prev._health_v420()
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        **_deployed_build(),
        "deterministic_gate": "v14-provenance-presenter-on-v13",
        "presenter_renderer": "cimt-native-v4.3-preview-pptx-pdf",
        "presenter_visual_contract": "white canvas + green serif hierarchy + gold corner rules + selective red emphasis + large source visuals + readable diagrams",
        "presenter_text_contract": "semantic shortening without visible ellipsis + curated source-safe visual annotations",
        "presenter_copy_source": "visual_plan.annotation_plan with provenance-safe fallback",
        "source_visual_contract": "information-bearing P1 visuals occupy the main teaching canvas; low-information title slides redraw locally",
        "cimt_reference_archive": CIMT_REFERENCE_ARCHIVE,
        "cross_discipline_visual_residue_guard": True,
        "presenter_exact_units": 20,
        "session_minutes": 90,
        "visual_lecture_engine": "CIMT+ v4.3",
        "hero_delivery": "css-native-no-asset",
        "hero_static_dependency": False,
        "public_experience": "CIMT+ computing Faculty Studio with source-backed compile, Gate v14, Output Lab, six export surfaces, and visual provenance",
        "design_language": "CIMT-native Saudi academic computing interface with CSS-native hero card and no external hero asset dependency",
        "release_contract": "semantic audit PASS AND every Gate v14 deterministic check PASS",
    })
    return data


engine.health = _health_v430

# Replace public routes that carry visual output/version semantics. All tested
# compile/job/local-repair/starter-kit routes remain mounted from v4.2.
app.router.routes[:] = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {
        "/", "/api/health", "/api/jobs/{job_id}/presenter", "/api/jobs/{job_id}/export/{fmt}"
    }
]


@app.get("/")
def faculty_studio_v430():
    path = Path(__file__).with_name("static") / "index_v410.html"
    body = path.read_text(encoding="utf-8")
    body = body.replace("v4.1.0 · Gate v12", "v4.3.0 · Gate v14")
    body = body.replace("v4.2.0 · Gate v13", "v4.3.0 · Gate v14")
    body = body.replace("v4.1.0", "v4.3.0").replace("v4.2.0", "v4.3.0")
    identity_css = '<link rel="stylesheet" href="/static/kau_identity_v410.css?v=4.3.0-kau">'
    native_css = '''<style id="cimt-native-v43-ui">
      .cimtNativeFlag{position:fixed;right:18px;bottom:18px;z-index:40;background:#fff;color:#055934;border:1px solid #86c242;border-radius:999px;padding:7px 11px;font:800 10px/1.2 Arial,sans-serif;box-shadow:0 8px 24px #0a353e18;text-decoration:none}
      .cimtNativeFlag:hover{transform:translateY(-1px);box-shadow:0 11px 28px #0a353e22}
    </style>'''
    identity_note = (
        '<div class="kauIdentityNote"><b>Visual identity:</b> Faculty Studio interface follows the selected Saudi academic palette. '
        'Learner-facing Presenter output uses the archived CIMT lecture visual grammar. ISCARB remains the project identity; '
        'this interface does not by itself constitute an official institutional endorsement.</div>'
    )
    native_flag = (
        f'<a class="cimtNativeFlag" href="{CIMT_REFERENCE_ARCHIVE}" target="_blank" rel="noopener noreferrer" '
        'title="Open the original CPIT-455 CIMT lecture archive used as the visual reference">'
        'CIMT archive ↗ · Presenter v4.3</a>'
    )
    body = body.replace("</head>", identity_css + native_css + "\n</head>")
    body = body.replace("</body>", identity_note + native_flag + "\n</body>")
    return HTMLResponse(body, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-ISCARB-Version": PUBLIC_VERSION,
    })


@app.get("/api/health")
def health_v430():
    data = prev.health_v420()
    data.update(_health_v430())
    return data


@app.get("/api/jobs/{job_id}/presenter")
def presenter_v430(job_id: str):
    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    return HTMLResponse(
        render_cimt_presenter_preview_v43(job.blueprint, job.status.upper()),
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@app.get("/api/jobs/{job_id}/export/{fmt}")
def export_v430(job_id: str, fmt: str):
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
        path = export_cimt_presenter_pptx_v43(bp, base.with_name(base.name + "_Visual_Presenter.pptx"))
        media = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif fmt in {"presenter-pdf", "presenter_pdf", "visual-pdf"}:
        path = export_cimt_presenter_pdf_v43(bp, base.with_name(base.name + "_Visual_Presenter.pdf"))
        media = "application/pdf"
    elif fmt == "pdf":
        path = export_detailed_pdf(bp, base.with_name(base.name + "_Faculty_Reading_Pack.pdf")); media = "application/pdf"
    elif fmt == "docx":
        path = export_instructor_guide(bp, base.with_name(base.name + "_Instructor_Guide.docx")); media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt in {"student", "student-docx", "activity"}:
        path = export_student_pack(bp, base.with_name(base.name + "_Student_Activity_Pack.docx")); media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "json":
        path = base.with_name(base.name + "_Blueprint.json")
        path.write_text(bp.model_dump_json(by_alias=True, indent=2), encoding="utf-8"); media = "application/json"
    else:
        raise HTTPException(400, "Format must be pptx, presenter-pdf, pdf, docx, student, or json")
    return FileResponse(path, media_type=media, filename=path.name)
