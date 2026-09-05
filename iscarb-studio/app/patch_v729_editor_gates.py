from __future__ import annotations

"""v7.2.9 - domain profile: engineering assurance/editor gates.

These 12 stricter checks are useful for dependability/reliability/safety/security
lectures, but they are NOT universal. v7.3.0 supplies the cross-course meta
structure. This profile activates only when the lecture title/focus indicates an
assurance domain, preventing MTBF/FMEA/STPA requirements from leaking into
unrelated subjects.
"""

from . import main as engine
from . import start_v440 as base

_PATCHED = False
_ORIGINAL_DRAFT = None

RULES = [
    ("R1 Breaking Variable", "Name the variable whose change would break the system or reverse the decision."),
    ("R2 Falsification First", "State the counter-evidence that would cancel or weaken the verdict."),
    ("R3 Quantified Uncertainty", "Express residual uncertainty as a confidence level or monitored trigger."),
    ("R4 Data Layer", "Treat data as a separate STS layer; check data bias and data drift independently from code."),
    ("R5 Dynamic Reliability", "Reliability is not only test pass; include continuous monitoring and maintenance."),
    ("R6 AI Accountability Boundary", "Name the human sign-off owner and what happens when AI surfaces unclear counter-evidence."),
    ("R7 Quantitative Analysis", "Support dependability claims with MTBF, availability, failure probability, or another number."),
    ("R8 Risk Decomposition", "Use FMEA, FTA, or STPA and name the component/interaction that exposes the hazard."),
    ("R9 Verification vs Validation", "Separate evidence that the implementation is correct from evidence that the requirement is right."),
    ("R10 Industry Variables", "Balance documentation burden against delivery speed in the final recommendation."),
    ("R11 Evidence Chain", "Approve only with claim -> evidence -> warrant -> counter-evidence -> residual uncertainty -> verdict."),
    ("R12 Local Owner", "For any local case, name the accountable owner: hospital, ministry, vendor, or unit."),
]

NOTE = "Assurance domain profile v7.2.9: 12 measurable checks for dependability/reliability/safety/security lectures; inactive for unrelated courses."


def _clean(v) -> str:
    return " ".join(str(v or "").split())


def _add_unique(seq, item, limit=None):
    rows = [_clean(x) for x in list(seq or []) if _clean(x)]
    if item not in rows:
        rows.append(item)
    return rows[:limit] if limit else rows


def _unit(bp, n):
    units = list(getattr(bp, "units", []) or [])
    return units[n-1] if len(units) >= n else None


def _tag_task(u, text):
    if not u:
        return
    task = _clean(getattr(u, "student_action", ""))
    if text.lower() not in task.lower():
        u.student_action = (task.rstrip(".") + "; " if task else "") + text


def _upgrade_unit(u, gates):
    if not u:
        return
    gate_texts = [f"{k}: {v}" for k, v in gates]
    existing = list(getattr(u, "elite_requirements", []) or [])
    for g in gate_texts:
        existing = _add_unique(existing, g, 16)
    u.elite_requirements = existing
    if len(gates) <= 3:
        for k, v in gates:
            line = f"EDITOR GATE - {k}: {v}"
            if not any(k.lower() in _clean(x).lower() for x in getattr(u, "pedagogy_content", []) or []):
                u.pedagogy_content = _add_unique(getattr(u, "pedagogy_content", []), line, 16)


def _assurance_profile(profile, bp) -> bool:
    text = " ".join([
        _clean(getattr(profile, "lecture_title", "")),
        _clean(getattr(profile, "weekly_focus", "")),
        _clean(getattr(bp, "lecture_title", "")),
        " ".join(_clean(x) for x in getattr(bp, "source_topic_families", []) or []),
    ]).lower()
    keys = (
        "dependab", "reliab", "safety", "security", "resilien", "fault",
        "availability", "hazard", "assurance", "critical system",
    )
    return any(k in text for k in keys)


def _apply_gates(bp):
    _upgrade_unit(_unit(bp, 10), [RULES[0], RULES[1], RULES[2]])
    _tag_task(_unit(bp, 10), "name the breaking variable, falsifier, and monitor/confidence level")

    _upgrade_unit(_unit(bp, 11), [RULES[11]])
    _tag_task(_unit(bp, 11), "name the accountable local owner")

    _upgrade_unit(_unit(bp, 12), [RULES[5], RULES[9]])
    _tag_task(_unit(bp, 12), "name owner, evidence, sign-off, and documentation-vs-speed trade-off")

    _upgrade_unit(_unit(bp, 13), [RULES[6], RULES[7]])
    _tag_task(_unit(bp, 13), "include one quantitative metric and one FMEA/FTA/STPA risk slice")

    _upgrade_unit(_unit(bp, 14), [RULES[4], RULES[9]])
    _tag_task(_unit(bp, 14), "include monitoring/maintenance and documentation burden")

    _upgrade_unit(_unit(bp, 15), [RULES[3], RULES[4], RULES[5], RULES[8]])
    _tag_task(_unit(bp, 15), "separate data bias/drift, AI accountability, verification, and validation")

    _upgrade_unit(_unit(bp, 16), [RULES[10], RULES[6]])
    _tag_task(_unit(bp, 16), "build the full evidence chain and include one number")
    _upgrade_unit(_unit(bp, 18), [RULES[1], RULES[10]])
    _tag_task(_unit(bp, 18), "include counter-evidence before verdict")
    _upgrade_unit(_unit(bp, 20), [RULES[0], RULES[1], RULES[2], RULES[10], RULES[11]])
    _tag_task(_unit(bp, 20), "submit only after all mandatory assurance-profile gates pass")

    checklist = "ASSURANCE PROFILE - breaking variable; falsifier; confidence/monitor; data bias/drift when applicable; continuous monitoring; human sign-off; quantitative metric; FMEA/FTA/STPA slice; verification vs validation; documentation-vs-speed trade-off; full evidence chain; local owner."
    notes = list(getattr(bp, "release_notes", []) or [])
    for item in (NOTE, checklist):
        if item not in notes:
            notes = notes[:18] + [item]
    bp.release_notes = notes[:20]
    return bp


def apply_v729_editor_gates_patch(app):
    global _PATCHED, _ORIGINAL_DRAFT
    if _PATCHED:
        return
    _PATCHED = True
    _ORIGINAL_DRAFT = engine._source_preserving_draft

    def draft(profile, bundle):
        bp = _ORIGINAL_DRAFT(profile, bundle)
        return _apply_gates(bp) if _assurance_profile(profile, bp) else bp

    engine._source_preserving_draft = draft
    base.engine._source_preserving_draft = draft

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "assurance_profile_version": "v7.2.9",
            "assurance_profile_count": 12,
            "assurance_profile_scope": "dependability/reliability/safety/security/assurance domains only",
            "assurance_profile_gates": [f"{k}: {v}" for k, v in RULES],
        })
        return data
    base._health_v440 = health
    base.engine.health = health
