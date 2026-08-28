from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse

from . import main as engine
from .models import Blueprint, JobState, AuditReport, AuditIssue
from .visual_output_v36 import export_presenter_pptx, render_presenter_preview, export_presenter_pdf
from .faculty_outputs import export_detailed_pdf, export_instructor_guide, export_student_pack

FACULTY_VERSION = "4.0.1"
PIPELINE_ID = "faculty-studio-v4.0.1-approved-hero-verified-links"

app = FastAPI(title="ISCARB Faculty Studio", version=FACULTY_VERSION)

for route in engine.app.router.routes:
    path = getattr(route, "path", None)
    if path in {"/", "/api/health", "/api/jobs/{job_id}/presenter", "/api/jobs/{job_id}/export/{fmt}"}:
        continue
    app.router.routes.append(route)


SOURCE_LIBRARY_PATCH = r"""
<script>
(function(){
  const VERIFIED_SOURCES = [
    {title:'Dependable Systems', detail:'Sommerville · Chapter 10 · 47 slides', url:'https://www.slideshare.net/slideshow/ch10-dependable-systems/43151515'},
    {title:'Reliability Engineering', detail:'Sommerville · Chapter 11', url:'https://www.slideshare.net/slideshow/ch11-reliability-engineering/43151516'},
    {title:'Safety Engineering', detail:'Sommerville · Chapter 12', url:'https://www.slideshare.net/slideshow/ch12-safety-engineering/43151517'},
    {title:'Security Engineering', detail:'Sommerville 9e · Chapter 14 · 48 slides', url:'https://www.slideshare.net/slideshow/ch14-5148075/5148075'},
    {title:'Resilience Engineering', detail:'Sommerville · Chapter 14', url:'https://www.slideshare.net/slideshow/ch14-resilience-engineering/43151521'},
    {title:'Software Reuse', detail:'Sommerville · Chapter 15', url:'https://www.slideshare.net/slideshow/ch15-software-reuse/43151523'},
    {title:'Component-Based SE', detail:'Sommerville · Chapter 16', url:'https://www.slideshare.net/slideshow/ch16-component-based-software-engineering/43151525'},
    {title:'Distributed Software Engineering', detail:'Sommerville · Chapter 17', url:'https://www.slideshare.net/slideshow/ch17-distributed-software-engineering/43151527'}
  ];

  function esc(s){return String(s).replace(/[&<>\"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[c]));}
  function primaryUrlInput(){
    return document.querySelector('input[name="primary_url"]') || document.querySelector('#primary_url') ||
           Array.from(document.querySelectorAll('input[type="url"],input[type="text"]')).find(x => /primary|lecture url|public link/i.test((x.name||'')+' '+(x.id||'')+' '+(x.placeholder||'')));
  }
  function useSource(url){
    const input = primaryUrlInput();
    if(input){
      input.value=url;
      input.dispatchEvent(new Event('input',{bubbles:true}));
      input.dispatchEvent(new Event('change',{bubbles:true}));
    }
    const upgrade=document.querySelector('.upgradeBox');
    if(upgrade){upgrade.id='upgrade'; upgrade.scrollIntoView({behavior:'smooth',block:'start'});}
  }
  window.ISCARB_USE_SOURCE = useSource;

  document.addEventListener('DOMContentLoaded',()=>{
    document.body.id='top';
    const library=document.querySelector('.libraryBox'); if(library) library.id='library';
    const upgrade=document.querySelector('.upgradeBox'); if(upgrade) upgrade.id='upgrade';
    const outputs=document.querySelector('.outputs'); if(outputs) outputs.id='outputs';

    const strip=document.querySelector('.sourceStrip');
    if(strip){
      strip.innerHTML = VERIFIED_SOURCES.map((s,i)=>`<article class="sourceCard"><div class="sourceBand"></div><div class="sourceInner"><b>${esc(s.title)}</b><small>${esc(s.detail)}<br>Verified public original source</small><div class="sourceActions"><a href="${s.url}" target="_blank" rel="noopener noreferrer">OPEN ORIGINAL</a><button type="button" data-source-index="${i}">USE SOURCE</button></div></div></article>`).join('');
      strip.querySelectorAll('button[data-source-index]').forEach(btn=>btn.addEventListener('click',()=>useSource(VERIFIED_SOURCES[Number(btn.dataset.sourceIndex)].url)));
    }
    const view=document.querySelector('.viewAll');
    if(view){
      view.href='#library';
      view.onclick=(e)=>{e.preventDefault(); if(strip){strip.classList.toggle('expanded'); view.textContent=strip.classList.contains('expanded')?'Show less ↑':'View all →';}};
    }

    document.querySelectorAll('a').forEach(a=>{
      const t=(a.textContent||'').trim().toLowerCase();
      if(t==='home') a.href='#top';
      else if(t.includes('source library')) a.href='#library';
      else if(t.includes('upgrade my lecture')) a.href='#upgrade';
      else if(t==='outputs') a.href='#outputs';
      else if(t==='guides') a.href='/starter-kit';
    });

    const version=document.querySelector('.version');
    if(version) version.textContent='v4.0.1 · Verified Links + Approved Hero';
  });
})();
</script>
"""


