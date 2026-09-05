import os

import run  # installs production patch chain
from app import start_v440 as base

assert os.getenv("ISCARB_BUILD_ID") == "7.3.3-golden-v660-final-readable", os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("final_readability_version") == "v7.3.3", health
assert "dominant" in health.get("figure_first_slide_policy", ""), health
assert "no broken label" in health.get("owner_flow_policy", ""), health
assert "shortened" in health.get("diagram_collision_policy", ""), health
print("PASS: v7.3.3 final figure-first readability + owner flow repair")
