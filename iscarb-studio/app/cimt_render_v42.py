from __future__ import annotations

"""ISCARB v4.2 full computing-wide Presenter renderer.

The previous visual layer adapted Units 6–10 but allowed legacy security-specific
renderers to leak into other computing subjects.  v4.2 renders all 20 cognitive
jobs from the actual Blueprint.  It keeps the ISCARB teaching sequence fixed
while deriving labels and visual content from the lecture itself.
"""

import html
import re
from pathlib import Path

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from .models import Blueprint, LectureUnit
from . import visual_engine as ve
from . import presenter_pdf as pp
from .cimt_render import _render_native


def _clean(text: str, n: int = 86) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) <= n:
        return text
    cut = text[: n - 1].rsplit(" ", 1)[0]
    return (cut or text[: n - 1]).rstrip(" ,;:-") + "…"


def _subject(bp: Blueprint) -> str:
    title = re.sub(r"^\s*chapter\s*\d+\s*[-:–—]?\s*", "", bp.lecture_title or "", flags=re.I).strip()
    return title or bp.lecture_title or "Computing System"


def _core(u: LectureUnit, n: int = 6) -> list[str]:
    return [_clean(x, 94) for x in list(u.core_content)[:n] if str(x).strip()]


def _ped(u: LectureUnit, n: int = 6) -> list[str]:
    return [_clean(x, 94) for x in list(u.pedagogy_content)[:n] if str(x).strip()]


def _pick(values: list[str], i: int, fallback: str) -> str:
    return values[i] if i < len(values) and values[i].strip() else fallback


def _html_flow(items: list[tuple[str, str]], accent: str = "#055934") -> str:
    chunks = []
    for i, (title, body) in enumerate(items):
        chunks.append(
            f'<div style="min-width:0;flex:1;border:1.5px solid {accent};border-radius:14px;padding:16px;background:#fff">'
            f'<small style="font-weight:900;color:{accent};letter-spacing:.06em">{html.escape(title)}</small>'
            f'<b style="display:block;margin-top:8px;font-size:14px;line-height:1.3">{html.escape(_clean(body,76))}</b></div>'
        )
        if i < len(items) - 1:
            chunks.append(f'<div style="font-size:24px;color:{accent};font-weight:900">→</div>')
    return '<div style="display:flex;align-items:center;gap:10px;width:100%">' + ''.join(chunks) + '</div>'


def _html_cards(items: list[tuple[str, str]], cols: int = 3, accent: str = "#055934") -> str:
    return f'<div style="display:grid;grid-template-columns:repeat({cols},1fr);gap:12px;width:100%;align-items:stretch">' + ''.join(
        f'<div style="border-top:4px solid {accent};background:#fff;border-radius:12px;padding:15px;box-shadow:0 8px 22px rgba(5,89,52,.07)"><small style="color:{accent};font-weight:950">{html.escape(t)}</small><b style="display:block;margin-top:8px;font-size:13px;line-height:1.35">{html.escape(_clean(b,82))}</b></div>'
        for t, b in items
    ) + '</div>'


def _technical_html(u: LectureUnit) -> str:
    t = u.knowledge_types[0] if u.knowledge_types else "CONCEPT"
    xs = _core(u, 6) or _ped(u, 6)
    if t == "CONCEPT":
        vals = xs[:4] or [u.takeaway]
        return _html_flow([(f"CONCEPT {i+1}", x) for i, x in enumerate(vals)], "#0A353E")
    if t == "ARCHITECTURE":
        vals = xs[:4] or ["Component", "Interface", "Constraint", "Decision"]
        return _html_flow([(f"BOUNDARY {i+1}", x) for i, x in enumerate(vals)], "#055934")
    if t == "PROCESS":
        vals = xs[:4] or ["Stage", "Handoff", "Check", "Feedback"]
        return _html_flow([(f"STAGE {i+1}", x) for i, x in enumerate(vals)], "#208D44")
    if t == "DESIGN_PRINCIPLE":
        vals = xs[:4] or ["Pressure", "Principle", "Application", "Boundary"]
        return _html_flow([(x, _pick(vals, i, x)) for i, x in enumerate(["PRESSURE", "PRINCIPLE", "APPLICATION", "BOUNDARY"])], "#055934")
    # Let the existing source-native grammar handle algorithm/code/equation/
    # protocol/data-model/system-behaviour/trade-off/empirical-result.
    from .cimt_render import cimt_visual_html
    return cimt_visual_html_dummy(u, cimt_visual_html)


