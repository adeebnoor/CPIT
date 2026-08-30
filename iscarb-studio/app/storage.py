from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from threading import Lock

from .models import JobState

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
JOBS = DATA / "jobs"
UPLOADS = DATA / "uploads"
EXPORTS = DATA / "exports"
# Rasterized source pages are large and regenerate on demand, so they expire
# with everything else rather than growing without bound.
VISUAL_CACHE = DATA / "source_visual_cache"
JOBS.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)
_LOCK = Lock()

# Faculty download their outputs in the same working session. Keeping raw
# uploads and rendered exports forever is what eventually fills the container
# disk and takes the whole service down for everyone.
RETENTION_HOURS = int(os.getenv("ISCARB_RETENTION_HOURS", "48"))


def save_job(job: JobState) -> None:
    with _LOCK:
        path = JOBS / f"{job.id}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(job.model_dump_json(indent=2), encoding="utf-8")
        tmp.replace(path)


def load_job(job_id: str) -> JobState:
    path = JOBS / f"{job_id}.json"
    if not path.exists():
        raise FileNotFoundError(job_id)
    return JobState.model_validate_json(path.read_text(encoding="utf-8"))


def upload_path(job_id: str, original_name: str) -> Path:
    safe = "".join(c for c in Path(original_name).name if c.isalnum() or c in "._- ") or "lecture"
    return UPLOADS / f"{job_id}__{safe}"


def prune_expired(now: float | None = None) -> int:
    """Delete job records, uploads and exports older than the retention window.

    Returns the number of filesystem entries removed. Never raises: a failed
    prune must not take down a compile request.
    """
    if RETENTION_HOURS <= 0:
        return 0
    cutoff = (now if now is not None else time.time()) - RETENTION_HOURS * 3600
    removed = 0
    for directory in (JOBS, UPLOADS, EXPORTS, VISUAL_CACHE):
        if not directory.exists():
            continue
        for entry in directory.iterdir():
            try:
                if entry.stat().st_mtime >= cutoff:
                    continue
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    entry.unlink(missing_ok=True)
                removed += 1
            except OSError:
                continue
    return removed