@app.get("/")
def faculty_studio():
    html = (engine.APP_ROOT / "static" / "studio_v40.html").read_text(encoding="utf-8")
    hero_css = '<link rel="stylesheet" href="/static/hero_override_v401.css?v=4.0.1">'
    html = html.replace("</head>", hero_css + "\n</head>")
    html = html.replace("</body>", SOURCE_LIBRARY_PATCH + "\n</body>")
    return HTMLResponse(html, headers={
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-ISCARB-Version": FACULTY_VERSION,
    })


@app.get("/starter-kit")
def starter_kit():
    html = (engine.APP_ROOT / "static" / "faculty_starter_kit.html").read_text(encoding="utf-8")
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


@app.get("/api/health")
def health():
    data = engine.health()
    data.update({
        "version": FACULTY_VERSION,
        "engine_version": engine.SERVICE_VERSION,
        "pipeline": PIPELINE_ID,
        "public_experience": "Final Saudi educational heritage Faculty Studio with approved hero image, verified original source library, source-backed compile, audit-safe Output Lab, five faculty outputs, and visual provenance",
        "ready_example_source": "https://www.slideshare.net/slideshow/ch14-5148075/5148075",
        "design_language": "Approved Saudi educational heritage hero image with Najdi architecture, camel caravan and integrated academic UI overlays",
        "source_library_verified": True,
        "verified_source_count": 8,
        "presenter_theme": "visual-first 20-unit presenter with explicit visual provenance",
        "output_system": [
            "Visual Presenter Preview + PPTX + Presenter PDF",
            "Faculty Reading Pack PDF",
            "Instructor Guide DOCX",
            "Student Activity Pack DOCX",
            "Blueprint JSON",
        ],
        "local_output_lab": True,
        "output_lab_release_rule": "render/repair only; source-dependent gates are NOT RE-AUDITED without P1 and are never represented as false FAIL in the Faculty Studio UI",
        "visual_provenance": "source-anchored visual / adapted from P1 / ISCARB visualization",
        "institutional_branding": "context only; no claim of official endorsement",
    })
    return data


@app.post("/api/render-blueprint")
async def render_blueprint(blueprint_file: UploadFile = File(...)):
    if not (blueprint_file.filename or "").lower().endswith(".json"):
        raise HTTPException(400, "Choose an ISCARB Blueprint JSON file.")
    raw = await blueprint_file.read()
    try:
        bp = Blueprint.model_validate_json(raw)
    except Exception as exc:
        raise HTTPException(400, f"Invalid ISCARB Blueprint JSON: {exc}") from exc

    job_id = uuid.uuid4().hex
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
                "Outputs were rendered locally from an existing Blueprint. The raw primary source and release-audit "
                "context are not present, so source fidelity and ETEC source-dependent checks are NOT RE-AUDITED."
            ),
            repair_instruction=(
                "Use these outputs for faculty review. Re-run Analyze Source with the original lecture source "
                "when ISCARB Verified release authority is required."
            ),
        )],
        strengths=["No Gemini call is required to iterate on visual or document outputs."],
    )
    job = JobState(
        id=job_id,
        status="blocked",
        progress=100,
        message=(
            "OUTPUT LAB — Blueprint imported locally. Outputs are available. Source-dependent gates are NOT RE-AUDITED; "
            "ISCARB Verified remains disabled until a full source-backed compile is run."
        ),
        filename=blueprint_file.filename or "imported_blueprint.json",
        model="local-render-only-v4.0.1",
        source_manifest=list(bp.source_manifest),
        blueprint=bp,
        audit=audit,
        deterministic_checks={},
    )
    engine.save_job(job)
    return {"job_id": job_id, "audit_state": "not_reaudited"}


@app.get("/api/jobs/{job_id}/presenter")
def faculty_presenter(job_id: str):
    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    return HTMLResponse(
        render_presenter_preview(job.blueprint, job.status.upper()),
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
        path = export_presenter_pptx(bp, base.with_name(base.name + "_Visual_Presenter.pptx")); media = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif fmt in {"presenter-pdf", "presenter_pdf", "visual-pdf"}:
        path = export_presenter_pdf(bp, base.with_name(base.name + "_Visual_Presenter.pdf")); media = "application/pdf"
    elif fmt == "pdf":
        path = export_detailed_pdf(bp, base.with_name(base.name + "_Faculty_Reading_Pack.pdf")); media = "application/pdf"
    elif fmt == "docx":
        path = export_instructor_guide(bp, base.with_name(base.name + "_Instructor_Guide.docx")); media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt in {"student", "student-docx", "activity"}:
        path = export_student_pack(bp, base.with_name(base.name + "_Student_Activity_Pack.docx")); media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "json":
        path = base.with_name(base.name + "_Blueprint.json"); path.write_text(bp.model_dump_json(by_alias=True, indent=2), encoding="utf-8"); media = "application/json"
    else:
        raise HTTPException(400, "Format must be pptx, presenter-pdf, pdf, docx, student, or json")
    return FileResponse(path, media_type=media, filename=path.name)
