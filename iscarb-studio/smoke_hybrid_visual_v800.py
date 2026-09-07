import os
from pathlib import Path

import run  # installs production patch chain
from app import start_v440 as base
from app import source_visuals as sv
from app import patch_v732_native_figures_cues as figures
from app import patch_v737_instructional_director as director
from app.hybrid_visual_engine import classify_visual, _numeric_scale_present
from app.visual_prompt_v800 import VISUAL_PROMPT_ADDENDUM

assert os.getenv("ISCARB_BUILD_ID") == "8.0.0-hybrid-visual-narrative", os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("build_id") == "8.0.0-hybrid-visual-narrative", health
assert health.get("hybrid_visual_narrative_version") == "8.0.0", health
assert "mandatory learner annotation" in health.get("hybrid_visual_policy", ""), health
assert "50/50" in health.get("hybrid_visual_layout", ""), health
assert health.get("learning_autosave_seconds") == 5, health
assert director.VERSION == "8.0.0", director.VERSION
assert {8, 11, 18}.issubset(figures.FIGURE_UNITS), figures.FIGURE_UNITS

graph = sv.VisualAsset(
    slide_number=15,
    alt_text="Cost/dependability curve Low Medium High Very-high Ultra-high Dependability Cost",
    source_kind="local-pdf",
)
assert classify_visual(graph) == "graph"
assert _numeric_scale_present(graph.alt_text) is False

table = sv.VisualAsset(
    slide_number=34,
    alt_text="Attributes of dependable processes Process characteristic Description Auditable Diverse Documentable Robust Standardized",
    source_kind="local-pdf",
)
assert classify_visual(table) == "table"

diagram = sv.VisualAsset(
    slide_number=19,
    alt_text="The sociotechnical systems stack Society Organization Business processes Application system Communications Operating system Equipment",
    source_kind="local-pdf",
)
assert classify_visual(diagram) == "diagram"

paths = {getattr(route, "path", "") for route in run.app.router.routes}
for path in (
    "/api/learning/{job_id}/hybrid-visuals",
    "/api/learning/{job_id}/hybrid-visual/{key}",
    "/api/learning/{job_id}/visual-annotation",
):
    assert path in paths, path

static = Path(__file__).parent / "app" / "static"
js = (static / "learning_v800.js").read_text(encoding="utf-8")
css = (static / "learning_v800.css").read_text(encoding="utf-8")
for needle in ("hybrid-visuals", "visual-annotation", "visualPin", "Zoom to read", "VISUAL EVIDENCE", "flushPending"):
    assert needle in js, needle
for needle in ("hybridVisualGrid", "grid-template-columns", "visualLightbox", "sourceWatermark", "visualAnnotationGate"):
    assert needle in css, needle
for needle in ("evidence, not decoration", "Never call a redraw a P1 figure", "3–5 critical source visuals"):
    assert needle in VISUAL_PROMPT_ADDENDUM, needle

print("PASS: v8.0 Hybrid Visual-Narrative Engine classification, mapping surface, 50/50 UI, zoom, annotation evidence, source provenance, prompt policy")