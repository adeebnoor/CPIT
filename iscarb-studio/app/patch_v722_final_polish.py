from __future__ import annotations

"""Final production polish: no legacy health/library residue and one visible presenter contract."""

import re
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

_REVIEW_REQUIRED = re.compile(r"\breview\s+required\b", re.I)


def _scrub_text(value):
    if not isinstance(value, str):
        return value
    return _REVIEW_REQUIRED.sub("faculty inspection needed", value)


def _scrub_list(values):
    if values is None:
        return values
    try:
        return [_scrub_text(x) if isinstance(x, str) else x for x in values]
    except TypeError:
        return values


def _scrub_review_required(bp):
    """Remove residual gate wording from learner/package metadata without weakening review semantics."""
    for attr in ("lecture_title","central_engineering_crisis","engineering_thesis"):
        if hasattr(bp, attr):
            try:
                setattr(bp, attr, _scrub_text(getattr(bp, attr)))
            except Exception:
                pass
    for u in list(getattr(bp,"units",[]) or []):
        for attr in ("title","engineering_question","student_action","takeaway","source_anchor"):
            if hasattr(u, attr):
                try:
                    setattr(u, attr, _scrub_text(getattr(u, attr)))
                except Exception:
                    pass
        for attr in ("core_content","pedagogy_content","scenario_assumptions","enrichment_content","enrichment_basis"):
            if hasattr(u, attr):
                try:
                    setattr(u, attr, _scrub_list(getattr(u, attr)))
                except Exception:
                    pass
        plan=getattr(u,"visual_plan",None)
        if plan is not None:
            field_names=list(getattr(type(plan),"model_fields",{}) or []) or ["visual_evidence_role","design_brief","annotation_plan","provenance","visual_kind"]
            for attr in field_names:
                if hasattr(plan, attr):
                    try:
                        val=getattr(plan, attr)
                        if isinstance(val, str):
                            setattr(plan, attr, _scrub_text(val))
                        elif isinstance(val, list):
                            setattr(plan, attr, _scrub_list(val))
                    except Exception:
                        pass
    return bp


def _ensure_blackbox(bp):
    units=list(getattr(bp,"units",[]) or [])
    if len(units)>=15:
        u=units[14]
        ai=any(str(x).upper().startswith("AI ASSURANCE LENS") for x in (getattr(u,"pedagogy_content",[]) or []))
        if ai and not any(str(x).upper().startswith("BLACK-BOX TEST") for x in (u.pedagogy_content or [])):
            u.pedagogy_content.append("BLACK-BOX TEST — If a model decision cannot be explained directly, require observable evidence that makes behavior auditable to an independent reviewer or regulator.")
    return bp


def _final_blueprint_clean(bp):
    return _scrub_review_required(_ensure_blackbox(bp))


def _install_final_close_patch():
    p=presenter

    def ppt_close(slide,bp,total):
        p._ppt_bg(slide); p._ppt_text(slide,.7,.6,3.0,.25,"ISCARB · CLOSE",8.5,p.CYAN,True)
        p._ppt_text(slide,.7,1.18,9.0,.5,"Bounded engineering verdict",25,p.TEXT,True)
        p._ppt_text(slide,.7,1.85,9.4,.55,"The lecture closes only after the assurance chain is inspectable.",13,p.MUTED)
        labs=["CLAIM","EVIDENCE","WARRANT","COUNTER-EVIDENCE","RESIDUAL UNCERTAINTY","VERDICT"]
        for i,lab in enumerate(labs): p._ppt_box(slide,.62+i*2.08,3.0,1.82,1.55,lab,"",[p.CYAN,p.GOLD,p.BLUE,p.MAGENTA,p.GREEN,p.DANGER][i],title_size=8.2)
        p._ppt_text(slide,.7,5.4,10.8,.55,"TAKE-HOME CHECKPOINT · State the final verdict and the one piece of evidence that would make you revisit it.",10.5,p.TEXT,True)
        p._ppt_text(slide,11.0,6.78,1.95,.25,f"CLOSE · {total:02d}/{total:02d}",7.4,p.MUTED,False,p.PP_ALIGN.RIGHT)
    p._ppt_close=ppt_close

    def pdf_close(c,bp,total):
        c.setFillColor(p.HexColor(p.BG)); c.rect(0,0,960,540,fill=1,stroke=0)
        p._pdf_text(c,50,485,180,18,"ISCARB · CLOSE",7.5,p.CYAN,True,max_lines=1)
        p._pdf_text(c,50,425,620,42,"Bounded engineering verdict",23,p.TEXT,True,max_lines=1)
        p._pdf_text(c,50,380,680,30,"The lecture closes only after the assurance chain is inspectable.",11,p.MUTED,max_lines=2)
        labs=["CLAIM","EVIDENCE","WARRANT","COUNTER-EVIDENCE","RESIDUAL UNCERTAINTY","VERDICT"]
        for i,lab in enumerate(labs): p._pdf_box(c,25+i*155,220,140,90,lab,"",[p.CYAN,p.GOLD,p.BLUE,p.MAGENTA,p.GREEN,p.DANGER][i],title_size=6.5)
        p._pdf_text(c,50,145,760,30,"TAKE-HOME CHECKPOINT · State the final verdict and the one piece of evidence that would make you revisit it.",8.5,p.TEXT,True,max_lines=2)
        p._pdf_text(c,795,55,140,16,f"CLOSE · {total:02d}/{total:02d}",6.4,p.MUTED,False,"right",1)
    p._pdf_close=pdf_close


def apply_v722_final_polish(app):
    global _PATCHED
    if _PATCHED:return
    _PATCHED=True

    _install_final_close_patch()

    # Make the actual faculty-facing route globals use the final production renderer.
    faculty_main.export_presenter_pptx=presenter.export_presenter_pptx
    faculty_main.render_presenter_preview=presenter.render_presenter_preview
    faculty_main.export_presenter_pdf=presenter.export_presenter_pdf

    # Last blueprint pass: preserve black-box auditability and remove residual gate wording.
    previous=engine._source_preserving_draft
    def final_draft(profile,bundle):return _final_blueprint_clean(previous(profile,bundle))
    engine._source_preserving_draft=final_draft
    base.engine._source_preserving_draft=final_draft

    previous_timebox=engine.apply_90_minute_timebox
    def final_timebox(blueprint,profile,bundle):return _final_blueprint_clean(previous_timebox(blueprint,profile,bundle))
    engine.apply_90_minute_timebox=final_timebox
    base.engine.apply_90_minute_timebox=final_timebox

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
            "close_slide_legacy_task_label":False,
        })
        return data
