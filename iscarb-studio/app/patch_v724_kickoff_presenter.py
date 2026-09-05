from __future__ import annotations

"""v7.2.4 — visual presenter specialization for kickoff/orientation lectures.

Blueprint v7.2.3 preserves kickoff scope. This layer makes the projected
PowerPoint/PDF/HTML tell that same story instead of reusing chapter-mechanism
labels and layouts that are semantically wrong for grading, roadmap or logistics.
It also operationalizes Unit 19 as the two-question in-class peer-review card;
the full 6x4 rubric remains in the detailed packs.
"""

import html
from fastapi.responses import HTMLResponse
from . import main as engine
from . import start_v440 as base
from . import faculty_main
from . import presenter_v67_prod as p

_PATCHED=False

_KICKOFF_TITLES={
    "Welcome to engineering decisions","Week 1 map","Five outcomes for the kickoff",
    "The engineering judgment contract","Prediction gate: what failed?","ISCARB Engineering Flow",
    "ISCARB in action: 60-second micro-case","Professional Standards & AI Literacy",
    "Earning your grade: defend your decisions","Roadmap & milestones: first half",
    "Core case: technical success, assurance failure","Core case: speed versus accountable assurance",
    "Roadmap & milestones: pressure points","Misconception: AI output is not assurance",
    "Assurance gate: defend before you sign","Post-class artifact: Decision Card #0",
    "Post-class artifact: constraint mutation","Post-class artifact: Engineering Defense rehearsal",
    "Post-class artifact: two-question peer review","Logistics & next steps",
}

class _KickoffAwareRuleNames(dict):
    def get(self,key,default=None):
        if str(default or "") in _KICKOFF_TITLES:
            return str(default)
        return super().get(key,default)


def _is_kickoff(bp):
    units=list(getattr(bp,"units",[]) or [])
    return len(units)==20 and any(str(getattr(u,"title","") or "") in _KICKOFF_TITLES for u in units)


def _texts(u,limit=6):
    vals=[]
    for raw in [*list(getattr(u,"core_content",[]) or []),*list(getattr(u,"pedagogy_content",[]) or [])]:
        lab,body=p._strip_label(str(raw))
        text=body or str(raw)
        if text and text not in vals:
            vals.append(text)
        if len(vals)>=limit:break
    return vals


def _ppt_cards(slide,entries,accent=None,cols=2,y0=1.85,row_h=1.58):
    entries=[x for x in entries if x[1]]
    cols=max(1,min(cols,len(entries) or 1)); gap=.32; total_w=12.0; w=(total_w-gap*(cols-1))/cols
    palette=[p.CYAN,p.MAGENTA,p.GOLD,p.BLUE,p.GREEN,p.DANGER]
    for i,(lab,body) in enumerate(entries):
        r,c=divmod(i,cols); x=.66+c*(w+gap); y=y0+r*row_h
        p._ppt_box(slide,x,y,w,1.28,lab,p._short(body,22),palette[i%len(palette)] if accent is None else accent,body_size=9.2,title_size=8.6)


def _pdf_cards(c,entries,cols=2,y_top=380,row_h=104):
    entries=[x for x in entries if x[1]]; cols=max(1,min(cols,len(entries) or 1)); gap=24; x0=45; total_w=870; w=(total_w-gap*(cols-1))/cols
    palette=[p.CYAN,p.MAGENTA,p.GOLD,p.BLUE,p.GREEN,p.DANGER]
    for i,(lab,body) in enumerate(entries):
        r,col=divmod(i,cols); x=x0+col*(w+gap); y=y_top-r*row_h
        p._pdf_box(c,x,y,w,82,lab,p._short(body,22),palette[i%len(palette)],body_size=7.8,title_size=7.2)


def _labeled_entries(u,names):
    vals=p._labeled(u,names); out=[]
    for name in names:
        body=vals.get(name)
        if body:out.append((name.upper(),body))
    return out


