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
from .storage import save_job, load_job, prune_expired, JOB_MISSING_MESSAGE, UPLOADS
from .gemini_service import GeminiService, is_transient_model_failure
from .source_profile_fallback import build_deterministic_source_profile, reconcile_source_profile
from .gate import deterministic_gate, all_required_pass, failed_check_names
from .session_gate import apply_90_minute_timebox, session_scope_gate
from .source_bundle import SourceBundle, SourceItem
from .exporters import export_docx, export_pdf
from .visual_engine import export_presenter_pptx, render_presenter_preview
from .url_source import materialize_url_source
from .deterministic_blueprint_fallback import build_deterministic_blueprint

APP_ROOT = Path(__file__).resolve().parent
EXPORTS = APP_ROOT.parent / "data" / "exports"
EXPORTS.mkdir(parents=True, exist_ok=True)

SERVICE_VERSION = "2.1.0"
PIPELINE_ID = "visual-grammar-v1-presenter-preview-content-gate-v7"

# This app object defines the pipeline routes but is NOT the app Render serves.
# faculty_main.py builds the served app and copies these route objects across;
# middleware, exception handlers and lifespan do not travel with a copied route,
# so anything app-wide must be registered on the served app instead.
app = FastAPI(title="ISCARB Lecture Studio", version=SERVICE_VERSION)
app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
executor = ThreadPoolExecutor(max_workers=int(os.getenv("ISCARB_WORKERS", "2")))
ALLOWED_EXTS = {".pdf", ".pptx", ".docx", ".txt", ".md"}
RELIABLE_DEFAULT_MODEL = "auto"
MAX_SUPPORTING = 7

# A 90-minute lecture source is a slide deck or chapter, not a media archive.
# Streaming with an explicit ceiling keeps one oversized upload from filling the
# container disk that every other faculty job shares.
MAX_UPLOAD_BYTES = int(os.getenv("ISCARB_MAX_UPLOAD_MB", "25")) * 1024 * 1024
UPLOAD_CHUNK = 1024 * 1024


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
    written = 0
    try:
        with path.open("wb") as f:
            while True:
                chunk = upload.file.read(UPLOAD_CHUNK)
                if not chunk:
                    break
                written += len(chunk)
                if written > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        413,
                        f"{name} is larger than the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit for one source. "
                        "Upload the lecture chapter itself rather than a full media archive.",
                    )
                f.write(chunk)
    except HTTPException:
        path.unlink(missing_ok=True)
        raise
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


def _is_model_unavailable(exc: Exception) -> bool:
    """True when Gemini could not answer, whatever the upstream reason.

    GeminiService already retries transient failures three times per model and
    fails over across models, so an exception reaching here means the model is
    genuinely unreachable for this job - exhausted quota and sustained 503 /
    overload / rate-limit alike. Both must reach the deterministic draft: a
    faculty member waiting on a lecture is better served by a source-complete
    BLOCKED draft than by a job that ends with no output at all.

    Programming errors inside our own pipeline still propagate, because they
    match neither classifier and must surface rather than be papered over.
    """
    return _is_quota_error(exc) or is_transient_model_failure(exc)


def _deterministic_fallback_audit(checks: dict[str, bool], reason: str) -> AuditReport:
    failed = [name for name, ok in checks.items() if not ok]
    # Do not expose raw provider errors (which may contain request details),
    # and do not call an intentionally offline draft a provider outage.
    reason_lower = reason.lower()
    if "timed out" in reason_lower or "time budget" in reason_lower or "timeout" in reason_lower:
        reason_label = "The model request exceeded its time limit."
    elif "quota" in reason_lower or "resource_exhausted" in reason_lower:
        reason_label = "The configured model quota was exhausted."
    elif "not yet performed" in reason_lower:
        reason_label = "Independent semantic audit has not been performed for this source-preserving draft."
    else:
        reason_label = "Independent semantic assurance is unavailable or incomplete."

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
                problem=f"{reason_label} No verified release is issued. Deterministic failures: {issue_text}",
                repair_instruction="Preserve the generated blueprint. Re-run the semantic audit when Gemini is reachable again; do not issue RELEASE without it.",
            )
        ],
        strengths=["The 20-unit review draft was preserved and local checks completed; semantic approval is not claimed."],
    )


