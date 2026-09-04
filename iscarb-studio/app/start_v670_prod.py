from __future__ import annotations
"""ISCARB Faculty Studio v6.7.0 production template release over stable v4.7 core."""
from fastapi import Body, Query, HTTPException
from fastapi.responses import Response
from urllib.parse import quote

from .start_v470 import app
from . import start_v440 as base
from . import start_v470 as prev
from . import main as engine_main
from . import presenter_v67_prod as presenter
from .gate_v19_prod import deterministic_gate as gate_v19
from .v670_contract import (
    SlideContract, Assurance, chapter_design_tokens,
    domain_spine_layout, local_context_motif, local_context_visual_request,
    physical_slide_plan, rubric_grid, verdict_eligible,
    pcdn_unlock_state, rubric_credit_allowed, decision_form_complete,
)

PUBLIC_VERSION="6.7.0"
PIPELINE_ID="faculty-studio-v6.7.0-production-automated-template"

# Existing v4.4 route functions resolve these module globals at request time.
base.engine.deterministic_gate=gate_v19
engine_main.deterministic_gate=gate_v19
base.render_presenter_preview=presenter.render_presenter_preview
base.export_presenter_pptx=presenter.export_presenter_pptx
base.export_presenter_pdf=presenter.export_presenter_pdf
base.PUBLIC_VERSION=PUBLIC_VERSION
base.PIPELINE_ID=PIPELINE_ID
prev.PUBLIC_VERSION=PUBLIC_VERSION
prev.PIPELINE_ID=PIPELINE_ID

_prev_health=base._health_v440

def _health_v670():
    data=_prev_health()
    data.update({
        "version":PUBLIC_VERSION,
        "pipeline":PIPELINE_ID,
        "deterministic_gate":"v19-production-template-on-v16",
        "presenter_renderer":"v6.7 physical-plan: cover + U01-U20 + SOURCE EXPANSION + close",
        "chapter_theme":"stable per-chapter high-contrast Design Tokens",
        "fixed_task_footer":"YOUR TASK is outside content-flow geometry",
        "strict_rule_payloads":"PCDN, knowledge-state and assurance-chain fields remain separate",
        "rubric_grid":"6 criteria x 4 substantive levels; placeholder cells are release-blocking",
        "domain_spine":"auto-layout with continuation pages when needed",
        "verdict_gate":"Bounded Verdict blocked until assurance chain and rubric are complete",
        "source_expansion":"character-aware non-lossy splitting under Balanced30",
        "local_context_background":"context-keyed procedural SVG fallback plus provider-agnostic image request",
    })
    return data

base._health_v440=_health_v670
base.engine.health=_health_v670

# Remove any accidentally inherited architecture endpoints before registering v6.7.
_replaced={"/api/schema/slide-contract","/api/design-tokens","/api/visual/local-context-request","/api/visual/local-context-background","/api/presentation/domain-spine-layout","/api/presentation/physical-plan","/api/assessment/verdict-eligibility","/api/interaction/pcdn-state","/api/assessment/rubric-eligibility","/api/assessment/decision-complete"}
app.router.routes[:]=[r for r in app.router.routes if getattr(r,"path",None) not in _replaced]

@app.get("/api/design-tokens")
def design_tokens(lecture_title:str=Query(default=""), primary:str=Query(default="")):
    tokens=chapter_design_tokens(lecture_title,primary)
    return {"lecture_title":lecture_title,"tokens":tokens.model_dump(),"css_variables":tokens.css_variables(),"contrast_checks":tokens.contrast_checks()}

@app.get("/api/schema/slide-contract")
def slide_contract_schema(): return SlideContract.model_json_schema()

@app.post("/api/validation/slide-contract")
def validate_slide_contract(payload:dict=Body(default_factory=dict)):
    return {"valid":True,"slide":SlideContract.model_validate(payload).model_dump(mode="json")}

@app.post("/api/interaction/pcdn-state")
def pcdn_state(payload:dict=Body(default_factory=dict)):
    return pcdn_unlock_state(str(payload.get("predict","")),str(payload.get("constraint","")),str(payload.get("derive","")))

@app.post("/api/assessment/rubric-eligibility")
def rubric_eligibility(payload:dict=Body(default_factory=dict)):
    level=str(payload.get("level","")); allowed=rubric_credit_allowed(level,artifact_url=str(payload.get("artifact_url","")),source_anchor=str(payload.get("source_anchor","")))
    return {"allowed":allowed,"requires_evidence":level.strip().lower() in {"ready","distinguished"}}

@app.post("/api/assessment/decision-complete")
def decision_complete(payload:dict=Body(default_factory=dict)):
    return {"complete":decision_form_complete({k:str(v) for k,v in payload.items()})}

@app.post("/api/visual/local-context-request")
def local_context_request(payload:dict=Body(default_factory=dict)):
    title=str(payload.get("lecture_title","")); context=str(payload.get("local_context",""))
    try: request=local_context_visual_request(title,context)
    except ValueError as exc: raise HTTPException(422,str(exc))
    request["fallback_url"]="/api/visual/local-context-background?lecture_title="+quote(title,safe="")+"&local_context="+quote(context,safe="")
    return request

