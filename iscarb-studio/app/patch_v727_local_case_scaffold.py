from __future__ import annotations

"""v7.2.7 — mandatory micro-case scaffolding before Rule 11 local application.

The approved Golden v6.6 grammar keeps Rule 11 as the Saudi/local transfer point.
This patch makes the transfer cognitively staged: learners first solve one tiny,
context-light case using a mechanism already taught, then apply the same reasoning
chain to the richer local case. The micro-case is explicitly ISCARB pedagogy, not P1.
"""

import re
from . import main as engine
from . import start_v440 as base

_PATCHED = False
_ORIGINAL_DRAFT = None


def _topic_blob(bp) -> str:
    vals = [getattr(bp, "lecture_title", ""), getattr(bp, "engineering_thesis", "")]
    vals += list(getattr(bp, "source_topic_families", []) or [])
    return " ".join(str(x or "") for x in vals).lower()


def _micro_case(bp) -> str:
    t = _topic_blob(bp)
    if any(k in t for k in ("dependab", "reliab", "fault", "safety", "redundan", "formal method")):
        return ("Two redundant service instances run on separate servers but share one power supply. "
                "The supply fails and both stop. Which assumption made the redundancy look safer than it was?")
    if any(k in t for k in ("security", "cyber", "authentication", "access control", "threat")):
        return ("A service requires MFA for normal login, but its account-recovery path accepts only an emailed link. "
                "Which security property is weakened, and what evidence would prove the recovery path is acceptable?")
    if any(k in t for k in ("database", "transaction", "locking", "serializ", "sql", "concurrency")):
        return ("Two transactions update the same record; one reads a value before the other commits. "
                "Which concurrency rule determines whether the observed result is acceptable?")
    if any(k in t for k in ("network", "routing", "protocol", "distributed")):
        return ("A service has two network paths, but both cross the same upstream router. The router fails and both paths disappear. "
                "Which hidden dependency invalidates the resilience claim?")
    return ("A small service changes one dependency version and one previously valid operation now fails. "
            "Which already-taught mechanism explains the change, and what evidence would confirm your diagnosis?")


def _strip_timebox(text: str) -> str:
    return re.sub(r"^\s*TIMEBOX:\s*[^-]{1,48}\s*-\s*", "", str(text or ""), flags=re.I).strip()


def _scaffold(bp):
    units = list(getattr(bp, "units", []) or [])
    if len(units) != 20:
        return bp
    u = units[10]
    case = _micro_case(bp)
    existing = [str(x).strip() for x in list(getattr(u, "pedagogy_content", []) or []) if str(x).strip()]
    existing = [x for x in existing if not re.match(r"^(MICRO-CASE|TRANSFER RULE)\s*[—:-]", x, re.I)]
    u.pedagogy_content = [
        f"MICRO-CASE — ISCARB scaffold (not P1): {case}",
        "TRANSFER RULE — Solve the small case first as mechanism → evidence → decision boundary; then reuse the same chain on the Saudi/local case.",
        *existing,
    ][:16]
    # Keep the visible timing contract, but make the two cognitive stages explicit.
    u.student_action = (
        "TIMEBOX: 1 min micro-case + 5 min transfer - Solve the micro-case first; then apply the same "
        "mechanism → evidence → decision-boundary chain to the Saudi/local case."
    )
    notes = list(getattr(bp, "release_notes", []) or [])
    note = "Rule 11 scaffolding locked: a visible micro-case precedes every Saudi/local transfer task."
    if note not in notes:
        notes = notes[:19] + [note]
    bp.release_notes = notes
    return bp


def apply_v727_local_case_scaffold_patch(app):
    global _PATCHED, _ORIGINAL_DRAFT
    if _PATCHED:
        return
    _PATCHED = True
    _ORIGINAL_DRAFT = engine._source_preserving_draft

    def scaffolded_draft(profile, bundle):
        return _scaffold(_ORIGINAL_DRAFT(profile, bundle))

    engine._source_preserving_draft = scaffolded_draft
    base.engine._source_preserving_draft = scaffolded_draft

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "rule11_scaffolding": "Mandatory visible micro-case before Saudi/local application; solve small case then transfer mechanism → evidence → boundary.",
            "rule11_microcase_provenance": "ISCARB pedagogy — explicitly not P1 source content.",
            "scaffolding_version": "v7.2.7",
        })
        return data
    base._health_v440 = health
    base.engine.health = health