def _major_coverage_gaps(blueprint, profile) -> tuple[list[str], list[str]]:
    """Return major P1 checkpoint ids that are missing or first taught after Unit 15."""
    ledger = {entry.coverage_id: entry for entry in blueprint.coverage_ledger}
    major = [row for row in profile.coverage_items if row.importance == "major"]
    missing = [row.id for row in major if row.id not in ledger]
    late = [
        row.id for row in major
        if row.id in ledger and ledger[row.id].first_taught_unit > 15
    ]
    return missing, late


def _critical_presenter_failures(checks: dict[str, bool]) -> list[str]:
    """Failures that make a 20-page file pedagogically unusable.

    Provenance/readiness defects may still leave a useful review draft.  A
    broken unit grammar, missing source detail, or near-empty technical span
    does not.  In those cases the complete deterministic source-bounded draft
    is safer than preserving a polished but hollow semantic draft.
    """
    critical = {
        "v14_major_chapter_items_are_actually_taught",
        "v14_technical_units_have_teaching_density",
        "v14_no_unit_is_a_near_empty_slide",
        "v14_source_supports_ten_teaching_units",
        "v15_complete_20_unit_grammar",
        "v15_technical_units_retain_source_detail",
        "v15_no_source_fragment_ends_mid_thought",
    }
    return [name for name in critical if checks.get(name) is False]


def _ensure_quota_safe_completeness(blueprint, profile, bundle, source_text: str, reason: str):
    """Guarantee atomic P1 completeness when the model becomes unreachable.

    A complete semantic Blueprint is preserved.  An incomplete semantic Blueprint
    is replaced by the tested deterministic source-bounded draft.  In both cases
    the result remains non-releasable because semantic assurance is unavailable.
    """
    missing, late = _major_coverage_gaps(blueprint, profile)
    original_checks = deterministic_gate(blueprint, profile, source_text)
    original_checks.update(session_scope_gate(blueprint, profile, bundle))
    presenter_failures = _critical_presenter_failures(original_checks)
    replaced = bool(missing or late or presenter_failures)
    if replaced:
        blueprint = build_deterministic_blueprint(profile)
        blueprint = apply_90_minute_timebox(blueprint, profile, bundle)
    checks = deterministic_gate(blueprint, profile, source_text)
    checks.update(session_scope_gate(blueprint, profile, bundle))
    audit = _deterministic_fallback_audit(checks, reason)
    return blueprint, checks, audit, replaced, missing, late


