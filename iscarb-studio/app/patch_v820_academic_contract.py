from __future__ import annotations

"""ISCARB v8.2 — academic-reference contract for the public Faculty Studio.

This is deliberately the final production patch.  It does not invent another
lecture grammar: it publishes the grammar in the v8 reference engine and makes
it visible on the Studio surface so faculty, generator and audit use the same
language.
"""

import inspect
import json
from typing import Any

from fastapi.responses import HTMLResponse

BUILD_ID = "8.2.0-academic-contract"
FLOW = ["CRISIS", "MAP", "TRADE-OFF", "EVIDENCE", "VERDICT"]
PHASES = ["UNDERSTAND", "PRACTISE", "MASTER", "DISTINGUISH"]

RULES = [
    (1, "Professional / ethical title + ill-structured crisis", "Decision under missing evidence, with a named consequence"),
    (2, "Domain spine", "Chapter as questions the crisis cannot yet answer"),
    (3, "Exactly five measurable outcomes", "Outcomes terminate in inspectable evidence"),
    (4, "Six engineering capabilities", "Each capability is bound to where it is exercised"),
    (5, "Predict → Constraint → Derive → Name", "Written commitment before any reveal"),
    (6, "Five-step engineering flow", "CRISIS → MAP → TRADE-OFF → EVIDENCE → VERDICT"),
    (7, "Decision card", "Six canonical fields carry the hour's artifact"),
    (8, "Sixty-second source case", "A real disagreement in the source, not decoration"),
    (9, "Measurement + falsification", "Evidence is paired with what would reverse the verdict"),
    (10, "Known / unknown / monitor", "Unknown becomes a trigger and an owner"),
    (11, "Micro-case → local case", "Repeat the reasoning chain in a different, locally meaningful domain"),
    (12, "Owner, evidence, sign-off", "Three accountable roles are explicit"),
    (13, "Breaking variable", "Name the change that reverses the student's verdict"),
    (14, "Practitioner workload", "Human load is treated as a system variable"),
    (15, "Critical AI literacy + permissibility gate", "Run the gate and write its verdict into the artifact"),
    (16, "Grade the decision", "Capability levels describe quality; live slides do not become marking grids"),
    (17, "Constraint mutation", "Present → Mutate → Reason → Defend → Verdict"),
    (18, "Evidence policy / make the system operable", "State what survives and what happens before next session"),
    (19, "Peer-review quick card", "Exactly two challenge questions; formal scoring stays off-slide"),
    (20, "Bounded assurance case + readiness", "Separate judgment gates from the outcome map read from evidence"),
]

AUDITS = [
    ("NUM-01", "BLOCK", "No percentage/currency claim without a source reference or explicit unmeasured label"),
    ("SRC-01", "BLOCK", "Every source-claim card on an X unit cites the source page"),
    ("FIG-01", "BLOCK/WARN", "Source figures are actually bound to earned units"),
    ("PRED-01", "BLOCK", "Prediction gate precedes the first source-figure reveal"),
    ("CARD-01", "BLOCK", "All six canonical decision-card fields exist"),
    ("READ-01", "BLOCK", "Every readiness evidence reference resolves"),
    ("DOM-01", "WARN", "Knowledge, Skill and Value are all represented"),
    ("CLAIM-01", "BLOCK", "No unsupported claim of national-exam equivalence/preparation"),
    ("TIME-01", "WARN", "Task load and cut points are visible"),
    ("TETHER-01", "WARN", "Early units remain tethered to the opening crisis"),
    ("OWN-01", "BLOCK", "Ownership and mutation force written answers"),
    ("FIT-01", "BLOCK", "No presenter unit overflows the fixed stage"),
]

