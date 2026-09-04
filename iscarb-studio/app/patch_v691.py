from __future__ import annotations

"""ISCARB v6.9.1: prefer explicit P1 incidents/failures for the opening crisis."""
import re

from . import patch_v690 as v690
from . import start_v440 as base

PUBLIC_VERSION = "6.9.1"
PIPELINE_ID = "faculty-studio-v6.9.1-explicit-source-crisis"
_PATCHED = False

_EXPLICIT_CASE = re.compile(
    r"\b(?:critical\s+failure|why\s+matters|case\s+study|incident|breach|root\s+causes?|"
    r"ransomware|data\s+expos(?:ed|ure)|unauthori[sz]ed\s+access|outage|explosion|wrong\s+treatments?)\b",
    re.I,
)
_CASE_LABEL = re.compile(r"\b(?:critical|failure|incident|breach|attack|case|why\s+matters|problem|scenario)\b", re.I)
_ACTIONABLE_HARM = re.compile(
    r"\b(?:expos(?:ed|ure)|unauthori[sz]\w*|attack(?:ed|ers?)?|breach(?:ed)?|ransomware|"
    r"outage|explosion|harm|damage|loss|stolen|steal(?:ing)?|manipulat(?:e|es|ed|ing)|"
    r"cannot|can't|prevent(?:ing)?|compromis(?:e|ed|ing)|vulnerab\w*)\b",
    re.I,
)
_NON_CRISIS = re.compile(
    r"^(?:security engineering focuses|security is (?:essential|an investment|the foundation)|"
    r"security testing is hard|asset something of value|threat circumstances|vulnerability a weakness)",
    re.I,
)


def source_specific_crisis_v691(profile) -> str:
    """Return an explicit incident/failure sentence from P1, or nothing.

    A topic sentence that merely says security is important is not a crisis. The
    opening earns automatic release only when P1 itself exposes a concrete attack,
    failure, breach, harm, or comparable decision-forcing case.
    """
    rows = list(getattr(profile, "coverage_items", []) or [])
    candidates: list[tuple[int, int, int, str]] = []
    for order, row in enumerate(rows):
        label = re.sub(r"\s+", " ", str(getattr(row, "label", "") or "")).strip()
        excerpt = str(getattr(row, "why_important", "") or "")
        context = f"{label} {excerpt}"
        context_score = 0
        if _EXPLICIT_CASE.search(context):
            context_score += 80
        if _CASE_LABEL.search(label):
            context_score += 35
        if getattr(row, "importance", "") == "major":
            context_score += 10
        for sentence in v690._sentences(excerpt):
            words = len(sentence.split())
            if not (7 <= words <= 55):
                continue
            if _NON_CRISIS.search(sentence):
                continue
            severity = 0
            if _EXPLICIT_CASE.search(sentence):
                severity += 70
            if _ACTIONABLE_HARM.search(sentence):
                severity += 45
            if v690._RISK.search(sentence):
                severity += 15
            if severity < 45:
                continue
            score = context_score + severity
            candidates.append((score, -abs(words - 18), -order, sentence.strip()))
    if not candidates:
        return ""
    best = max(candidates)
    return best[3] if best[0] >= 100 else ""


def apply_v691_patch(app):
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True
    v690.source_specific_crisis = source_specific_crisis_v691
    base.PUBLIC_VERSION = PUBLIC_VERSION
    base.PIPELINE_ID = PIPELINE_ID
    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "version": PUBLIC_VERSION,
            "pipeline": PIPELINE_ID,
            "opening_crisis_selector": "explicit P1 incident/failure first; weak generic risk prose blocks release",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