def _compile(job_id: str, bundle: SourceBundle, model: str, repair_rounds: int) -> None:
    service: GeminiService | None = None
    stage = "startup"
    try:
        job = load_job(job_id)
        source_text = bundle.combined_local_text()

        # Save a source-preserving draft before any external-model request.
        # A model outage must never take the user's source or downloads hostage.
        _update(job, "analyzing", 10, "Mapping source pages and preparing a downloadable review draft…")
        profile = build_deterministic_source_profile(bundle)
        blueprint = build_deterministic_blueprint(profile)
        blueprint = apply_90_minute_timebox(blueprint, profile, bundle)
        job.source_profile = profile
        job.blueprint = blueprint
        checks = deterministic_gate(blueprint, profile, source_text)
        checks.update(session_scope_gate(blueprint, profile, bundle))
        job.deterministic_checks = checks
        job.audit = _deterministic_fallback_audit(checks, "Source-preserving draft; independent semantic audit not yet performed.")
        save_job(job)
        if model == "source-only":
            _update(job, "blocked", 100, "Source-preserving review draft ready. No AI calls were made. Review the learning activities and download the original source alongside the presenter; this is not an independently audited release.")
            return
        service = GeminiService(model=model)

        stage = "source-bundle analysis"
        _update(job, "analyzing", 10, "1/4 · Source Lock: identifying all major P1 topics and technical boundaries…")
        try:
            profile = service.profile_source(bundle)
            profile = reconcile_source_profile(profile, bundle)
        except Exception as exc:
            if not _is_model_unavailable(exc):
                raise
            profile = build_deterministic_source_profile(bundle, str(exc))
        job.source_profile = profile
        save_job(job)

        stage = "20-unit generation + readiness alignment"
        _update(job, "generating", 35, "2/4 · Building the source-allocation plan, then five batches of four units…")
        def save_batch(snapshot, completed):
            job.blueprint = snapshot
            job.audit = _deterministic_fallback_audit({}, "Independent semantic audit not yet performed.")
            job.deterministic_checks = {"batch_all_units_generated": False}
            _update(job, "generating", 35 + completed, f"Generated {completed}/20 units. Unfinished units remain source-only review drafts; semantic audit pending.")
        service.on_batch = save_batch
        try:
            blueprint = service.generate_blueprint(bundle, profile)
        except Exception as exc:
            if not _is_model_unavailable(exc):
                raise
            blueprint = getattr(service, "partial_blueprint", None) or build_deterministic_blueprint(profile)
            blueprint = apply_90_minute_timebox(blueprint, profile, bundle)
            job.blueprint = blueprint
            checks = deterministic_gate(blueprint, profile, source_text)
            checks.update(session_scope_gate(blueprint, profile, bundle))
            job.deterministic_checks = checks
            job.audit = _deterministic_fallback_audit(checks, str(exc))
            save_job(job)
            _update(job, "blocked", 100, "BLOCKED — Gemini was unreachable during generation. Completed batches and remaining source-review units were preserved; readiness is UNVERIFIED and RELEASE is forbidden until semantic generation/audit succeeds.")
            return
        blueprint = apply_90_minute_timebox(blueprint, profile, bundle)
        job.blueprint = blueprint
        save_job(job)

        stage = "Content Gate v7"
        _update(job, "auditing", 70, "3/4 · Precision Gate: checking rigor, provenance, ETEC readiness, bounded assurance and Unit-role fidelity…")
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
            if not _is_model_unavailable(exc):
                raise
            semantic_available = False
            audit = _deterministic_fallback_audit(checks, str(exc))
        job.audit = audit
        save_job(job)

        if semantic_available and all_required_pass(checks) and audit.overall_pass:
            job.blueprint = blueprint
            _update(job, "ready", 100, "RELEASE — content passed Precision Gate. Presenter Preview and all Visual Lecture Engine assets are ready.")
            return

        for round_no in range(repair_rounds):
            if not det_fail and not semantic_available:
                break

            stage = f"repair round {round_no + 1}"
            _update(job, "repairing", 84 + min(round_no * 5, 8), f"4/4 · Repairing gate failures while preserving all primary topics (round {round_no + 1})…")
            try:
                blueprint = service.repair(bundle, blueprint, audit, det_fail)
            except Exception as exc:
                if _is_model_unavailable(exc):
                    blueprint, checks, audit, replaced, missing, late = _ensure_quota_safe_completeness(
                        blueprint, profile, bundle, source_text, str(exc)
                    )
                    job.blueprint = blueprint
                    job.deterministic_checks = checks
                    job.audit = audit
                    job.error = None
                    save_job(job)
                    if replaced:
                        gap_text = ", ".join([*missing, *late]) or "presenter completeness checks"
                        _update(job, "blocked", 100, f"BLOCKED — Gemini was unreachable during repair. The incomplete semantic draft was replaced by a complete source-checkpoint draft covering every major P1 checkpoint by Unit 15. Readiness is UNVERIFIED and RELEASE is forbidden until semantic audit succeeds. Recovered: {gap_text}")
                    else:
                        _update(job, "blocked", 100, "BLOCKED — Gemini was unreachable during repair. The source-complete semantic draft was preserved; readiness remains UNVERIFIED and RELEASE is forbidden until semantic audit succeeds.")
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
                if not _is_model_unavailable(exc):
                    raise
                semantic_available = False
                audit = _deterministic_fallback_audit(checks, str(exc))
            job.audit = audit
            save_job(job)

            if semantic_available and all_required_pass(checks) and audit.overall_pass:
                _update(job, "ready", 100, f"RELEASE — passed Precision Gate after repair round {round_no + 1}; Presenter Preview and assets are ready.")
                return

        job.blueprint = blueprint
        if not semantic_available:
            blueprint, checks, audit, replaced, missing, late = _ensure_quota_safe_completeness(
                blueprint, profile, bundle, source_text, "Gemini became unreachable before semantic release assurance completed."
            )
            job.blueprint = blueprint
            job.deterministic_checks = checks
            job.audit = audit
            job.error = None
            save_job(job)
            if replaced:
                _update(job, "blocked", 100, "BLOCKED — semantic assurance is unavailable because Gemini could not be reached. A complete source-checkpoint draft now covers every major P1 checkpoint by Unit 15; readiness is UNVERIFIED and no RELEASE is issued.")
            else:
                _update(job, "blocked", 100, "BLOCKED — source-complete blueprint preserved and local gates completed; semantic audit is unavailable because Gemini could not be reached. Preview and exports remain available, but no RELEASE is issued.")
        else:
            # Major P1 completeness is non-negotiable even when Gemini remained
            # available through every repair round.
            missing, late = _major_coverage_gaps(blueprint, profile)
            presenter_failures = _critical_presenter_failures(checks)
            if missing or late or presenter_failures:
                recovered = ", ".join([*missing, *late, *presenter_failures])
                blueprint = build_deterministic_blueprint(profile)
                blueprint = apply_90_minute_timebox(blueprint, profile, bundle)
                checks = deterministic_gate(blueprint, profile, source_text)
                checks.update(session_scope_gate(blueprint, profile, bundle))
                audit = _deterministic_fallback_audit(
                    checks,
                    "Semantic repair ended with unresolved major P1 coverage gaps; a source-complete review draft was substituted.",
                )
                job.blueprint = blueprint
                job.deterministic_checks = checks
                job.audit = audit
                job.error = None
                save_job(job)
                _update(job, "blocked", 100, "BLOCKED — semantic repair exhausted with unresolved chapter coverage or learner-visible Unit grammar. The hollow draft was replaced by a source-complete review draft covering every major P1 checkpoint by Unit 15. Readiness is UNVERIFIED; no RELEASE is issued. Recovered: " + recovered)
            else:
                _update(job, "blocked", 100, "BLOCKED — Precision Gate found unresolved content issues. Preview and exports remain available for faculty review.")

    except Exception as exc:
        try:
            job = load_job(job_id)
            from .batched_generation import GenerationContractError
            if job.blueprint is not None and isinstance(exc, GenerationContractError):
                job.error = None
                job.audit = _deterministic_fallback_audit({}, "Generated content failed local quality validation.")
                job.audit.issues.append(AuditIssue(severity="major", unit_numbers=[],
                    requirement="Generation batch source-evidence contract", problem=str(exc),
                    repair_instruction="Repair the identified source-evidence defect before release; preserved draft units are not semantically approved."))
                _update(job, "blocked", 100, "REVIEW REQUIRED — a generated batch failed source-evidence validation after its correction attempt. Completed batches and the source-review draft remain available; no verified release is issued. " + str(exc))
            elif job.blueprint is not None and _is_model_unavailable(exc):
                job.error = None
                _update(job, "blocked", 100, f"BLOCKED — generated blueprint preserved; Gemini became unreachable during {stage}. Preview and exports remain available.")
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
        try:
            prune_expired()
        except Exception:
            pass


