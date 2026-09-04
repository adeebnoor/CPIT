from __future__ import annotations

"""ISCARB v7.0.5 source-detail floor for public-web teaching units.

Gate v15 requires each technical teaching unit to retain at least 12 words of P1
technical content. A final readability fit can legitimately collapse a dense unit
to one short source heading (for example, an 8-word lifecycle step), leaving a
beautiful slide that is too thin to teach. This repair does not lower the gate and
does not add subject matter. When a web unit falls below the source-detail floor,
it replaces that thin heading with the shortest complete statement already present
in one of that unit's own P1 anchors, then runs the normal readability fit again.
"""

import re

from . import main as engine
from . import source_profile_fallback as profile_mod
from . import start_v440 as base

_PATCHED = False
MIN_TECHNICAL_WORDS = 12
MAX_REPAIR_WORDS = 32


def _is_web_bundle(bundle) -> bool:
    try:
        text = profile_mod.extract_source_text(bundle.primary.path, limit=5000)
        return "SOURCE TYPE: public web page" in text
    except Exception:
        return False


def _section_numbers(anchor: str) -> set[int]:
    return {int(x) for x in re.findall(r"SECTION\s+(\d+)", str(anchor or ""), flags=re.I)}


def _row_section(row) -> int | None:
    match = re.search(r"SECTION\s+(\d+)", str(getattr(row, "source_anchor", "") or ""), flags=re.I)
    return int(match.group(1)) if match else None


def _complete_statements(text: str):
    raw = " ".join(str(text or "").split()).strip()
    for part in re.split(r"\s*[·•▪■◆]\s*|(?<=[.!?])\s+", raw):
        clean = " ".join(part.split()).strip(" -•·:;,")
        words = clean.split()
        if MIN_TECHNICAL_WORDS <= len(words) <= MAX_REPAIR_WORDS:
            yield clean


def _repair_thin_technical_units(blueprint, profile):
    rows = list(getattr(profile, "coverage_items", []) or [])
    for unit in getattr(blueprint, "units", []) or []:
        number = int(getattr(unit, "number", 0) or 0)
        if not (6 <= number <= 15) or number == 10:
            continue
        core = [str(x).strip() for x in (getattr(unit, "core_content", []) or []) if str(x).strip()]
        if sum(len(x.split()) for x in core) >= MIN_TECHNICAL_WORDS:
            continue
        anchors = _section_numbers(getattr(unit, "source_anchor", ""))
        candidates: list[str] = []
        for row in rows:
            section = _row_section(row)
            if anchors and section not in anchors:
                continue
            candidates.extend(_complete_statements(getattr(row, "why_important", "")))
        # Prefer the shortest complete statement that clears the gate: this adds
        # the minimum source material needed and protects presenter readability.
        candidates = list(dict.fromkeys(candidates))
        candidates.sort(key=lambda x: (len(x.split()), len(x)))
        if candidates:
            unit.core_content = [candidates[0]]
    return blueprint


def apply_v704_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    previous_draft = engine._source_preserving_draft

    def source_preserving_draft(profile, bundle):
        blueprint = previous_draft(profile, bundle)
        if _is_web_bundle(bundle):
            blueprint = _repair_thin_technical_units(blueprint, profile)
            blueprint = engine.fit_presenter_text(blueprint)
        return blueprint

    engine._source_preserving_draft = source_preserving_draft
    base.engine._source_preserving_draft = source_preserving_draft

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "web_source_detail_floor": "v7.0.5",
            "technical_source_word_floor": MIN_TECHNICAL_WORDS,
            "source_detail_gate_weakened": False,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
