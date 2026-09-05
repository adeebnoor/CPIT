from __future__ import annotations

"""v7.2.6 — visible time-boxing for every ISCARB YOUR TASK footer.

Keeps the user-approved v6.6 Balanced30 visual grammar intact. The only change
is that every learner task carries a concise time budget so in-class cognition is
bounded rather than open-ended.
"""

import re
from . import main as engine
from . import start_v440 as base
from . import v670_contract as contract
from . import presenter_v67_prod as presenter

_PATCHED = False
_ORIGINAL_DRAFT = None
_ORIGINAL_PLAN_EXPANSIONS = None
_TIMEBOX_RE = re.compile(r"^\s*(?:TIMEBOX|⏱)\s*[:：]?\s*[^—-]{1,32}\s*[—-]\s*", re.I)


def _clean_task(text: str) -> str:
    return _TIMEBOX_RE.sub("", str(text or "")).strip()


def _box_for_unit(n: int | None, title: str = "") -> str:
    t = str(title or "").lower()
    if n in {1, 2, 3, 4, 5, 7, 8, 9, 10, 13, 14, 15, 17}:
        return "60-90 sec"
    if n in {6, 12}:
        return "2 min"
    if n == 11 or "local" in t or "saudi" in t:
        return "5-7 min"
    if n == 16 or "artifact" in t:
        return "5-7 min"
    if n == 18 or "defend" in t:
        return "4 min"
    if n == 19 or "rubric" in t:
        return "3 min"
    if n == 20 or "take-home" in t or "verdict" in t:
        return "post-class"
    return "90 sec"


def _box_for_expansion(title: str = "", after_unit: int | None = None) -> str:
    t = str(title or "").lower()
    if after_unit in {10, 11, 12, 14, 15} or any(k in t for k in ("regulation", "redundancy", "process", "formal")):
        return "2 min"
    return "90 sec"


def _with_timebox(task: str, label: str) -> str:
    task = _clean_task(task)
    return f"TIMEBOX: {label} - {task}" if task else f"TIMEBOX: {label}"


def _timebox_blueprint(bp):
    for u in list(getattr(bp, "units", []) or []):
        n = getattr(u, "number", None)
        title = getattr(u, "title", "")
        u.student_action = _with_timebox(getattr(u, "student_action", ""), _box_for_unit(n, title))
    notes = list(getattr(bp, "release_notes", []) or [])
    note = "Visible time-boxing locked: every YOUR TASK footer carries a bounded in-class or post-class duration."
    if note not in notes:
        notes = notes[:19] + [note]
    bp.release_notes = notes
    return bp


def _timebox_specs(specs):
    rows = []
    for s in list(specs or []):
        d = dict(s)
        d["student_task"] = _with_timebox(d.get("student_task", ""), _box_for_expansion(d.get("title", ""), d.get("after_unit")))
        rows.append(d)
    return rows


def apply_v726_timebox_tasks_patch(app):
    global _PATCHED, _ORIGINAL_DRAFT, _ORIGINAL_PLAN_EXPANSIONS
    if _PATCHED:
        return
    _PATCHED = True
    _ORIGINAL_DRAFT = engine._source_preserving_draft
    _ORIGINAL_PLAN_EXPANSIONS = contract.plan_expansions

    def timeboxed_draft(profile, bundle):
        return _timebox_blueprint(_ORIGINAL_DRAFT(profile, bundle))

    def timeboxed_expansions(bp, *args, **kwargs):
        return _timebox_specs(_ORIGINAL_PLAN_EXPANSIONS(bp, *args, **kwargs))

    engine._source_preserving_draft = timeboxed_draft
    base.engine._source_preserving_draft = timeboxed_draft
    contract.plan_expansions = timeboxed_expansions
    for mod in (presenter, base):
        if hasattr(mod, "plan_expansions"):
            setattr(mod, "plan_expansions", timeboxed_expansions)

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "time_boxing": "Every YOUR TASK footer includes a visible duration: 60-90 sec, 2 min, 3-4 min, 5-7 min, or post-class.",
            "time_boxing_version": "v7.2.6",
        })
        return data
    base._health_v440 = health
    base.engine.health = health
