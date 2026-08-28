from __future__ import annotations

from dataclasses import dataclass

from .models import LectureUnit


@dataclass(frozen=True)
class VisualProvenance:
    label: str
    citation: str
    note: str


# Units whose visual form directly re-expresses a source mechanism/figure structure.
# These are redraws, not screenshots or copied artwork.
DIRECT_SOURCE_ADAPTATIONS = {6, 7, 8, 9, 12, 13}

# Units that use source facts but the visual grammar itself is an ISCARB construct.
SOURCE_ANCHORED = {1, 2, 5, 11, 14, 18}


def classify_visual(unit: LectureUnit) -> VisualProvenance:
    anchor = (unit.source_anchor or "").strip()
    has_p1 = "P1" in anchor.upper()

    if unit.number in DIRECT_SOURCE_ADAPTATIONS and has_p1:
        return VisualProvenance(
            label="ADAPTED FROM P1",
            citation=anchor,
            note="Redrawn in ISCARB visual language from source-supported structure; no source artwork copied.",
        )

    if unit.number in SOURCE_ANCHORED and has_p1:
        return VisualProvenance(
            label="SOURCE-ANCHORED VISUAL",
            citation=anchor,
            note="ISCARB visualization built only from source-supported technical content.",
        )

    if has_p1:
        return VisualProvenance(
            label="SOURCE-ANCHORED VISUAL",
            citation=anchor,
            note="Visual grammar is ISCARB; technical claims remain anchored to the cited primary source.",
        )

    return VisualProvenance(
        label="ISCARB VISUALIZATION",
        citation="ISCARB pedagogy — no external technical source claim",
        note="Original instructional visualization; not presented as a source figure.",
    )
