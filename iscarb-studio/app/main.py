from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .models import JobState, AuditReport, AuditIssue
from .storage import save_job, load_job, UPLOADS
from .gemini_service import GeminiService
from .gate import deterministic_gate, all_required_pass, failed_check_names
from .session_gate import apply_90_minute_timebox, session_scope_gate
from .source_bundle import SourceBundle, SourceItem
from .exporters import export_docx, export_pptx, export_pdf
from .url_source import materialize_url_source

APP_ROOT = Path(__file__).resolve().parent
EXPORTS = APP_ROOT.parent / "data" / "exports"
EXPORTS.mkdir(parents=True, exist_ok=True)

SERVICE_VERSION = "2.0.0"
PIPELINE_ID = "visual-lecture-engine-v1-content-gate-v7"

app = FastAPI(title="ISCARB Lecture Studio", version=SERVICE_VERSION)
app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
executor = ThreadPoolExecutor(max_workers=int(os.getenv("ISCARB_WORKERS", "2")))
ALLOWED_EXTS = {".pdf", ".pptx", ".docx", ".txt", ".md"}
RELIABLE_DEFAULT_MODEL = "auto"
MAX_SUPPORTING = 7


def _update(job: JobState, status: str, progress: int, message: str) -> JobState:
    job.status = status  # type: ignore
    job.progress = progress
    job.message = message
    save_job(job)
    return job


def _safe_filename(name: str, fallback: str) -> str:
    safe = "".join(c for c in Path(name or "").name if c.isalnum() or c in "._- ").strip()
    return safe or fallback


def _save_upload(job_id: str, upload: UploadFile, stem: str) -> Path:
    name = _safe_filename(upload.filename or "", stem)
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"Unsupported file type {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTS))}")
    job_dir = UPLOADS / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    path = job_dir / f"{stem}__{name}"
    with path.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


def _parse_support_urls(raw: str) -> list[str]:
    urls: list[str] = []
    for line in (raw or "").replace(";", "\n").splitlines():
        u = line.strip()
        if u and u not in urls:
            urls.append(u)
    return urls


def _is_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(marker in text for marker in (
        "quota is exhausted",
        "quota exhausted",
        "resource_exhausted",
        "quota exceeded",
        "free_tier_requests",
        "generaterequestsperdayperprojectpermodel",
    ))


def _deterministic_fallback_audit(checks: dict[str, bool], reason: str) -> AuditReport:
    failed = [name for name, ok in checks.items() if not ok]

    def category_pass(markers: tuple[str, ...]) -> bool:
        return not any(any(marker in name for marker in markers) for name in failed)

    source_pass = category_pass((
        "source_", "primary_", "topic_coverage", "topic_list", "p1_anchor",
        "technical_anchors", "unsourced_terms_in_core", "weekly_source_anchor",
    ))
    rigor_pass = category_pass((
        "unit1_", "unit5_", "unit8_", "unit9_", "unit10_", "unit17_",
        "first_taught", "rubric_covers", "bounded_assurance", "prediction",
    ))
    cumulative_pass = category_pass((
        "phase_", "unit2_", "unit3_", "unit4_", "cimt_", "coverage_idr",
        "coverage_eer", "dominant", "named_ethical", "unit11_", "unit12_",
        "unit13_", "unit14_", "unit15_", "unit16_", "unit18_", "unit19_", "unit20_",
    ))
    readiness_pass = category_pass(("readiness_", "etec"))
    provenance_pass = category_pass((
        "provenance", "enrichment", "pedagogy_channel", "hypothetical",
        "unsourced", "source_anchor", "verify_flags",
    ))

    issue_text = ", ".join(failed[:24]) if failed else "No deterministic failures; semantic audit is still required before RELEASE."
    return AuditReport(
        overall_pass=False,
        source_fidelity_pass=source_pass,
        engineering_rigor_pass=rigor_pass,
        cumulative_fidelity_pass=cumulative_pass,
        readiness_alignment_pass=readiness_pass,
        provenance_separation_pass=provenance_pass,
        issues=[
            AuditIssue(
                severity="major",
                unit_numbers=[],
                requirement="Semantic release audit",
                problem=f"Semantic audit unavailable because model quota is exhausted. Deterministic failures: {issue_text}",
                repair_instruction="Preserve the generated blueprint. Re-run the semantic audit when Gemini quota is available; do not issue RELEASE without it.",
            )
        ],
        strengths=["The 20-unit blueprint was preserved and deterministic Content Gate checks completed before quota interruption."],
    )


