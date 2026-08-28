from __future__ import annotations

"""ISCARB process bootstrap for Faculty Studio v4.0.2.

Gate v9 remains the source-backed release gate. Output Lab stays in REVIEW MODE
and never manufactures source-dependent PASS/FAIL results without the original
P1 bundle. v4.0.2 also serves the approved heritage hero inline so the homepage
cannot lose its main visual because of static-file routing or cache behavior.
"""

import uuid

from fastapi import HTTPException
from fastapi.responses import HTMLResponse

from . import main as engine
from .gate_v9 import deterministic_gate as gate_v9
from .normalizer_v38 import normalize_source_backed_v38, normalize_output_lab_v38
from .models import AuditIssue, AuditReport, JobState

PUBLIC_VERSION = "4.0.2"
PIPELINE_ID = "faculty-studio-v4.0.2-inline-hero-navigation-complete"

_original_timebox = engine.apply_90_minute_timebox
_original_health = engine.health


def _timebox_v40(bp, profile, bundle):
    bp = _original_timebox(bp, profile, bundle)
    try:
        source_text = bundle.combined_local_text()
    except Exception:
        source_text = ""
    return normalize_source_backed_v38(bp, source_text=source_text, profile=profile)


def _health_v40():
    data = _original_health()
    data.update({
        "deterministic_gate": "v9-claim-level-fidelity",
        "faculty_experience": "v4.0.2-approved-heritage-inline-hero",
        "visual_output": "visual-first-presenter-with-provenance",
        "local_pre_gate_normalizer": True,
        "local_gate_repair": True,
        "output_lab_audit_mode": "review-mode-not-reaudited-no-false-fails",
        "local_normalizer_scope": [
            "Unit 3 exactly five CLOs in pedagogy channel",
            "hypothetical enrichment bounded as scenario assumptions",
            "IDR-7 progression metadata",
            "EER-7 estimate-before-precision scaffold",
            "enrichment-state consistency",
            "visible Unit 5 first-principles scaffold",
            "Unit 10 information ledger",
            "Unit 20 bounded assurance",
            "unsourced precision labeled synthetic",
            "human-factors provenance",
            "readiness orientation references",
        ],
    })
    return data


engine.deterministic_gate = gate_v9
engine.apply_90_minute_timebox = _timebox_v40
engine.health = _health_v40

from . import faculty_main as faculty  # noqa: E402

app = faculty.app

# Remove the public routes supplied by faculty_main so this bootstrap can serve
# the fully self-contained final homepage and a version-consistent health route.
app.router.routes[:] = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in {"/", "/api/health"}
]

ABOUT_HTML = """
<section id="about" class="aboutStrip">
  <div>
    <span class="aboutKicker">ABOUT ISCARB</span>
    <h2>Source fidelity. Engineering judgment. Evidence. Cultural alignment.</h2>
    <p>ISCARB upgrades how a university lecture is taught without replacing the technical authority of its primary source. The public Faculty Studio is an academic teaching tool; institutional names and national frameworks are used only as contextual or readiness references and do not imply endorsement.</p>
  </div>
  <div class="aboutActions">
    <a href="/starter-kit">Open Faculty Starter Kit →</a>
    <a href="#sources">Browse original lecture sources →</a>
  </div>
</section>
"""

FINAL_CSS = """
<style id="iscarb-v402-final-css">
.hero{grid-template-columns:44% 56%;height:400px}
.heroVisual{min-height:400px;background-position:center center!important;background-size:cover!important;background-repeat:no-repeat!important}
.aboutStrip{display:grid;grid-template-columns:1.5fr .7fr;gap:28px;padding:30px 54px 34px;border-top:1px solid #65452b;border-bottom:1px solid #65452b;background:linear-gradient(90deg,#0a0706,#17100c 54%,#090706);align-items:center}
.aboutKicker{font-size:.58rem;letter-spacing:.18em;color:#47cbd1;font-weight:900}.aboutStrip h2{margin:7px 0 8px;font-size:1.2rem;color:#f4eadf}.aboutStrip p{margin:0;color:#b8aa9d;font-size:.67rem;line-height:1.55;max-width:900px}.aboutActions{display:grid;gap:9px}.aboutActions a{display:block;text-decoration:none;border:1px solid #60452f;border-radius:6px;padding:10px 12px;color:#e9dccd;font-size:.62rem;font-weight:900;background:#100c09}.aboutActions a:first-child{border-color:#47cbd1;color:#47cbd1}
@media(max-width:1100px){.hero{grid-template-columns:1fr;height:auto}.heroVisual{height:300px;min-height:300px;background-position:center!important}.aboutStrip{grid-template-columns:1fr;padding:24px 20px}}
</style>
"""

