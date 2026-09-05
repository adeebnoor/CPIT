from types import SimpleNamespace as NS
import inspect
import os

# Importing run installs the exact production patch chain without starting uvicorn.
import run  # noqa: F401
from app import start_v440 as base
from app import start_v670_prod as prod
from app import v670_contract as contract
from app import presenter_v67_prod as presenter
from app import patch_v729_ztm_theme as ztm

EXPECTED_BUILD = "7.2.9-golden-v660-ztm"
assert os.getenv("ISCARB_BUILD_ID") == EXPECTED_BUILD, os.getenv("ISCARB_BUILD_ID")

health = dict(base._health_v440())
assert health.get("ztm_theme_version") == "v7.2.9", health
assert "three" in str(health.get("progressive_disclosure", "")).lower() or "stage 1" in str(health.get("progressive_disclosure", "")).lower(), health
assert "two-question" in str(health.get("rule19_learner_surface", "")).lower(), health
assert "micro-case" in str(health.get("rule11_learner_surface", "")).lower(), health
assert health.get("ztm_tokens", {}).get("bg_base") == "#FFFFFF", health
assert health.get("ztm_tokens", {}).get("alert_urgent") == "#F43F5E", health

# Exact user-approved token contract.
t = prod.chapter_design_tokens("Dependable systems")
css = t.css_variables()
assert css["--bg-base"] == "#FFFFFF"
assert css["--bg-surface"] == "#F8FAFC"
assert css["--text-heading"] == "#0F172A"
assert css["--text-body"] == "#475569"
assert css["--accent-primary"] == "#4F46E5"
assert css["--accent-cyan"] == "#06B6D4"
assert css["--alert-urgent"] == "#F43F5E"
assert all(t.contrast_checks().values()), t.contrast_checks()

# The active renderer must resolve to white ZTM surfaces and reserve rose for urgency.
assert presenter.BG == "#FFFFFF"
assert presenter.PANEL == "#F8FAFC"
assert presenter.TEXT == "#0F172A"
assert presenter.MUTED == "#475569"
assert presenter.MAGENTA == "#4F46E5"
assert presenter.DANGER == "#4F46E5"  # reject/verdict is not allowed to consume alert rose.
assert presenter._ppt_footer is ztm._ppt_footer
assert presenter._ppt_expansion is ztm._ppt_expansion
assert presenter._pdf_expansion is ztm._pdf_expansion
assert base.render_presenter_preview is ztm.render_presenter_preview_ztm

# Timebox parsing is visual-system logic, not plain text decoration.
assert ztm._timebox_parts("TIMEBOX: 3-5 min - Compare two alternatives.") == ("3-5 min", "Compare two alternatives.")
assert ztm._timebox_parts("TIMEBOX: 1 min micro-case + 5 min transfer - Apply the chain.")[0] == "1 min micro-case + 5 min transfer"

# Golden physical sequencing must consume semantic expansion specs from the current contract.
old = contract.plan_expansions
try:
    contract.plan_expansions = lambda bp, target=30: [
        {"after_unit": 6, "expansion_id": "X01", "title": "A", "content": ["DECISION EVIDENCE BOX - Decision: x. Evidence: y."], "source_anchor": "[P1] SLIDE 8", "student_task": "Use it."},
        {"after_unit": 11, "expansion_id": "X02", "title": "B", "content": ["Source detail"], "source_anchor": "[P1] SLIDE 26", "student_task": "Use it."},
    ]
    fake = NS(units=[NS(number=i) for i in range(1, 21)])
    plan = ztm._ztm_contract_plan(fake, strict=False)
    assert len(plan) == 24, len(plan)  # cover + 20 core + 2 expansions + close
    assert [x.get("unit_number") for x in plan if x["kind"] == "CORE"] == list(range(1, 21))
    assert [x.get("expansion_id") for x in plan if x["kind"] == "SOURCE_EXPANSION"] == ["X01", "X02"]
finally:
    contract.plan_expansions = old

# Progressive disclosure, taskbar gradient, pulse and reduced-motion protection are code-level invariants.
src = inspect.getsource(ztm.render_presenter_preview_ztm)
for needle in ("data-stage='1'", "linear-gradient", "TIMEBOX", "@keyframes pulse", "prefers-reduced-motion"):
    assert needle in src, needle

print("PASS: ZTM v7.2.9 tokens + floating cards + taskbar + semantic expansions + progressive disclosure")