def _compile(job_id: str, bundle: SourceBundle, model: str, repair_rounds: int) -> None:
    service: GeminiService | None = None
    stage = "startup"
    try:
        job = load_job(job_id)
        service = GeminiService(model=model)
        source_text = bundle.combined_local_text()

        stage = "source-bundle analysis"
        _update(job, "analyzing", 10, "1/4 · Reading the primary + supporting bundle and identifying ALL major P1 topics for one fixed 90-minute lecture…")
        profile = service.profile_source(bundle)
        job.source_profile = profile
        save_job(job)

        stage = "20-unit generation + readiness alignment"
        _update(job, "generating", 35, "2/4 · Building 20 Units with complete P1 coverage. Dense material is compressed intelligently, never deferred…")
        blueprint = service.generate_blueprint(bundle, profile)
        blueprint = apply_90_minute_timebox(blueprint, profile, bundle)
        job.blueprint = blueprint
        save_job(job)

        stage = "Content Gate v7"
        _update(job, "auditing", 70, "3/4 · Running Content Gate v7 before visual rendering: full coverage, prediction order, Unit roles, provenance, ISCARB capability rubric, bounded assurance, and ETEC atomicity…")
        checks = deterministic_gate(blueprint, profile, source_text)
        checks.update(session_scope_gate(blueprint, profile, bundle))
        job.deterministic_checks = checks
        det_fail = failed_check_names(checks)
        save_job(job)

        semantic_available = True
        stage = "semantic content audit"
        try:
            audit = service.audit(bundle, blueprint, det_fail)
        except Exception as exc:
            if not _is_quota_error(exc):
                raise
            semantic_available = False
            audit = _deterministic_fallback_audit(checks, str(exc))
        job.audit = audit
        save_job(job)

        if semantic_available and all_required_pass(checks) and audit.overall_pass:
            job.blueprint = blueprint
            _update(job, "ready", 100, "RELEASE — content passed Precision Gate and is ready for Visual Lecture Engine export.")
            return

        for round_no in range(repair_rounds):
            if not det_fail and not semantic_available:
                break

            stage = f"repair round {round_no + 1}"
            _update(job, "repairing", 84 + min(round_no * 5, 8), f"4/4 · Repairing Content Gate failures while preserving all primary topics (round {round_no + 1})…")
            try:
                blueprint = service.repair(bundle, blueprint, audit, det_fail)
            except Exception as exc:
                if _is_quota_error(exc):
                    job.blueprint = blueprint
                    job.audit = audit
                    _update(job, "blocked", 100, "BLOCKED — blueprint preserved. Repair could not run because Gemini quota is exhausted; visual/detailed exports remain available for review.")
                    return
                raise

            blueprint = apply_90_minute_timebox(blueprint, profile, bundle)
            job.blueprint = blueprint
            save_job(job)

            checks = deterministic_gate(blueprint, profile, source_text)
            checks.update(session_scope_gate(blueprint, profile, bundle))
            job.deterministic_checks = checks
            det_fail = failed_check_names(checks)
            save_job(job)

            stage = f"post-repair audit {round_no + 1}"
            try:
                audit = service.audit(bundle, blueprint, det_fail)
                semantic_available = True
            except Exception as exc:
                if not _is_quota_error(exc):
                    raise
                semantic_available = False
                audit = _deterministic_fallback_audit(checks, str(exc))
            job.audit = audit
            save_job(job)

            if semantic_available and all_required_pass(checks) and audit.overall_pass:
                _update(job, "ready", 100, f"RELEASE — passed Precision Gate after repair round {round_no + 1}; visual exports are ready.")
                return

        job.blueprint = blueprint
        if not semantic_available:
            _update(job, "blocked", 100, "BLOCKED — blueprint preserved and local gates completed, but semantic release audit is unavailable because Gemini quota is exhausted. Visual and detailed exports remain available for review; no RELEASE is issued without semantic audit.")
        else:
            _update(job, "blocked", 100, "BLOCKED — blueprint generated, but Precision Content Gate found unresolved issues. Exports remain available for faculty review.")

    except Exception as exc:
        try:
            job = load_job(job_id)
            if job.blueprint is not None and _is_quota_error(exc):
                job.error = None
                _update(job, "blocked", 100, f"BLOCKED — generated blueprint preserved; downstream Gemini quota became unavailable during {stage}. Exports remain available.")
            else:
                job.status = "error"
                job.progress = 100
                job.message = f"Compilation stopped during {stage}."
                job.error = f"{type(exc).__name__}: {exc}"
                save_job(job)
        except Exception:
            pass
    finally:
        if service is not None:
            service.close()