@app.get("/")
def root():
    html_text = (APP_ROOT / "static" / "studio_v21.html").read_text(encoding="utf-8")
    return HTMLResponse(
        html_text,
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
        "visual_system": "20-unit visual grammar + in-browser presenter preview + presenter PPTX + detailed PDF + instructor guide",
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
        message="Queued — source analysis, batched generation, source-evidence checks, then independent audit…",
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
        raise HTTPException(404, JOB_MISSING_MESSAGE)


@app.get("/api/jobs/{job_id}/presenter")
def presenter_preview(job_id: str):
    try:
        job = load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, JOB_MISSING_MESSAGE)
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    return HTMLResponse(
        render_presenter_preview(job.blueprint, job.status.upper()),
        headers={"Cache-Control": "no-store", "X-ISCARB-Preview": "visual-grammar-v1"},
    )


@app.get("/api/jobs/{job_id}/export/{fmt}")
def export_job(job_id: str, fmt: str):
    try:
        job = load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, JOB_MISSING_MESSAGE)
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
        path = export_presenter_pptx(job.blueprint, base.with_suffix(".pptx"))
        media = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    elif fmt == "pdf":
        path = export_pdf(job.blueprint, base.with_suffix(".pdf"))
        media = "application/pdf"
    else:
        raise HTTPException(400, "Format must be json, docx, pptx, or pdf")

    return FileResponse(path, media_type=media, filename=path.name)
