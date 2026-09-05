import os

import run  # installs production patch chain
from app import start_v440 as base
from app import patch_v729_editor_gates as gates

assert os.getenv("ISCARB_BUILD_ID") == "7.2.9-golden-v660-editor-gates"
health = dict(base._health_v440())
assert health.get("editor_gates_version") == "v7.2.9", health
assert health.get("editor_gates_count") == 12, health
text = "\n".join(health.get("editor_gates", []))
for needle in (
    "Breaking Variable", "Falsification First", "Quantified Uncertainty",
    "Data Layer", "Dynamic Reliability", "AI Accountability Boundary",
    "Quantitative Analysis", "Risk Decomposition", "Verification vs Validation",
    "Industry Variables", "Evidence Chain", "Local Owner",
):
    assert needle in text, needle
assert "returns it for revision" in health.get("submission_feedback_loop", "")
assert len(gates.RULES) == 12
print("PASS: v7.2.9 measurable editor/readiness gates locked")