def _ppt_peer_review(slide,u):
    vals=_texts(u,8)
    q1=next((x for x in vals if "independently inspect" in x.lower()),"Can another person independently inspect the evidence?")
    q2=next((x for x in vals if "invalidate" in x.lower() or "edge case" in x.lower()),"What variable or edge case would invalidate the claim?")
    p._ppt_box(slide,.8,2.05,5.8,3.25,"1 · INSPECTABILITY",q1,p.CYAN,body_size=14,title_size=11)
    p._ppt_box(slide,6.75,2.05,5.8,3.25,"2 · FALSIFIABILITY",q2,p.MAGENTA,body_size=14,title_size=11)
    p._ppt_text(slide,1.0,5.72,11.3,.42,"Use the full 6×4 rubric after class; keep live peer review to these two questions.",10.5,p.GOLD,True,p.PP_ALIGN.CENTER)


def _pdf_peer_review(c,u):
    vals=_texts(u,8); q1=next((x for x in vals if "independently inspect" in x.lower()),"Can another person independently inspect the evidence?"); q2=next((x for x in vals if "invalidate" in x.lower() or "edge case" in x.lower()),"What variable or edge case would invalidate the claim?")
    p._pdf_box(c,55,205,400,175,"1 · INSPECTABILITY",q1,p.CYAN,body_size=11,title_size=9)
    p._pdf_box(c,505,205,400,175,"2 · FALSIFIABILITY",q2,p.MAGENTA,body_size=11,title_size=9)
    p._pdf_text(c,120,145,720,28,"Full 6×4 rubric after class; live peer review uses only these two questions.",8.8,p.GOLD,True,"center",2)


def _ppt_kickoff_semantic(slide,bp,u,accent):
    n=u.number
    if n in {1,2,3,5,8,12,15}:
        return _OLD_PPT_SEM(slide,bp,u,accent)
    if n==4:
        vals=_texts(u,6); entries=[("DESIGN",vals[0] if vals else "Design is judged by how it works."),("EVIDENCE",vals[1] if len(vals)>1 else "A claim needs inspectable support."),("DEFENSE",vals[2] if len(vals)>2 else "A decision must survive changed constraints.")]
        return _ppt_cards(slide,entries,cols=3,y0=2.25,row_h=1.6)
    if n==6:
        labs=["CRISIS","MAP","TRADE-OFF","EVIDENCE","VERDICT"]; cols=[p.CYAN,p.BLUE,p.GOLD,p.MAGENTA,p.GREEN]
        for i,lab in enumerate(labs):
            p._ppt_box(slide,.35+i*2.58,2.22,2.25,1.9,lab,"",cols[i],title_size=10)
            if i<4:p._ppt_text(slide,2.43+i*2.58,2.92,.55,.25,"→",15,p.GOLD,True,p.PP_ALIGN.CENTER)
        vals=_texts(u,6); reason=next((x for x in vals if "predict" in x.lower()),"Predict → Constraint → Derive → Name")
        p._ppt_box(slide,2.0,4.78,9.35,.92,"REASONING SEQUENCE",reason,p.MAGENTA,fill=p.PANEL2,body_size=10,title_size=8.5);return
    if n in {7,11}:
        entries=_labeled_entries(u,["crisis","map","trade-off","evidence","verdict"])
        if len(entries)<4:
            entries=[(f"STEP {i+1}",x) for i,x in enumerate(_texts(u,5))]
        return _ppt_cards(slide,entries,cols=3,y0=1.82,row_h=1.65)
    if n==9:
        vals=[x for x in list(getattr(u,"core_content",[]) or []) if str(x).strip()][:4]
        entries=[(f"ASSESSMENT {i+1}",x) for i,x in enumerate(vals)]
        return _ppt_cards(slide,entries,cols=2,y0=1.93,row_h=1.72)
    if n in {10,13}:
        vals=[x for x in list(getattr(u,"core_content",[]) or []) if str(x).strip()]
        entries=[(f"MILESTONE {i+1}",x) for i,x in enumerate(vals[:6])]
        return _ppt_cards(slide,entries,cols=3,y0=1.83,row_h=1.62)
    if n==14:
        vals=p._labeled(u,["plausible-but-wrong","source check","operating consequence"])
        entries=[("PLAUSIBLE BUT WRONG",vals.get("plausible-but-wrong") or "A fluent AI answer is sufficient engineering evidence."),("SOURCE RULE",vals.get("source check") or "AI output still requires independent validation."),("CONSEQUENCE",vals.get("operating consequence") or "Unsupported output fails accountability.")]
        return _ppt_cards(slide,entries,cols=3,y0=2.25,row_h=1.5)
    if n==16:
        vals=p._labeled(u,["claim","p1 evidence","trade-off","reversal condition"]); entries=[]
        for lab,key in [("CLAIM","claim"),("P1 EVIDENCE","p1 evidence"),("TRADE-OFF","trade-off"),("REVERSAL CONDITION","reversal condition")]:entries.append((lab,vals.get(key) or "Complete this field with one inspectable statement."))
        return _ppt_cards(slide,entries,cols=4,y0=2.05,row_h=1.6)
    if n==17:
        vals=p._labeled(u,["change one constraint","rerun","compare"]); entries=[("1 · CHANGE",vals.get("change one constraint") or "Change one decision-sensitive constraint."),("2 · RERUN",vals.get("rerun") or "Apply the same reasoning under the new condition."),("3 · COMPARE",vals.get("compare") or "State what survived and what changed.")]
        return _ppt_cards(slide,entries,cols=3,y0=2.25,row_h=1.6)
    if n==18:
        vals=p._labeled(u,["defend","challenge","respond","residual uncertainty"]); entries=[("DEFEND",vals.get("defend") or "State the decision and evidence."),("CHALLENGE",vals.get("challenge") or "Accept one changed constraint."),("RESPOND",vals.get("respond") or "Revise only what the new constraint invalidates."),("RESIDUAL UNCERTAINTY",vals.get("residual uncertainty") or "State what still needs verification.")]
        return _ppt_cards(slide,entries,cols=4,y0=2.05,row_h=1.6)
    if n==19:return _ppt_peer_review(slide,u)
    if n==20:
        vals=list(getattr(u,"core_content",[]) or []); entries=[]
        for raw in vals[:6]:
            lab,body=p._strip_label(str(raw)); entries.append((lab or "COURSE DETAIL",body or str(raw)))
        return _ppt_cards(slide,entries,cols=2,y0=1.78,row_h=1.52)
    return _OLD_PPT_SEM(slide,bp,u,accent)


