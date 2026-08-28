from __future__ import annotations

import html
import re
from pathlib import Path

from pptx.dml.color import RGBColor

from .models import Blueprint, LectureUnit
from . import visual_engine as ve

# ISCARB Original Identity — Saudi academic engineering language.
INK = RGBColor(29, 41, 33)
MUTED = RGBColor(101, 113, 105)
PAPER = RGBColor(250, 249, 246)
WHITE = RGBColor(255, 255, 255)
LINE = RGBColor(221, 228, 223)
GREEN = RGBColor(12, 83, 61)
GREEN2 = RGBColor(29, 139, 86)
TEAL = RGBColor(10, 53, 62)
PURPLE = RGBColor(86, 60, 125)
PURPLE2 = RGBColor(130, 100, 167)
GOLD = RGBColor(196, 162, 79)
RED = RGBColor(184, 77, 82)
SOFT_GREEN = RGBColor(231, 244, 236)
SOFT_TEAL = RGBColor(231, 240, 241)
SOFT_PURPLE = RGBColor(238, 232, 245)
SOFT_GOLD = RGBColor(247, 241, 224)
SOFT_RED = RGBColor(250, 235, 236)


def _faculty_short(text: str, n: int = 90) -> str:
    """Strict Presenter-first text budget.

    Full wording remains in Reading Pack / Instructor Guide / Blueprint. Presenter
    surfaces carry only the minimum text needed to drive reasoning in the room.
    """
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    cap = min(int(n), 64)
    if len(text) <= cap:
        return text
    cut = text[: cap - 1].rstrip()
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:-") + "…"


def _apply_theme() -> None:
    ve.INK = INK
    ve.MUTED = MUTED
    ve.PAPER = PAPER
    ve.WHITE = WHITE
    ve.LINE = LINE
    ve.BLUE = PURPLE
    ve.GREEN = GREEN2
    ve.AMBER = GOLD
    ve.VIOLET = TEAL
    ve.RED = RED
    ve.SOFT_BLUE = SOFT_PURPLE
    ve.SOFT_GREEN = SOFT_GREEN
    ve.SOFT_AMBER = SOFT_GOLD
    ve.SOFT_VIOLET = SOFT_TEAL
    ve.SOFT_RED = SOFT_RED
    ve.PHASE_COLOR = {
        "IFHAM": PURPLE,
        "MARIS": GREEN2,
        "ATQAN": GOLD,
        "MAYYIZ": TEAL,
    }
    ve.PHASE_SOFT = {
        "IFHAM": SOFT_PURPLE,
        "MARIS": SOFT_GREEN,
        "ATQAN": SOFT_GOLD,
        "MAYYIZ": SOFT_TEAL,
    }
    ve._short = _faculty_short


def export_faculty_presenter_pptx(blueprint: Blueprint, path: Path) -> Path:
    _apply_theme()
    return ve.export_presenter_pptx(blueprint, Path(path))


def _e(text: str) -> str:
    return html.escape(_faculty_short(text, 92))


def _strip(text: str) -> str:
    text = re.sub(r"^\s*[•\-–—]\s*", "", str(text or ""))
    text = re.sub(r"^\s*\[[^\]]+\]\s*", "", text)
    return text.strip()


def _pick(items: list[str], keyword: str, fallback: str = "") -> str:
    for item in items:
        if keyword.lower() in item.lower():
            return _strip(item)
    return fallback


def _cards(items: list[tuple[str, str]], cls: str = "cards") -> str:
    return f'<div class="{cls}">' + "".join(
        f'<div class="vcard"><b>{html.escape(t)}</b><span>{_e(b)}</span></div>' for t, b in items
    ) + '</div>'


def _chain(items: list[tuple[str, str]]) -> str:
    chunks = []
    for i, (t, b) in enumerate(items):
        chunks.append(f'<div class="node"><b>{html.escape(t)}</b><span>{_e(b)}</span></div>')
        if i < len(items) - 1:
            chunks.append('<div class="arrow">→</div>')
    return '<div class="chain">' + ''.join(chunks) + '</div>'