@app.get("/")
def root():
    html = (APP_ROOT / "static" / "studio_v2.html").read_text(encoding="utf-8")
    return HTMLResponse(
        html,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-ISCARB-Version": SERVICE_VERSION,
        },
    )


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "version": SERVICE_VERSION,
        "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "default_model": RELIABLE_DEFAULT_MODEL,
        "url_sources": True,
        "multi_source_bundle": True,
        "session_minutes": 90,
        "full_primary_coverage": True,
        "primary_topic_deferral_allowed": False,
        "max_sources": 8,
        "pipeline": PIPELINE_ID,
        "readiness_standard": "ETEC Academic Standards for Information Technology Programs 2025 v2.0",
        "visual_system": "presenter-deck-v1 + detailed-deck + instructor-guide + blueprint",
    }


@app.post("/api/compile")
async def compile_lecture(
    primary_lecture: UploadFile | None = File(default=None),
    primary_url: str = Form(default=""),
    supporting_files: list[UploadFile] | None = File(default=None),
    supporting_urls: str = Form(default=""),
    lecture_focus: str = Form(default=""),
    model: str = Form(default=""),
    repair_rounds: int = Form(default=1),
):
    primary_url = primary_url.strip()
    lecture_focus = lecture_focus.strip()
    has_primary_file = primary_lecture is not None and bool(primary_lecture.filename)
    if not has_primary_file and not primary_url:
        raise HTTPException(400, "Choose exactly one PRIMARY lecture source: upload a file OR paste a primary URL.")
    if has_primary_file and primary_url:
        raise HTTPException(400, "For the PRIMARY source use either a file or a URL, not both.")

    support_files = [f for f in (supporting_files or []) if f is not None and bool(f.filename)]
    support_urls = _parse_support_urls(supporting_urls)
    if len(support_files) + len(support_urls) > MAX_SUPPORTING:
        raise HTTPException(400, f"Use at most {MAX_SUPPORTING} supporting sources for one 90-minute lecture.")

    repair_rounds = max(0, min(int(repair_rounds), 2))
    job_id = uuid.uuid4().hex
    job_dir = UPLOADS / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    items: list[SourceItem] = []

    if primary_url:
        try:
            path = materialize_url_source(primary_url, job_dir / "P1")
        except ValueError as exc:
            raise HTTPException(400, f"Primary URL: {exc}") from exc
        items.append(SourceItem("primary", "P1", primary_url, path, primary_url))
        display_name = primary_url
    else:
        assert primary_lecture is not None
        path = _save_upload(job_id, primary_lecture, "P1")
        name = primary_lecture.filename or path.name
        items.append(SourceItem("primary", "P1", name, path, name))
        display_name = name

    support_index = 1
    for upload in support_files:
        path = _save_upload(job_id, upload, f"S{support_index}")
        name = upload.filename or path.name
        items.append(SourceItem("supporting", f"S{support_index}", name, path, name))
        support_index += 1

    for url in support_urls:
        try:
            path = materialize_url_source(url, job_dir / f"S{support_index}")
        except ValueError as exc:
            raise HTTPException(400, f"Supporting URL {support_index}: {exc}") from exc
        items.append(SourceItem("supporting", f"S{support_index}", url, path, url))
        support_index += 1

    try:
        bundle = SourceBundle(items=items, lecture_focus=lecture_focus, session_minutes=90)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    chosen_model = model.strip() or RELIABLE_DEFAULT_MODEL
    job = JobState(
        id=job_id,
        status="queued",
        progress=2,
        message="Queued for ISCARB v2.0 — source lock, Precision Content Gate, then Visual Lecture Engine assets…",
        filename=display_name,
        model=chosen_model,
        source_manifest=bundle.manifest_lines(),
        lecture_focus=lecture_focus,
    )
    save_job(job)
    executor.submit(_compile, job_id, bundle, chosen_model, repair_rounds)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    try:
        return load_job(job_id).model_dump(by_alias=True)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")


@app.get("/api/jobs/{job_id}/export/{fmt}")
def export_job(job_id: str, fmt: str):
    try:
        job = load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    if job.status not in {"ready", "blocked", "error"}:
        raise HTTPException(409, "Compilation is still in progress")

    base = EXPORTS / f"ISCARB_{job_id}"
    fmt = fmt.lower()
    if fmt == "json":
        path = base.with_suffix(".json")
        path.write_text(job.blueprint.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
        media = "application/json"
    elif fmt == "docx":
        path = export_docx(job.blueprint, base.with_suffix(".docx"))
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "pptx":
        path = export_pptx(job.blueprint, base.with_suffix(".pptx"))
        media = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif fmt == "pdf":
        path = export_pdf(job.blueprint, base.with_suffix(".pdf"))
        media = "application/pdf"
    else:
        raise HTTPException(400, "Format must be json, docx, pptx, or pdf")

    return FileResponse(path, media_type=media, filename=path.name)
