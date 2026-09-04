from __future__ import annotations

"""ISCARB v6.8 source-locked production patch.

Restores the approved dark semantic presenter contract:
- P1/source visuals only; never opportunistic Wikipedia/public-web images.
- Approved dark v6.7 semantic renderer for preview/PPTX/PDF.
- 20 core units + genuine source overflow only.
- Versioned export cache so stale white/public-image files cannot be served.
- Source-only opening anchored to a real P1 statement instead of generic boilerplate.
"""

from pathlib import Path
import re

from . import main as engine
from . import start_v440 as base
from . import presenter_v67_prod as presenter
from . import presenter_v44
from . import source_visuals as sv
from . import source_visuals_v42 as sv42
from . import master_guidelines_v470 as master
from . import patch_v671 as reliability

_PATCHED = False


def _source_only_plan(bp, unit, registry=None):
    visual_type = sv.VISUAL_TYPES.get(unit.number, "concept-visual")
    purpose = sv.TEACHING_PURPOSE.get(unit.number, "Make the engineering decision visible.")
    anchor = (unit.source_anchor or "").strip()
    source_backed = sv._looks_source_backed(anchor)
    if registry and source_backed and unit.number in sv.SOURCE_VISUAL_PRIORITY:
        anchors = set(sv.anchor_slides(anchor))
        pool = [a for a in registry.assets if (not anchors or a.slide_number in anchors)]
        ranked = sorted(pool, key=lambda a: sv42._quality_score(a, unit, anchors), reverse=True)
        ranked = sv42._prefer_source_picture(ranked, unit, anchors)
        for asset in ranked:
            score = sv42._quality_score(asset, unit, anchors)
            if score >= 10.0 and not sv42._looks_like_title_only(asset) and sv42._is_presentable(asset):
                return sv.VisualPlan(
                    visual_type, purpose, "USE",
                    f"Source visual: [P1] Slide/Page {asset.slide_number} · {registry.source_title}",
                    True, asset.slide_number, asset, (unit.takeaway, unit.student_action),
                )
    return sv.VisualPlan(
        visual_type, purpose, "REDRAW" if source_backed else "NEW",
        anchor or "ISCARB pedagogy — native visualization",
        False, None, None, (unit.takeaway, unit.student_action),
    )


def _source_only_plans(bp, source_root=None):
    registry = sv.load_registry(bp, source_root=source_root)
    return [_source_only_plan(bp, u, registry) for u in bp.units]


def _balanced30_plan(bp):
    """Cover + U01-U20 + up to 8 real overflow pages + close.

    The domain-spine inventory remains coverage metadata and must not become a
    stack of list-only expansion slides.
    """
    plan = [("cover", None, None)]
    budget = 8
    x = 0
    for u in bp.units:
        plan.append(("unit", u, None))
        if budget <= 0:
            continue
        extra = [str(v).strip() for v in (u.overflow_content or []) if str(v).strip()]
        for i in range(0, len(extra), 6):
            if budget <= 0:
                break
            chunk = extra[i:i + 6]
            if not chunk:
                continue
            x += 1
            plan.append(("expansion", u, (x, chunk)))
            budget -= 1
    plan.append(("close", None, None))
    return plan


_FURNITURE = re.compile(
    r"^(chapter\s+\d+|\d{1,2}/\d{1,2}/\d{2,4}|security engineering\s*·?\s*chapter|primary source)$",
    re.I,
)


def _first_real_p1_statement(bp) -> str:
    for u in bp.units[5:15]:
        for raw in list(u.core_content or []):
            text = re.sub(r"\s+", " ", str(raw or "")).strip(" ·•-–—")
            if len(text.split()) < 7 or _FURNITURE.match(text):
                continue
            return text
    return ""


def _tighten_source_draft(bp, profile):
    try:
        u1 = bp.units[0]
        source_stake = _first_real_p1_statement(bp)
        if source_stake:
            u1.core_content = [source_stake]
        majors = [x for x in getattr(profile, "coverage_items", []) if getattr(x, "importance", "") == "major"]
        focus = str(majors[0].label or "").strip() if majors else ""
        if not focus:
            families = list(getattr(profile, "topic_families", []) or [])
            focus = str(families[0].name if families else profile.lecture_title).strip()
        crisis = str(getattr(profile, "industry_crisis", "") or "").strip()
        u1.title = "The engineering decision"
        u1.engineering_question = crisis or f"What decision about {focus} becomes unsafe if the source mechanism is misunderstood?"
        u1.pedagogy_content = [
            f"DECISION — identify the P1 mechanism that controls {focus} before choosing a solution.",
            "UNKNOWN — name the missing evidence that could reverse the decision.",
        ]
        u1.student_action = "State the decision, the missing evidence, and what would make you change your mind."
        u1.takeaway = "Begin with the source-supported stake and the evidence gap, not a generic scenario."
    except Exception:
        pass
    return bp


def _versioned_cache_paths(job_id: str) -> dict[str, Path]:
    root = engine.EXPORTS
    tag = "v680"
    return {
        "pptx": root / f"ISCARB_{job_id}_{tag}_Visual_Presenter.pptx",
        "presenter-pdf": root / f"ISCARB_{job_id}_{tag}_Visual_Presenter.pdf",
        "pdf": root / f"ISCARB_{job_id}_{tag}_Faculty_Reading_Pack.pdf",
        "docx": root / f"ISCARB_{job_id}_{tag}_Instructor_Guide.docx",
        "student": root / f"ISCARB_{job_id}_{tag}_Student_Activity_Pack.docx",
        "json": root / f"ISCARB_{job_id}_{tag}_Blueprint.json",
    }


def apply_v680_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    # Hard-disable every legacy public-image path. The only acceptable external
    # picture is one already inside the uploaded P1 source.
    if hasattr(sv, "_build_public_visual_for_unit"):
        sv._build_public_visual_for_unit = lambda *a, **k: None
    sv.plan_for_unit = _source_only_plan
    sv.plans_for_blueprint = _source_only_plans
    if hasattr(master, "_public_candidates"):
        master._public_candidates = lambda *a, **k: []
    if hasattr(master, "plans_for_blueprint_v470"):
        master.plans_for_blueprint_v470 = _source_only_plans
    if hasattr(sv42, "plans_for_blueprint_v42"):
        sv42.plans_for_blueprint_v42 = _source_only_plans
    if hasattr(presenter_v44, "plans_for_blueprint_v42"):
        presenter_v44.plans_for_blueprint_v42 = _source_only_plans

    # Approved dark visual contract and Balanced30 behavior.
    presenter._physical_plan = _balanced30_plan
    base.render_presenter_preview = presenter.render_presenter_preview
    base.export_presenter_pptx = presenter.export_presenter_pptx
    base.export_presenter_pdf = presenter.export_presenter_pdf

    # Source-only compile must use actual P1 content, not generic fallback prose.
    original_draft = engine._source_preserving_draft
    def source_locked_draft(profile, bundle):
        return _tighten_source_draft(original_draft(profile, bundle), profile)
    engine._source_preserving_draft = source_locked_draft
    base.engine._source_preserving_draft = source_locked_draft

    # A previous white/Public-image export must never be served from cache.
    reliability._cache_paths = _versioned_cache_paths
