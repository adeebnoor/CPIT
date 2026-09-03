"""ISCARB visual identity tokens for rendered slide images.

One place decides colour, type and geometry so a PNG posted to a channel is
recognisably the same product as the projected presenter deck. Nothing
downstream hard-codes a colour: re-skinning every rendered image is an edit
here.

Two themes ship because they answer different questions. `dark` matches the
approved v4.8 presenter surface, so an exported image sits beside a projected
slide without looking foreign. `light` is the shareable treatment - navy and
gold on off-white - which survives being pasted into a document, printed, or
read on a phone in daylight, where a near-black slide turns into a mirror.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Palette:
    ground: str          # page behind the card
    card: str            # panels and step cards
    card_edge: str
    display: str         # unit title
    accent: str          # step labels, rules, eyebrow
    accent_soft: str     # arrows, dividers, quiet marks
    ink: str             # body text
    ink_soft: str        # question bar, captions
    bar: str             # question / task bars
    source_panel: str    # the source column's own ground


# Near-white headings carry the punch; one hot accent marks the single thing
# that matters on the slide. #f51767 is where the ISCARB magenta and the
# reference lecture style land on the same colour, so nothing is compromised to
# get both.
DARK = Palette(
    ground="#0b0a0e", card="#17161d", card_edge="#292731",
    display="#f4efe8", accent="#f51767", accent_soft="#7d2745",
    ink="#e9e5e9", ink_soft="#9c95a0", bar="#161520", source_panel="#151420",
)

# Navy carries structure, gold marks the source. Both hold their contrast
# against the off-white ground at small sizes, which a mid-grey would not.
LIGHT = Palette(
    ground="#f4f2ed", card="#ffffff", card_edge="#d8d3c8",
    display="#12243f", accent="#1a4f9c", accent_soft="#9fb6d6",
    ink="#1c2733", ink_soft="#5d6875", bar="#eceadf", source_panel="#f0ece0",
)

THEMES = {"dark": DARK, "light": LIGHT}


@dataclass(frozen=True)
class Typography:
    # Installed locally; no network fetch at render time. The Arabic face is
    # listed first for Arabic runs and the Latin face resolves the rest, so a
    # mixed Arabic/English line keeps one visual rhythm.
    latin: str = "'Noto Sans', 'DejaVu Sans', sans-serif"
    arabic: str = "'Noto Naskh Arabic', 'Noto Sans Arabic', 'Noto Sans', sans-serif"
    title_px: int = 60
    eyebrow_px: int = 25
    question_px: int = 26
    label_px: int = 21
    step_label_px: int = 30
    body_px: int = 27
    task_px: int = 24
    footer_px: int = 17
    # Dynamic resizing floor. Below this a slide is not projectable and the
    # renderer says so rather than shipping an unreadable image.
    min_body_px: int = 16


@dataclass(frozen=True)
class Geometry:
    width: int = 1920            # fixed 16:9 stage, so nothing reflows per slide
    height: int = 1080
    margin: int = 58
    card_radius: int = 18
    gutter: int = 40


PALETTE = DARK
TYPE = Typography()
GEOMETRY = Geometry()


def theme(name: str) -> Palette:
    return THEMES.get(str(name or "").lower(), DARK)


__all__ = ["Palette", "Typography", "Geometry", "DARK", "LIGHT", "THEMES",
           "PALETTE", "TYPE", "GEOMETRY", "theme", "replace"]
