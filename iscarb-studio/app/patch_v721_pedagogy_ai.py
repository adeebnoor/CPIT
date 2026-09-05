from __future__ import annotations

"""ISCARB v7.2.1 pedagogy + AI-era dependability layer.

This layer does not widen P1's factual scope. It changes *how* the twenty fixed
ISCARB jobs are enacted in class, and adds clearly labelled contemporary
extensions only when the lecture context makes them pedagogically relevant.
"""

import re
from . import main as engine
from . import start_v440 as base

_PATCHED = False
_AI_CONTEXT = re.compile(
    r"\b(?:dependab\w*|reliab\w*|safety(?:-critical)?|security|assurance|formal methods?|"
    r"fault[- ]toler\w*|mission[- ]critical|safety[- ]critical|artificial intelligence|"
    r"machine learning|generative ai|\bai\b|\bllm\b|neural network|foundation model)\b", re.I,
)
_TPS_UNITS = {5, 8, 10, 14, 15}
_CORE_CASE_UNITS = {11, 12}
_POST_CLASS_UNITS = {16, 17, 18, 19}


def _text_blob(bp) -> str:
    parts=[getattr(bp,"lecture_title",""),getattr(bp,"engineering_thesis",""),getattr(bp,"central_engineering_crisis",""),*list(getattr(bp,"source_topic_families",[]) or [])]
    for u in getattr(bp,"units",[]) or []: parts.extend([getattr(u,"title",""),*list(getattr(u,"core_content",[]) or [])])
    return " ".join(str(x) for x in parts if str(x).strip())


def _replace_prefixed(items,prefix,value):
    out=[str(x) for x in (items or []) if not str(x).upper().startswith(prefix.upper())]; out.append(value); return out


def _set_activity_budget(bp):
    for u in list(getattr(bp,"units",[]) or []):
        n=int(getattr(u,"number",0) or 0)
        if n in _TPS_UNITS:
            u.student_action="THINK–PAIR–SHARE · 1 MIN — make one choice, compare with a partner, then state the evidence that would change it."
            if getattr(u,"planned_minutes",0)>0: u.planned_minutes=max(2,int(u.planned_minutes))
        elif n in _CORE_CASE_UNITS:
            u.student_action="CORE IN-CLASS CASE · 5–7 MIN — analyse the case as a team, defend one decision, and identify the evidence that would reverse it."
            u.planned_minutes=max(6,int(getattr(u,"planned_minutes",0) or 0))
        elif n in _POST_CLASS_UNITS:
            u.student_action="POST-CLASS ARTIFACT — complete or review the evidence artifact individually after class; submit a traceable decision and reversal condition."
            if getattr(u,"planned_minutes",0)>2: u.planned_minutes=2
        else:
            u.student_action="CHECKPOINT — follow the reasoning; respond only if the lecturer calls for a quick check."


def _add_case_scaffold(bp):
    units=list(getattr(bp,"units",[]) or [])
    if len(units)<11:return
    u=units[10]
    u.pedagogy_content=_replace_prefixed(u.pedagogy_content,"MICRO-EXAMPLE","MICRO-EXAMPLE — Before the full local case, trace one small change: a platform, library, device or service update invalidates a previously safe technical assumption. Check the affected requirement, independent evidence, decision, and reversal condition.")
    u.pedagogy_content=_replace_prefixed(u.pedagogy_content,"TRANSFER STEP","TRANSFER STEP — Apply the same sequence to the full case: observed change → affected requirement → independent evidence → decision → reversal condition.")


def _add_decision_boxes(bp):
    for u in list(getattr(bp,"units",[]) or [])[5:15]:
        u.pedagogy_content=_replace_prefixed(u.pedagogy_content,"DECISION BOX","DECISION BOX — What engineering decision does this source rule support, and what evidence would make you change that decision?")


def _add_peer_review_card(bp):
    units=list(getattr(bp,"units",[]) or [])
    if len(units)<19:return
    u=units[18]
    u.pedagogy_content=_replace_prefixed(u.pedagogy_content,"PEER-REVIEW CARD","PEER-REVIEW CARD — (1) Can another person independently inspect the evidence? (2) What variable or edge case would invalidate the claim?")
    u.student_action="POST-CLASS ARTIFACT — use the full 6×4 rubric after class; in class use only the two-question peer-review card."