def cimt_visual_html_dummy(u: LectureUnit, old_fn) -> str:
    # Re-implement the specialized types directly to avoid calling the old
    # function with a security-specific fallback.
    t = u.knowledge_types[0] if u.knowledge_types else "CONCEPT"
    xs = _core(u, 6) or _ped(u, 6)
    e = lambda s: html.escape(_clean(s, 82))
    if t == "ALGORITHM":
        vals = xs[:4] or ["Problem", "Invariant / intuition", "Trace", "Complexity / trade-off"]
        return _html_flow([(str(i+1), v) for i, v in enumerate(vals)], "#208D44")
    if t == "CODE":
        left = xs[:3] or ["Input / code", "Execution state", "Observed output"]
        right = xs[3:6] or ["Mutation", "Failure", "Fix evidence"]
        return '<div style="display:grid;grid-template-columns:1.15fr .85fr;gap:16px;width:100%"><div style="background:#0A353E;color:#fff;border-radius:14px;padding:17px;font-family:ui-monospace,Consolas,monospace">' + ''.join(f'<div style="padding:8px 0;border-bottom:1px solid #395959"><span style="color:#8FD9BE">{i+1:02d}</span> {e(x)}</div>' for i,x in enumerate(left)) + '</div>' + _html_cards([(f"STATE {i+1}", x) for i,x in enumerate(right)], 1, "#208D44") + '</div>'
    if t == "EQUATION":
        vals = xs[:3] or ["Known quantities", "Derive relationship", "Interpret sensitivity"]
        return _html_flow([("KNOWN", vals[0]), ("DERIVE", vals[1]), ("INTERPRET", vals[2])], "#0A353E")
    if t == "PROTOCOL":
        vals = xs[:4] or ["Request", "Validate", "Respond", "Failure path"]
        return _html_flow([(f"MESSAGE {i+1}", x) for i,x in enumerate(vals)], "#02735E")
    if t == "DATA_MODEL":
        vals = xs[:4] or ["Entity A", "Relationship", "Constraint", "Query / use"]
        return _html_cards([("ENTITY / DATA", vals[0]), ("RELATION", vals[1]), ("CONSTRAINT", vals[2]), ("QUERY / USE", vals[3])], 2, "#055934")
    if t == "SYSTEM_BEHAVIOR":
        vals = xs[:4] or ["State A", "Event", "State B", "Consequence"]
        return _html_flow([("STATE" if i != 1 else "EVENT", x) for i,x in enumerate(vals)], "#0A353E")
    if t == "TRADE_OFF":
        vals = xs[:5] or ["Alternative A", "Alternative B", "Evidence", "Cost", "Risk"]
        return _html_cards([("ALTERNATIVE A", vals[0]), ("ALTERNATIVE B", vals[1]), ("DECISION CRITERIA", " · ".join(vals[2:5]))], 3, "#208D44")
    if t == "EMPIRICAL_RESULT":
        vals = xs[:4] or ["Setup", "Measure", "Result", "Uncertainty"]
        return _html_flow([("SETUP", vals[0]), ("MEASURE", vals[1]), ("RESULT", vals[2]), ("UNCERTAINTY", vals[3])], "#208D44")
    return _html_flow([(f"ELEMENT {i+1}", x) for i,x in enumerate(xs[:4] or [u.takeaway])], "#055934")