def _visual_html(bp: Blueprint, u: LectureUnit) -> str:
    core = [_strip(x) for x in u.core_content]
    ped = [_strip(x) for x in u.pedagogy_content]
    enrich = [_strip(x) for x in u.enrichment_content]

    if u.number == 1:
        signals = core[:3] or [u.takeaway]
        return '<div class="incident"><div class="crisis"><small>INCIDENT</small><strong>' + _e(bp.central_engineering_crisis) + '</strong></div><div class="signals">' + ''.join(f'<div><b>SIGNAL {i+1}</b><span>{_e(s)}</span></div>' for i,s in enumerate(signals)) + '</div><div class="decision"><small>DECISION</small><strong>What evidence would change your first diagnosis?</strong></div></div>'
    if u.number == 2:
        fams = bp.source_topic_families[:6]
        return '<div class="orbit"><div class="hub">SECURITY<br>ENGINEERING</div>' + ''.join(f'<div class="orb o{i+1}">{_e(f)}</div>' for i,f in enumerate(fams)) + '</div>'
    if u.number == 3:
        return _cards([(c.id, c.statement) for c in bp.clOs[:5]], 'cards five')
    if u.number == 4:
        names = ["ANALYTICAL", "JUDGMENT", "EVIDENCE", "SOCIO-TECH", "RISK-AWARE", "ETHICAL"]
        bodies = ped[:6]
        return _cards([(n, bodies[i] if i < len(bodies) else "") for i,n in enumerate(names)], 'cards three')
    if u.number == 5:
        return _chain([
            ("PREDICT", _pick(ped,"predict",u.student_action)),
            ("CONSTRAIN", "What cannot be violated?"),
            ("DERIVE", _pick(ped,"deriv",u.takeaway)),
            ("NAME", "Only now reveal the formal principle"),
        ])
    if u.number == 6:
        return _chain([
            ("ASSET", "What has value?"), ("THREAT", "How can it be harmed?"),
            ("VULNERABILITY", "Where is exposure?"), ("CONTROL", "What changes the risk?"),
        ])
    if u.number == 7:
        return '<div class="layers"><div class="layer outer"><b>PLATFORM PROTECTION</b><div class="layer middle"><b>APPLICATION PROTECTION</b><div class="layer inner"><b>RECORD / ASSET</b></div></div></div><div class="trade">PROTECTION ↔ DISTRIBUTION<br><small>More control can cost usability; more distribution can cost protection complexity.</small></div></div>'
    if u.number == 8:
        a = _pick(ped,"alternative a", core[0] if core else "Standard COTS client")
        b = _pick(ped,"alternative b", core[1] if len(core)>1 else "Restricted client")
        return '<div class="compare"><div class="choice"><em>A</em><b>FLEXIBILITY</b><span>'+_e(a)+'</span></div><div class="scales"><div>USABILITY</div><div>↔</div><div>EXPOSURE</div></div><div class="choice"><em>B</em><b>CONTROL</b><span>'+_e(b)+'</span></div></div>'
    if u.number == 9:
        return _chain([("GUIDELINE","State the rule"),("MECHANISM","Show how it works"),("TEST","Define evidence"),("FALSIFY","What result proves failure?")])
    if u.number == 10:
        return '<div class="quad">' + ''.join(f'<div><b>{t}</b><span>{_e(b)}</span></div>' for t,b in [
            ("KNOWN",_pick(ped,"known","Verified facts")),
            ("UNKNOWN",_pick(ped,"unknown","Unresolved evidence")),
            ("DECISION-SENSITIVE",_pick(ped,"decision-sensitive","What could change approval?")),
            ("MONITOR",_pick(ped,"monitor","What evidence reduces uncertainty?")),
        ]) + '</div>'
    if u.number == 11:
        return _chain([("SAUDI CONTEXT","Hypothetical local operating condition"),("RISK SHIFT","Environment changes threat probability"),("DESIGN IMPACT","Adapt controls without inventing mechanisms")])
    if u.number == 12:
        return _chain([("SOFTWARE ENGINEER","Design-safe defaults"),("DEPLOYMENT ENGINEER","Validate configuration"),("OPERATOR","Observe and recover"),("ACCOUNTABILITY","Who owns the consequence?")])
    if u.number == 13:
        return _chain([("ENDURING","Resistance · Recognition · Recovery"),("NOW","Apply to current architecture"),("NEXT","What changes under faster attacks?")])
    if u.number == 14:
        return _chain([("DESIGN FRICTION","Opaque configuration"),("COGNITIVE LOAD","More decisions under pressure"),("RECOVERY DESIGN","Clear paths + fewer steps"),("WELLBEING","Lower avoidable operational burden")])
    if u.number == 15:
        return '<div class="ai"><div class="yes"><b>AI MAY ASSIST</b><span>Draft · compare · brainstorm tests</span></div><div class="no"><b>AI MUST NOT APPROVE</b><span>Architecture · security claims · sign-off</span></div></div>' + _chain([("CLAIM",""),("SOURCE CHECK",""),("TEST",""),("FAILURE SEARCH",""),("HUMAN SIGN-OFF","")])
    if u.number == 16:
        return _cards([(x,y) for x,y in [
            ("PROBLEM","Frame the system"),("RISK","Threats + vulnerabilities"),("ARCHITECTURE","Layered protection"),("TRADE-OFF","Defend alternatives"),("EVIDENCE","Show proof"),("ASSURANCE","Bound the claim")
        ]], 'cards three')
    if u.number == 17:
        return _chain([("BEFORE","Current design"),("MUTATION","Constraints change"),("ADAPT","Use only taught mechanisms"),("CRITIQUE","Peer challenge")])
    if u.number == 18:
        return _chain([("CLAIM",""),("EVIDENCE",""),("WARRANT",""),("COUNTER-EVIDENCE",""),("RESIDUAL UNCERTAINTY","")])
    if u.number == 19:
        criteria = [c.criterion for c in bp.rubric_criteria[:6]]
        return '<div class="rubric"><div class="rhead">CAPABILITY</div><div class="rhead">4 · DISTINGUISHED</div><div class="rhead">3 · READY</div><div class="rhead">2 · DEVELOPING</div><div class="rhead">1 · NOT YET</div>' + ''.join(f'<div class="crit">{_e(c)}</div><div class="dot good"></div><div class="dot ready"></div><div class="dot dev"></div><div class="dot bad"></div>' for c in criteria) + '</div>'
    if u.number == 20:
        return '<div class="assurance"><div class="claim">TOP CLAIM<br><small>'+_e(u.takeaway)+'</small></div><div class="evidence-row">' + ''.join(f'<div>{html.escape(c.id)}<small>{_e(c.evidence_expected)}</small></div>' for c in bp.clOs[:5]) + '</div><div class="decisions"><b>APPROVE</b><b>CONDITIONAL</b><b>REDESIGN</b><b>REJECT</b></div></div>'
    return _cards([(f"{i+1:02d}",x) for i,x in enumerate((core or ped)[:4])])