def _add_ai_era_dependability(bp):
    if not _AI_CONTEXT.search(_text_blob(bp)):return
    units=list(getattr(bp,"units",[]) or [])
    if len(units)<15:return
    u12=units[11]
    item="AI-ERA ASSURANCE — AI may prepare code, tests, summaries or evidence, but assurance ownership remains human. Sign-off requires independently inspectable evidence, explicit edge cases, and a named reversal condition."
    if item not in u12.enrichment_content:
        u12.enrichment_content.append(item); u12.enrichment_basis.append("ISCARB contemporary extension — not asserted as P1 content")
    u12.contextual_enrichment=True
    u13=units[12]
    contemporary=[
        "AI-ERA SYSTEM BEHAVIOR — deterministic software assumptions are insufficient for probabilistic model components; test distributions and failure envelopes, not only nominal inputs.",
        "AI-ERA FAILURE MODES — include hallucination, data bias, distribution shift, prompt/context sensitivity and silent model/version change in the assurance argument when an AI component is present.",
        "AI-GENERATED CODE — treat generated code as untrusted implementation until static analysis, tests, review and—where justified—formal verification establish the required property.",
    ]
    for x in contemporary:
        if x not in u13.enrichment_content:
            u13.enrichment_content.append(x); u13.enrichment_basis.append("ISCARB contemporary extension — not asserted as P1 content")
    u13.contextual_enrichment=True
    u15=units[14]
    # Exact labels are consumed by the production semantic renderer, so the
    # contemporary assurance layer is visible to students rather than hidden in JSON.
    u15.pedagogy_content=_replace_prefixed(u15.pedagogy_content,"AI MAY ASSIST","AI MAY ASSIST — For probabilistic components, probe robustness, distribution shift, adversarial cases and guardrails; do not treat nominal accuracy as assurance.")
    u15.pedagogy_content=_replace_prefixed(u15.pedagogy_content,"AI MUST NOT BE TRUSTED AUTONOMOUSLY","AI MUST NOT BE TRUSTED AUTONOMOUSLY — Treat AI-generated code as untrusted until static analysis, tests, review and formal verification where justified establish the required property.")
    u15.pedagogy_content=_replace_prefixed(u15.pedagogy_content,"HUMAN SIGN-OFF","HUMAN SIGN-OFF — Own auditability: inspect evidence, edge cases, provenance and the condition that would invalidate the claim, including black-box model behavior.")
    u15.pedagogy_content=_replace_prefixed(u15.pedagogy_content,"AI ASSURANCE LENS","AI ASSURANCE LENS — ISCARB ENRICHMENT, NOT P1: model performance and system assurance are different claims.")


def _clean_visual_metadata(bp):
    for u in list(getattr(bp,"units",[]) or []):
        plan=getattr(u,"visual_plan",None)
        if plan is not None and "faculty review required before release" in str(getattr(plan,"visual_evidence_role","") or "").lower():
            plan.visual_evidence_role="Draft visualization; inspect source alignment before any verified release."


def _enhance(bp):
    if not getattr(bp,"units",None) or len(bp.units)!=20:return bp
    _set_activity_budget(bp); _add_case_scaffold(bp); _add_decision_boxes(bp); _add_peer_review_card(bp); _add_ai_era_dependability(bp); _clean_visual_metadata(bp); return bp


def _activity_label(action:str)->str:
    a=str(action or "").upper()
    if a.startswith("THINK–PAIR–SHARE") or a.startswith("THINK-PAIR-SHARE"):return "THINK–PAIR–SHARE"
    if a.startswith("CORE IN-CLASS CASE"):return "CORE CASE"
    if a.startswith("POST-CLASS ARTIFACT"):return "POST-CLASS"
    return "CHECKPOINT"


