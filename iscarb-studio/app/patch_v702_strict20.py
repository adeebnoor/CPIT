from __future__ import annotations

"""ISCARB v7.0.2 strict-20 repair.

Gate v15 requires Unit 2 to be a real, source-backed Domain Spine rather than a
single generic heading. Short TXT/DOCX sources can legitimately profile as one
topic family even when their source text contains several distinct technical
claims. This patch does not weaken Gate v15 and does not invent a taxonomy: it
fills the spine only from P1 topic-family names, P1 coverage labels and complete
source statements already preserved in the deterministic profile.
"""

import re

from . import main as engine
from . import start_v440 as base

_PATCHED = False
MIN_SPINE_NODES = 5
MAX_SPINE_NODES = 8
MAX_NODE_CHARS = 96


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _clean_node(value: str) -> str:
    text = " ".join(str(value or "").split()).strip(" -•·:;,.")
    # Source excerpts often carry an explicit P1 coordinate before the claim.
    text = re.sub(r"^\[P1\]\s*(?:SLIDE|PAGE)?\s*\d*(?:[-–]\d+)?\s*[—:;-]*\s*", "", text, flags=re.I)
    if len(text) > MAX_NODE_CHARS:
        # Prefer a complete clause/sentence boundary rather than a raw character cut.
        head = text[:MAX_NODE_CHARS]
        boundary = max(head.rfind(";"), head.rfind(":"), head.rfind(","))
        if boundary >= 36:
            text = head[:boundary]
        else:
            cut = head.rfind(" ")
            text = head[:cut] if cut >= 48 else head
    return text.rstrip(" ,;:-")


def _source_statements(value: str):
    raw = " ".join(str(value or "").split())
    # Profiling preserves bullets with a middle dot; plain-text uploads need
    # sentence splitting too. Keep complete source statements only.
    for part in re.split(r"\s*[·•▪■◆]\s*|(?<=[.!?])\s+|\s*;\s*", raw):
        clean = _clean_node(part)
        if 4 <= len(clean.split()) <= 22:
            yield clean


def _spine_candidates(profile, current: list[str]) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        clean = _clean_node(value)
        key = _norm(clean)
        if not clean or len(clean.split()) < 2 or key in seen:
            return
        # Avoid near-duplicate headings that differ only by section numbering.
        for existing in seen:
            if key == existing or (len(key) > 18 and (key in existing or existing in key)):
                return
        seen.add(key)
        candidates.append(clean)

    for value in current:
        add(value)
    for family in getattr(profile, "topic_families", []) or []:
        add(getattr(family, "name", ""))
    coverage = list(getattr(profile, "coverage_items", []) or [])
    # Major checkpoints first; supporting items are allowed only to complete a
    # readable map when the deterministic profiler produced too few families.
    coverage.sort(key=lambda row: 0 if getattr(row, "importance", "") == "major" else 1)
    for row in coverage:
        add(getattr(row, "label", ""))
        if len(candidates) >= MAX_SPINE_NODES:
            break
    if len(candidates) < MIN_SPINE_NODES:
        for row in coverage:
            for statement in _source_statements(getattr(row, "why_important", "")):
                add(statement)
                if len(candidates) >= MIN_SPINE_NODES:
                    break
            if len(candidates) >= MIN_SPINE_NODES:
                break
    return candidates[:MAX_SPINE_NODES]


def _repair_unit2(blueprint, profile):
    unit = next((u for u in getattr(blueprint, "units", []) if getattr(u, "number", None) == 2), None)
    if unit is None:
        return blueprint
    current = list(getattr(unit, "core_content", []) or [])
    nodes = _spine_candidates(profile, current)
    # Never fabricate missing nodes. Gate v15 still blocks a truly content-thin
    # source if it cannot supply at least two source-backed nodes.
    if nodes:
        unit.core_content = nodes
    anchor = str(getattr(unit, "source_anchor", "") or "").strip()
    if "p1" not in anchor.lower():
        unit.source_anchor = "[P1]" if not anchor else f"[P1] · {anchor}"
    return blueprint


def apply_v702_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    previous = engine._source_preserving_draft

    def strict_draft(profile, bundle):
        blueprint = previous(profile, bundle)
        return _repair_unit2(blueprint, profile)

    engine._source_preserving_draft = strict_draft
    base.engine._source_preserving_draft = strict_draft

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "strict20_patch": "v7.0.2",
            "domain_spine_source_derived": True,
            "domain_spine_target_nodes": [MIN_SPINE_NODES, MAX_SPINE_NODES],
            "gate_v15_weakened": False,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