ACADEMIC_CSS = r"""
<style id="iscarb-v820-academic-contract">
.academicContract{margin:28px auto 44px;max-width:1320px;padding:0 22px;color:#f5f5f8}
.academicContract .acHead{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:16px}
.academicContract h2{margin:0;font-size:clamp(24px,3vw,42px);letter-spacing:-.035em}
.academicContract h2 em{font-style:normal;color:#ff258c}.academicContract .acLead{max-width:690px;color:#b7bdc8;line-height:1.6;font-size:14px}
.academicContract .flowRail{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:18px 0 16px}
.academicContract .flowRail span{border:1px solid rgba(44,220,255,.28);background:#071118;padding:11px 10px;border-radius:10px;text-align:center;font-weight:850;font-size:12px;letter-spacing:.07em;color:#2cdcff}
.academicContract .phaseRail{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:18px}
.academicContract .phaseRail span{padding:8px 10px;border-radius:999px;background:#151219;border:1px solid rgba(220,181,107,.24);text-align:center;color:#dcb56b;font-size:11px;font-weight:800;letter-spacing:.06em}
.academicContract .acGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.academicContract .rule{min-height:122px;border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:13px;background:linear-gradient(180deg,#0e1118,#090b10)}
.academicContract .rule .n{color:#ff258c;font-size:11px;font-weight:900;letter-spacing:.1em}.academicContract .rule b{display:block;margin:6px 0 5px;font-size:13px;line-height:1.28}.academicContract .rule p{margin:0;color:#9fa8b6;font-size:11px;line-height:1.45}
.academicContract .xRule{margin:16px 0;padding:13px 15px;border-left:3px solid #dcb56b;background:rgba(220,181,107,.07);color:#d9d3ca;font-size:12px;line-height:1.55}
.academicContract .auditGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.academicContract .audit{border:1px solid rgba(255,255,255,.09);border-radius:10px;padding:10px;background:#090b10}.academicContract .audit strong{color:#2cdcff;font-size:11px}.academicContract .audit i{float:right;font-style:normal;color:#dcb56b;font-size:9px;font-weight:900}.academicContract .audit small{display:block;clear:both;margin-top:5px;color:#9fa8b6;line-height:1.35}
@media(max-width:980px){.academicContract .acGrid,.academicContract .auditGrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.academicContract .acHead{display:block}.academicContract .flowRail{grid-template-columns:1fr}.academicContract .phaseRail,.academicContract .acGrid,.academicContract .auditGrid{grid-template-columns:1fr}}
</style>
"""


def _contract_html() -> str:
    rules = "".join(
        f'<article class="rule"><span class="n">RULE {n:02d}</span><b>{title}</b><p>{purpose}</p></article>'
        for n, title, purpose in RULES
    )
    audits = "".join(
        f'<div class="audit"><strong>{code}</strong><i>{level}</i><small>{desc}</small></div>'
        for code, level, desc in AUDITS
    )
    flow = "".join(f"<span>{x}</span>" for x in FLOW)
    phases = "".join(f"<span>{x}</span>" for x in PHASES)
    return f'''<section class="academicContract" id="academic-contract">
      <div class="acHead"><div><div style="color:#2cdcff;font-size:11px;font-weight:900;letter-spacing:.12em">ACADEMIC REFERENCE · v8.2</div><h2>Twenty rules. <em>One defensible decision.</em></h2></div><p class="acLead">The public Studio now follows the same academic contract as the hand-built reference engine: commit before reveal, falsify rather than merely assert, preserve source figures, and issue only a bounded verdict supported by inspectable evidence.</p></div>
      <div class="flowRail">{flow}</div><div class="phaseRail">{phases}</div>
      <div class="acGrid">{rules}</div>
      <div class="xRule"><b>Source-expansion rule (X01…Xn):</b> the twenty rules are the fixed learning jobs. Source figures may create additional X units only when a preceding rule earns the reveal. An unbound figure is dropped, never appended as filler. Therefore the quality contract is <b>20 core rules + earned source expansion</b>, not an arbitrary 20-page cap.</div>
      <h3 style="margin:22px 0 10px">Release audit</h3><div class="auditGrid">{audits}</div>
    </section>'''