def cimt_visual_html_v42(bp: Blueprint, u: LectureUnit) -> str:
    core = _core(u, 6)
    ped = _ped(u, 8)
    subject = _subject(bp)

    if u.number == 1:
        signals = core[:3] or [u.takeaway]
        return _html_cards([
            ("INCIDENT", bp.central_engineering_crisis),
            ("EVIDENCE", " | ".join(signals)),
            ("DECISION", "What evidence would change the first diagnosis?"),
        ], 3, "#055934")
    if u.number == 2:
        fams = list(bp.source_topic_families)[:8]
        return '<div style="display:grid;grid-template-columns:1fr 180px 1fr;gap:14px;align-items:center;width:100%"><div>' + ''.join(f'<div style="margin:8px 0;border-left:4px solid #208D44;padding:9px 12px;background:#fff"><b>{html.escape(_clean(x,55))}</b></div>' for x in fams[::2]) + f'</div><div style="width:180px;height:180px;border-radius:50%;background:#055934;color:#fff;display:grid;place-items:center;text-align:center;padding:18px;font-size:18px;font-weight:950">{html.escape(_clean(subject,36))}</div><div>' + ''.join(f'<div style="margin:8px 0;border-right:4px solid #0A353E;padding:9px 12px;background:#fff;text-align:right"><b>{html.escape(_clean(x,55))}</b></div>' for x in fams[1::2]) + '</div></div>'
    if u.number == 3:
        return _html_cards([(c.id, c.statement) for c in bp.clOs[:5]], 5, "#208D44")
    if u.number == 4:
        comp = [
            ("ANALYTICAL", "Decompose the source mechanism and reason from evidence."),
            ("JUDGMENT", "Choose among defensible alternatives under constraints."),
            ("EVIDENCE", "Link claims to source or learner-generated evidence."),
            ("SOCIO-TECH", "Trace technical decisions into people, process, and context."),
            ("RISK-AWARE", "State failure modes, uncertainty, and decision sensitivity."),
            ("ETHICAL", "Own consequences and professional responsibility."),
        ]
        return _html_cards(comp, 3, "#055934")
    if u.number == 5:
        return _html_flow([
            ("PREDICT", u.student_action),
            ("CONSTRAINT", _pick(core, 0, "Identify what the source says cannot be violated.")),
            ("DERIVE", _pick(core, 1, _pick(ped, 0, u.takeaway))),
            ("NAME", _pick(core, 2, u.takeaway)),
        ], "#0A353E")
    if 6 <= u.number <= 10:
        return _technical_html(u)
    if u.number == 11:
        return _html_flow([
            ("HYPOTHETICAL SAUDI CONDITION", _pick(u.scenario_assumptions, 0, u.engineering_question)),
            ("P1 MECHANISM", _pick(core, 0, "Use only the source-taught mechanism.")),
            ("DECISION CHANGE", u.takeaway),
        ], "#208D44")
    if u.number == 12:
        return _html_flow([
            ("SOURCE DECISION", _pick(core, 0, u.takeaway)),
            ("EVIDENCE", u.evidence or _pick(core, 1, "Observable evidence")),
            ("OWNER", _pick(ped, 0, "Name the responsible engineering role.")),
            ("CONSEQUENCE", u.student_action),
        ], "#055934")
    if u.number == 13:
        return _html_flow([
            ("ENDURING", _pick(core, 0, "Source principle")),
            ("CURRENT", _pick(core, 1, u.takeaway)),
            ("NEXT", _pick(u.enrichment_content, 0, u.student_action)),
        ], "#0A353E")
    if u.number == 14:
        return _html_flow([
            ("DESIGN FRICTION", _pick(core, 0, "Source-grounded operational pressure")),
            ("HUMAN LOAD", _pick(ped, 0, "Identify avoidable cognitive or coordination burden.")),
            ("DESIGN RESPONSE", u.student_action),
            ("RESIDUAL BURDEN", u.takeaway),
        ], "#208D44")
    if u.number == 15:
        return _html_flow([
            ("AI MAY ASSIST", "Draft or compare candidate reasoning."),
            ("SOURCE CHECK", _pick(core, 0, "Trace the technical claim to P1.")),
            ("TEST", u.student_action),
            ("HUMAN SIGN-OFF", "Engineer owns the final bounded decision."),
        ], "#0A353E")
    if u.number == 16:
        return _html_cards([
            ("PROBLEM", bp.central_engineering_crisis),
            ("SOURCE MECHANISM", _pick(core, 0, _pick(bp.units[5].core_content, 0, "P1 mechanism"))),
            ("DESIGN", u.student_action),
            ("TRADE-OFF", bp.units[7].takeaway),
            ("EVIDENCE", u.evidence or "Evidence artifact"),
            ("ASSURANCE", u.takeaway),
        ], 3, "#055934")
    if u.number == 17:
        return _html_flow([
            ("BEFORE", _pick(core, 0, bp.units[15].takeaway)),
            ("MUTATION", _pick(u.scenario_assumptions, 0, u.engineering_question)),
            ("REDESIGN", u.student_action),
            ("CRITIQUE", _pick(ped, 0, "Peer challenges the changed decision.")),
        ], "#208D44")
    if u.number == 18:
        vals = ped or ["Claim", "Evidence", "Warrant", "Counter-evidence", "Residual uncertainty"]
        return _html_flow([
            ("CLAIM", _pick(vals, 0, u.takeaway)),
            ("EVIDENCE", u.evidence or _pick(vals, 1, "Observed evidence")),
            ("WARRANT", _pick(vals, 2, "Explain why evidence supports the claim.")),
            ("COUNTER", _pick(vals, 3, "State disconfirming evidence.")),
            ("UNCERTAINTY", _pick(vals, 4, "Keep the residual bound visible.")),
        ], "#0A353E")
    if u.number == 19:
        return _html_cards([(f"{i+1} · {c.criterion}", c.ready) for i,c in enumerate(bp.rubric_criteria[:6])], 3, "#208D44")
    if u.number == 20:
        return _html_cards([
            ("TOP CLAIM", u.takeaway),
            ("EVIDENCE", u.evidence or "Trace to CLO evidence and source bounds."),
            ("RESIDUAL UNCERTAINTY", _pick(ped, 0, "State what remains unknown.")),
            ("VERDICT", "APPROVE · CONDITIONALLY APPROVE · REDESIGN · REJECT"),
        ], 2, "#055934")
    return _html_cards([(f"{i+1}", x) for i,x in enumerate(core or ped)], 3, "#055934")


