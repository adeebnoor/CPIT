from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import JobState
from .storage import save_job, load_job, upload_path
from .gemini_service import GeminiService
from .gate import deterministic_gate, all_required_pass, failed_check_names
from .exporters import export_docx, export_pptx, export_pdf
from .url_source import materialize_url_source

APP_ROOT = Path(__file__).resolve().parent
EXPORTS = APP_ROOT.parent / "data" / "exports"
EXPORTS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ISCARB Lecture Studio", version="1.5.0")
app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
executor = ThreadPoolExecutor(max_workers=int(os.getenv("ISCARB_WORKERS", "2")))
ALLOWED_EXTS = {".pdf", ".pptx", ".docx", ".txt", ".md"}
RELIABLE_DEFAULT_MODEL = "gemini-3.6-flash"


def _update(job: JobState, status: str, progress: int, message: str) -> JobState:
    job.status = status  # type: ignore
    job.progress = progress
    job.message = message
    save_job(job)
    return job


def _compile(job_id: str, file_path: Path, model: str, repair_rounds: int) -> None:
    service: GeminiService | None = None
    stage = "startup"
    try:
        job = load_job(job_id)
        service = GeminiService(model=model)

        stage = "source analysis"
        _update(job, "analyzing", 10, "1/4 · Locking the weekly technical source and extracting all major topic families…")
        profile = service.profile_source(file_path)
        job.source_profile = profile
        save_job(job)

        stage = "20-unit generation + readiness alignment"
        _update(job, "generating", 35, "2/4 · Building 20 units with exact ETEC SLO→KLO mapping and provenance separation…")
        blueprint = service.generate_blueprint(file_path, profile)
        job.blueprint = blueprint
        save_job(job)

        stage = "Content Gate v3"
        _update(job, "auditing", 70, "3/4 · Running Content Gate v3: source provenance, elite engineering rigor, exact ETEC mapping, and cumulative fidelity…")
        checks = deterministic_gate(blueprint, profile)
        job.deterministic_checks = checks
        det_fail = failed_check_names(checks)

        stage = "semantic content audit"
        audit = service.audit(file_path, blueprint, det_fail)
        job.audit = audit
        save_job(job)

        if all_required_pass(checks) and audit.overall_pass:
            job.blueprint = blueprint
            _update(job, "ready", 100, "RELEASE — passed Content Gate v3, semantic source audit, and exact ETEC readiness alignment.")
            return

        for round_no in range(repair_rounds):
            stage = f"repair round {round_no + 1}"
            _update(job, "repairing", 84 + min(round_no * 5, 8), f"4/4 · Repairing only detected Content Gate v3 failures (round {round_no + 1})…")
            blueprint = service.repair(file_path, blueprint, audit, det_fail)
            job.blueprint = blueprint
            save_job(job)

            checks = deterministic_gate(blueprint, profile)
            job.deterministic_checks = checks
            det_fail = failed_check_names(checks)
            stage = f"post-repair audit {round_no + 1}"
            audit = service.audit(file_path, blueprint, det_fail)
            job.audit = audit
            save_job(job)
            if all_required_pass(checks) and audit.overall_pass:
                _update(job, "ready", 100, f"RELEASE — passed Content Gate v3 after repair round {round_no + 1}.")
                return

        job.blueprint = blueprint
        _update(job, "blocked", 100, "BLOCKED — blueprint generated, but Content Gate v3 found unresolved source, rigor, provenance, or readiness issues.")

    except Exception as exc:
        try:
            job = load_job(job_id)
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
    return FileResponse(APP_ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "version": "1.5.0",
        "gemini_api_key_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "default_model": RELIABLE_DEFAULT_MODEL,
        "url_sources": True,
        "pipeline": "content-gate-v3-exact-etec-provenance",
        "readiness_standard": "ETEC Academic Standards for Information Technology Programs 2025 v2.0",
        "visual_system": "interface-v2; lecture visual rendering follows content release",
    }


@app.post("/api/compile")
async def compile_lecture(
    lecture: UploadFile | None = File(default=None),
    source_url: str = Form(default=""),
    model: str = Form(default=""),
    repair_rounds: int = Form(default=1),
):
    source_url = source_url.strip()
    has_file = lecture is not None and bool(lecture.filename)
    if not has_file and not source_url:
        raise HTTPException(400, "Upload one weekly lecture OR paste one public lecture URL.")
    if has_file and source_url:
        raise HTTPException(400, "Use one source at a time: either a file or a URL, not both.")

    repair_rounds = max(0, min(int(repair_rounds), 2))
    job_id = uuid.uuid4().hex

    if source_url:
        try:
            target_dir = upload_path(job_id, "linked_source").parent / job_id
            target = materialize_url_source(source_url, target_dir)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        display_name = source_url
    else:
        assert lecture is not None
        ext = Path(lecture.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTS:
            raise HTTPException(400, f"Unsupported file type {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTS))}")
        target = upload_path(job_id, lecture.filename or f"lecture{ext}")
        with target.open("wb") as f:
            shutil.copyfileobj(lecture.file, f)
        display_name = lecture.filename or target.name

    chosen_model = model.strip() or RELIABLE_DEFAULT_MODEL
    job = JobState(
        id=job_id,
        status="queued",
        progress=2,
        message="Queued for ISCARB v1.5 compilation…",
        filename=display_name,
        model=chosen_model,
    )
    save_job(job)
    executor.submit(_compile, job_id, target, chosen_model, repair_rounds)
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
    if job.status not in {"ready", "blocked"}:
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
