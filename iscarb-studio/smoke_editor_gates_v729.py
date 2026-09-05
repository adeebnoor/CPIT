import os

import run  # installs production patch chain
from app import start_v440 as base
from app import patch_v729_editor_gates as gates

assert os.getenv("ISCARB_BUILD_ID") in {
    "7.3.0-golden-v660-universal-meta-gates",
    "7.3.1-golden-v660-clean-projection",
}, os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("assurance_profile_version") == "v7.2.9", health
assert health.get("assurance_profile_count") == 12, health
assert "only" in health.get("assurance_profile_scope", ""), health
text = "\n".join(health.get("assurance_profile_gates", []))
for needle in (
    "Breaking Variable", "Falsification First", "Quantified Uncertainty",
    "Data Layer", "Dynamic Reliability", "AI Accountability Boundary",
    "Quantitative Analysis", "Risk Decomposition", "Verification vs Validation",
    "Industry Variables", "Evidence Chain", "Local Owner",
):
    assert needle in text, needle
assert len(gates.RULES) == 12
print("PASS: v7.2.9 assurance domain profile remains available under universal meta layer")