def _ppt_flow(slide, u: LectureUnit, items: list[tuple[str, str]], y: float = 2.45, h: float = 2.45) -> None:
    n = max(1, len(items)); gap = .18; left = .55; total = 12.2
    w = (total - gap * (n - 1)) / n
    c = ve.PHASE_COLOR[u.phase]; soft = ve.PHASE_SOFT[u.phase]
    for i,(title,body) in enumerate(items):
        x = left + i * (w + gap)
        ve._box(slide, x, y, w, h, title, _clean(body, 88), fill=soft if i % 2 == 0 else ve.WHITE, line=c, title_color=c, title_size=10.5, body_size=9.5)
        if i < n - 1:
            ve._arrow(slide, x + w + .02, y + h/2, gap - .04, .18, c)


def _ppt_cards(slide, u: LectureUnit, items: list[tuple[str,str]], cols: int = 3) -> None:
    c=ve.PHASE_COLOR[u.phase]; soft=ve.PHASE_SOFT[u.phase]
    rows=(len(items)+cols-1)//cols; gapx=.22; gapy=.22; left=.65; top=2.15; total=12.0
    w=(total-gapx*(cols-1))/cols; h=min(1.65, (4.0-gapy*(rows-1))/max(rows,1))
    for i,(title,body) in enumerate(items):
        r=i//cols; cc=i%cols; x=left+cc*(w+gapx); y=top+r*(h+gapy)
        ve._box(slide,x,y,w,h,title,_clean(body,90),fill=soft if i%2==0 else ve.WHITE,line=c,title_color=c,title_size=10.2,body_size=8.8)


