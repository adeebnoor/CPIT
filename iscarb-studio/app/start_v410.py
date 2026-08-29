from __future__ import annotations

"""ISCARB Faculty Studio v4.1.0 — CIMT+ Computing Lecture Engine.

Release goals:
- Preserve v4.0.4 release consistency, provenance and ETEC discipline.
- Add atomic chapter/source coverage across computing disciplines.
- Add source-native computing knowledge typing and adaptive visual grammar.
- Drive the actual browser Presenter and PPTX with that adaptive grammar.
- Keep exactly 20 Units / 90 minutes / five CLOs.
"""

from pathlib import Path
from fastapi.responses import HTMLResponse

from . import start_v404 as prev
from .gate_v12 import deterministic_gate as gate_v12
from .cimt_plus import normalize_cimt_plus
from . import faculty_visual as faculty_visual
from .cimt_render import cimt_visual_html, export_cimt_presenter_pptx

engine = prev.engine
app = prev.app

PUBLIC_VERSION = "4.1.0"
PIPELINE_ID = "faculty-studio-v4.1.0-cimt-plus-computing-coverage"


def _timebox_v410(bp, profile, bundle):
    bp = prev._timebox_v404(bp, profile, bundle)
    return normalize_cimt_plus(bp, profile)


# Activate computing-wide runtime before any new compile request.
engine.deterministic_gate = gate_v12
engine.apply_90_minute_timebox = _timebox_v410

# The Presenter must embody the plan, not merely store it in JSON.
_original_visual_html = faculty_visual._visual_html
faculty_visual._visual_html = lambda bp, unit: cimt_visual_html(bp, unit, _original_visual_html)
faculty_visual.ve.export_presenter_pptx = export_cimt_presenter_pptx


def _health_v410():
    data = prev._health_v404()
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v12-cimt-plus-computing-coverage-on-v11",
        "faculty_experience": "cimt-plus-computing-studio",
        "visual_output": "cimt-plus-source-native-visual-grammar-live-preview-and-pptx",
        "computing_scope": [
            "computer science", "information technology", "software engineering",
            "information systems", "cybersecurity", "AI/ML", "data science",
            "databases", "operating systems", "computer networks", "distributed systems",
            "cloud computing", "algorithms", "programming", "web/mobile", "HCI",
            "dependability", "reliability", "safety", "security", "resilience",
        ],
        "knowledge_types": [
            "CONCEPT", "ALGORITHM", "CODE", "ARCHITECTURE", "EQUATION", "PROTOCOL",
            "PROCESS", "DATA_MODEL", "SYSTEM_BEHAVIOR", "DESIGN_PRINCIPLE", "TRADE_OFF",
            "EMPIRICAL_RESULT", "EXAMPLE", "OTHER",
        ],
        "coverage_contract": "every major P1 coverage item appears in coverage_ledger and is first taught by Unit 15",
        "visual_contract": "one dominant visual per Unit; representation adapts to computing knowledge type",
        "source_visual_policy": "USE/ADAPT/REDRAW/NEW with no unverifiable source-visual claims",
        "session_minutes": 90,
        "full_primary_coverage": True,
        "primary_topic_deferral_allowed": False,
        "visual_lecture_engine": "CIMT+",
        "presenter_renderer": "source-native-v4.1-preview-and-pptx",
        "release_contract": "semantic audit PASS AND every v12 deterministic gate PASS",
    })
    return data


engine.health = _health_v410

# Replace public root + health routes only.
app.router.routes[:] = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {"/", "/api/health"}
]


@app.get("/")
def faculty_studio_v410():
    path = Path(__file__).with_name("static") / "index_v410.html"
    body = path.read_text(encoding="utf-8")
    return HTMLResponse(body, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-ISCARB-Version": PUBLIC_VERSION,
    })


@app.get("/api/health")
def health_v410():
    data = prev.health_v404()
    data.update(_health_v410())
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v12-cimt-plus-computing-coverage-on-v11",
    })
    return data