@app.get("/api/visual/local-context-background")
def local_context_background(lecture_title:str=Query(default=""),local_context:str=Query(default="")):
    motif=local_context_motif(local_context); t=chapter_design_tokens(lecture_title)
    bg,panel,primary,cyan,gold=t.bg,t.panel_soft,t.primary,t.cyan,t.heritage
    drawings={
      "clinical":f'<path d="M800 210v260M670 340h260" stroke="{cyan}" stroke-width="36" stroke-linecap="round"/><path d="M430 590h130l35-80 42 145 55-110h300" fill="none" stroke="{primary}" stroke-width="12"/>',
      "banking":''.join(f'<rect x="{520+i*120}" y="{620-h}" width="62" height="{h}" fill="none" stroke="{gold}" stroke-width="10"/>' for i,h in enumerate((130,220,310,410)))+f'<circle cx="1030" cy="280" r="105" fill="none" stroke="{cyan}" stroke-width="12"/>',
      "crowd":''.join(f'<circle cx="{460+c*78+(r%2)*18}" cy="{260+r*82}" r="12" fill="{cyan}"/>' for r in range(4) for c in range(8))+f'<path d="M340 660 C560 500 830 720 1220 535" fill="none" stroke="{primary}" stroke-width="14"/>',
      "industrial":f'<circle cx="670" cy="390" r="145" fill="none" stroke="{gold}" stroke-width="15"/><circle cx="670" cy="390" r="52" fill="none" stroke="{cyan}" stroke-width="12"/><circle cx="1010" cy="480" r="100" fill="none" stroke="{primary}" stroke-width="15"/>',
      "government":f'<path d="M500 260h600M470 310h660M530 310v300M680 310v300M830 310v300M980 310v300M450 625h700" fill="none" stroke="{gold}" stroke-width="12"/><circle cx="800" cy="185" r="58" fill="none" stroke="{cyan}" stroke-width="11"/>',
      "heritage":f'<path d="M290 665 C470 475 650 710 840 560 C1010 440 1190 570 1320 490" fill="none" stroke="{gold}" stroke-width="17"/><circle cx="960" cy="280" r="145" fill="none" stroke="{primary}" stroke-width="11"/><circle cx="960" cy="280" r="82" fill="none" stroke="{primary}" stroke-width="7"/>'}
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900"><rect width="1600" height="900" fill="{bg}"/><rect x="190" y="90" width="1220" height="690" rx="72" fill="{panel}" stroke="{primary}" stroke-width="5" opacity=".96"/>{drawings[motif]}<path d="M0 790 Q390 660 760 800 T1600 760 V900 H0Z" fill="{gold}" opacity=".16"/></svg>'
    return Response(svg,media_type="image/svg+xml",headers={"Cache-Control":"public,max-age=86400","X-ISCARB-Motif":motif})

@app.post("/api/presentation/domain-spine-layout")
def presentation_domain_spine_layout(payload:dict=Body(default_factory=dict)):
    families=payload.get("families",[])
    if not isinstance(families,list): raise HTTPException(422,"families must be a list")
    return {"pages":domain_spine_layout([str(x) for x in families])}

@app.post("/api/presentation/physical-plan")
def presentation_physical_plan(payload:dict=Body(default_factory=dict)):
    from .models import Blueprint
    bp=Blueprint.model_validate(payload.get("blueprint",payload)); target=int(payload.get("target_physical_slides",30)) if "blueprint" in payload else 30
    try: plan=physical_slide_plan(bp,target=target,strict=True)
    except ValueError as exc: raise HTTPException(422,str(exc))
    return {"slides":plan,"physical_total":len(plan),"core_units":20,"source_expansions":sum(x["kind"]=="SOURCE_EXPANSION" for x in plan)}

@app.post("/api/assessment/verdict-eligibility")
def verdict_eligibility(payload:dict=Body(default_factory=dict)):
    if "blueprint" in payload or "units" in payload:
        from .models import Blueprint
        bp=Blueprint.model_validate(payload.get("blueprint",payload)); return {"eligible":verdict_eligible(bp),"rubric_complete":rubric_grid(bp) is not None}
    try: chain=Assurance.model_validate(payload)
    except Exception: return {"eligible":False,"reason":"five separate assurance fields are required"}
    return {"eligible":chain.complete,"reason":"complete" if chain.complete else "incomplete assurance chain"}

_original_critical=engine_main._critical_presenter_failures
def _critical_v670(checks):
    failures=list(_original_critical(checks))
    for name in ("v19_dynamic_chapter_theme_contrast","v19_pcdn_fields_are_separate","v19_known_unknown_monitor_fields_are_separate","v19_assurance_chain_fields_are_separate","v19_rubric_grid_has_6x4_substantive_cells","v19_domain_spine_auto_layout_preserves_all_families","v19_source_expansion_textboxes_within_character_cap","v19_verdict_gate_requires_assurance_chain","v19_physical_plan_contains_all_20_core_units","v19_local_context_background_is_variable","v19_narrative_contract_complete","v19_production_template_pass"):
        if checks.get(name) is False and name not in failures: failures.append(name)
    return failures
engine_main._critical_presenter_failures=_critical_v670
