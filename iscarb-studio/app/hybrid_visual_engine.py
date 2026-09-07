from __future__ import annotations

"""ISCARB v8.0 hybrid visual-narrative engine.

This layer does not manufacture source visuals. It reuses P1 assets already
rendered by ``source_visuals`` and adds: semantic classification, criticality,
unit mapping, accessible alt text, table-to-card extraction, and source-safe
interaction prompts. The primary source remains authoritative.
"""

from dataclasses import dataclass, asdict
from functools import lru_cache
from pathlib import Path
import re
from typing import Any

import pdfplumber

from . import source_visuals as sv
from .models import Blueprint, LectureUnit
from .storage import UPLOADS

_STOP = {
    "the", "and", "for", "with", "from", "into", "that", "this", "what", "which",
    "how", "why", "unit", "engineering", "software", "system", "systems", "student",
    "students", "lecture", "source", "primary", "chapter", "using", "used", "use",
    "your", "you", "are", "was", "were", "will", "may", "must", "should", "can",
}

_GRAPH = ("curve", "graph", "chart", "trend", "cost", "probability", "rate", "distribution", "histogram")
_TABLE = ("table", "characteristic description", "attribute", "criteria", "matrix")
_DIAGRAM = (
    "diagram", "stack", "architecture", "model", "properties", "structure", "flow",
    "layer", "layers", "pipeline", "network", "mechanism", "component", "components",
    "redundancy", "diversity", "refinement", "transformation",
)
_FORMAL = ("formal method", "formal specification", "verification", "proof", "refinement", "b method")


