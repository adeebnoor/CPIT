"""Inline line-art icons for step cards.

Drawn as SVG paths rather than fetched or generated. Three reasons: the render
must work with no network, an icon set has to stay identical across every
slide in a deck, and an image model asked for "an icon representing derive"
returns something different every call - which reads as inconsistency, not
variety.

Every glyph is stroke-only on a 24x24 grid and inherits `currentColor`, so a
theme change recolours the whole set with no edit here.
"""

from __future__ import annotations

_WRAP = (
    "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.7' "
    "stroke-linecap='round' stroke-linejoin='round'>{}</svg>"
)

_PATHS = {
    # A prediction is a guess with light behind it.
    "predict": "<path d='M9 18h6M10 21h4'/><path d='M12 3a6 6 0 0 0-3.6 10.8c.5.4.8 1 .9 1.7h5.4c.1-.7.4-1.3.9-1.7A6 6 0 0 0 12 3z'/>",
    # A constraint is a boundary you cannot cross.
    "constraint": "<path d='M4 9h16M4 15h16'/><path d='M7 4v16M12 4v16M17 4v16'/>",
    # Deriving moves from one node to consequences.
    "derive": "<circle cx='5' cy='12' r='2.2'/><circle cx='19' cy='6' r='2.2'/><circle cx='19' cy='18' r='2.2'/><path d='M7.2 11 17 6.8M7.2 13 17 17.2'/>",
    # Naming attaches a label to the thing.
    "name": "<path d='M3 12V5a2 2 0 0 1 2-2h7l9 9-9 9-9-9z'/><circle cx='7.5' cy='7.5' r='1.4'/>",
    "measure": "<path d='M3 8h18v8H3z'/><path d='M7 8v4M11 8v3M15 8v4M19 8v3'/>",
    "falsifier": "<circle cx='12' cy='12' r='9'/><path d='M8.5 8.5l7 7M15.5 8.5l-7 7'/>",
    "alternative": "<path d='M4 7h6l4 10h6'/><path d='M4 17h6l4-10h6'/><path d='M17 4l3 3-3 3M17 14l3 3-3 3'/>",
    "tradeoff": "<path d='M12 4v16M4 8h16'/><path d='M4 8l-2 5a3 3 0 0 0 6 0zM20 8l-2 5a3 3 0 0 0 6 0z'/>",
    "decide": "<path d='M12 3l9 9-9 9-9-9z'/><path d='M9 12l2 2 4-4'/>",
    "boundary": "<path d='M4 4h16v16H4z' stroke-dasharray='3 3'/><path d='M9 12h6'/>",
    "stress": "<path d='M3 17l5-6 4 3 4-7 5 4'/><path d='M3 21h18'/>",
    "evidence": "<path d='M6 3h9l4 4v14H6z'/><path d='M15 3v4h4'/><path d='M9 13h6M9 17h4'/>",
    "source": "<path d='M4 5a2 2 0 0 1 2-2h6v18H6a2 2 0 0 1-2-2z'/><path d='M20 5a2 2 0 0 0-2-2h-6v18h6a2 2 0 0 0 2-2z'/>",
    "step": "<circle cx='12' cy='12' r='9'/><path d='M12 7v10M7 12h10'/>",
}

# A label is matched by the word it starts with, so "CONSTRAINT" and
# "HYPOTHETICAL SAUDI/LOCAL CONSTRAINT" resolve to the same glyph.
_ALIASES = {
    "predict": "predict", "prediction": "predict", "توقّع": "predict", "توقع": "predict",
    "constraint": "constraint", "constrain": "constraint", "قيد": "constraint",
    "derive": "derive", "derivation": "derive", "اشتقاق": "derive",
    "name": "name", "naming": "name", "سمّ": "name", "تسمية": "name",
    "measure": "measure", "metric": "measure",
    "falsifier": "falsifier", "falsification": "falsifier",
    "alternative": "alternative", "alternatives": "alternative",
    "trade-off": "tradeoff", "tradeoff": "tradeoff",
    "decide": "decide", "decision": "decide",
    "boundary": "boundary", "bounded": "boundary",
    "stress": "stress", "scalability": "stress", "fail-first": "stress",
    "evidence": "evidence", "artifact": "evidence", "primary": "source",
    "source": "source",
}


def icon_for(label: str) -> str:
    """Return SVG markup for a step label, falling back to a neutral step mark."""
    words = [w.strip(" :.,").lower() for w in str(label or "").split() if w.strip(" :.,")]
    for word in words:
        key = _ALIASES.get(word)
        if key:
            return _WRAP.format(_PATHS[key])
    return _WRAP.format(_PATHS["step"])


def source_icon() -> str:
    return _WRAP.format(_PATHS["source"])