def _pdf_kickoff_semantic(c,bp,u,accent):
    n=u.number
    if n==19:return _pdf_peer_review(c,u)
    if n in {1,2,3,5,8,12,15}:return _OLD_PDF_SEM(c,bp,u,accent)
    if n==4:
        vals=_texts(u,6);return _pdf_cards(c,[("DESIGN",vals[0] if vals else "Design is judged by how it works."),("EVIDENCE",vals[1] if len(vals)>1 else "A claim needs inspectable support."),("DEFENSE",vals[2] if len(vals)>2 else "A decision must survive changed constraints.")],cols=3,y_top=245)
    if n==6:
        labs=["CRISIS","MAP","TRADE-OFF","EVIDENCE","VERDICT"]
        for i,lab in enumerate(labs):p._pdf_box(c,22+i*184,220,165,125,lab,"",[p.CYAN,p.BLUE,p.GOLD,p.MAGENTA,p.GREEN][i],title_size=7.5)
        vals=_texts(u,6);reason=next((x for x in vals if "predict" in x.lower()),"Predict → Constraint → Derive → Name");p._pdf_box(c,170,145,620,52,"REASONING SEQUENCE",reason,p.MAGENTA,fill=p.PANEL2,body_size=7,title_size=6.5);return
    if n in {7,11}:
        entries=_labeled_entries(u,["crisis","map","trade-off","evidence","verdict"]) or [(f"STEP {i+1}",x) for i,x in enumerate(_texts(u,5))];return _pdf_cards(c,entries,cols=3,y_top=330,row_h=100)
    if n==9:return _pdf_cards(c,[(f"ASSESSMENT {i+1}",x) for i,x in enumerate(list(getattr(u,"core_content",[]) or [])[:4])],cols=2,y_top=310,row_h=120)
    if n in {10,13}:return _pdf_cards(c,[(f"MILESTONE {i+1}",x) for i,x in enumerate(list(getattr(u,"core_content",[]) or [])[:6])],cols=3,y_top=320,row_h=100)
    if n==14:
        vals=p._labeled(u,["plausible-but-wrong","source check","operating consequence"]);return _pdf_cards(c,[("PLAUSIBLE BUT WRONG",vals.get("plausible-but-wrong") or "A fluent AI answer is sufficient engineering evidence."),("SOURCE RULE",vals.get("source check") or "AI output still requires independent validation."),("CONSEQUENCE",vals.get("operating consequence") or "Unsupported output fails accountability.")],cols=3,y_top=245)
    if n==16:
        vals=p._labeled(u,["claim","p1 evidence","trade-off","reversal condition"]);return _pdf_cards(c,[("CLAIM",vals.get("claim") or "Complete this field."),("P1 EVIDENCE",vals.get("p1 evidence") or "Complete this field."),("TRADE-OFF",vals.get("trade-off") or "Complete this field."),("REVERSAL CONDITION",vals.get("reversal condition") or "Complete this field.")],cols=4,y_top=230)
    if n==17:
        vals=p._labeled(u,["change one constraint","rerun","compare"]);return _pdf_cards(c,[("1 · CHANGE",vals.get("change one constraint") or "Change one constraint."),("2 · RERUN",vals.get("rerun") or "Rerun the reasoning."),("3 · COMPARE",vals.get("compare") or "State what changed.")],cols=3,y_top=245)
    if n==18:
        vals=p._labeled(u,["defend","challenge","respond","residual uncertainty"]);return _pdf_cards(c,[("DEFEND",vals.get("defend") or "State the decision and evidence."),("CHALLENGE",vals.get("challenge") or "Accept one changed constraint."),("RESPOND",vals.get("respond") or "Revise only what is invalidated."),("RESIDUAL UNCERTAINTY",vals.get("residual uncertainty") or "State what remains uncertain.")],cols=4,y_top=230)
    if n==20:
        entries=[]
        for raw in list(getattr(u,"core_content",[]) or [])[:6]:
            lab,body=p._strip_label(str(raw));entries.append((lab or "COURSE DETAIL",body or str(raw)))
        return _pdf_cards(c,entries,cols=2,y_top=330,row_h=100)
    return _OLD_PDF_SEM(c,bp,u,accent)


