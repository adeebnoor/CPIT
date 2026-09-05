import os
from types import SimpleNamespace as NS

import run  # installs production patch chain
from app import start_v440 as base
from app import patch_v731_projection_legibility as leg

assert os.getenv("ISCARB_BUILD_ID") == "7.3.1-golden-v660-clean-projection", os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("projection_legibility_version") == "v7.3.1", health
assert health.get("projection_min_ppt_task_pt", 0) >= 10.0, health
assert health.get("projection_min_pdf_task_pt", 0) >= 8.0, health
assert "two-question" in health.get("projection_rule19", ""), health
assert "3+2" in health.get("projection_five_card_reflow", ""), health
assert "adaptively" in health.get("projection_expansion_fill", ""), health
assert "assessment layer" in health.get("projection_gate_visibility", ""), health

# Long editor prose must never be dumped into learner-visible pedagogy.
u = NS(
    pedagogy_content=[
        "EDITOR GATE - VERY LONG: this should stay in the assessment layer",
        "UNIVERSAL CHECK - another long gate",
        "MICRO-CASE - keep this visible",
    ],
    student_action="TIMEBOX: 5-7 min - " + " ".join(["word"] * 40),
)
bp = NS(units=[u])
leg._clean_visible_gates(bp)
assert len(u.pedagogy_content) == 1 and u.pedagogy_content[0].startswith("MICRO-CASE"), u.pedagogy_content
assert u.student_action.startswith("TIMEBOX: 5-7 min - "), u.student_action
assert len(leg._split_timebox(u.student_action)[1].split()) <= 23, u.student_action

print("PASS: v7.3.1 projection legibility + whitespace guard")