ACADEMIC_JS = r"""
<script id="iscarb-v820-runtime">
(function(){
  const V='8.2.0 · ACADEMIC CONTRACT';
  function textReplace(root, from, to){
    const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT); let n;
    while(n=w.nextNode()){ if(n.nodeValue && n.nodeValue.includes(from)) n.nodeValue=n.nodeValue.split(from).join(to); }
  }
  function apply(){
    document.querySelectorAll('.version').forEach(x=>x.textContent=V);
    textReplace(document.body,'CRISIS · PREDICT','CRISIS · FRAME');
    textReplace(document.body,'ANALYSE · FALSIFY','MAP · FALSIFY');
    textReplace(document.body,'DESIGN · OWN','TRADE-OFF · OWN');
    textReplace(document.body,'EVIDENCE · CHALLENGE','EVIDENCE · CHALLENGE');
    textReplace(document.body,'BOUND THE VERDICT','VERDICT · BOUND IT');
    textReplace(document.body,'Twenty fixed learning jobs; technical content remains source-locked.','Twenty fixed rule-jobs; source figures expand only where a preceding rule earns the reveal.');
    textReplace(document.body,'Twenty units. Twenty real jobs.','Twenty core rules. Earned source expansion.');
    const build=document.querySelector('a[href="#builder"],a[href="#build"],a[href="#upgrade"]');
    if(build && !document.querySelector('a[href="#academic-contract"]')){
      const a=document.createElement('a'); a.href='#academic-contract'; a.textContent='Academic Contract'; a.style.cssText='margin-left:12px;color:#dcb56b;font-size:12px;font-weight:800;text-decoration:none'; build.parentElement && build.parentElement.appendChild(a);
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',apply); else apply();
})();
</script>
"""


def _decorate_html(html: str) -> str:
    # The contract is inserted just before the footer rather than replacing the
    # existing builder.  Faculty can therefore compare promise, workflow and
    # release criteria on one page.
    if "iscarb-v820-academic-contract" not in html:
        html = html.replace("</head>", ACADEMIC_CSS + "\n</head>", 1)
    if "id=\"academic-contract\"" not in html:
        marker = "</footer>"
        if marker in html:
            html = html.replace(marker, _contract_html() + "\n" + marker, 1)
        else:
            html = html.replace("</body>", _contract_html() + "\n</body>", 1)
    if "iscarb-v820-runtime" not in html:
        html = html.replace("</body>", ACADEMIC_JS + "\n</body>", 1)
    return html


async def _call_endpoint(endpoint, *args, **kwargs):
    value = endpoint(*args, **kwargs)
    if inspect.isawaitable(value):
        value = await value
    return value


def apply_v820_academic_contract_patch(app) -> None:
    if getattr(app.state, "iscarb_v820_patched", False):
        return
    app.state.iscarb_v820_patched = True

    # Capture whichever home route survived all earlier production patches.
    home_routes = [r for r in app.router.routes if getattr(r, "path", None) == "/" and "GET" in (getattr(r, "methods", set()) or set())]
    if not home_routes:
        raise RuntimeError("ISCARB v8.2 could not find the production home route")
    previous = home_routes[-1].endpoint
    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/"]

    @app.get("/", include_in_schema=False)
    async def academic_home():
        response = await _call_endpoint(previous)
        if isinstance(response, HTMLResponse):
            html = response.body.decode(response.charset or "utf-8")
            headers = dict(response.headers)
            headers.pop("content-length", None)
            headers["X-ISCARB-Academic-Contract"] = BUILD_ID
            headers["X-ISCARB-Flow"] = "crisis-map-tradeoff-evidence-verdict"
            return HTMLResponse(_decorate_html(html), status_code=response.status_code, headers=headers)
        if isinstance(response, str):
            return HTMLResponse(_decorate_html(response), headers={"X-ISCARB-Academic-Contract": BUILD_ID})
        return response

    @app.get("/api/academic-contract", include_in_schema=False)
    def academic_contract() -> dict[str, Any]:
        return {
            "build_id": BUILD_ID,
            "flow": FLOW,
            "phases": PHASES,
            "core_rule_count": 20,
            "source_expansion": "X01…Xn only after a rule earns a source-figure reveal",
            "rules": [{"number": n, "rule": title, "forces": purpose} for n, title, purpose in RULES],
            "release_audit": [{"id": c, "level": l, "rule": d} for c, l, d in AUDITS],
            "hard_constraints": [
                "Commit before reveal",
                "Falsify, do not merely assert",
                "Cite the page or say unmeasured",
                "No unsupported claim of national-exam equivalence or preparation",
                "Source figures are bound to learning jobs, never decorative filler",
            ],
        }