def _render_ppt_unit(slide, bp: Blueprint, u: LectureUnit) -> None:
    core=_core(u,6); ped=_ped(u,8)
    if 6 <= u.number <= 10:
        _render_native(slide,bp,u); return
    if u.number==1:
        _ppt_cards(slide,u,[("INCIDENT",bp.central_engineering_crisis),("EVIDENCE"," | ".join(core[:3]) or u.takeaway),("DECISION","What evidence changes the diagnosis?")],3); return
    if u.number==2:
        _ppt_cards(slide,u,[(f"{_clean(_subject(bp),24)} · {i+1}",x) for i,x in enumerate(bp.source_topic_families[:8])],4); return
    if u.number==3:
        _ppt_cards(slide,u,[(c.id,c.statement) for c in bp.clOs[:5]],5); return
    if u.number==4:
        _ppt_cards(slide,u,[
            ("ANALYTICAL","Decompose mechanism and evidence."),("JUDGMENT","Choose under constraints."),("EVIDENCE","Link claim to proof."),
            ("SOCIO-TECH","Trace people + process effects."),("RISK-AWARE","Expose failure + uncertainty."),("ETHICAL","Own professional consequence."),
        ],3); return
    if u.number==5:
        _ppt_flow(slide,u,[("PREDICT",u.student_action),("CONSTRAINT",_pick(core,0,"Source constraint")),("DERIVE",_pick(core,1,_pick(ped,0,u.takeaway))),("NAME",_pick(core,2,u.takeaway))]); return
    if u.number==11:
        _ppt_flow(slide,u,[("HYPOTHETICAL SAUDI CONDITION",_pick(u.scenario_assumptions,0,u.engineering_question)),("P1 MECHANISM",_pick(core,0,"Source mechanism")),("DECISION CHANGE",u.takeaway)]); return
    if u.number==12:
        _ppt_flow(slide,u,[("SOURCE DECISION",_pick(core,0,u.takeaway)),("EVIDENCE",u.evidence or _pick(core,1,"Evidence")),("OWNER",_pick(ped,0,"Responsible role")),("CONSEQUENCE",u.student_action)]); return
    if u.number==13:
        _ppt_flow(slide,u,[("ENDURING",_pick(core,0,"Source principle")),("CURRENT",_pick(core,1,u.takeaway)),("NEXT",_pick(u.enrichment_content,0,u.student_action))]); return
    if u.number==14:
        _ppt_flow(slide,u,[("DESIGN FRICTION",_pick(core,0,"Operational pressure")),("HUMAN LOAD",_pick(ped,0,"Avoidable burden")),("DESIGN RESPONSE",u.student_action),("RESIDUAL BURDEN",u.takeaway)]); return
    if u.number==15:
        _ppt_flow(slide,u,[("AI MAY ASSIST","Draft / compare reasoning"),("SOURCE CHECK",_pick(core,0,"Trace to P1")),("TEST",u.student_action),("HUMAN SIGN-OFF","Engineer owns final decision")]); return
    if u.number==16:
        _ppt_cards(slide,u,[("PROBLEM",bp.central_engineering_crisis),("SOURCE MECHANISM",_pick(core,0,_pick(_core(bp.units[5]),0,"P1 mechanism"))),("DESIGN",u.student_action),("TRADE-OFF",bp.units[7].takeaway),("EVIDENCE",u.evidence or "Evidence artifact"),("ASSURANCE",u.takeaway)],3); return
    if u.number==17:
        _ppt_flow(slide,u,[("BEFORE",_pick(core,0,bp.units[15].takeaway)),("MUTATION",_pick(u.scenario_assumptions,0,u.engineering_question)),("REDESIGN",u.student_action),("CRITIQUE",_pick(ped,0,"Peer challenge"))]); return
    if u.number==18:
        vals=ped or []
        _ppt_flow(slide,u,[("CLAIM",_pick(vals,0,u.takeaway)),("EVIDENCE",u.evidence or _pick(vals,1,"Evidence")),("WARRANT",_pick(vals,2,"Why it supports")),("COUNTER",_pick(vals,3,"Disconfirming evidence")),("UNCERTAINTY",_pick(vals,4,"Residual bound"))]); return
    if u.number==19:
        _ppt_cards(slide,u,[(c.criterion,c.ready) for c in bp.rubric_criteria[:6]],3); return
    if u.number==20:
        _ppt_cards(slide,u,[("TOP CLAIM",u.takeaway),("EVIDENCE",u.evidence or "CLO evidence + source bounds"),("RESIDUAL UNCERTAINTY",_pick(ped,0,"State remaining uncertainty")),("VERDICT","APPROVE / CONDITIONAL / REDESIGN / REJECT")],2); return
    _ppt_cards(slide,u,[(str(i+1),x) for i,x in enumerate(core or ped)],3)


