from __future__ import annotations

"""ISCARB v8.0 — Hybrid Visual-Narrative Engine.

A source figure is never decorative: it must support an explicit learner action.
P1 remains the technical authority. Redraws are allowed only when labelled as
ISCARB redraws and are never represented as original source figures.
"""

from pathlib import Path
import json
import re
import time
from typing import Any

from fastapi import Body, HTTPException, Query
from fastapi.responses import FileResponse

from . import learning_experience as learning
from . import patch_v737_instructional_director as director
from . import patch_v732_native_figures_cues as figures
from . import presenter_v67_prod as presenter
from . import source_visuals as sv
from . import source_visuals_v42 as sv42
from . import start_v440 as base
from .hybrid_visual_engine import build_hybrid_visual_map, resolve_visual_path, classify_visual

VERSION = "8.0.0"
BUILD_ID = "8.0.0-hybrid-visual-narrative"
_PREV_STUDENT_PAGE = None
_PREV_SAVE_STATE = None
_PREV_HEALTH = None
_PREV_SOURCE_ASSET = None


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _tokens(value: str) -> set[str]:
    stop = {"the","and","for","with","from","into","that","this","what","which","how","why","unit","engineering","software","system","systems","student","source","primary","chapter","your","you"}
    return {w for w in re.findall(r"[A-Za-z][A-Za-z0-9+/#_.-]{2,}", _clean(value).lower()) if w not in stop}


def _asset_is_information_visual(asset) -> bool:
    low = _clean(getattr(asset, "alt_text", "")).lower()
    if getattr(asset, "source_kind", "") in {sv.FIGURE_KIND, sv.PICTURE_KIND}:
        return True
    # Vector diagrams in slide PDFs can have zero embedded-image area. These
    # title/label cues keep real graphs such as Cost/dependability eligible.
    cues = (
        "curve", "graph", "chart", "stack", "properties", "architecture", "diagram",
        "table", "process characteristic", "model", "redundancy", "diversity",
        "formal approaches", "refinement", "verification",
    )
    return any(cue in low for cue in cues)


def _presenter_source_asset(bp, unit, registry):
    if registry is None:
        return None
    unit_text = " ".join([
        _clean(getattr(unit, "title", "")), _clean(getattr(unit, "engineering_question", "")),
        _clean(getattr(unit, "student_action", "")), _clean(getattr(unit, "takeaway", "")),
        " ".join(_clean(x) for x in (getattr(unit, "core_content", []) or [])),
    ])
    ut = _tokens(unit_text)
    try:
        anchors = set(sv.anchor_slides(presenter._anchor(unit)))
    except Exception:
        anchors = set()

    # Keep one best representation per P1 page. Cropped figures/pictures beat
    # whole pages, except vector-only lecture pages where the whole render is the
    # actual diagram and must remain eligible.
    by_page: dict[int, list[Any]] = {}
    for asset in registry.assets:
        path = sv.local_asset(asset)
        if path and Path(path).exists() and int(asset.slide_number) != 1:
            by_page.setdefault(int(asset.slide_number), []).append(asset)
    candidates = []
    for page, items in by_page.items():
        def kind_rank(a):
            return 3 if a.source_kind == sv.FIGURE_KIND else 2 if a.source_kind == sv.PICTURE_KIND else 1
        candidates.append(max(items, key=lambda a: (kind_rank(a), float(getattr(a, "visual_area_ratio", 0.0)), len(_clean(a.alt_text)))))

    scored = []
    n = int(getattr(unit, "number", 0) or 0)
    for asset in candidates:
        text = _clean(asset.alt_text)
        low = text.lower()
        overlap = len(ut & _tokens(text))
        score = overlap * 3.0
        if asset.slide_number in anchors:
            score += 32.0
        if _asset_is_information_visual(asset):
            score += 12.0
        if asset.source_kind == sv.FIGURE_KIND:
            score += 9.0
        elif asset.source_kind == sv.PICTURE_KIND:
            score += 5.0
        if n == 8 and any(x in low for x in ("cost", "curve", "trade")):
            score += 26.0
        if n == 11 and any(x in low for x in ("stack", "layer", "architecture", "sociotechnical")):
            score += 24.0
        if n == 13 and any(x in low for x in ("redundancy", "diversity", "common")):
            score += 20.0
        if n in {12,14,15} and any(x in low for x in ("table", "process characteristic", "auditable", "documentable")):
            score += 16.0
        if n == 18 and any(x in low for x in ("formal", "verification", "proof", "refinement", "specification")):
            score += 18.0
        scored.append((score, asset))

    scored.sort(key=lambda x: x[0], reverse=True)
    if scored and scored[0][0] >= 12.0:
        asset = scored[0][1]
        path = sv.local_asset(asset)
        if path and Path(path).exists():
            return asset, path
    return _PREV_SOURCE_ASSET(bp, unit, registry) if _PREV_SOURCE_ASSET else None


def _student_page_v800(job_id: str) -> str:
    html = _PREV_STUDENT_PAGE(job_id)
    html = html.replace(
        "</head>",
        f"<link rel='stylesheet' href='/static/learning_v800.css?v={VERSION}'>\n</head>",
        1,
    )
    html = html.replace(
        "</body>",
        f"<script src='/static/learning_v800.js?v={VERSION}' defer></script>\n</body>",
        1,
    )
    return html


