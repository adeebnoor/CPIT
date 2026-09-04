from __future__ import annotations

"""Generic-IT surface and complete source-bundle package for ISCARB production.

The pedagogy and source-lock stay fixed, but the product is course-agnostic across
Information Technology / computing. Faculty may provide one PRIMARY source as a
file or public URL plus up to seven optional supporting sources. P1 controls the
mandatory technical scope; supporting sources may clarify/evidence the same
lecture but never silently replace or expand P1.
"""

import json
import zipfile
from pathlib import Path

from fastapi import HTTPException

from . import main as engine
from . import patch_v671 as reliability
from . import start_v440 as base
from .free_workflow import authoring_prompt, load_bundle

_PATCHED = False
_ORIGINAL_ENSURE = None
PACKAGE_TAG = "generic-it-v2"
IT_SCOPE = (
    "Programming & software development",
    "Databases & data management",
    "Networks & infrastructure",
    "Cybersecurity",
    "AI & data science",
    "Cloud & distributed systems",
    "Human-computer interaction",
    "Systems & architecture",
    "IT governance & service management",
    "Other IT / computing",
)
ACCEPTED_FILES = ("PDF", "PPTX", "DOCX", "TXT", "MD")
PRIMARY_MODES = ("public website / direct public document URL", "uploaded file")
MAX_SUPPORTING_SOURCES = 7


def _safe_name(value: str, fallback: str = "lecture") -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in str(value or "")).strip()
    return cleaned[:120] or fallback


def _package_path(job_id: str) -> Path:
    return engine.EXPORTS / f"ISCARB_{job_id}_{PACKAGE_TAG}_Complete_Package.zip"


def _good_zip(path: Path) -> bool:
    try:
        if not path.exists() or path.stat().st_size < 4096:
            return False
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            return (
                "00_README.txt" in names
                and "06_Blueprint.json" in names
                and any(name.startswith("00_Original_Sources/P1__") for name in names)
            )
    except (OSError, zipfile.BadZipFile):
        return False


