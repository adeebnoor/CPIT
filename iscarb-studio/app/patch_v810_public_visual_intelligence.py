from __future__ import annotations

"""ISCARB v8.1 — licensed public visual intelligence layer."""

from pathlib import Path
import os
import re
import time
from typing import Any
from urllib.request import Request, urlopen

from fastapi import Body, Header, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse

from . import learning_experience as learning
from . import patch_v737_instructional_director as director
from . import start_v440 as base
from .hybrid_visual_engine import build_hybrid_visual_map
from .public_image_search_v810 import (
    VERSION,
    cached_image_path,
    get_settings,
    public_visual_for_unit,
    save_settings,
    selected_candidate,
    selected_image_history,
)

BUILD_ID = "8.1.0-public-visual-intelligence"
_PREV_STUDENT_PAGE = None
_PREV_HEALTH = None


def _student_page_v810(job_id: str) -> str:
    html = _PREV_STUDENT_PAGE(job_id)
    html = html.replace(
        "</head>",
        f"<link rel='stylesheet' href='/static/learning_v810.css?v={VERSION}'>\n</head>",
        1,
    )
    html = html.replace(
        "</body>",
        f"<script src='/static/learning_v810.js?v={VERSION}' defer></script>\n</body>",
        1,
    )
    return html


def _health_v810() -> dict[str, Any]:
    data = dict(_PREV_HEALTH()) if _PREV_HEALTH else {}
    data.update({
        "build_id": BUILD_ID,
        "public_visual_intelligence_version": VERSION,
        "public_visual_search": "on-demand licensed search only when no suitable P1 visual exists",
        "public_visual_providers": {
            "openverse": True,
            "pexels_configured": bool(os.getenv("PEXELS_API_KEY", "").strip()),
            "pixabay_configured": bool(os.getenv("PIXABAY_API_KEY", "").strip()),
            "unsplash_configured": bool(os.getenv("UNSPLASH_ACCESS_KEY", "").strip()),
        },
        "public_visual_semantics": "Gemini-authored visual_plan/visual_suggestion -> 3-5 runtime search queries; deterministic fallback in source-only mode.",
        "public_visual_rank_weights": {"semantic":40,"quality":25,"license":20,"diversity":10,"recency":5},
        "public_visual_clip": "Optional local CLIP reranker; response metadata discloses clip_used and never labels lexical fallback as CLIP.",
        "public_visual_license_policy": "Exact provider/Creative Commons metadata is shown. Pexels/Pixabay/Unsplash are not mislabeled CC0.",
        "public_visual_fallback": "No arbitrary web image: explicit icon/no-image fallback; AI-generator hook remains opt-in by deployment configuration.",
        "public_visual_privacy": "Public images are server-proxied when provider terms permit; learner evidence stores opaque student id + annotation only.",
        "selected_image_registry": True,
        "visual_search_admin_settings": True,
        "learning_autosave_seconds": 5,
    })
    return data


def _p1_visual_exists(job, unit_no: int) -> bool:
    try:
        mapping = build_hybrid_visual_map(job, max_critical=5)
        return str(unit_no) in (mapping.get("units") or {})
    except Exception:
        return False