def export_cimt_presenter_pptx_v42(bp: Blueprint, out: Path) -> Path:
    prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
    for u in bp.units:
        slide=ve._blank(prs); ve._base(slide,u); _render_ppt_unit(slide,bp,u)
    prs.save(out); return out


def _pdf_flow(c, u: LectureUnit, items: list[tuple[str,str]]) -> None:
    pp._chain(c, [(t, _clean(b,72)) for t,b in items])


def _pdf_cards(c, u: LectureUnit, items: list[tuple[str,str]], cols: int = 3) -> None:
    rows=(len(items)+cols-1)//cols; gap=14; left=48; total=864; w=(total-gap*(cols-1))/cols; h=min(105,(290-gap*(rows-1))/max(rows,1))
    top=330
    for i,(title,body) in enumerate(items):
        r=i//cols; cc=i%cols; x=left+cc*(w+gap); y=top-(r+1)*h-r*gap
        pp._node(c,x,y,w,h,_clean(title,34),_clean(body,80),pp.WHITE,pp.PHASE[u.phase])


def render_presenter_pdf_unit_v42(c, bp: Blueprint, u: LectureUnit) -> None:
    core=_core(u,6); ped=_ped(u,8)
    if 6 <= u.number <= 10:
        # PDF source images are overlaid later when useful.  For redraw cases,
        # use the actual unit content rather than legacy security templates.
        t=u.knowledge_types[0] if u.knowledge_types else "CONCEPT"
        vals=core[:4] or ped[:4] or [u.takeaway]
        if t=="TRADE_OFF" and len(vals)>=2:
            _pdf_cards(c,u,[("ALTERNATIVE A",vals[0]),("ALTERNATIVE B",vals[1]),("CRITERIA"," · ".join(vals[2:4]) or u.takeaway)],3)
        else:
            _pdf_flow(c,u,[(t if i==0 else f"{t} {i+1}",x) for i,x in enumerate(vals[:4])])
        return
    if u.number==1:
        _pdf_cards(c,u,[("INCIDENT",bp.central_engineering_crisis),("EVIDENCE"," | ".join(core[:3]) or u.takeaway),("DECISION","What evidence changes the diagnosis?")],3); return
    if u.number==2:
        _pdf_cards(c,u,[(f"{_subject(bp)} · {i+1}",x) for i,x in enumerate(bp.source_topic_families[:8])],4); return
    if u.number==3:
        _pdf_cards(c,u,[(x.id,x.statement) for x in bp.clOs[:5]],5); return
    if u.number==4:
        _pdf_cards(c,u,[
            ("ANALYTICAL","Decompose mechanism and evidence."),("JUDGMENT","Choose under constraints."),("EVIDENCE","Link claim to proof."),
            ("SOCIO-TECH","Trace people + process effects."),("RISK-AWARE","Expose failure + uncertainty."),("ETHICAL","Own professional consequence."),
        ],3); return
    if u.number==5:
        _pdf_flow(c,u,[("PREDICT",u.student_action),("CONSTRAINT",_pick(core,0,"Source constraint")),("DERIVE",_pick(core,1,_pick(ped,0,u.takeaway))),("NAME",_pick(core,2,u.takeaway))]); return
    if u.number==11:
        _pdf_flow(c,u,[("HYPOTHETICAL SAUDI CONDITION",_pick(u.scenario_assumptions,0,u.engineering_question)),("P1 MECHANISM",_pick(core,0,"Source mechanism")),("DECISION CHANGE",u.takeaway)]); return
    if u.number==12:
        _pdf_flow(c,u,[("SOURCE DECISION",_pick(core,0,u.takeaway)),("EVIDENCE",u.evidence or _pick(core,1,"Evidence")),("OWNER",_pick(ped,0,"Responsible role")),("CONSEQUENCE",u.student_action)]); return
    if u.number==13:
        _pdf_flow(c,u,[("ENDURING",_pick(core,0,"Source principle")),("CURRENT",_pick(core,1,u.takeaway)),("NEXT",_pick(u.enrichment_content,0,u.student_action))]); return
    if u.number==14:
        _pdf_flow(c,u,[("DESIGN FRICTION",_pick(core,0,"Operational pressure")),("HUMAN LOAD",_pick(ped,0,"Avoidable burden")),("DESIGN RESPONSE",u.student_action),("RESIDUAL BURDEN",u.takeaway)]); return
    if u.number==15:
        _pdf_flow(c,u,[("AI MAY ASSIST","Draft / compare reasoning"),("SOURCE CHECK",_pick(core,0,"Trace to P1")),("TEST",u.student_action),("HUMAN SIGN-OFF","Engineer owns final decision")]); return
    if u.number==16:
        _pdf_cards(c,u,[("PROBLEM",bp.central_engineering_crisis),("SOURCE MECHANISM",_pick(core,0,_pick(_core(bp.units[5]),0,"P1 mechanism"))),("DESIGN",u.student_action),("TRADE-OFF",bp.units[7].takeaway),("EVIDENCE",u.evidence or "Evidence artifact"),("ASSURANCE",u.takeaway)],3); return
    if u.number==17:
        _pdf_flow(c,u,[("BEFORE",_pick(core,0,bp.units[15].takeaway)),("MUTATION",_pick(u.scenario_assumptions,0,u.engineering_question)),("REDESIGN",u.student_action),("CRITIQUE",_pick(ped,0,"Peer challenge"))]); return
    if u.number==18:
        vals=ped or []
        _pdf_flow(c,u,[("CLAIM",_pick(vals,0,u.takeaway)),("EVIDENCE",u.evidence or _pick(vals,1,"Evidence")),("WARRANT",_pick(vals,2,"Why it supports")),("COUNTER",_pick(vals,3,"Disconfirming evidence")),("UNCERTAINTY",_pick(vals,4,"Residual bound"))]); return
    if u.number==19:
        _pdf_cards(c,u,[(x.criterion,x.ready) for x in bp.rubric_criteria[:6]],3); return
    if u.number==20:
        _pdf_cards(c,u,[("TOP CLAIM",u.takeaway),("EVIDENCE",u.evidence or "CLO evidence + source bounds"),("RESIDUAL UNCERTAINTY",_pick(ped,0,"State remaining uncertainty")),("VERDICT","APPROVE / CONDITIONAL / REDESIGN / REJECT")],2); return
    _pdf_cards(c,u,[(str(i+1),x) for i,x in enumerate(core or ped)],3)
