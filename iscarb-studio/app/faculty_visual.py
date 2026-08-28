from __future__ import annotations

import re
from pathlib import Path

from pptx.dml.color import RGBColor

from .models import Blueprint
from . import visual_engine as ve

# ISCARB Original Identity — Saudi academic engineering language.
INK = RGBColor(29, 41, 33)
MUTED = RGBColor(101, 113, 105)
PAPER = RGBColor(250, 249, 246)
WHITE = RGBColor(255, 255, 255)
LINE = RGBColor(221, 228, 223)
GREEN = RGBColor(12, 83, 61)
GREEN2 = RGBColor(29, 139, 86)
TEAL = RGBColor(10, 53, 62)
PURPLE = RGBColor(86, 60, 125)
PURPLE2 = RGBColor(130, 100, 167)
GOLD = RGBColor(196, 162, 79)
RED = RGBColor(184, 77, 82)
SOFT_GREEN = RGBColor(231, 244, 236)
SOFT_TEAL = RGBColor(231, 240, 241)
SOFT_PURPLE = RGBColor(238, 232, 245)
SOFT_GOLD = RGBColor(247, 241, 224)
SOFT_RED = RGBColor(250, 235, 236)


def _faculty_short(text: str, n: int = 145) -> str:
    """Presenter-first text budget.

    The Detailed Deck and Instructor Guide preserve full wording. Presenter assets
    intentionally cap most visual text so a slide behaves like a teaching surface,
    not a projected document. Existing renderer-specific limits are respected when
    shorter; longer limits are capped near one short sentence.
    """
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    cap = min(int(n), 96)
    if len(text) <= cap:
        return text
    cut = text[: cap - 1].rstrip()
    # Prefer a clean word boundary when possible.
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:-") + "…"


def _apply_theme() -> None:
    ve.INK = INK
    ve.MUTED = MUTED
    ve.PAPER = PAPER
    ve.WHITE = WHITE
    ve.LINE = LINE
    ve.BLUE = PURPLE
    ve.GREEN = GREEN2
    ve.AMBER = GOLD
    ve.VIOLET = TEAL
    ve.RED = RED
    ve.SOFT_BLUE = SOFT_PURPLE
    ve.SOFT_GREEN = SOFT_GREEN
    ve.SOFT_AMBER = SOFT_GOLD
    ve.SOFT_VIOLET = SOFT_TEAL
    ve.SOFT_RED = SOFT_RED
    ve.PHASE_COLOR = {
        "IFHAM": PURPLE,
        "MARIS": GREEN2,
        "ATQAN": GOLD,
        "MAYYIZ": TEAL,
    }
    ve.PHASE_SOFT = {
        "IFHAM": SOFT_PURPLE,
        "MARIS": SOFT_GREEN,
        "ATQAN": SOFT_GOLD,
        "MAYYIZ": SOFT_TEAL,
    }
    # Visual-first presenter budget; full content stays intact in Blueprint/Detailed/Guide.
    ve._short = _faculty_short


def export_faculty_presenter_pptx(blueprint: Blueprint, path: Path) -> Path:
    _apply_theme()
    return ve.export_presenter_pptx(blueprint, Path(path))


def render_faculty_presenter_preview(blueprint: Blueprint, release_state: str = "BLOCKED") -> str:
    _apply_theme()
    html = ve.render_presenter_preview(blueprint, release_state)
    # Preview renderer owns its structure. These replacements only move the
    # presentation chrome into the ISCARB Original Identity palette.
    replacements = {
        "#0d141d": "#0a353e",
        "#111b26": "#ffffff",
        "#273444": "#dde4df",
        "#9fb0c0": "#657169",
        "#172330": "#f3f5f2",
        "#cdd7e0": "#1d2921",
        "#263647": "#d8e0da",
        "#6f8ff7": "#563c7d",
        "#1c2d45": "#eee8f5",
        "#90a3b5": "#7b877f",
        "#f7f9fb": "#faf9f6",
        "#3568e8": "#563c7d",
        "#16856b": "#1d8b56",
        "#b77b1d": "#c4a24f",
        "#7955dc": "#0a353e",
        "#b64040": "#b84d52",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    return html
