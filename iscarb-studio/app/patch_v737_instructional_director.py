from __future__ import annotations

"""v7.3.7 — Engine-wide Instructional Director amendments.

A1-A4: progressive disclosure, glossary, task drawer, journey bar.
B1-B3: direct-address tasks, mandatory logical bridges, crisis anchoring.
C1-C3: P1-verbatim U00 knowledge anchor, define-before-apply, flip cards.

U00 is deliberately outside the fixed twenty-unit Blueprint contract.
"""

import re
from typing import Any

from . import learning_experience as learning
from . import start_v440 as base
from .definition_extractor import extract_job_definitions

VERSION = "7.3.7"
BUILD_ID = "7.3.7-instructional-director"
_PREVIOUS_HEALTH = None

STATIONS = [
    {"id": "crisis", "label": "Crisis", "units": [1]},
    {"id": "map", "label": "Map", "units": [2, 3, 4, 5]},
    {"id": "mechanism", "label": "Mechanism", "units": list(range(6, 16))},
    {"id": "evidence", "label": "Evidence", "units": [16, 17, 18, 19]},
    {"id": "decision", "label": "Decision", "units": [20]},
]

TRANSITIONS = dict(learning.TRANSITIONS)
TRANSITIONS.update({
    2: "THEREFORE — map the terrain before you choose a solution.",
    5: "THEREFORE — commit to your prediction before the mechanism is revealed.",
    6: "THEREFORE — now test your prediction against the actual mechanism.",
    8: "BUT — is the technical solution alone enough?",
    10: "IN CONTRAST — a measured result can still hide an unmanaged risk.",
    12: "MORE IMPORTANTLY — a design without an accountable owner cannot be defended.",
    16: "THEREFORE — turn your reasoning into inspectable evidence.",
    20: "FINALLY — issue only the verdict your evidence can support.",
})

_TIMEBOX_RE = re.compile(r"^\s*TIMEBOX\s*:\s*(.+?)\s+(?:-|–|—)\s+(.*)$", re.I | re.S)
_IMPERATIVE_RE = re.compile(r"^(identify|select|choose|compare|explain|analyse|analyze|evaluate|design|build|derive|name|state|justify|defend|inspect|test|decide|write|map|rank|classify|propose|calculate|quantify|predict|review|trace)\b", re.I)


def _split_timebox(text: str, fallback_minutes: int = 0) -> tuple[str, str]:
    value = " ".join(str(text or "").split())
    match = _TIMEBOX_RE.match(value)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return (f"{fallback_minutes} min" if fallback_minutes else "", value)


def _youify(text: str) -> str:
    """Make the task direct-address without changing its technical requirement."""
    value = " ".join(str(text or "").split()).strip()
    if not value:
        return "You are the responsible engineer. State the decision you must make next."
    low = value.lower()
    if low.startswith(("you ", "you’re ", "you're ", "as the ")):
        return value
    if _IMPERATIVE_RE.match(value):
        return "You are the responsible engineer. " + value[0].upper() + value[1:]
    return "You are the responsible engineer. Your task now is to " + value[0].lower() + value[1:]


def _short_crisis(value: str, cap: int = 230) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= cap else text[: cap - 1].rstrip() + "…"


def _public_blueprint_v737(job) -> dict[str, Any]:
    data = learning._PUBLIC_BLUEPRINT_V736(job)  # type: ignore[attr-defined]
    crisis = _short_crisis(data.get("central_engineering_crisis", ""))
    for unit in data.get("units", []):
        number = int(unit.get("number") or 0)
        timebox, task = _split_timebox(unit.get("student_action", ""), int(unit.get("planned_minutes") or 0))
        unit["task_text"] = _youify(task)
        unit["timebox"] = timebox
        unit["student_action"] = unit["task_text"]
        unit["transition"] = TRANSITIONS.get(number, "")
        unit["crisis_anchor"] = f"Remember the opening crisis: {crisis}" if number in {6, 8, 10} and crisis else ""
    return data


def _student_page_v737(job_id: str) -> str:
    return f"""<!doctype html><html lang='en' dir='ltr' data-theme='dark'><head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>ISCARB Instructional Director</title>
<link rel='stylesheet' href='/static/learning_v736.css?v=7.3.6'>
<link rel='stylesheet' href='/static/learning_v737.css?v={VERSION}'>
</head><body data-job='{job_id}' data-role='student'>
<div id='app'><div class='boot'>Preparing the engineering journey…</div></div>
<script src='/static/learning_v737.js?v={VERSION}' defer></script></body></html>"""


def _health_v737() -> dict[str, Any]:
    previous = _PREVIOUS_HEALTH
    data = dict(previous()) if previous is not None else {}
    data.update({
        "build_id": BUILD_ID,
        "instructional_director_version": VERSION,
        "instructional_director_visual": "A1 progressive disclosure; A2 fixed glossary; A3 task drawer; A4 five-station journey bar",
        "instructional_director_narrative": "B1 direct-address tasks; B2 mandatory logical bridges; B3 crisis anchors at U06/U08/U10",
        "instructional_director_knowledge": "C1 P1-verbatim U00; C2 accessible 3-second define-before-apply acknowledgement; C3 flip cards",
        "knowledge_anchor_contract": "U00 is a pre-unit learning layer and does not alter the fixed 20-unit Blueprint grammar.",
    })
    return data


def apply_v737_instructional_director_patch(app) -> None:
    global _PREVIOUS_HEALTH
    if getattr(learning, "_V737_PATCHED", False):
        return
    learning._V737_PATCHED = True

    if not hasattr(learning, "_PUBLIC_BLUEPRINT_V736"):
        learning._PUBLIC_BLUEPRINT_V736 = learning._public_blueprint
    learning.VERSION = VERSION
    learning.STATIONS = STATIONS
    learning.TRANSITIONS.clear()
    learning.TRANSITIONS.update(TRANSITIONS)
    learning._public_blueprint = _public_blueprint_v737
    learning._student_page = _student_page_v737

    app.router.routes[:] = [
        route for route in app.router.routes
        if getattr(route, "path", None) != "/api/learning/{job_id}/bootstrap"
    ]

    from fastapi import Query

    @app.get("/api/learning/{job_id}/bootstrap")
    def learning_bootstrap_v737(job_id: str, student_id: str = Query(...)):
        sid = learning._student_id(student_id)
        job = learning._load_job(job_id)
        state = learning._load_state(job_id, sid)
        payload = state.get("payload") or {}
        definitions = extract_job_definitions(job, limit=12)
        return {
            "version": VERSION,
            "job_id": job_id,
            "release_state": job.status,
            "blueprint": _public_blueprint_v737(job),
            "stations": STATIONS,
            "knowledge_anchor": {
                "id": "U00",
                "label": "Knowledge Anchor",
                "definitions": definitions,
                "required_count": min(5, len(definitions)),
                "minimum_exposure_seconds": 3,
                "source_policy": "Definitions are verbatim P1 extractions. Missing definitions are never fabricated.",
            },
            "settings": learning._settings(job_id),
            "state": state,
            "rubric": learning._rubric(payload),
            "suggestions": learning._adaptive_suggestions(job, payload),
            "persistence": {
                "backend": "sqlite",
                "path_configurable": True,
                "durability": "persistent only when ISCARB_LEARNING_DB_PATH points to a mounted persistent disk",
            },
        }

    _PREVIOUS_HEALTH = base._health_v440
    base._health_v440 = _health_v737
    base.engine.health = _health_v737
