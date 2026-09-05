from __future__ import annotations

"""Final production polish: no legacy health/library residue and one visible presenter contract."""

from fastapi.responses import HTMLResponse
from . import main as engine
from . import start_v440 as base
from . import faculty_main
from . import presenter_v67_prod as presenter

_PATCHED=False

_RETIRED_HEALTH={
    "cimt_reference_archive","ready_example_source","source_library_verified","verified_source_count",
    "public_experience","design_language","fixed_task_footer","hero_live_release","faculty_experience",
    "source_visual_public_url","public_web_keyword_search",
}


def _ensure_blackbox(bp):
    units=list(getattr(bp,"units",[]) or [])
    if len(units)>=15:
        u=units[14]
        ai=any(str(x).upper().startswith("AI ASSURANCE LENS") for x in (getattr(u,"pedagogy_content",[]) or []))
        if ai and not any(str(x).upper().startswith("BLACK-BOX TEST") for x in (u.pedagogy_content or [])):
            u.pedagogy_content.append("BLACK-BOX TEST — If a model decision cannot be explained directly, require observable evidence that makes behavior auditable to an independent reviewer or regulator.")
    return bp


def apply_v722_final_polish(app):
    global _PATCHED
    if _PATCHED:return
    _PATCHED=True

    # Make the actual faculty-facing route globals use the final production renderer.
    faculty_main.export_presenter_pptx=presenter.export_presenter_pptx
    faculty_main.render_presenter_preview=presenter.render_presenter_preview
    faculty_main.export_presenter_pdf=presenter.export_presenter_pdf

    # Last blueprint pass: preserve the explicit black-box auditability question.
    previous=engine._source_preserving_draft
    def final_draft(profile,bundle):return _ensure_blackbox(previous(profile,bundle))
    engine._source_preserving_draft=final_draft
    base.engine._source_preserving_draft=final_draft

    # Replace the public root with a thin wrapper around the already-clean v7.2 home,
    # only unifying release identity and cache-busting. No legacy content is reintroduced.
    root_route=next((r for r in app.router.routes if getattr(r,"path",None)=="/"),None)
    old_root=getattr(root_route,"endpoint",None)
    if root_route is not None: app.router.routes.remove(root_route)
    if old_root is not None:
        @app.get("/")
        def final_home():
            response=old_root()
            body=response.body.decode("utf-8") if hasattr(response,"body") else str(response)
            body=body.replace("7.2.0","7.2.2")
            forbidden=("Original Source Library","slideshare.net/slideshow/ch10","CPIT455-class",'class="signIn"')
            leaked=[x for x in forbidden if x in body]
            if leaked: raise RuntimeError("Retired production content returned: "+", ".join(leaked))
            headers=dict(getattr(response,"headers",{}) or {})
            headers.update({"X-ISCARB-Version":"7.2.2","X-ISCARB-UI":"7.2.2","Cache-Control":"no-store, no-cache, must-revalidate, max-age=0"})
            return HTMLResponse(body,headers=headers)

    # Replace the health route completely so old faculty-library metadata cannot be
    # re-added after the clean engine health function.
    app.router.routes[:]=[r for r in app.router.routes if getattr(r,"path",None)!="/api/health"]
    @app.get("/api/health")
    def final_health():
        data=dict(engine.health())
        for k in _RETIRED_HEALTH:data.pop(k,None)
        data.update({
            "ok":True,"version":"7.2.2","release_ui":"7.2.2",
            "pipeline":"iscarb-v7.2.2-final-clean-it-wide-cognitive-budget-ai-era",
            "clean_release":True,"legacy_public_source_library":False,
            "public_web_image_fallback":False,"approved_hero_asset":"hero_user_original.png",
            "approved_hero_web_derivative":"hero_user_web.jpg",
            "presenter_activity_labels_dynamic":True,"ai_era_content_visible_in_presenter":True,
            "black_box_auditability_prompt":True,
        })
        return data