def _build_package(job_id: str) -> Path:
    global _ORIGINAL_ENSURE
    if _ORIGINAL_ENSURE is None:
        raise HTTPException(500, "Package exporter is not initialized.")

    job = base._presenter_job(job_id)
    if not getattr(job, "blueprint", None):
        raise HTTPException(409, "The lecture draft is not ready for download yet.")

    package = _package_path(job_id)
    if _good_zip(package):
        return package

    outputs = {
        "01_Visual_Presenter.pptx": _ORIGINAL_ENSURE(job_id, "pptx"),
        "02_Visual_Presenter.pdf": _ORIGINAL_ENSURE(job_id, "presenter-pdf"),
        "03_Faculty_Reading_Pack.pdf": _ORIGINAL_ENSURE(job_id, "pdf"),
        "04_Instructor_Guide.docx": _ORIGINAL_ENSURE(job_id, "docx"),
        "05_Student_Activity_Pack.docx": _ORIGINAL_ENSURE(job_id, "student"),
        "06_Blueprint.json": _ORIGINAL_ENSURE(job_id, "json"),
    }

    root = engine.UPLOADS / job_id
    try:
        bundle = load_bundle(job, root)
    except Exception as exc:
        raise HTTPException(409, "The original lecture sources are no longer available for packaging.") from exc

    lock = reliability._job_lock(job_id)
    with lock:
        if _good_zip(package):
            return package
        tmp = package.with_suffix(".tmp")
        tmp.unlink(missing_ok=True)
        try:
            with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                title = getattr(job.blueprint, "lecture_title", "Your IT lecture")
                readme = "\n".join([
                    "ISCARB — COMPLETE IT LECTURE PACKAGE",
                    f"Lecture: {title}",
                    f"Job: {job_id}",
                    f"State: {str(getattr(job, 'status', 'review')).upper()}",
                    "",
                    "SOURCE CONTRACT",
                    "P1 is the PRIMARY source and controls the mandatory lecture scope, terminology and conflict precedence.",
                    "S1..S7 are optional SUPPORTING sources. They may clarify, evidence, exemplify, contextualize or verify P1; they do not silently replace or expand the mandatory scope.",
                    "ISCARB accepts a primary public website/direct document URL or an uploaded PDF, PPTX, DOCX, TXT or MD file.",
                    "Up to seven additional files/URLs may be supplied for the same lecture.",
                    "",
                    "VISUAL CONTRACT",
                    "Source figure -> native ISCARB diagram -> local-context visual -> text-first.",
                    "Random/public keyword image fallback is disabled.",
                    "",
                    "CONTENTS",
                    "00_Original_Sources/  — exact uploaded/materialized P1 and supporting sources",
                    "01_Visual_Presenter.pptx",
                    "02_Visual_Presenter.pdf",
                    "03_Faculty_Reading_Pack.pdf",
                    "04_Instructor_Guide.docx",
                    "05_Student_Activity_Pack.docx",
                    "06_Blueprint.json",
                    "07_Authoring_Prompt.txt (when a source profile is available)",
                    "08_Source_Manifest.json",
                ])
                zf.writestr("00_README.txt", readme)

                # Preserve every source in the package, not only P1. This makes
                # multi-source jobs auditable and lets faculty keep the exact
                # evidence bundle beside the generated lecture.
                for item in bundle.items:
                    role_prefix = item.source_id or ("P1" if item.role == "primary" else "S")
                    arc = f"00_Original_Sources/{role_prefix}__{_safe_name(item.path.name, role_prefix + '-source')}"
                    zf.write(item.path, arc)

                for arcname, path in outputs.items():
                    zf.write(path, arcname)
                if getattr(job, "source_profile", None) is not None:
                    try:
                        zf.writestr("07_Authoring_Prompt.txt", authoring_prompt(job, bundle))
                    except Exception:
                        pass
                zf.writestr("08_Source_Manifest.json", json.dumps({
                    "lecture_focus": getattr(job, "lecture_focus", ""),
                    "source_manifest": list(getattr(job, "source_manifest", []) or []),
                    "source_hierarchy": {
                        "primary": "P1 controls mandatory technical scope, terminology and conflict precedence",
                        "supporting": "S1..S7 clarify/evidence the same lecture without silently replacing P1",
                    },
                    "accepted_primary_modes": list(PRIMARY_MODES),
                    "accepted_file_types": list(ACCEPTED_FILES),
                    "max_supporting_sources": MAX_SUPPORTING_SOURCES,
                    "it_scope": list(IT_SCOPE),
                    "scope_policy": "generic IT/computing; no CPIT-455 or Software Engineering course dependency",
                    "strict_20_unit_gate": "v15_complete_20_unit_grammar",
                }, ensure_ascii=False, indent=2))
            tmp.replace(package)
        finally:
            tmp.unlink(missing_ok=True)
    return package


def apply_generic_it_patch(app) -> None:
    global _PATCHED, _ORIGINAL_ENSURE
    if _PATCHED:
        return
    _PATCHED = True

    _ORIGINAL_ENSURE = reliability._ensure_export

    def ensure_export(job_id: str, fmt: str) -> Path:
        if str(fmt).lower() in {"package", "zip", "all"}:
            return _build_package(job_id)
        return _ORIGINAL_ENSURE(job_id, fmt)

    reliability._ensure_export = ensure_export

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "generic_it_scope": True,
            "course_hardcoding": False,
            "software_engineering_dependency": False,
            "it_scope_profile": "computing-wide-source-adaptive-v2",
            "supported_it_domains": list(IT_SCOPE),
            "primary_source_modes": list(PRIMARY_MODES),
            "accepted_file_types": list(ACCEPTED_FILES),
            "primary_source_exactly_one": True,
            "supporting_sources_enabled": True,
            "max_supporting_sources": MAX_SUPPORTING_SOURCES,
            "source_hierarchy": "P1 mandatory scope; S1..S7 optional clarification/evidence",
            "complete_package_export": True,
            "complete_package_format": "zip",
            "package_preserves_all_sources": True,
            "single_interface_language": True,
            "interface_languages": ["en", "ar"],
            "interface_default_language": "en",
            "strict_20_unit_contract": True,
            "strict_20_unit_gate": "v15_complete_20_unit_grammar",
            "unit_role_checks": "v15_unit01..v15_unit20",
            "approved_hero_asset": "hero_v672.webp",
            "approved_hero_blob": "600190c7bec39e20e0f1578682c11e94f0c9337e",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