def _ppt_kickoff_cover(slide,bp,total):
    p._ppt_bg(slide);p._ppt_text(slide,.7,.52,2.0,.25,"ISCARB",9,p.MAGENTA,True);p._ppt_text(slide,.7,1.12,7.2,.28,"WEEK 1 · ELITE KICKOFF",9,p.CYAN,True);p._ppt_text(slide,.7,1.62,8.7,1.25,bp.lecture_title,29,p.TEXT,True)
    u1=bp.units[0];welcome=next((x for x in list(getattr(u1,"core_content",[]) or []) if "memor" in str(x).lower() or "critical engineering" in str(x).lower()),"Stop memorizing definitions; start making critical engineering decisions.")
    p._ppt_text(slide,.72,3.1,8.4,.78,p._short(welcome,24),14,p.MUTED)
    p._ppt_box(slide,.72,4.45,5.8,1.05,"WEEK 1 CONTRACT","Flow · evidence · accountability · assessment · roadmap · next action",p.CYAN,body_size=9,title_size=8.5);p._ppt_text(slide,.72,6.55,6.7,.3,"CRISIS → MAP → TRADE-OFF → EVIDENCE → VERDICT",8.5,p.GOLD,True)


def _pdf_kickoff_cover(c,bp,total):
    c.setFillColor(p.HexColor(p.BG));c.rect(0,0,960,540,fill=1,stroke=0);p._pdf_text(c,48,493,140,20,"ISCARB",8,p.MAGENTA,True,max_lines=1);p._pdf_text(c,48,448,250,20,"WEEK 1 · ELITE KICKOFF",8,p.CYAN,True,max_lines=1);p._pdf_text(c,48,335,650,100,bp.lecture_title,26,p.TEXT,True,max_lines=3)
    u1=bp.units[0];welcome=next((x for x in list(getattr(u1,"core_content",[]) or []) if "memor" in str(x).lower() or "critical engineering" in str(x).lower()),"Stop memorizing definitions; start making critical engineering decisions.");p._pdf_text(c,50,270,610,50,p._short(welcome,24),11,p.MUTED,max_lines=3);p._pdf_box(c,50,160,430,72,"WEEK 1 CONTRACT","Flow · evidence · accountability · assessment · roadmap · next action",p.CYAN,body_size=7.6,title_size=7.2);p._pdf_text(c,50,112,520,20,"CRISIS → MAP → TRADE-OFF → EVIDENCE → VERDICT",7.3,p.GOLD,True,max_lines=1)


