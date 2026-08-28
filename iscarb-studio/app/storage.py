from __future__ import annotations

from pathlib import Path
from threading import Lock

from .models import JobState

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
JOBS = DATA / "jobs"
UPLOADS = DATA / "uploads"
JOBS.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)
_LOCK = Lock()


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