def _merge_safe_save(job_id: str, student_id: str, body: dict[str, Any]) -> dict[str, Any]:
    incoming = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    existing = learning._load_state(job_id, student_id).get("payload") or {}
    # v7.3.7 owns its in-memory state. v8 visual annotations are saved through a
    # dedicated endpoint, so preserve them when an older browser state autosaves.
    if "visual_annotations" not in incoming and existing.get("visual_annotations"):
        incoming = dict(incoming)
        incoming["visual_annotations"] = existing["visual_annotations"]
        body = dict(body)
        body["payload"] = incoming
    return _PREV_SAVE_STATE(job_id, student_id, body)


def _health_v800() -> dict[str, Any]:
    data = dict(_PREV_HEALTH()) if _PREV_HEALTH else {}
    data.update({
        "build_id": BUILD_ID,
        "hybrid_visual_narrative_version": VERSION,
        "hybrid_visual_policy": "P1 visual -> semantic classification -> 3-5 critical visuals -> narrative-unit mapping -> mandatory learner annotation; no decorative images.",
        "hybrid_visual_classes": ["graph", "diagram", "table", "formal-process", "figure", "photo", "source-page"],
        "hybrid_visual_layout": "50/50 source visual + analysis; click-to-zoom; source anchor always visible.",
        "hybrid_visual_evidence": "Click-to-pin annotation + decision note is stored as learner evidence.",
        "hybrid_table_policy": "P1 tables are extracted into interactive row cards when extraction is reliable.",
        "hybrid_quant_policy": "No numeric break-even claim unless P1 exposes a usable numeric scale or instructor supplies values.",
        "hybrid_redraw_policy": "ISCARB redraws must be labelled as redraws; they may not impersonate P1 figures.",
        "learning_autosave_seconds": 5,
    })
    return data


def apply_v800_hybrid_visual_narrative_patch(app) -> None:
    global _PREV_STUDENT_PAGE, _PREV_SAVE_STATE, _PREV_HEALTH, _PREV_SOURCE_ASSET
    if getattr(learning, "_V800_PATCHED", False):
        return
    learning._V800_PATCHED = True

    _PREV_STUDENT_PAGE = learning._student_page
    _PREV_SAVE_STATE = learning._save_state
    _PREV_HEALTH = base._health_v440
    _PREV_SOURCE_ASSET = presenter._source_asset_for_unit

    learning._student_page = _student_page_v800
    learning._save_state = _merge_safe_save
    learning.VERSION = VERSION
    director.VERSION = VERSION

    # Presenter exports now use the same semantic source-visual decision as the
    # interactive student surface. Add the narrative-role units that were not in
    # the older figure-first allowlist.
    presenter._source_asset_for_unit = _presenter_source_asset
    figures.FIGURE_UNITS.update({8, 11, 18})

    @app.get("/api/learning/{job_id}/hybrid-visuals")
    def hybrid_visuals(job_id: str, student_id: str = Query(...)):
        sid = learning._student_id(student_id)
        job = learning._load_job(job_id)
        result = build_hybrid_visual_map(job, max_critical=5)
        payload = learning._load_state(job_id, sid).get("payload") or {}
        result["visual_annotations"] = payload.get("visual_annotations") or {}
        return result

    @app.get("/api/learning/{job_id}/hybrid-visual/{key}")
    def hybrid_visual_file(job_id: str, key: str):
        job = learning._load_job(job_id)
        path = resolve_visual_path(job, key.lower())
        if path is None or not path.exists() or not path.is_file():
            raise HTTPException(404, "No source-backed visual is mapped to this learning step.")
        return FileResponse(path, media_type="image/png", headers={
            "Cache-Control": "private, max-age=300",
            "X-ISCARB-Visual-Provenance": "P1",
            "X-Content-Type-Options": "nosniff",
        })

    @app.post("/api/learning/{job_id}/visual-annotation")
    def save_visual_annotation(job_id: str, body: dict[str, Any] = Body(default_factory=dict)):
        learning._load_job(job_id)
        sid = learning._student_id(body.get("student_id", ""))
        key = str(body.get("unit_key") or "").strip().lower()
        if key != "u00" and not re.fullmatch(r"(?:[1-9]|1\d|20)", key):
            raise HTTPException(400, "unit_key must be u00 or a Unit number 1-20.")
        try:
            x = max(0.0, min(1.0, float(body.get("x", 0.5))))
            y = max(0.0, min(1.0, float(body.get("y", 0.5))))
        except Exception:
            raise HTTPException(400, "Annotation coordinates must be numeric fractions between 0 and 1.")
        note = learning._safe_text(body.get("note"), 1200)
        if len(note) < 8:
            raise HTTPException(400, "Explain in at least 8 characters why the marked visual element changes your decision.")
        state = learning._load_state(job_id, sid)
        payload = dict(state.get("payload") or {})
        annotations = dict(payload.get("visual_annotations") or {})
        annotations[key] = {"x": round(x, 4), "y": round(y, 4), "note": note, "updated_at": time.time()}
        payload["visual_annotations"] = annotations
        saved = _PREV_SAVE_STATE(job_id, sid, {"display_name": state.get("display_name", ""), "payload": payload})
        return {"saved": True, "annotation": annotations[key], "updated_at": saved.get("updated_at")}

    base._health_v440 = _health_v800
    base.engine.health = _health_v800