def _ppt_kickoff_close(slide,bp,total):
    p._ppt_bg(slide);u=bp.units[19];p._ppt_text(slide,.7,.6,3,.25,"ISCARB · WEEK 1 CLOSE",8.5,p.CYAN,True);p._ppt_text(slide,.7,1.2,9,.55,"Ready to engineer?",28,p.TEXT,True);p._ppt_text(slide,.7,1.88,10.8,.5,"Leave with the course contract, schedule, contact path and next action explicit.",13,p.MUTED)
    vals=list(getattr(u,"core_content",[]) or []);entries=[]
    for raw in vals[:4]:lab,body=p._strip_label(str(raw));entries.append((lab or "NEXT STEP",body or str(raw)))
    _ppt_cards(slide,entries,cols=2,y0=2.55,row_h=1.48);p._ppt_text(slide,.7,6.55,10.8,.34,"TAKE-HOME CHECKPOINT · Review the syllabus and configure your lab environment.",9.5,p.GOLD,True)


def _pdf_kickoff_close(c,bp,total):
    c.setFillColor(p.HexColor(p.BG));c.rect(0,0,960,540,fill=1,stroke=0);u=bp.units[19];p._pdf_text(c,50,485,220,18,"ISCARB · WEEK 1 CLOSE",7.5,p.CYAN,True,max_lines=1);p._pdf_text(c,50,425,620,44,"Ready to engineer?",24,p.TEXT,True,max_lines=1);p._pdf_text(c,50,385,760,30,"Leave with the course contract, schedule, contact path and next action explicit.",10,p.MUTED,max_lines=2)
    vals=list(getattr(u,"core_content",[]) or []);entries=[]
    for raw in vals[:4]:lab,body=p._strip_label(str(raw));entries.append((lab or "NEXT STEP",body or str(raw)))
    _pdf_cards(c,entries,cols=2,y_top=285,row_h=100);p._pdf_text(c,50,92,760,24,"TAKE-HOME CHECKPOINT · Review the syllabus and configure your lab environment.",8,p.GOLD,True,max_lines=2)