def _install_presenter_visibility_patch():
    from . import presenter_v67_prod as p

    def ppt_footer(slide,u):
        sh=slide.shapes.add_shape(p.MSO_SHAPE.RECTANGLE,p.Inches(0),p.Inches(6.96),p.Inches(p.PPT_W),p.Inches(.54)); sh.fill.solid(); sh.fill.fore_color.rgb=p._rgb(p.PANEL2); sh.line.fill.background()
        lab=_activity_label(u.student_action); width=1.55 if lab!="THINK–PAIR–SHARE" else 2.05
        p._ppt_text(slide,.34,7.07,width,.2,lab,7.0,p.MAGENTA,True)
        p._ppt_text(slide,.34+width+.08,7.045,9.25-width,.25,p._short(u.student_action,28),7.8,p.TEXT)
        p._ppt_text(slide,9.85,7.055,3.1,.22,p._short(p._anchor(u),13),6.7,p.MUTED,False,p.PP_ALIGN.RIGHT)
    p._ppt_footer=ppt_footer

    def pdf_footer(c,u):
        c.setFillColor(p.HexColor(p.PANEL2)); c.rect(0,0,960,39,fill=1,stroke=0); lab=_activity_label(u.student_action)
        p._pdf_text(c,24,11,105,15,lab,6.1,p.MAGENTA,True,max_lines=1); p._pdf_text(c,133,9,583,18,p._short(u.student_action,28),7.0,p.TEXT,max_lines=2); p._pdf_text(c,725,10,210,16,p._short(p._anchor(u),13),5.8,p.MUTED,False,"right",1)
    p._pdf_footer=pdf_footer

    old_ppt_exp=p._ppt_expansion
    def ppt_expansion(slide,u,idx,chunk,page_idx,total):
        old_ppt_exp(slide,u,idx,chunk,page_idx,total)
        # Replace legacy task label/content already drawn by the base renderer.
        for shape in slide.shapes:
            if not hasattr(shape,"text_frame"):continue
            txt=shape.text.strip()
            if txt=="YOUR TASK": shape.text="DECISION BOX"
            elif txt.startswith("Connect one continued source family"):
                shape.text="What decision does this P1 detail support, and what evidence would change it?"
    p._ppt_expansion=ppt_expansion

    old_pdf_exp=p._pdf_expansion
    def pdf_expansion(c,u,idx,chunk,page_idx,total):
        # Re-render cleanly rather than leave a contradictory activity label.
        c.setFillColor(p.HexColor(p.BG)); c.rect(0,0,960,540,fill=1,stroke=0); accent=p.PHASE_ACCENT.get(u.phase,p.CYAN)
        p._pdf_text(c,24,508,300,16,"SOURCE EXPANSION",7.3,accent,True,max_lines=1); p._pdf_text(c,800,508,135,16,f"X{idx:02d} · {page_idx:02d}/{total:02d}",6.4,p.MUTED,False,"right",1)
        title="Domain spine — continued" if u.number==2 else f"{u.title} — source detail"; p._pdf_text(c,24,465,900,40,title,19,p.TEXT,True,max_lines=1); p._pdf_text(c,24,439,900,22,"Keep complete source propositions readable; do not compress them into a wall of text.",8.3,p.MUTED,max_lines=1)
        for i,item in enumerate(chunk[:6]):
            r,col=divmod(i,2); p._pdf_box(c,45+col*460,330-r*92,410,70,f"P1 · {i+1}",p._short(item,20),accent,body_size=8,title_size=6.8)
        c.setFillColor(p.HexColor(p.PANEL2)); c.rect(0,0,960,39,fill=1,stroke=0); p._pdf_text(c,24,11,90,15,"DECISION BOX",6.0,p.MAGENTA,True,max_lines=1); p._pdf_text(c,118,9,598,18,"What decision does this P1 detail support, and what evidence would change it?",7.0,p.TEXT,max_lines=2); p._pdf_text(c,725,10,210,16,p._short(p._anchor(u),13),5.8,p.MUTED,False,"right",1)
    p._pdf_expansion=pdf_expansion

    old_preview=p.render_presenter_preview
    def preview(bp,release_state="REVIEW",source_root=None):
        html=old_preview(bp,release_state=release_state,source_root=source_root)
        html=html.replace("<b>YOUR TASK</b>THINK–PAIR–SHARE", "<b>THINK–PAIR–SHARE</b>")
        html=html.replace("<b>YOUR TASK</b>THINK-PAIR-SHARE", "<b>THINK–PAIR–SHARE</b>")
        html=html.replace("<b>YOUR TASK</b>CORE IN-CLASS CASE", "<b>CORE CASE</b>")
        html=html.replace("<b>YOUR TASK</b>POST-CLASS ARTIFACT", "<b>POST-CLASS</b>")
        html=html.replace("<b>YOUR TASK</b>CHECKPOINT", "<b>CHECKPOINT</b>")
        html=html.replace("<b>YOUR TASK</b>Connect one continued source family to the chapter decision.","<b>DECISION BOX</b>What decision does this P1 detail support, and what evidence would change it?")
        return html
    p.render_presenter_preview=preview

    # Patch all modules that imported these renderer functions by value.
    for mod in (engine,base.engine):
        if hasattr(mod,"export_presenter_pptx"):mod.export_presenter_pptx=p.export_presenter_pptx
        if hasattr(mod,"render_presenter_preview"):mod.render_presenter_preview=p.render_presenter_preview


def apply_v721_pedagogy_ai_patch(app)->None:
    global _PATCHED
    if _PATCHED:return
    _PATCHED=True
    previous_timebox=engine.apply_90_minute_timebox
    def timebox_v721(blueprint,profile,bundle):return _enhance(previous_timebox(blueprint,profile,bundle))
    engine.apply_90_minute_timebox=timebox_v721; base.engine.apply_90_minute_timebox=timebox_v721
    previous_draft=engine._source_preserving_draft
    def draft_v721(profile,bundle):return _enhance(previous_draft(profile,bundle))
    engine._source_preserving_draft=draft_v721; base.engine._source_preserving_draft=draft_v721
    _install_presenter_visibility_patch()
    previous_health=base._health_v440
    def health():
        data=dict(previous_health())
        for key in ("cimt_reference_archive","ready_example_source","source_library_verified","verified_source_count","public_experience","design_language","fixed_task_footer","hero_live_release","faculty_experience"):data.pop(key,None)
        data.update({"version":"7.2.1","release_ui":"7.2.1","pipeline":"iscarb-v7.2.1-clean-it-wide-cognitive-budget-ai-era","cognitive_budget":"5 one-minute Think-Pair-Share + 2 core in-class cases + post-class artifact build/review","learner_action_labels":["CHECKPOINT","THINK-PAIR-SHARE","CORE IN-CLASS CASE","POST-CLASS ARTIFACT"],"micro_example_before_context_case":True,"source_expansion_decision_box":True,"peer_review_quick_card":"2 questions","ai_era_dependability":True,"ai_extension_provenance":"enrichment-only unless supported by P1","approved_hero_asset":"hero_user_original.png","approved_hero_web_derivative":"hero_user_web.jpg","public_web_image_fallback":False,"presenter_activity_labels_dynamic":True,"ai_era_content_visible_in_presenter":True})
        return data
    base._health_v440=health; base.engine.health=health
