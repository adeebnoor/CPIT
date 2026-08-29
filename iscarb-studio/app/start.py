from __future__ import annotations

"""ISCARB process bootstrap for Faculty Studio v4.0.3.

Gate v9 remains the source-backed release gate. Output Lab stays in REVIEW MODE
and never manufactures source-dependent PASS/FAIL results without the original
P1 bundle. Visual Lecture Engine v2 uses local P1 PDF pages when available and
keeps explicit source-slide anchors authoritative. v4.0.3 also makes transient
Gemini-capacity failures truthful: no Blueprint means gates are NOT RUN and no
export links are exposed.
"""

import uuid

from fastapi import HTTPException
from fastapi.responses import HTMLResponse

from . import main as engine
from .gate_v9 import deterministic_gate as gate_v9
from .normalizer_v38 import normalize_source_backed_v38, normalize_output_lab_v38
from .models import AuditIssue, AuditReport, JobState
from . import source_visual_patch_v2  # noqa: F401  # harden source-slide selection before output modules load

PUBLIC_VERSION = "4.0.3"
PIPELINE_ID = "faculty-studio-v4.0.3-capacity-safe-visual-lecture-engine-v2"

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
        "faculty_experience": "v4.0.3-capacity-safe-approved-heritage-inline-hero",
        "visual_output": "visual-lecture-engine-v2-source-aware-pdf-first",
        "source_visual_policy": "explicit-anchor-first-local-pdf-then-best-effort-public-then-redraw",
        "local_pre_gate_normalizer": True,
        "local_gate_repair": True,
        "output_lab_audit_mode": "review-mode-not-reaudited-no-false-fails",
        "capacity_retry_policy": "3 transient attempts per model with exponential backoff and automatic model failover",
        "no_blueprint_release_semantics": "NOT RUN gates; exports hidden; retry offered",
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
<style id="iscarb-v403-final-css">
.hero{grid-template-columns:44% 56%;height:400px}
.heroVisual{min-height:400px;background-position:center center!important;background-size:cover!important;background-repeat:no-repeat!important}
.aboutStrip{display:grid;grid-template-columns:1.5fr .7fr;gap:28px;padding:30px 54px 34px;border-top:1px solid #65452b;border-bottom:1px solid #65452b;background:linear-gradient(90deg,#0a0706,#17100c 54%,#090706);align-items:center}
.aboutKicker{font-size:.58rem;letter-spacing:.18em;color:#47cbd1;font-weight:900}.aboutStrip h2{margin:7px 0 8px;font-size:1.2rem;color:#f4eadf}.aboutStrip p{margin:0;color:#b8aa9d;font-size:.67rem;line-height:1.55;max-width:900px}.aboutActions{display:grid;gap:9px}.aboutActions a{display:block;text-decoration:none;border:1px solid #60452f;border-radius:6px;padding:10px 12px;color:#e9dccd;font-size:.62rem;font-weight:900;background:#100c09}.aboutActions a:first-child{border-color:#47cbd1;color:#47cbd1}
.assetUnavailable{display:block;color:#8f8176;font-size:.54rem;line-height:1.35;font-weight:750}.asset.waiting{opacity:.72;border-style:dashed}.retryCapacity{margin-top:10px;background:#17120d;color:#d5a345;border:1px solid #d5a345;border-radius:5px;padding:9px 12px;font-weight:900;font-size:.63rem;cursor:pointer}.reviewState.capacity{color:#d5a345}
@media(max-width:1100px){.hero{grid-template-columns:1fr;height:auto}.heroVisual{height:300px;min-height:300px;background-position:center!important}.aboutStrip{grid-template-columns:1fr;padding:24px 20px}}
</style>
"""

FINAL_JS = """
<script id="iscarb-v403-final-js">
(function(){
  function capacityError(text){
    const t=String(text||'').toLowerCase();
    return t.includes('503') || t.includes('unavailable') || t.includes('high demand') ||
           t.includes('temporarily overloaded') || t.includes('temporarily unavailable') ||
           t.includes('service unavailable');
  }
  function quotaError(text){
    const t=String(text||'').toLowerCase();
    return t.includes('quota') || t.includes('resource_exhausted') || t.includes('free_tier_requests');
  }
  function safeGate(name,ok,local,hasBlueprint){
    if(!hasBlueprint) return `<div class="gate"><b>${name}</b><span class="na">NOT RUN</span></div>`;
    return `<div class="gate"><b>${name}</b><span class="${local?'na':ok?'pass':'fail'}">${local?'NOT RE-AUDITED':ok?'PASS':'FAIL'}</span></div>`;
  }
  function unavailableAssets(){
    return `<div class="assets">
      <div class="asset waiting"><b>Visual Presenter</b><span class="assetUnavailable">Waiting for a valid Blueprint. Preview, PPTX and PDF are not created yet.</span></div>
      <div class="asset waiting"><b>Reading Pack</b><span class="assetUnavailable">Waiting for Blueprint</span></div>
      <div class="asset waiting"><b>Instructor Guide</b><span class="assetUnavailable">Waiting for Blueprint</span></div>
      <div class="asset waiting"><b>Student Pack</b><span class="assetUnavailable">Waiting for Blueprint</span></div>
      <div class="asset waiting"><b>Blueprint</b><span class="assetUnavailable">Not created</span></div>
    </div>`;
  }
  function availableAssets(id){
    return `<div class="assets">
      <div class="asset"><b>Visual Presenter</b><a target="_blank" href="/api/jobs/${id}/presenter">Preview</a><a href="/api/jobs/${id}/export/pptx">PPTX</a><a href="/api/jobs/${id}/export/presenter-pdf">PDF</a></div>
      <div class="asset"><b>Reading Pack</b><a href="/api/jobs/${id}/export/pdf">PDF</a></div>
      <div class="asset"><b>Instructor Guide</b><a href="/api/jobs/${id}/export/docx">DOCX</a></div>
      <div class="asset"><b>Student Pack</b><a href="/api/jobs/${id}/export/student">DOCX</a></div>
      <div class="asset"><b>Blueprint</b><a href="/api/jobs/${id}/export/json">JSON</a></div>
    </div>`;
  }

  friendlyError=function(text){
    const t=String(text||'');
    if(quotaError(t)) return 'Gemini quota is exhausted. No new model-dependent step can run until quota is available; an already-created Blueprint remains usable in Output Lab.';
    if(capacityError(t)) return 'Gemini is temporarily at capacity (503). ISCARB already retried with backoff and model failover. If no Blueprint appears, retry the analysis in a moment.';
    return t;
  };

  renderResult=function(id,j){
    const state=document.getElementById('reviewState');
    const msg=document.getElementById('reviewMsg');
    const errorBox=document.getElementById('err');
    const resultBody=document.getElementById('reviewBody');
    const a=j.audit||{};
    const hasBlueprint=!!j.blueprint;
    const local=String(j.model||'').startsWith('local-');
    const ready=j.status==='ready'&&!local&&hasBlueprint;
    const capacity=!hasBlueprint&&capacityError(j.error||j.message||'');

    state.className='reviewState '+(ready?'ready':local?'local':capacity?'capacity':'blocked');
    state.textContent=ready?'ISCARB VERIFIED':local?'REVIEW MODE · NOT RE-AUDITED':capacity?'MODEL BUSY · RETRY':hasBlueprint?'REVIEW REQUIRED':'COMPILATION ERROR';
    msg.textContent=j.message||'';
    errorBox.textContent=j.error?friendlyError(j.error):'';

    const gates=`<div class="gateGrid">${safeGate('Source fidelity',!!a.source_fidelity_pass,local,hasBlueprint)}${safeGate('Engineering rigor',!!a.engineering_rigor_pass,local,hasBlueprint)}${safeGate('Cumulative fidelity',!!a.cumulative_fidelity_pass,local,hasBlueprint)}${safeGate('ETEC readiness',!!a.readiness_alignment_pass,local,hasBlueprint)}${safeGate('Provenance split',!!a.provenance_separation_pass,local,hasBlueprint)}</div>`;
    const issues=hasBlueprint?(a.issues||[]).map(x=>`<div class="issue ${local?'neutral':''}"><b>${x.requirement||'Review note'}</b><div>${x.problem||''}</div></div>`).join(''):'';

    let notice='';
    if(!hasBlueprint&&capacity){
      notice='<div class="notice"><b>No pedagogical gate failed.</b> Gemini returned a temporary capacity error before Blueprint creation. The five checks above were therefore NOT RUN, and output files do not exist yet.</div>';
    }else if(!hasBlueprint){
      notice='<div class="notice"><b>Compilation ended before Blueprint creation.</b> Release gates were NOT RUN and exports are intentionally unavailable.</div>';
    }else if(local){
      notice='<div class="notice"><b>Audit state rule:</b> Output Lab does not possess the raw P1 bundle. These release checks are therefore NOT RE-AUDITED—not failed.</div>';
    }

    const retry=(!hasBlueprint&&capacity)?'<button class="retryCapacity" type="button" onclick="document.getElementById(\'compileBtn\').click()">↻ Retry analysis →</button>':'';
    const repair=hasBlueprint?`<button class="repair" onclick="localRepair('${id}')">Presentation-safe repair · NO GEMINI →</button>`:'';
    resultBody.innerHTML=gates+notice+(issues?`<div class="issues">${issues}</div>`:'')+retry+repair+(hasBlueprint?availableAssets(id):unavailableAssets());
  };

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
    if(version) version.textContent='v4.0.3 · Capacity-Safe Visual Lecture Engine v2';
  });
})();
</script>
"""


@app.get("/")
def final_faculty_studio():
    html = (engine.APP_ROOT / "static" / "studio_v40.html").read_text(encoding="utf-8")
    hero_css = (engine.APP_ROOT / "static" / "hero_override_v401.css").read_text(encoding="utf-8")
    html = html.replace("</head>", f"<style id=\"iscarb-approved-hero-inline\">{hero_css}</style>\n{FINAL_CSS}\n</head>")
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
        "visual_lecture_engine": "v2",
        "source_visual_primary": "uploaded-p1-pdf",
        "source_visual_public_url": "best-effort-only",
        "capacity_retry_attempts_per_model": 3,
        "capacity_failover": True,
        "no_blueprint_exports": "hidden",
        "no_blueprint_gate_state": "NOT RUN",
    })
    return data


@app.post("/api/jobs/{job_id}/local-repair")
def local_gate_repair(job_id: str):
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
            "OUTPUT LAB REPAIR COMPLETE — presentation-safe v4.0.3 normalization applied with 0 Gemini calls. "
            "Source-dependent gates are NOT RE-AUDITED; full source-backed compile is required for ISCARB Verified."
        ),
        filename=old.filename,
        model="local-output-repair-v4.0.3",
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
