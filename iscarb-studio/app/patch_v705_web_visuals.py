from __future__ import annotations

"""ISCARB v7.0.8 - source-page figure registry for linked web lectures.

A linked HTML lecture is still P1. Its figures are treated like figures in an
uploaded P1 PDF: source figure first, then a native ISCARB redraw, then text-first.
Only figures authored into the supplied page are eligible; there is no public
image search or keyword fallback.

For HTML sources each figure is used at most once. Repeating the same risk diagram
across five slides is not visual pedagogy; after its best semantic match the other
units return to native, source-grounded diagrams. Local-PDF behavior stays exactly
on the approved v6.9.4 path so earlier lectures do not regress.
"""

import json
from pathlib import Path

from . import patch_v694 as latency
from . import source_visuals as sv
from . import source_visuals_v42 as sv42
from . import presenter_v44
from . import presenter_v67_prod as presenter
from . import start_v440 as base
from .url_source import WEB_IMAGE_MANIFEST

_PATCHED = False
SOURCE_WEB_KIND = "source-web"
WEB_FIGURE_REUSE_CAP = 1


def _source_url(bp) -> str:
    return str(sv.primary_url_from_manifest(getattr(bp, "source_manifest", []) or []) or "").strip()


def _manifest_candidates(bp, source_root: Path | None = None) -> list[Path]:
    candidates: list[Path] = []
    if source_root is not None:
        root = Path(source_root)
        if root.is_file():
            root = root.parent
        direct = root / WEB_IMAGE_MANIFEST
        if direct.exists():
            candidates.append(direct)
        try:
            candidates.extend(p for p in root.glob(f"**/{WEB_IMAGE_MANIFEST}") if p.is_file())
        except Exception:
            pass

    wanted_url = _source_url(bp)
    if wanted_url and sv.UPLOAD_ROOT.exists():
        try:
            for manifest in sv.UPLOAD_ROOT.glob(f"*/{WEB_IMAGE_MANIFEST}"):
                if manifest in candidates or not manifest.is_file():
                    continue
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if str(data.get("source_url") or "").strip() == wanted_url:
                    candidates.append(manifest)
        except Exception:
            pass
    return candidates


def _registry_from_manifest(bp, source_root: Path | None = None):
    wanted_url = _source_url(bp)
    for manifest in _manifest_candidates(bp, source_root):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            continue
        source_url = str(data.get("source_url") or "").strip()
        if wanted_url and source_url and source_url != wanted_url:
            continue
        assets = []
        for row in data.get("assets", []) or []:
            local_path = Path(str(row.get("local_path") or ""))
            if not local_path.exists() or local_path.stat().st_size < 1000:
                continue
            context = " · ".join(
                x for x in [str(row.get("alt_text") or "").strip(), str(row.get("context") or "").strip()]
                if x
            )[:1600]
            try:
                section = max(1, int(row.get("section") or 1))
            except Exception:
                section = 1
            assets.append(sv.VisualAsset(
                slide_number=section,
                image_url=str(row.get("image_url") or ""),
                alt_text=context or f"Primary source figure near section {section}",
                source_url=source_url,
                local_path=str(local_path),
                source_kind=SOURCE_WEB_KIND,
                visual_area_ratio=1.0,
            ))
        if assets:
            return sv.VisualRegistry(
                source_url or wanted_url or "source-web",
                str(data.get("source_title") or "Primary web lecture"),
                tuple(assets),
                SOURCE_WEB_KIND,
            )
    return None


def _source_first_load_registry(bp, source_root: Path | None = None):
    local_pdf_registry = latency._fast_load_registry(bp, source_root=source_root)
    if local_pdf_registry is not None:
        return local_pdf_registry
    return _registry_from_manifest(bp, source_root=source_root)


def _web_unique_plans(bp, source_root: Path | None = None):
    """Assign every embedded P1 web figure to only its strongest unit match."""
    registry = _source_first_load_registry(bp, source_root=source_root)
    if registry is None or registry.source_kind != SOURCE_WEB_KIND:
        # Delegate local-PDF and no-registry behavior to the original planner.
        return _PREVIOUS_PLANS(bp, source_root=source_root)

    # Start from native/source-grounded redraw plans. Then promote only the best
    # one-to-one unit/figure matches to USE.
    plans = [sv.plan_for_unit(bp, unit, None) for unit in bp.units]
    candidates: list[tuple[float, int, int]] = []
    for unit_index, unit in enumerate(bp.units):
        if unit.number not in sv.SOURCE_VISUAL_PRIORITY or not sv._looks_source_backed(unit.source_anchor or ""):
            continue
        anchors = set(sv.anchor_slides(unit.source_anchor or ""))
        for asset_index, asset in enumerate(registry.assets):
            score = sv._asset_score(asset, unit, anchors)
            if score >= 8.0:
                candidates.append((score, unit_index, asset_index))

    candidates.sort(key=lambda row: row[0], reverse=True)
    used_units: set[int] = set()
    used_assets: set[int] = set()
    for score, unit_index, asset_index in candidates:
        if unit_index in used_units or asset_index in used_assets:
            continue
        unit = bp.units[unit_index]
        asset = registry.assets[asset_index]
        plans[unit_index] = sv.VisualPlan(
            sv.VISUAL_TYPES.get(unit.number, "concept-visual"),
            sv.TEACHING_PURPOSE.get(unit.number, "Make the engineering decision visible."),
            "USE",
            f"Source figure: [P1] section {asset.slide_number} · {registry.source_title}",
            True,
            asset.slide_number,
            asset,
            (unit.takeaway, unit.student_action),
        )
        used_units.add(unit_index)
        used_assets.add(asset_index)
    return plans


_PREVIOUS_PLANS = sv.plans_for_blueprint


def apply_v705_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    sv.load_registry = _source_first_load_registry
    sv.plans_for_blueprint = _web_unique_plans
    for module in (sv42, presenter_v44, presenter):
        if hasattr(module, "load_registry"):
            setattr(module, "load_registry", _source_first_load_registry)
        if hasattr(module, "plans_for_blueprint"):
            setattr(module, "plans_for_blueprint", _web_unique_plans)

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "web_source_visuals": "v7.0.8-source-page-only-unique",
            "visual_priority": "P1 source figure > ISCARB native redraw > text-first",
            "linked_html_source_figures": True,
            "same_page_image_capture": True,
            "source_web_figure_reuse_cap": WEB_FIGURE_REUSE_CAP,
            "public_web_image_fallback": False,
            "random_keyword_image_search": False,
            "legacy_local_pdf_visuals_preserved": True,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
