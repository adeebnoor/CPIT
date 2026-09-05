import os
from types import SimpleNamespace as NS

import run  # installs production patch chain
from app import start_v440 as base
from app import patch_v730_universal_meta_gates as meta
from app import patch_v729_editor_gates as assurance

assert os.getenv("ISCARB_BUILD_ID") in {
    "7.3.0-golden-v660-universal-meta-gates",
    "7.3.1-golden-v660-clean-projection",
}, os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("universal_meta_gates_version") == "v7.3.0", health
assert health.get("universal_meta_gates_count") == 12, health
assert "Universal meta-layer first" in health.get("universal_gate_architecture", ""), health
assert health.get("assurance_profile_scope", "").endswith("only"), health

rules = meta.UNIVERSAL_RULES
assert len(rules) == 12
assert [r["id"] for r in rules] == [f"U{i:02d}" for i in range(1, 13)]
for name in (
    "Global Breaking Variable", "Quantify vs Qualify", "Verification vs Validation",
    "Ownership & Accountability", "Data Layer", "AI Assist + Continuous Monitoring",
    "Human-in-the-Loop", "Evidence Chain", "Tool Standardization",
    "Inspectable Artifact", "Timebox Consistency", "Local Transfer",
):
    assert any(r["name"] == name for r in rules), name

bad = meta.evaluate_universal_gate_responses({"answers": {"U01": "schedule slips if staffing drops"}})
assert bad["status"] == "RETURN_FOR_REVISION" and bad["failed"], bad

answers = {
    "U01": "Staffing below four engineers reverses the delivery verdict.",
    "U02": "Schedule variance must remain below ten percent.",
    "U03": "Tests verify implementation; stakeholder acceptance validates the requirement.",
    "U04": "The programme manager owns the decision and the sponsor signs off.",
    "U05": "N/A because this bounded example uses no decision data source.",
    "U06": "AI drafts evidence only; the team monitors schedule variance weekly.",
    "U07": "N/A because AI has no decision authority in this example.",
    "U08": "Claim evidence warrant counter-evidence residual uncertainty and verdict are all documented.",
    "U09": "Critical path analysis is used and the constrained path is shown.",
    "U10": "The signed decision record and calculation sheet are independently inspectable.",
    "U12": "A Saudi delivery case names the programme manager as accountable owner.",
}
good = meta.evaluate_universal_gate_responses({"answers": answers})
assert good["status"] == "ACCEPT_FOR_REVIEW" and good["overall_pass"], good

profile = NS(lecture_title="Project Management", weekly_focus="Scheduling and delivery")
bp = NS(lecture_title="Project scheduling", source_topic_families=["Critical path", "Resources"])
assert assurance._assurance_profile(profile, bp) is False
profile2 = NS(lecture_title="Dependable Systems", weekly_focus="Reliability and safety")
bp2 = NS(lecture_title="Dependable Systems", source_topic_families=["Dependability properties"])
assert assurance._assurance_profile(profile2, bp2) is True

print("PASS: v7.3.0 universal meta-gates + conditional assurance domain profile")
