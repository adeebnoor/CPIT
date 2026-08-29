from __future__ import annotations

"""ISCARB Faculty Studio v4.2.0 — CIMT+ Computing Lecture Engine.

v4.2 fixes the production defects exposed by the Dependable Systems lecture:
- no security-specific visual residue outside a security lecture,
- source visuals must be information-bearing rather than title-only,
- every one of the 20 Presenter units is rendered from the actual Blueprint,
- generated absolutist language is bounded without rewriting P1 core content,
- unsupported Saudi context is explicitly hypothetical,
- the KAU visual-identity palette remains applied to the public studio.
"""

from pathlib import Path

from fastapi.responses import HTMLResponse
from pptx.dml.color import RGBColor
from reportlab.lib import colors

from . import start_v404 as prev
from .gate_v13 import deterministic_gate as gate_v13
from .cimt_plus import normalize_cimt_plus
from .cimt_sanity_v42 import normalize_cimt_sanity_v42
from . import faculty_visual
from . import presenter_pdf
from . import visual_output_v36
from .cimt_render_v42 import (
    cimt_visual_html_v42,
    export_cimt_presenter_pptx_v42,
    render_presenter_pdf_unit_v42,
)
from .source_visuals_v42 import plans_for_blueprint_v42

engine = prev.engine
app = prev.app

PUBLIC_VERSION = "4.2.0"
PIPELINE_ID = "faculty-studio-v4.2.0-cimt-plus-full-computing-presenter"


def _timebox_v420(bp, profile, bundle):
    bp = prev._timebox_v404(bp, profile, bundle)
    bp = normalize_cimt_plus(bp, profile)
    try:
        source_text = bundle.combined_local_text()
    except Exception:
        source_text = ""
    return normalize_cimt_sanity_v42(bp, source_text=source_text, profile=profile)


# -----------------------------------------------------------------------------
# KAU-derived visual palette for the teaching surface.
# ISCARB remains the project identity; no university-logo endorsement is implied.
# -----------------------------------------------------------------------------
faculty_visual.INK = RGBColor(29, 41, 33)          # neutral Black 3 C
faculty_visual.MUTED = RGBColor(92, 102, 96)       # neutral 417 C
faculty_visual.PAPER = RGBColor(242, 247, 237)     # primary light
faculty_visual.GREEN = RGBColor(5, 89, 52)         # #055934
faculty_visual.GREEN2 = RGBColor(32, 141, 68)      # #208D44
faculty_visual.TEAL = RGBColor(10, 53, 62)         # #0A353E
faculty_visual.PURPLE = RGBColor(10, 53, 62)       # phase distinction via official secondary dark teal
faculty_visual.GOLD = RGBColor(134, 194, 66)       # #86C242
faculty_visual.SOFT_GREEN = RGBColor(211, 230, 190) # #D3E6BE
faculty_visual.SOFT_TEAL = RGBColor(238, 248, 245)  # #EEF8F5
faculty_visual.SOFT_PURPLE = RGBColor(238, 248, 245)
faculty_visual.SOFT_GOLD = RGBColor(242, 247, 237)

presenter_pdf.INK = colors.HexColor('#1D2921')
presenter_pdf.MUTED = colors.HexColor('#5C6660')
presenter_pdf.PAPER = colors.HexColor('#F2F7ED')
presenter_pdf.GREEN = colors.HexColor('#055934')
presenter_pdf.GREEN2 = colors.HexColor('#208D44')
presenter_pdf.TEAL = colors.HexColor('#0A353E')
presenter_pdf.PURPLE = colors.HexColor('#0A353E')
presenter_pdf.GOLD = colors.HexColor('#86C242')
presenter_pdf.SOFT_GREEN = colors.HexColor('#D3E6BE')
presenter_pdf.SOFT_TEAL = colors.HexColor('#EEF8F5')
presenter_pdf.SOFT_PURPLE = colors.HexColor('#EEF8F5')
presenter_pdf.SOFT_GOLD = colors.HexColor('#F2F7ED')
presenter_pdf.PHASE = {
    'IFHAM': presenter_pdf.TEAL,
    'MARIS': presenter_pdf.GREEN2,
    'ATQAN': presenter_pdf.GOLD,
    'MAYYIZ': presenter_pdf.GREEN,
}


# Activate v4.2 runtime before any compile request.
engine.deterministic_gate = gate_v13
engine.apply_90_minute_timebox = _timebox_v420

# All 20 visual jobs now come from the computing-wide renderer.
faculty_visual._visual_html = cimt_visual_html_v42
faculty_visual.ve.export_presenter_pptx = export_cimt_presenter_pptx_v42
presenter_pdf._render = render_presenter_pdf_unit_v42

# Source-aware export layer imported the planner by value; patch that binding too.
visual_output_v36.plans_for_blueprint = plans_for_blueprint_v42


def _health_v420():
    data = prev._health_v404()
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v13-bounded-computing-on-v12-v11",
        "faculty_experience": "cimt-plus-computing-studio-kau-identity",
        "visual_output": "full-20-unit-source-native-cimt-plus-preview-pptx-pdf",
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
        "visual_contract": "all 20 units use lecture-derived labels/content; computing representation adapts to knowledge type",
        "source_visual_policy": "USE only for information-bearing anchored visuals; title-only slides are REDRAW",
        "cross_discipline_visual_residue_guard": True,
        "bounded_generated_language": True,
        "hypothetical_unsourced_saudi_context": True,
        "session_minutes": 90,
        "full_primary_coverage": True,
        "primary_topic_deferral_allowed": False,
        "visual_lecture_engine": "CIMT+ v4.2",
        "presenter_renderer": "full-computing-v4.2-preview-pptx-pdf",
        "release_contract": "semantic audit PASS AND every v13 deterministic gate PASS",
        "interface_identity": "KAU visual identity guide palette + Alexandria hierarchy + line-wave motif; ISCARB project mark retained; no institutional-endorsement claim",
    })
    return data


engine.health = _health_v420

# Replace public root + health only; compile/export endpoints remain the tested ones.
app.router.routes[:] = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {"/", "/api/health"}
]


@app.get("/")
def faculty_studio_v420():
    path = Path(__file__).with_name("static") / "index_v410.html"
    body = path.read_text(encoding="utf-8")
    body = body.replace("v4.1.0 · Gate v12", "v4.2.0 · Gate v13")
    body = body.replace("v4.1.0", "v4.2.0")
    identity_css = '<link rel="stylesheet" href="/static/kau_identity_v410.css?v=4.2.0-kau">'
    identity_note = (
        '<div class="kauIdentityNote"><b>Visual identity:</b> Interface styling follows the '
        'King Abdulaziz University visual-identity guide for palette, typography hierarchy and line-wave motifs. '
        'ISCARB remains the project identity; this interface does not by itself constitute an official institutional endorsement.</div>'
    )
    body = body.replace("</head>", identity_css + "\n</head>")
    body = body.replace("</body>", identity_note + "\n</body>")
    return HTMLResponse(body, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-ISCARB-Version": PUBLIC_VERSION,
    })


@app.get("/api/health")
def health_v420():
    data = prev.health_v404()
    data.update(_health_v420())
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "deterministic_gate": "v13-bounded-computing-on-v12-v11",
    })
    return data
