import os
from pathlib import Path

import run  # installs full production patch chain
from app import start_v440 as base
from app.definition_extractor import extract_definitions_from_text
from app.patch_v737_instructional_director import STATIONS, TRANSITIONS, _split_timebox, _youify

assert os.getenv("ISCARB_BUILD_ID") in {"7.3.7-instructional-director", "8.0.0-hybrid-visual-narrative"}, os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("build_id") in {"7.3.7-instructional-director", "8.0.0-hybrid-visual-narrative"}, health
assert health.get("instructional_director_version") in {"7.3.7", "8.0.0"}, health
assert "U00" in health.get("instructional_director_knowledge", ""), health
assert "3-second" in health.get("instructional_director_knowledge", ""), health
assert "20-unit" in health.get("knowledge_anchor_contract", ""), health

sample = """--- Page 8 ---
Principal properties
Availability
The probability that the system will be up and running and able to deliver useful services to users.
Reliability
The probability that the system will correctly deliver services as expected by users.
Safety
A judgment of how likely it is that the system will cause damage to people or its environment.
--- Page 9 ---
Security
A judgment of how likely it is that the system can resist accidental or deliberate intrusions.
Resilience
A judgment of how well a system can maintain the continuity of its critical services in the presence of disruptive events.
"""
defs = extract_definitions_from_text(sample, limit=8)
terms = [d["term"] for d in defs]
for required in ("Availability", "Reliability", "Safety", "Security", "Resilience"):
    assert required in terms, (required, defs)
assert all(d.get("verbatim") is True for d in defs)
assert {d.get("page") for d in defs}.issuperset({8, 9})

label, task = _split_timebox("TIMEBOX: 5-7 min - Select the defensible mechanism.")
assert label == "5-7 min", (label, task)
assert task == "Select the defensible mechanism.", task
you_task = _youify(task)
assert you_task.startswith("You are the responsible engineer."), you_task
assert "Select the defensible mechanism" in you_task, you_task

assert [s["label"] for s in STATIONS] == ["Crisis", "Map", "Mechanism", "Evidence", "Decision"]
assert TRANSITIONS[8] == "BUT — is the technical solution alone enough?"

static = Path(__file__).parent / "app" / "static"
js = (static / "learning_v737.js").read_text(encoding="utf-8")
css = (static / "learning_v737.css").read_text(encoding="utf-8")
for needle in (
    "showOpening", "showKnowledgeAnchor", "flipCard", "definition_ack",
    "revealSource", "taskDrawer", "timeboxBadge", "glossarySidebar",
    "showBridge", "crisis_anchor",
):
    assert needle in js, needle
for needle in ("journeyDock", "focusQuestion", "taskDrawer", "glossarySidebar", "flipCard", "bridgeStatement"):
    assert needle in css, needle

paths = {getattr(route, "path", "") for route in run.app.router.routes}
assert "/learn/{job_id}" in paths
assert "/api/learning/{job_id}/bootstrap" in paths

print("PASS: Instructional Director A1-A4 B1-B3 C1-C3 contract preserved under current build")