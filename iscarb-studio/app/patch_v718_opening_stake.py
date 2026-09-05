from __future__ import annotations

"""ISCARB v7.1.8 final source-stake guard.

Some deterministic extractors preserve an important P1 sentence in a teaching
unit even when the intermediate profile excerpt no longer exposes that sentence
to the older crisis selector.  The final opening therefore gets one last,
strictly source-bounded pass over P1-anchored unit evidence.  Nothing is
invented: the selected stake is copied from P1-backed core content verbatim.
"""

import re

from . import main as engine
from . import start_v440 as base
from . import patch_v690 as v690

_PATCHED = False


def _sentences(text: str) -> list[str]:
    blob = re.sub(r"\s+", " ", str(text or "")).strip()
    return [
        p.strip(" ·•-–—")
        for p in re.split(r"\s*[·•▪■◆]\s*|(?<=[.!?])\s+", blob)
        if p.strip(" ·•-–—")
    ]


def _source_unit_stake(bp) -> str:
    candidates: list[str] = []
    for unit in getattr(bp, "units", []) or []:
        if getattr(unit, "number", 0) in (1, 2):
            continue
        anchor = str(getattr(unit, "source_anchor", "") or "")
        if "[P1]" not in anchor.upper():
            continue
        for item in getattr(unit, "core_content", []) or []:
            for sentence in _sentences(item):
                words = sentence.split()
                if not (7 <= len(words) <= 55):
                    continue
                if "REVIEW REQUIRED" in sentence.upper() or v690._GENERIC_CRISIS.search(sentence):
                    continue
                if v690._RISK.search(sentence):
                    candidates.append(sentence)
    if not candidates:
        return ""
    return min(candidates, key=lambda x: (abs(len(x.split()) - 22), len(x)))


def _apply_source_stake(bp):
    if not getattr(bp, "units", None):
        return bp
    if v690.crisis_is_source_specific(bp):
        return bp
    stake = _source_unit_stake(bp)
    if not stake:
        return bp
    bp.central_engineering_crisis = stake
    u1 = bp.units[0]
    u1.title = "The source-defined engineering stake"
    u1.engineering_question = "Which design choice controls this P1-supported risk, and which P1 evidence would reverse that choice?"
    u1.core_content = [stake]
    u1.pedagogy_content = [
        "DECISION — identify the design response the P1 stake actually requires.",
        "UNKNOWN — name the missing P1 evidence that could reverse the decision.",
    ]
    u1.student_action = "State the decision, cite the P1 stake, and name the evidence that would make you change your mind."
    return bp


def apply_v718_opening_stake_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    previous = engine._source_preserving_draft

    def final_source_stake_draft(profile, bundle):
        return _apply_source_stake(previous(profile, bundle))

    engine._source_preserving_draft = final_source_stake_draft
    base.engine._source_preserving_draft = final_source_stake_draft

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "release_ui": "7.1.6",
            "opening_stake_release": "7.1.8",
            "opening_crisis_final_guard": "verbatim P1-backed unit evidence; no generic fallback",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