@dataclass(frozen=True)
class HybridVisual:
    page: int
    category: str
    criticality: float
    title: str
    alt_text: str
    surrounding_text: str
    source_anchor: str
    source_kind: str
    local_path: str
    interaction_prompt: str
    table_cards: tuple[dict[str, str], ...] = ()
    numeric_scale_present: bool = False


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _tokens(value: str) -> set[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+/#_.-]{2,}", _clean(value).lower())
    return {w for w in words if w not in _STOP}


def _title_from_text(text: str, fallback: str) -> str:
    parts = [x.strip() for x in str(text or "").splitlines() if x.strip()]
    if not parts:
        return fallback
    candidate = _clean(parts[0])
    return candidate[:120] if candidate else fallback


def classify_visual(asset: sv.VisualAsset) -> str:
    text = _clean(asset.alt_text).lower()
    if any(c in text for c in _TABLE):
        return "table"
    if any(c in text for c in _GRAPH):
        return "graph"
    if any(c in text for c in _FORMAL):
        return "formal-process"
    if any(c in text for c in _DIAGRAM):
        return "diagram"
    if asset.source_kind == sv.PICTURE_KIND:
        return "photo"
    if asset.source_kind == sv.FIGURE_KIND:
        return "figure"
    return "source-page"


def _pixel_size(asset: sv.VisualAsset) -> tuple[int, int] | None:
    path = sv.local_asset(asset)
    if not path or not Path(path).exists():
        return None
    try:
        from PIL import Image
        with Image.open(path) as im:
            return int(im.width), int(im.height)
    except Exception:
        return None


def _is_landscape(asset: sv.VisualAsset) -> bool:
    size = _pixel_size(asset)
    return bool(size and size[0] >= size[1])


def _numeric_scale_present(text: str) -> bool:
    # Multiple distinct numeric labels are required before a quantitative prompt
    # is allowed. One page number/date does not constitute a graph scale.
    nums = re.findall(r"(?<!\w)(?:\d+(?:\.\d+)?%?)(?!\w)", text or "")
    meaningful = [n for n in nums if not re.fullmatch(r"(?:19|20)\d{2}", n)]
    return len(set(meaningful)) >= 3


def _interaction_prompt(category: str, numeric_scale: bool) -> str:
    if category == "graph":
        if numeric_scale:
            return "Mark the point or region that changes your decision, then quantify the trade-off using only values visible in P1."
        return "Mark the point or region that changes your decision. P1 has no usable numeric scale here, so state what measurement would be needed before calculating a break-even point."
    if category in {"diagram", "formal-process", "figure"}:
        return "Mark the node, layer, relation, or transformation whose failure would most change your engineering decision, then explain why."
    if category == "table":
        return "Open the row that matters most, identify the criterion that changes your decision, and state what evidence would verify it."
    if category == "photo":
        return "Mark the visual feature that changes your interpretation of the engineering situation, then connect it to one source-backed claim."
    return "Mark the source element that most changes your engineering decision and explain the evidence it contributes."


def _criticality(asset: sv.VisualAsset, bp: Blueprint) -> float:
    text = _clean(asset.alt_text)
    low = text.lower()
    category = classify_visual(asset)
    score = 0.0
    if category in {"graph", "diagram", "table", "formal-process", "figure"}:
        score += 16.0
    elif category == "photo":
        score += 5.0
    if asset.source_kind == sv.FIGURE_KIND:
        score += 10.0
    elif asset.source_kind == sv.PICTURE_KIND:
        score += 6.0
    if asset.visual_area_ratio >= .20:
        score += 7.0
    if _is_landscape(asset):
        score += 4.0
    if asset.slide_number == 1:
        score -= 30.0

    bp_text = " ".join([
        _clean(bp.lecture_title), _clean(bp.engineering_thesis),
        " ".join(_clean(x) for x in (bp.source_topic_families or [])),
    ])
    score += min(18.0, len(_tokens(text) & _tokens(bp_text)) * 2.5)

    for cue in (
        "properties", "cost", "dependability", "stack", "architecture", "process",
        "table", "formal", "verification", "redundancy", "diversity", "risk", "model",
    ):
        if cue in low:
            score += 2.0
    return round(score, 2)


def _best_asset_per_page(registry: sv.VisualRegistry) -> list[sv.VisualAsset]:
    grouped: dict[int, list[sv.VisualAsset]] = {}
    for asset in registry.assets:
        path = sv.local_asset(asset)
        if not path or not Path(path).exists():
            continue
        grouped.setdefault(int(asset.slide_number), []).append(asset)

    out: list[sv.VisualAsset] = []
    for page, assets in grouped.items():
        # Prefer true crop > picture crop > high-information whole-page render.
        def rank(a: sv.VisualAsset) -> tuple[int, float, int]:
            kind_rank = 3 if a.source_kind == sv.FIGURE_KIND else 2 if a.source_kind == sv.PICTURE_KIND else 1
            return kind_rank, float(a.visual_area_ratio), len(_clean(a.alt_text))
        out.append(max(assets, key=rank))
    return sorted(out, key=lambda a: a.slide_number)


def _extract_table_cards(pdf_path: Path, page: int) -> tuple[dict[str, str], ...]:
    if page < 1:
        return ()
    try:
        with pdfplumber.open(str(pdf_path)) as doc:
            if page > len(doc.pages):
                return ()
            tables = doc.pages[page - 1].extract_tables() or []
    except Exception:
        return ()
    best: list[list[str | None]] | None = None
    for table in tables:
        if not table or len(table) < 2:
            continue
        if best is None or len(table) > len(best):
            best = table
    if not best:
        return ()
    cards: list[dict[str, str]] = []
    for row in best[1:9]:
        if not row:
            continue
        left = _clean(row[0] if len(row) > 0 else "")
        right = _clean(row[1] if len(row) > 1 else "")
        if left and right:
            cards.append({"label": left[:120], "description": right[:520]})
    return tuple(cards)


def _hybrid_from_asset(asset: sv.VisualAsset, bp: Blueprint, pdf_path: Path | None) -> HybridVisual:
    text = _clean(asset.alt_text)
    category = classify_visual(asset)
    page = int(asset.slide_number)
    title = _title_from_text(asset.alt_text, f"P1 visual on page {page}")
    numeric = _numeric_scale_present(text)
    cards = _extract_table_cards(pdf_path, page) if pdf_path and category == "table" else ()
    return HybridVisual(
        page=page,
        category=category,
        criticality=_criticality(asset, bp),
        title=title,
        alt_text=f"Primary-source {category} from P1 page {page}: {title}",
        surrounding_text=text[:1800],
        source_anchor=f"[P1] Page {page}",
        source_kind=asset.source_kind,
        local_path=str(sv.local_asset(asset) or ""),
        interaction_prompt=_interaction_prompt(category, numeric),
        table_cards=cards,
        numeric_scale_present=numeric,
    )


def _unit_text(unit: LectureUnit) -> str:
    return " ".join([
        _clean(unit.title), _clean(unit.engineering_question), _clean(unit.student_action),
        _clean(unit.takeaway), " ".join(_clean(x) for x in (unit.core_content or [])),
    ])


def _anchor_bonus(unit: LectureUnit, page: int) -> float:
    try:
        anchors = set(sv.anchor_slides(_clean(unit.source_anchor)))
    except Exception:
        anchors = set()
    return 35.0 if page in anchors else 0.0


def _role_bonus(unit: LectureUnit, visual: HybridVisual) -> float:
    n = int(unit.number)
    low = (visual.title + " " + visual.surrounding_text).lower()
    score = 0.0
    if n == 8 and visual.category == "graph":
        score += 24.0
    if n == 8 and any(x in low for x in ("cost", "trade", "dependability", "benefit")):
        score += 18.0
    if n == 11 and visual.category in {"diagram", "figure"} and any(x in low for x in ("stack", "architecture", "layer", "system")):
        score += 24.0
    if n == 13 and any(x in low for x in ("redundancy", "diversity", "failure", "architecture")):
        score += 20.0
    if n in {12, 14, 15} and visual.category == "table":
        score += 16.0
    if n == 18 and any(x in low for x in ("formal", "verification", "proof", "refinement", "specification")):
        score += 18.0
    return score


def _mapping_score(unit: LectureUnit, visual: HybridVisual) -> float:
    ut = _tokens(_unit_text(unit))
    vt = _tokens(visual.title + " " + visual.surrounding_text)
    overlap = len(ut & vt)
    score = min(36.0, overlap * 3.0)
    score += _anchor_bonus(unit, visual.page)
    score += _role_bonus(unit, visual)
    score += visual.criticality * .16
    return round(score, 2)


def build_hybrid_visual_map(job: Any, max_critical: int = 5) -> dict[str, Any]:
    bp: Blueprint = job.blueprint
    root = UPLOADS / str(job.id)
    registry = sv.load_registry(bp, source_root=root)
    if registry is None:
        return {"u00": None, "units": {}, "critical_visuals": [], "source_policy": "No P1 visual registry was available; no image was fabricated."}

    pdf_path = sv._find_local_primary_pdf(root)
    visuals = [_hybrid_from_asset(a, bp, pdf_path) for a in _best_asset_per_page(registry)]
    # Do not let a title-only page outrank an actual visual-bearing teaching page.
    visuals = [v for v in visuals if v.page != 1 and v.local_path]
    ranked = sorted(visuals, key=lambda v: v.criticality, reverse=True)
    critical = ranked[: max(3, min(max_critical, len(ranked)))] if ranked else []

    # U00 prefers a conceptual overview / map. Never force a graph when a
    # concept diagram exists.
    u00_candidates = sorted(
        visuals,
        key=lambda v: (
            1 if v.category in {"diagram", "figure"} else 0,
            1 if any(x in (v.title + " " + v.surrounding_text).lower() for x in ("properties", "overview", "model", "map")) else 0,
            v.criticality,
        ),
        reverse=True,
    )
    u00 = u00_candidates[0] if u00_candidates else None

    mapping: dict[str, dict[str, Any]] = {}
    candidate_pool = critical or visuals
    for unit in bp.units:
        scored = sorted((( _mapping_score(unit, v), v) for v in candidate_pool), key=lambda x: x[0], reverse=True)
        if not scored:
            continue
        score, visual = scored[0]
        # An exact source anchor may be used even with modest lexical overlap;
        # otherwise require a real semantic connection.
        if score < 12.0:
            continue
        payload = asdict(visual)
        payload["mapping_score"] = score
        payload["image_url"] = f"/api/learning/{job.id}/hybrid-visual/{unit.number}"
        payload["unit"] = int(unit.number)
        mapping[str(unit.number)] = payload

    critical_payload = []
    for visual in critical:
        item = asdict(visual)
        item.pop("local_path", None)
        critical_payload.append(item)

    u00_payload = asdict(u00) if u00 else None
    if u00_payload:
        u00_payload["image_url"] = f"/api/learning/{job.id}/hybrid-visual/u00"
        u00_payload.pop("local_path", None)

    for item in mapping.values():
        item.pop("local_path", None)

    return {
        "version": "8.0.0",
        "u00": u00_payload,
        "units": mapping,
        "critical_visuals": critical_payload,
        "source_policy": "P1 visuals only. ISCARB redraws, when later used, must be explicitly labelled and may not impersonate P1 figures.",
        "quant_policy": "Numeric calculation is permitted only when P1 exposes a usable numeric scale or the instructor supplies explicit values; otherwise the learner defines the measurement needed.",
    }


def resolve_visual_path(job: Any, key: str) -> Path | None:
    bp: Blueprint = job.blueprint
    root = UPLOADS / str(job.id)
    registry = sv.load_registry(bp, source_root=root)
    if registry is None:
        return None
    pdf_path = sv._find_local_primary_pdf(root)
    visuals = [_hybrid_from_asset(a, bp, pdf_path) for a in _best_asset_per_page(registry)]
    visuals = [v for v in visuals if v.page != 1 and v.local_path]
    if not visuals:
        return None
    if key == "u00":
        ordered = sorted(
            visuals,
            key=lambda v: (
                1 if v.category in {"diagram", "figure"} else 0,
                1 if any(x in (v.title + " " + v.surrounding_text).lower() for x in ("properties", "overview", "model", "map")) else 0,
                v.criticality,
            ), reverse=True,
        )
        return Path(ordered[0].local_path) if ordered else None
    try:
        number = int(key)
    except Exception:
        return None
    unit = next((u for u in bp.units if int(u.number) == number), None)
    if unit is None:
        return None
    candidate_pool = sorted(visuals, key=lambda v: v.criticality, reverse=True)[:5] or visuals
    scored = sorted(((_mapping_score(unit, v), v) for v in candidate_pool), key=lambda x: x[0], reverse=True)
    if not scored or scored[0][0] < 12.0:
        return None
    return Path(scored[0][1].local_path)