def _track_unsplash(candidate) -> None:
    url = str(getattr(candidate, "download_tracking_url", "") or "").strip()
    if not url:
        return
    try:
        req = Request(url, headers={"Authorization": f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY','').strip()}", "User-Agent":"ISCARB-Lecture-Studio/8.1"})
        with urlopen(req, timeout=3) as resp:
            resp.read(256)
    except Exception:
        # Tracking failure must not convert a licensed recommendation into a
        # fabricated local image. The client will still use the provider's own
        # hotlinked URL and visible attribution.
        pass


def apply_v810_public_visual_intelligence_patch(app) -> None:
    global _PREV_STUDENT_PAGE, _PREV_HEALTH
    if getattr(learning, "_V810_PATCHED", False):
        return
    learning._V810_PATCHED = True

    _PREV_STUDENT_PAGE = learning._student_page
    _PREV_HEALTH = base._health_v440
    learning._student_page = _student_page_v810
    learning.VERSION = VERSION
    director.VERSION = VERSION

    @app.get("/api/learning/{job_id}/public-visual/{unit_no}")
    def public_visual(job_id: str, unit_no: int, student_id: str = Query(...)):
        learning._student_id(student_id)
        if unit_no < 1 or unit_no > 20:
            raise HTTPException(400, "unit_no must be 1-20.")
        job = learning._load_job(job_id)
        result = public_visual_for_unit(job, unit_no, p1_visual_exists=_p1_visual_exists(job, unit_no))
        return result

    @app.get("/api/learning/{job_id}/public-visual-image/{unit_no}")
    def public_visual_image(job_id: str, unit_no: int):
        learning._load_job(job_id)
        if unit_no < 1 or unit_no > 20:
            raise HTTPException(400, "unit_no must be 1-20.")
        candidate = selected_candidate(job_id, unit_no)
        if candidate is None:
            raise HTTPException(404, "No licensed public visual has been selected for this Unit.")
        if candidate.delivery_mode == "hotlink":
            if candidate.provider.lower() == "unsplash":
                _track_unsplash(candidate)
            return RedirectResponse(candidate.image_url, status_code=307, headers={
                "Cache-Control":"private, max-age=180",
                "X-ISCARB-Visual-Provenance":"external-licensed",
            })
        path = cached_image_path(job_id, unit_no)
        if path is None or not Path(path).exists():
            raise HTTPException(502, "The selected public image could not be materialized safely.")
        media = "image/png" if path.suffix.lower() == ".png" else "image/webp" if path.suffix.lower() == ".webp" else "image/gif" if path.suffix.lower() == ".gif" else "image/jpeg"
        return FileResponse(path, media_type=media, headers={
            "Cache-Control":"private, max-age=86400",
            "X-ISCARB-Visual-Provenance":"external-licensed",
            "X-Content-Type-Options":"nosniff",
        })

    @app.post("/api/learning/{job_id}/public-visual-annotation")
    def save_public_visual_annotation(job_id: str, body: dict[str, Any] = Body(default_factory=dict)):
        learning._load_job(job_id)
        sid = learning._student_id(body.get("student_id", ""))
        try:
            unit_no = int(body.get("unit_no"))
        except Exception:
            raise HTTPException(400, "unit_no must be 1-20.")
        if unit_no < 1 or unit_no > 20:
            raise HTTPException(400, "unit_no must be 1-20.")
        candidate = selected_candidate(job_id, unit_no)
        if candidate is None:
            raise HTTPException(409, "No selected public visual exists for this Unit.")
        try:
            x = max(0.0, min(1.0, float(body.get("x", .5))))
            y = max(0.0, min(1.0, float(body.get("y", .5))))
            radius = max(.025, min(.30, float(body.get("radius", .075))))
        except Exception:
            raise HTTPException(400, "Annotation coordinates/radius must be numeric fractions.")
        note = learning._safe_text(body.get("note"), 1200)
        if len(note) < 8:
            raise HTTPException(400, "Explain why the selected image region changes your engineering decision.")
        state = learning._load_state(job_id, sid)
        payload = dict(state.get("payload") or {})
        annotations = dict(payload.get("public_visual_annotations") or {})
        annotations[str(unit_no)] = {
            "x":round(x,4), "y":round(y,4), "radius":round(radius,4), "note":note,
            "provider":candidate.provider, "provider_id":candidate.provider_id,
            "license_label":candidate.license_label, "landing_url":candidate.landing_url,
            "updated_at":time.time(),
        }
        payload["public_visual_annotations"] = annotations
        saved = learning._save_state(job_id, sid, {"display_name":state.get("display_name", ""), "payload":payload})
        return {"saved":True, "annotation":annotations[str(unit_no)], "updated_at":saved.get("updated_at")}

    @app.get("/api/learning/{job_id}/visual-search-settings")
    def visual_search_settings(job_id: str, x_iscarb_instructor_key: str = Header(default="")):
        learning._load_job(job_id)
        learning._require_instructor_key(job_id, x_iscarb_instructor_key)
        return get_settings(job_id)

    @app.put("/api/learning/{job_id}/visual-search-settings")
    def update_visual_search_settings(job_id: str, body: dict[str, Any] = Body(default_factory=dict), x_iscarb_instructor_key: str = Header(default="")):
        learning._load_job(job_id)
        learning._require_instructor_key(job_id, x_iscarb_instructor_key)
        return save_settings(body, job_id)

    @app.get("/api/learning/{job_id}/selected-image-history")
    def image_history(job_id: str, limit: int = Query(default=100, ge=1, le=500), x_iscarb_instructor_key: str = Header(default="")):
        learning._load_job(job_id)
        learning._require_instructor_key(job_id, x_iscarb_instructor_key)
        return {"items":[x for x in selected_image_history(limit) if x.get("lecture_id") == job_id]}

    base._health_v440 = _health_v810
    base.engine.health = _health_v810
