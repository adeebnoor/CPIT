"""Draw the unit's own structure as a diagram.

The direction board asks for "رسم واحد بدل الفقرات" - one drawing instead of
paragraphs. That is only honest when the drawing comes from the unit's own
content. A diagram invented to fill space is the "meaningless decorative
image" the handoff forbids, and it is worse than text because a student trusts
a picture faster than a sentence.

So a diagram is emitted only when the unit already contains a structure to
draw: a labelled sequence, or two-to-five source statements that survive
compression into honest node labels. Otherwise this module returns nothing and
the caller falls back to text, which is the correct answer for a unit that has
no shape to show.

Nodes are HTML boxes, not SVG text. SVG would need font metrics to wrap, and
the whole point of rendering in a browser is that the browser already knows
them - so shrink-to-fit reflows a diagram exactly as it reflows a paragraph.
"""

from __future__ import annotations

import html

from .compress import label
from .icons import icon_for

# Which shape serves which teaching job. `visual_suggestion` is already carried
# per unit in the blueprint; this only decides how to draw it.
_SHAPE = {
    "process": "pipeline",
    "architecture": "pipeline",
    "algorithm": "pipeline",
    "protocol": "pipeline",
    "concept-map": "map",
    "comparison": "versus",
    "table": "map",
    "verdict": "ladder",
    "argument": "ladder",
    "mutation": "pipeline",
    "portfolio": "ladder",
}

_ARROW = (
    "<svg viewBox='0 0 20 24' fill='none' stroke='currentColor' stroke-width='2.4' "
    "stroke-linecap='round' stroke-linejoin='round'><path d='M2 12h12'/>"
    "<path d='M10 7l5 5-5 5'/></svg>"
)


def _esc(text: str) -> str:
    return html.escape(str(text or ""))


def _node(text: str, icon: str | None = None, *, sub: str = "", tone: str = "") -> str:
    glyph = f"<span class='nic'>{icon}</span>" if icon else ""
    # The label alone can lose the constraint that made the step matter, so a
    # node keeps one compressed line under it when the source had one.
    tail = f"<span class='nsub'>{_esc(sub)}</span>" if sub else ""
    return (f"<div class='node {tone}'>{glyph}"
            f"<span class='ntx'><span class='nnm'>{_esc(text)}</span>{tail}</span></div>")


def _pipeline(items: list[tuple[str, str]]) -> str:
    """Left-to-right flow. Wraps to a second row when it has to."""
    parts = []
    for i, (name, body) in enumerate(items):
        if i:
            parts.append(f"<div class='harrow'>{_ARROW}</div>")
        parts.append(_node(name, icon_for(name), sub=body))
    return f"<div class='dg pipeline'>{''.join(parts)}</div>"


def _map(items: list[tuple[str, str]], centre: str) -> str:
    """A hub and what hangs off it."""
    spokes = "".join(_node(name, icon_for(name), sub=b) for name, b in items)
    return (
        f"<div class='dg map'>"
        f"<div class='hub'>{_esc(centre)}</div>"
        f"<div class='spokes'>{spokes}</div></div>"
    )


def _versus(items: list[tuple[str, str]]) -> str:
    left, right = items[0], items[1]
    rest = "".join(
        f"<div class='vnote'>{_esc(name)}</div>" for name, _b in items[2:3]
    )
    return (
        f"<div class='dg versus'>"
        f"<div class='vcol'>{_node(left[0], icon_for(left[0]))}"
        f"<p>{_esc(left[1])}</p></div>"
        f"<div class='vs'>VS</div>"
        f"<div class='vcol'>{_node(right[0], icon_for(right[0]))}"
        f"<p>{_esc(right[1])}</p></div>{rest}</div>"
    )


def _ladder(items: list[tuple[str, str]]) -> str:
    rows = "".join(
        f"<div class='rung'><span class='rk'>{i + 1}</span>"
        f"<span class='rn'>{_esc(name)}</span>"
        f"<span class='rb'>{_esc(body)}</span></div>"
        for i, (name, body) in enumerate(items)
    )
    return f"<div class='dg ladder'>{rows}</div>"


def _nodes_from(steps: list[tuple[str, str]], core: list[str]) -> list[tuple[str, str]]:
    """Prefer the unit's labelled sequence; fall back to its source statements."""
    if steps:
        return [(name, label(body, 9)) for name, body in steps][:6]
    made: list[tuple[str, str]] = []
    for item in core:
        name = label(item, 5)
        if name and len(name.split()) >= 2:
            made.append((name, ""))
    return made[:5] if len(made) >= 2 else []


def build_diagram(unit: dict, steps: list[tuple[str, str]],
                  core: list[str]) -> tuple[str, str]:
    """Return (html, shape). ("", "") means this unit has no shape to draw."""
    nodes = _nodes_from(steps, core)
    if len(nodes) < 2:
        return "", ""

    suggestion = str(unit.get("visual_suggestion") or "").strip().lower()
    shape = _SHAPE.get(suggestion, "")
    if not shape:
        # No suggestion the drawer understands. A labelled sequence is still a
        # sequence, so it is drawn; an unlabelled set of statements is not.
        shape = "pipeline" if steps else "map"

    if shape == "versus" and len(nodes) < 2:
        shape = "pipeline"
    if shape == "ladder" and not steps:
        shape = "map"

    if shape == "pipeline":
        return _pipeline(nodes), shape
    if shape == "versus":
        return _versus(nodes), shape
    if shape == "ladder":
        return _ladder(nodes), shape
    centre = label(unit.get("title") or "", 4) or "P1"
    return _map(nodes, centre), shape