def _install():
    global _OLD_PPT_SEM,_OLD_PDF_SEM
    p.RULE_NAMES=_KickoffAwareRuleNames(p.RULE_NAMES)
    _OLD_PPT_SEM=p._ppt_semantic;_OLD_PDF_SEM=p._pdf_semantic
    old_ppt_header=p._ppt_header;old_pdf_header=p._pdf_header;old_ppt_cover=p._ppt_cover;old_pdf_cover=p._pdf_cover;old_ppt_close=p._ppt_close;old_pdf_close=p._pdf_close

    def ppt_sem(slide,bp,u,accent):
        if u.number==19:return _ppt_peer_review(slide,u)
        return _ppt_kickoff_semantic(slide,bp,u,accent) if _is_kickoff(bp) else _OLD_PPT_SEM(slide,bp,u,accent)
    def pdf_sem(c,bp,u,accent):
        if u.number==19:return _pdf_peer_review(c,u)
        return _pdf_kickoff_semantic(c,bp,u,accent) if _is_kickoff(bp) else _OLD_PDF_SEM(c,bp,u,accent)
    p._ppt_semantic=ppt_sem;p._pdf_semantic=pdf_sem

    def ppt_cover(slide,bp,total):return _ppt_kickoff_cover(slide,bp,total) if _is_kickoff(bp) else old_ppt_cover(slide,bp,total)
    def pdf_cover(c,bp,total):return _pdf_kickoff_cover(c,bp,total) if _is_kickoff(bp) else old_pdf_cover(c,bp,total)
    def ppt_close(slide,bp,total):return _ppt_kickoff_close(slide,bp,total) if _is_kickoff(bp) else old_ppt_close(slide,bp,total)
    def pdf_close(c,bp,total):return _pdf_kickoff_close(c,bp,total) if _is_kickoff(bp) else old_pdf_close(c,bp,total)
    p._ppt_cover=ppt_cover;p._pdf_cover=pdf_cover;p._ppt_close=ppt_close;p._pdf_close=pdf_close

    old_preview=p.render_presenter_preview
    def preview(bp,release_state="REVIEW",source_root=None):
        html_out=old_preview(bp,release_state=release_state,source_root=source_root)
        # RULE_NAMES is now kickoff-aware, so the existing semantic HTML body can stay;
        # give the close card the source-appropriate identity as well.
        if _is_kickoff(bp):
            html_out=html_out.replace("Bounded engineering verdict","Ready to engineer?")
            html_out=html_out.replace("CLAIM · EVIDENCE · WARRANT · COUNTER-EVIDENCE · RESIDUAL UNCERTAINTY · VERDICT","Course contract · roadmap · logistics · next action")
        return html_out
    p.render_presenter_preview=preview

    # Any route that imported renderer functions by value must point at the final preview/export functions.
    faculty_main.render_presenter_preview=p.render_presenter_preview
    faculty_main.export_presenter_pptx=p.export_presenter_pptx
    faculty_main.export_presenter_pdf=p.export_presenter_pdf
    for mod in (engine,base.engine):
        if hasattr(mod,"render_presenter_preview"):mod.render_presenter_preview=p.render_presenter_preview
        if hasattr(mod,"export_presenter_pptx"):mod.export_presenter_pptx=p.export_presenter_pptx
        if hasattr(mod,"export_presenter_pdf"):mod.export_presenter_pdf=p.export_presenter_pdf


def apply_v724_kickoff_presenter_patch(app):
    global _PATCHED
    if _PATCHED:return
    _PATCHED=True;_install()

    # Final public identity, preserving all v7.2.3 health claims.
    root=next((r for r in app.router.routes if getattr(r,"path",None)=="/"),None);old_root=getattr(root,"endpoint",None)
    if root is not None:app.router.routes.remove(root)
    if old_root is not None:
        @app.get("/")
        def home_v724():
            response=old_root();body=response.body.decode("utf-8") if hasattr(response,"body") else str(response);body=body.replace("7.2.3","7.2.4");headers=dict(getattr(response,"headers",{}) or {});headers.update({"X-ISCARB-Version":"7.2.4","X-ISCARB-UI":"7.2.4","Cache-Control":"no-store, no-cache, must-revalidate, max-age=0"});return HTMLResponse(body,headers=headers)
    health=next((r for r in app.router.routes if getattr(r,"path",None)=="/api/health"),None);old_health=getattr(health,"endpoint",None)
    if health is not None:app.router.routes.remove(health)
    if old_health is not None:
        @app.get("/api/health")
        def health_v724():
            data=dict(old_health());data.update({"version":"7.2.4","release_ui":"7.2.4","pipeline":"iscarb-v7.2.4-final-clean-it-wide-kickoff-visual","kickoff_presenter_source_faithful":True,"kickoff_dynamic_unit_titles":True,"kickoff_roadmap_timeline":True,"kickoff_logistics_surface":True,"peer_review_two_question_presenter":True});return data