FINAL_JS = """
<script id="iscarb-v402-final-js">
document.addEventListener('DOMContentLoaded',()=>{
  const sources=document.querySelector('.libraryBox');
  if(sources) sources.id='sources';
  document.querySelectorAll('a').forEach(a=>{
    const text=(a.textContent||'').trim().toLowerCase();
    if(text==='home') a.href='#home';
    else if(text.includes('source library') || text.includes('explore library')) a.href='#sources';
    else if(text.includes('upgrade my lecture')) a.href='#upgrade';
    else if(text==='outputs') a.href='#outputs';
    else if(text==='guides') a.href='/starter-kit';
    else if(text==='about') a.href='#about';
  });
  const version=document.querySelector('.version');
  if(version) version.textContent='v4.0.2 · Complete Hero + Link QA';
});
</script>
"""


@app.get("/")
def final_faculty_studio():
    html = (engine.APP_ROOT / "static" / "studio_v40.html").read_text(encoding="utf-8")
    hero_css = (engine.APP_ROOT / "static" / "hero_override_v401.css").read_text(encoding="utf-8")

    # Deliver the hero CSS inline. This avoids the static-route failure that left
    # the production hero visually blank in v4.0.1.
    html = html.replace("</head>", f"<style id=\"iscarb-approved-hero-inline\">{hero_css}</style>\n{FINAL_CSS}\n</head>")

    # Keep the verified source-library behavior, then apply final navigation and
    # About-section fixes after it so #sources remains the single canonical ID.
    html = html.replace('href="#sources"', 'href="#sources"')
    html = html.replace('<div class="footer">', ABOUT_HTML + '\n<div class="footer">')
    html = html.replace("</body>", faculty.SOURCE_LIBRARY_PATCH + "\n" + FINAL_JS + "\n</body>")

    return HTMLResponse(html, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-ISCARB-Version": PUBLIC_VERSION,
    })


@app.get("/api/health")
def public_health():
    data = faculty.health()
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "hero_delivery": "inline-data-uri",
        "hero_static_dependency": False,
        "navigation_qa": ["home", "sources", "upgrade", "outputs", "guides", "about"],
        "verified_source_count": 8,
        "source_library_verified": True,
    })
    return data


@app.post("/api/jobs/{job_id}/local-repair")
def local_gate_repair(job_id: str):
    """Apply source-independent Blueprint repairs without Gemini.

    This endpoint is deliberately NOT a release audit. Imported Blueprint JSON
    does not contain the raw P1 source text required for source fidelity and
    source-dependent ETEC validation. The UI therefore reports NOT RE-AUDITED.
    """
    try:
        old = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if old.blueprint is None:
        raise HTTPException(409, "No Blueprint is available to repair")

    repaired = normalize_output_lab_v38(old.blueprint)

    new_id = uuid.uuid4().hex
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
            requirement="Output Lab — release audit not repeated",
            problem=(
                "Presentation-safe structural repairs were applied with 0 Gemini calls. Source fidelity, source-dependent "
                "ETEC checks, semantic engineering audit, and release authority were not re-evaluated because P1 is absent."
            ),
            repair_instruction=(
                "Use the repaired outputs for design/faculty review. Run Analyze Source with the original lecture source "
                "when ISCARB Verified release authority is required."
            ),
        )],
        strengths=[
            "Unit 3 CLO channel repaired locally.",
            "Hypothetical enrichment framing repaired locally.",
            "IDR-7/EER-7 pedagogy metadata and estimation scaffold repaired locally.",
            "Visual/document outputs can be iterated with zero model calls.",
        ],
    )
    job = JobState(
        id=new_id,
        status="blocked",
        progress=100,
        message=(
            "OUTPUT LAB REPAIR COMPLETE — presentation-safe v4.0.2 normalization applied with 0 Gemini calls. "
            "Source-dependent gates are NOT RE-AUDITED; full source-backed compile is required for ISCARB Verified."
        ),
        filename=old.filename,
        model="local-output-repair-v4.0.2",
        source_manifest=list(old.source_manifest),
        lecture_focus=old.lecture_focus,
        source_profile=old.source_profile,
        blueprint=repaired,
        audit=audit,
        deterministic_checks={},
        error=None,
    )
    engine.save_job(job)
    return {"job_id": new_id, "audit_state": "not_reaudited"}
