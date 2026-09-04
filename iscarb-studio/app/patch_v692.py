from __future__ import annotations

"""ISCARB v6.9.2: hard source-native release lock and stale-export bust."""
import os
from pathlib import Path

from . import main as engine
from . import start_v440 as base
from . import patch_v671 as reliability
from . import patch_v690 as v690
from . import source_visuals as sv
from . import source_visuals_v42 as sv42
from . import master_guidelines_v470 as master
from . import presenter_v44
from . import presenter_v67_prod as presenter

PUBLIC_VERSION = "6.9.2"
PIPELINE_ID = "faculty-studio-v6.9.2-source-native-release-lock"
_PATCHED = False


def _cache_paths(job_id: str) -> dict[str, Path]:
    """Never serve an export produced before the v6.9.2 visual/release contract."""
    root = engine.EXPORTS
    tag = "v692"
    return {
        "pptx": root / f"ISCARB_{job_id}_{tag}_Visual_Presenter.pptx",
        "presenter-pdf": root / f"ISCARB_{job_id}_{tag}_Visual_Presenter.pdf",
        "pdf": root / f"ISCARB_{job_id}_{tag}_Faculty_Reading_Pack.pdf",
        "docx": root / f"ISCARB_{job_id}_{tag}_Instructor_Guide.docx",
        "student": root / f"ISCARB_{job_id}_{tag}_Student_Activity_Pack.docx",
        "json": root / f"ISCARB_{job_id}_{tag}_Blueprint.json",
    }


def apply_v692_patch(app) -> None:
    """Re-assert the approved policy at the last production patch point.

    Older presenter modules remain in the image for compatibility, so the final
    patch deliberately overwrites every public-image hook after all earlier
    modules have imported. This makes the runtime order deterministic:
    P1 source figure -> native diagram -> local-context/generated visual -> text-first.
    """
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    os.environ["ISCARB_DISABLE_PUBLIC_IMAGES"] = "1"
    os.environ["ISCARB_VISUAL_POLICY"] = "p1-source>native>local-context>text-first"

    # Final hard kill for the legacy public-web keyword fallback.
    if hasattr(sv, "_build_public_visual_for_unit"):
        sv._build_public_visual_for_unit = lambda *a, **k: None
    if hasattr(master, "_public_candidates"):
        master._public_candidates = lambda *a, **k: []
    master.PUBLIC_VISUAL_UNITS = frozenset()

    # Keep every live presenter entry point on the strict v6.9 source/native planner.
    sv.plan_for_unit = v690._strict_plan
    sv.plans_for_blueprint = v690._strict_plans
    sv.local_asset = v690._safe_local_asset
    if hasattr(sv42, "plans_for_blueprint_v42"):
        sv42.plans_for_blueprint_v42 = v690._strict_plans
    if hasattr(presenter_v44, "plans_for_blueprint_v42"):
        presenter_v44.plans_for_blueprint_v42 = v690._strict_plans
    for name in ("plans_for_blueprint_v470", "plans_for_blueprint_v42", "plans_for_blueprint"):
        if hasattr(presenter, name):
            setattr(presenter, name, v690._strict_plans)
    if hasattr(presenter, "local_asset"):
        presenter.local_asset = v690._safe_local_asset
    if hasattr(presenter, "_public_candidates"):
        presenter._public_candidates = lambda *a, **k: []

    # v6.9.1 changed the opening selector but retained a v6.9.0 cache name.
    # Busting the cache here guarantees Chapter 13 is rebuilt under the current
    # crisis, Domain Spine and visual rules rather than re-serving an older PDF.
    reliability._cache_paths = _cache_paths

    base.PUBLIC_VERSION = PUBLIC_VERSION
    base.PIPELINE_ID = PIPELINE_ID
    try:
        from . import start_v670_prod as prod
        prod.PUBLIC_VERSION = PUBLIC_VERSION
        prod.PIPELINE_ID = PIPELINE_ID
    except Exception:
        pass

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "version": PUBLIC_VERSION,
            "pipeline": PIPELINE_ID,
            "visual_policy": "P1 source figure -> native diagram -> generated/local-context visual -> text-first",
            "public_web_image_fallback": False,
            "public_web_keyword_search": "DISABLED",
            "domain_spine": "curated 5-8 chapter-level nodes; full source coverage kept outside the spine",
            "opening_crisis": "explicit source incident/failure or REVIEW REQUIRED; generic crisis cannot release",
            "export_cache": "v692 — stale v6.9.0/v6.9.1 presenter exports are not reused",
            "presenter_contract": "BlackNative/TextGold; 20 core units; source expansion only when warranted",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
