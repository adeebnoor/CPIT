from types import SimpleNamespace as NS
import os

# Importing run installs the exact production patch chain without starting uvicorn.
import run  # noqa: F401
from app import start_v440 as base
from app import patch_v726_timebox_tasks as timebox
from app import patch_v727_local_case_scaffold as scaffold
from app import patch_v728_peer_review_decision_boxes as v728

# v7.2.9 changes only the visual projection; all v7.2.8 classroom invariants
# below must remain true under the new ZTM layer.
EXPECTED_BUILDS = {
    "7.2.8-golden-v660-timeboxed-scaffolded-peerreview",
    "7.2.9-golden-v660-ztm",
}
assert os.getenv("ISCARB_BUILD_ID") in EXPECTED_BUILDS, os.getenv("ISCARB_BUILD_ID")

health = dict(base._health_v440())
assert health.get("time_boxing_version") == "v7.2.6", health
assert health.get("scaffolding_version") == "v7.2.7", health
assert health.get("visual_ergonomics_version") == "v7.2.8", health
assert "two questions" in str(health.get("peer_review_quick_card", "")).lower(), health
assert "decision evidence box" in str(health.get("source_expansion_decision_box", "")).lower(), health

# Time-boxing is an engine rule, not a Ch10-only edit.
assert timebox._box_for_unit(5) == "60-90 sec"
assert timebox._box_for_unit(11, "Saudi/local application") == "5-7 min"
assert timebox._box_for_unit(16, "Build the decision artifact") == "5-7 min"

# Rule 11 must stage a small mechanism-first case before the richer local transfer.
probe = NS(
    lecture_title="Dependable systems",
    engineering_thesis="Dependability requires evidence and bounded assumptions",
    source_topic_families=["Redundancy and diversity"],
)
case = scaffold._micro_case(probe).lower()
assert "redund" in case and "power" in case, case

# Rule 19 learner surface is the two-question quick card; the 6x4 rubric stays elsewhere.
units = [NS(number=i, title=f"U{i}", engineering_question="q", core_content=[], pedagogy_content=[], student_action="TIMEBOX: 3 min - old task", takeaway="") for i in range(1, 21)]
bp = NS(units=units, release_notes=[])
v728._operationalize_rule19(bp)
u19 = bp.units[18]
assert u19.title == "Peer-review quick card", u19.title
assert len(u19.core_content) == 2, u19.core_content
assert "independently inspectable" in u19.core_content[0].lower()
assert "what variable" in u19.core_content[1].lower()

# Every Source Expansion gets an explicit bridge from theory to decision + inspectable evidence.
spec = {
    "title": "Formal methods — mechanism, benefits, adoption limits",
    "source_anchor": "[P1] SLIDES 39–45",
    "content": ["Formal specification can expose inconsistencies before implementation."],
}
out = v728._add_decision_box_to_specs([spec])[0]
assert out["content"][0].startswith("DECISION EVIDENCE BOX"), out
assert "artifact or test" in out["content"][0].lower(), out["content"][0]

print("PASS: Golden v6.6 + time-boxing + Rule 11 scaffold + peer-review quick card + Source Expansion decision boxes")
