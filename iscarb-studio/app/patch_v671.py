from __future__ import annotations

"""ISCARB v6.7.1 runtime reliability patch."""
import json
import threading
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse
from . import main as engine
from . import start_v440 as base
from .faculty_outputs import export_detailed_pdf, export_instructor_guide, export_student_pack
from .source_visuals import _find_local_primary_pdf

_PATCHED=False
_JOB_LOCKS:dict[str,threading.Lock]={}
_LOCKS_GUARD=threading.Lock()

def _job_lock(job_id:str)->threading.Lock:
    with _LOCKS_GUARD:
        return _JOB_LOCKS.setdefault(job_id,threading.Lock())

def _cache_paths(job_id:str)->dict[str,Path]:
    root=engine.EXPORTS
    return {
        "pptx":root/f"ISCARB_{job_id}_Visual_Presenter.pptx",
        "presenter-pdf":root/f"ISCARB_{job_id}_Visual_Presenter.pdf",
        "pdf":root/f"ISCARB_{job_id}_Faculty_Reading_Pack.pdf",
        "docx":root/f"ISCARB_{job_id}_Instructor_Guide.docx",
        "student":root/f"ISCARB_{job_id}_Student_Activity_Pack.docx",
        "json":root/f"ISCARB_{job_id}_Blueprint.json",
    }

def _good(path:Path,minimum:int=64)->bool:
    try:return path.exists() and path.stat().st_size>=minimum
    except OSError:return False

def _ensure_u11_contract(blueprint):
    unit=next((u for u in getattr(blueprint,"units",[]) if getattr(u,"number",None)==11),None)
    if unit is None:return blueprint
    durable=("Apply the source mechanism to one concrete Saudi/Gulf constraint; "
             "keep that local context explicitly hypothetical unless P1 supports it.")
    content=list(getattr(unit,"pedagogy_content",[]) or [])
    if content:content[0]=durable
    else:content=[durable]
    unit.pedagogy_content=content
    return blueprint

def _write_json(job,path:Path)->None:
    payload=job.blueprint.model_dump(mode="json") if hasattr(job.blueprint,"model_dump") else job.blueprint
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")

def _warm_exports(job_id:str)->None:
    lock=_job_lock(job_id)
    if not lock.acquire(blocking=False):return
    try:
        try:job=base._presenter_job(job_id)
        except Exception:return
        if not getattr(job,"blueprint",None):return
        paths=_cache_paths(job_id);source_root=engine.UPLOADS/job_id
        if not _good(paths["json"]):_write_json(job,paths["json"])
        if not _good(paths["pptx"],1024):base.export_presenter_pptx(job.blueprint,paths["pptx"],source_root=source_root,release_state=job.status)
        if not _good(paths["presenter-pdf"],1024):base.export_presenter_pdf(job.blueprint,paths["presenter-pdf"],source_root=source_root,release_state=job.status)
        if not _good(paths["pdf"],512):export_detailed_pdf(job.blueprint,paths["pdf"])
        if not _good(paths["docx"],512):export_instructor_guide(job.blueprint,paths["docx"])
        if not _good(paths["student"],512):export_student_pack(job.blueprint,paths["student"])
    except Exception as exc:
        print(f"ISCARB export warmup failed for {job_id}: {exc!r}",flush=True)
    finally:lock.release()

def _ensure_export(job_id:str,fmt:str)->Path:
    paths=_cache_paths(job_id)
    canonical={"pptx":"pptx","presenter-pdf":"presenter-pdf","presenter_pdf":"presenter-pdf","visual-pdf":"presenter-pdf","pdf":"pdf","docx":"docx","student":"student","json":"json"}.get(fmt)
    if canonical is None:raise HTTPException(404,"Unknown export format")
    path=paths[canonical];minimum=64 if canonical=="json" else 512
    if _good(path,minimum):return path
    lock=_job_lock(job_id)
    with lock:
        if _good(path,minimum):return path
        job=base._presenter_job(job_id)
        if not getattr(job,"blueprint",None):raise HTTPException(409,"The lecture draft is not ready for export yet.")
        source_root=engine.UPLOADS/job_id
        try:
            if canonical=="json":_write_json(job,path)
            elif canonical=="pptx":base.export_presenter_pptx(job.blueprint,path,source_root=source_root,release_state=job.status)
            elif canonical=="presenter-pdf":base.export_presenter_pdf(job.blueprint,path,source_root=source_root,release_state=job.status)
            elif canonical=="pdf":export_detailed_pdf(job.blueprint,path)
            elif canonical=="docx":export_instructor_guide(job.blueprint,path)
            elif canonical=="student":export_student_pack(job.blueprint,path)
        except Exception as exc:
            raise HTTPException(500,f"Export failed: {type(exc).__name__}: {exc}") from exc
    if not _good(path,64):raise HTTPException(500,"The export finished without producing a usable file.")
    return path

def apply_v671_patch(app)->None:
    global _PATCHED
    if _PATCHED:return
    _PATCHED=True
    original_draft=engine._source_preserving_draft
    def patched_draft(profile,bundle):return _ensure_u11_contract(original_draft(profile,bundle))
    engine._source_preserving_draft=patched_draft
    base.engine._source_preserving_draft=patched_draft
    original_update=engine._update
    def patched_update(job,status,progress,message):
        result=original_update(job,status,progress,message)
        if status in {"ready","blocked"} and getattr(job,"blueprint",None):
            try:engine.executor.submit(_warm_exports,job.id)
            except Exception as exc:print(f"ISCARB could not schedule export warmup for {job.id}: {exc!r}",flush=True)
        return result
    engine._update=patched_update
    app.router.routes[:]=[route for route in app.router.routes if getattr(route,"path",None)!="/api/jobs/{job_id}/export/{fmt}"]
    @app.get("/api/jobs/{job_id}/exports-status")
    def v671_exports_status(job_id:str):
        base._presenter_job(job_id);paths=_cache_paths(job_id)
        return {"pptx":_good(paths["pptx"],1024),"presenter_pdf":_good(paths["presenter-pdf"],1024),"reading_pdf":_good(paths["pdf"],512),"instructor_docx":_good(paths["docx"],512),"student_docx":_good(paths["student"],512),"json":_good(paths["json"],64)}
    @app.get("/api/jobs/{job_id}/export/{fmt}")
    def v671_cached_export(job_id:str,fmt:str):
        if fmt=="source-pdf":
            base._presenter_job(job_id);source=_find_local_primary_pdf(engine.UPLOADS/job_id)
            if source is None or not source.exists():raise HTTPException(404,"The original PDF is not available for this source type.")
            return FileResponse(source,filename=source.name,media_type="application/pdf")
        path=_ensure_export(job_id,fmt)
        media={".pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",".pdf":"application/pdf",".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",".json":"application/json"}.get(path.suffix.lower(),"application/octet-stream")
        return FileResponse(path,filename=path.name,media_type=media)
