"""No-API authoring round trip; local checks never impersonate semantic approval."""
from __future__ import annotations

import json
import re
import shutil
import uuid
from pathlib import Path

from fastapi import File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from .models import AuditIssue, AuditReport, Blueprint, JobState
from .source_bundle import SourceBundle, SourceItem
from .storage import UPLOADS

DEFAULT_MODE = "source-only"
FREE_MODEL = "gemini-3.5-flash-lite"
# Keep old bookmarks/clients usable without letting an arbitrary model name
# select a paid-only model. The optional API path requires an unbilled project.
LEGACY_MODES = {"auto", "gemini-3.6-flash", "gemini-3.5-flash", FREE_MODEL}


def resolve_mode(value: str) -> str:
    value = value.strip() or DEFAULT_MODE
    if value in LEGACY_MODES:
        return "free"
    if value not in {DEFAULT_MODE, "free"}:
        raise ValueError("Choose Free draft (no API) or Free-tier AI. Other model routes are disabled.")
    return value


def save_bundle(bundle: SourceBundle, root: Path) -> None:
    data = [{"role": item.role, "source_id": item.source_id,
             "display_name": item.display_name, "origin": item.origin,
             "path": str(item.path.resolve().relative_to(root.resolve()))}
            for item in bundle.items]
    (root / "source_bundle.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def load_bundle(job: JobState, root: Path) -> SourceBundle:
    manifest = root / "source_bundle.json"
    if not manifest.is_file():
        raise HTTPException(409, "The original source files are unavailable for this workflow. Build a new free draft from the original lecture first.")
    items = []
    for record in json.loads(manifest.read_text(encoding="utf-8")):
        path = (root / record["path"]).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise HTTPException(409, "An original source file is missing. Build a new free draft first.")
        items.append(SourceItem(record["role"], record["source_id"], record["display_name"], path, record["origin"]))
    return SourceBundle(items=items, lecture_focus=job.lecture_focus, session_minutes=90)


def authoring_prompt(job: JobState, bundle: SourceBundle) -> str:
    from .prompts import MASTER_PROMPT
    from .quality_rules import QUALITY_ADDENDUM
    from .readiness import READINESS_CONTEXT
    from .readiness_map import READINESS_KLO_MAP_CONTEXT
    from .unit_contract import contract_text

    return "\n\n".join([
        "ISCARB — MANUAL AUTHORING / NO WEBSITE API CALLS",
        "Attach the original P1 lecture (and any supporting files) when using this prompt in a tool you already have access to. "
        "The extracted text below is a reading aid, not a replacement for source figures or tables. "
        "No subscription or paid API is required by the website for downloading this prompt or importing its result. "
        "Your chosen authoring tool has its own usage limits. Do not upload confidential material to an unapproved tool.",
        "TASK: Return one complete Blueprint JSON file, not commentary, a JobState, or an audit report. "
        "It must contain exactly 20 units with unique numbers 1–20, five CLOs, the full coverage ledger and all required fields. "
        "Do not omit mechanisms, examples, figures, limitations, or list members from P1. "
        "Use core_content and coverage_evidence (exact excerpts of visible core), not the batch-only source_passages field. "
        "Keep technical claims separate from hypothetical scenarios and instructional scaffolding. "
        "Do not invent official readiness mappings or claim RELEASE, PASS, or independent semantic approval. "
        "Unresolved content must remain explicitly marked for faculty review. "
        "The website runs its local gates again after import and keeps the result a REVIEW DRAFT.",
        MASTER_PROMPT, QUALITY_ADDENDUM, contract_text(),
        "OFFICIAL READINESS CONTEXT (do not invent mappings):\n" + READINESS_CONTEXT + "\n" + READINESS_KLO_MAP_CONTEXT,
        "LOCKED SOURCE PROFILE — retain every major coverage ID and its coordinates:\n" + job.source_profile.model_dump_json(indent=2),
        "SOURCE TEXT — attach originals for complete visual information:\n" + bundle.combined_local_text(),
        "OUTPUT JSON SCHEMA:\n" + json.dumps(Blueprint.model_json_schema(by_alias=True), ensure_ascii=False),
    ])


def install_routes(app, engine) -> None:
    def source_job(job_id: str):
        if not re.fullmatch(r"[a-f0-9]{32}", job_id):
            raise HTTPException(404, "Job not found.")
        try:
            job = engine.load_job(job_id)
        except FileNotFoundError:
            raise HTTPException(404, "Job not found. Build a new free draft from your original lecture.")
        if job.blueprint is None or job.source_profile is None:
            raise HTTPException(409, "The source draft is not available yet.")
        if job.status not in {"ready", "blocked", "error"}:
            raise HTTPException(409, "Wait for this job to finish before editing its saved source draft.")
        return job, load_bundle(job, UPLOADS / job_id)

    @app.get("/api/jobs/{job_id}/authoring-prompt")
    def download_prompt(job_id: str):
        job, bundle = source_job(job_id)
        return PlainTextResponse(authoring_prompt(job, bundle), headers={
            "Content-Disposition": f'attachment; filename="ISCARB_{job_id}_Authoring_Prompt.txt"',
            "Cache-Control": "no-store",
        })

    @app.post("/api/jobs/{job_id}/import-blueprint")
    async def import_blueprint(job_id: str, blueprint_file: UploadFile = File(...)):
        parent, bundle = source_job(job_id)
        if not (blueprint_file.filename or "").lower().endswith(".json"):
            raise HTTPException(400, "Choose the completed Blueprint JSON file.")
        raw = await blueprint_file.read(engine.MAX_UPLOAD_BYTES + 1)
        if len(raw) > engine.MAX_UPLOAD_BYTES:
            raise HTTPException(413, "Blueprint file exceeds the upload limit.")
        try:
            bp = Blueprint.model_validate_json(raw)
        except ValueError:
            raise HTTPException(400, "Invalid Blueprint JSON. Use the downloaded authoring prompt and return all required fields with exactly 20 units.")
        if sorted(u.number for u in bp.units) != list(range(1, 21)):
            raise HTTPException(400, "Unit numbers must be unique and cover 1–20 exactly.")
        bp.units.sort(key=lambda u: u.number)
        bp.source_manifest = parent.source_manifest.copy()
        bp.generation_mode = "manual-no-api"
        checks = engine.deterministic_gate(bp, parent.source_profile, bundle.combined_local_text())
        checks.update(engine.session_scope_gate(bp, parent.source_profile, bundle))
        audit = AuditReport(
            overall_pass=False, source_fidelity_pass=False, engineering_rigor_pass=False,
            cumulative_fidelity_pass=False, readiness_alignment_pass=False, provenance_separation_pass=False,
            issues=[AuditIssue(severity="major", unit_numbers=[], requirement="Manual authoring — semantic review pending",
                problem="Local source, role and layout checks were run against the saved original source. Independent semantic audit was not performed; no verified release is issued.",
                repair_instruction="Inspect the local failures and compare the complete lecture against P1 before classroom use. No Gemini call is needed to edit and import another draft.")],
            strengths=["The original source files and locked source profile were preserved. Zero model API calls."],
        )
        new_id = uuid.uuid4().hex
        # Copy into a new job: never overwrite a faculty draft or borrow another
        # lecture's source visuals. Only server-created source files are copied.
        root = UPLOADS / new_id
        root.mkdir()
        copied = []
        for item in bundle.items:
            relative = item.path.relative_to((UPLOADS / job_id).resolve())
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item.path, target)
            copied.append(SourceItem(item.role, item.source_id, item.display_name, target, item.origin))
        save_bundle(SourceBundle(copied, parent.lecture_focus, 90), root)
        job = JobState(id=new_id, status="blocked", progress=100,
            message="FREE WORKSPACE — imported and locally checked against the original source. No API calls. REVIEW DRAFT; independent semantic approval is still pending.",
            filename=parent.filename, model="manual-no-api", source_manifest=parent.source_manifest.copy(),
            lecture_focus=parent.lecture_focus, source_profile=parent.source_profile.model_copy(deep=True),
            blueprint=bp, audit=audit, deterministic_checks=checks)
        engine.save_job(job)
        return {"job_id": new_id, "api_calls": 0, "audit_state": "semantic_review_pending"}