def render_faculty_presenter_preview(blueprint: Blueprint, release_state: str = "BLOCKED") -> str:
    """Presenter v5 browser preview: mirrors the visual grammar, not generic text cards."""
    slides = []
    thumbs = []
    phase_color = {"IFHAM":"#563c7d","MARIS":"#1d8b56","ATQAN":"#c4a24f","MAYYIZ":"#0a353e"}
    for i,u in enumerate(blueprint.units):
        color = phase_color[u.phase]
        thumbs.append(f'<button class="thumb{" active" if i==0 else ""}" data-i="{i}"><b>{u.number:02d} · {html.escape(u.phase)}</b><span>{html.escape(_faculty_short(u.title,52))}</span></button>')
        slides.append(f'''<section class="slide{" show" if i==0 else ""}" data-slide="{i}" style="--accent:{color}">
          <div class="meta"><span>UNIT {u.number:02d}</span><span>{html.escape(u.phase)}</span><span>{u.planned_minutes} MIN</span></div>
          <h2>{html.escape(u.title)}</h2>
          <div class="question">{html.escape(_faculty_short(u.engineering_question,150))}</div>
          <div class="visual">{_visual_html(blueprint,u)}</div>
          <div class="foot"><strong>YOU TRY</strong><span>{html.escape(_faculty_short(u.student_action,110))}</span><em>{html.escape(_faculty_short(u.source_anchor or 'ISCARB pedagogy',55))}</em></div>
        </section>''')
    css = r'''
    *{box-sizing:border-box}body{margin:0;font-family:Inter,Aptos,system-ui,sans-serif;background:#0b1f20;color:#1d2921}.deck{height:100vh;display:grid;grid-template-columns:250px 1fr}.rail{background:#102b2c;color:#fff;padding:18px;overflow:auto;border-right:1px solid #274446}.brand{font-weight:950;letter-spacing:.08em;font-size:12px}.rail p{font-size:10px;color:#aec2bd;line-height:1.5}.thumb{width:100%;text-align:left;border:1px solid #315051;background:#173738;color:#dce9e5;border-radius:10px;padding:9px 10px;margin:6px 0;cursor:pointer}.thumb.active{background:#fff;color:#1d2921;border-color:#fff}.thumb b{font-size:9px}.thumb span{display:block;font-size:9px;margin-top:3px;opacity:.76}.stage{display:grid;place-items:center;padding:24px;background:radial-gradient(circle at 70% 10%,#183b3d 0,#0b1f20 58%)}.slide{display:none;width:min(1180px,calc(100vw - 310px));aspect-ratio:16/9;background:#faf9f6;border-radius:18px;padding:26px 34px 0;box-shadow:0 28px 80px rgba(0,0,0,.4);overflow:hidden;grid-template-rows:auto auto auto 1fr auto}.slide.show{display:grid}.meta{display:flex;gap:8px;font-size:9px;font-weight:900;color:var(--accent)}.meta span{border:1px solid color-mix(in srgb,var(--accent) 45%,#fff);padding:5px 8px;border-radius:999px}.slide h2{font-size:28px;letter-spacing:-.035em;margin:10px 0 4px}.question{font-size:14px;color:#657169;font-weight:750;max-width:1000px}.visual{display:grid;align-items:center;margin:16px 0;min-height:0}.foot{height:44px;margin:0 -34px;background:#1d2921;color:#fff;display:grid;grid-template-columns:80px 1fr 220px;align-items:center;padding:0 30px;font-size:8.5px}.foot strong{color:#7ee0ad}.foot em{text-align:right;color:#bdc9c1;font-style:normal}.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.cards.three{grid-template-columns:repeat(3,1fr)}.cards.five{grid-template-columns:repeat(5,1fr)}.vcard{border:2px solid var(--accent);border-radius:16px;padding:18px;background:#fff;min-height:120px;display:flex;flex-direction:column;justify-content:space-between}.vcard b{font-size:12px;color:var(--accent)}.vcard span{font-size:11px;line-height:1.35;color:#657169}.chain{display:flex;align-items:center;justify-content:center;gap:8px}.node{min-width:145px;max-width:190px;height:150px;border:2px solid var(--accent);border-radius:18px;padding:16px;background:#fff;display:flex;flex-direction:column;justify-content:center;text-align:center}.node b{font-size:12px;color:var(--accent)}.node span{font-size:10px;color:#657169;margin-top:8px}.arrow{font-size:28px;color:var(--accent);font-weight:900}.incident{display:grid;grid-template-columns:1.05fr 1fr .85fr;gap:14px}.crisis,.decision{border-radius:18px;padding:20px;color:#fff;display:flex;flex-direction:column;justify-content:center}.crisis{background:#b84d52}.decision{background:#563c7d}.crisis small,.decision small{font-weight:900;letter-spacing:.1em;opacity:.8}.crisis strong,.decision strong{font-size:16px;margin-top:8px}.signals{display:grid;gap:9px}.signals div{border:1px solid #dde4df;background:#fff;border-radius:12px;padding:11px}.signals b{display:block;font-size:9px;color:#0c533d}.signals span{font-size:9px;color:#657169}.orbit{position:relative;height:330px}.hub{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:190px;height:190px;border-radius:50%;background:#0c533d;color:#fff;display:grid;place-items:center;text-align:center;font-weight:950;font-size:18px}.orb{position:absolute;width:190px;height:62px;border:2px solid #563c7d;border-radius:999px;background:#fff;display:grid;place-items:center;text-align:center;font-size:10px;font-weight:800}.o1{left:5%;top:7%}.o2{right:5%;top:7%}.o3{left:0;top:43%}.o4{right:0;top:43%}.o5{left:8%;bottom:4%}.o6{right:8%;bottom:4%}.layers{display:grid;place-items:center;gap:10px}.layer{display:grid;place-items:center;border-radius:22px;padding:18px;font-size:11px}.outer{width:88%;height:250px;background:#eee8f5;border:2px solid #563c7d}.middle{width:72%;height:165px;background:#e7f4ec;border:2px solid #1d8b56}.inner{width:58%;height:78px;background:#eef4f4;border:2px solid #0a353e}.trade{text-align:center;font-weight:900;color:#657169}.trade small{font-weight:600}.compare{display:grid;grid-template-columns:1fr 160px 1fr;gap:16px;align-items:center}.choice{height:250px;border:2px solid var(--accent);border-radius:22px;padding:22px;background:#fff;display:flex;flex-direction:column}.choice em{font-size:50px;font-weight:950;color:var(--accent);font-style:normal}.choice b{font-size:14px}.choice span{font-size:10px;color:#657169;margin-top:14px}.scales{text-align:center;font-size:11px;font-weight:900;color:#657169}.scales div:nth-child(2){font-size:40px;color:#c4a24f}.quad{display:grid;grid-template-columns:1fr 1fr;gap:14px}.quad>div{height:140px;border:2px solid var(--accent);border-radius:18px;padding:18px;background:#fff}.quad b{display:block;color:var(--accent);font-size:13px}.quad span{font-size:10px;color:#657169}.ai{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}.ai>div{height:130px;border-radius:20px;padding:22px;color:#fff}.ai b{font-size:18px;display:block}.ai span{font-size:11px}.yes{background:#1d8b56}.no{background:#b84d52}.rubric{display:grid;grid-template-columns:2.2fr repeat(4,1fr);gap:6px;align-items:center}.rhead{font-size:8px;font-weight:900;text-align:center;color:#657169}.crit{font-size:9px;font-weight:800}.dot{height:22px;border-radius:6px}.good{background:#1d8b56}.ready{background:#563c7d}.dev{background:#c4a24f}.bad{background:#b84d52}.assurance{display:grid;gap:14px}.claim{background:#0a353e;color:#fff;padding:14px 20px;border-radius:14px;text-align:center;font-size:13px;font-weight:900}.claim small{display:block;font-size:9px;font-weight:500;margin-top:5px}.evidence-row{display:grid;grid-template-columns:repeat(5,1fr);gap:9px}.evidence-row>div{border:2px solid #0a353e;border-radius:12px;padding:12px;text-align:center;font-weight:900}.evidence-row small{display:block;font-size:7px;color:#657169;margin-top:5px;font-weight:500}.decisions{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.decisions b{padding:12px;border-radius:999px;text-align:center;color:#fff;background:#563c7d}.decisions b:nth-child(1){background:#1d8b56}.decisions b:nth-child(3){background:#c4a24f;color:#1d2921}.decisions b:nth-child(4){background:#b84d52}@media(max-width:900px){.deck{grid-template-columns:1fr}.rail{display:none}.slide{width:96vw}.stage{padding:8px}.cards.three,.cards.five{grid-template-columns:repeat(2,1fr)}}
    '''
    js = r'''
    const slides=[...document.querySelectorAll('.slide')], thumbs=[...document.querySelectorAll('.thumb')];let idx=0;
    function go(i){idx=(i+slides.length)%slides.length;slides.forEach((s,n)=>s.classList.toggle('show',n===idx));thumbs.forEach((t,n)=>t.classList.toggle('active',n===idx));thumbs[idx]?.scrollIntoView({block:'nearest'})}
    thumbs.forEach((t,i)=>t.onclick=()=>go(i));document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='PageDown')go(idx+1);if(e.key==='ArrowLeft'||e.key==='PageUp')go(idx-1)});
    '''
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(blueprint.lecture_title)} · Presenter</title><style>{css}</style></head><body><div class="deck"><aside class="rail"><div class="brand">ISCARB · PRESENTER v5</div><p>{html.escape(_faculty_short(blueprint.engineering_thesis,180))}</p><p><b>{html.escape(release_state)}</b> · 20 visual units · use ← →</p>{''.join(thumbs)}</aside><main class="stage">{''.join(slides)}</main></div><script>{js}</script></body></html>'''
