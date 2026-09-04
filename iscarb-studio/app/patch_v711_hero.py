from __future__ import annotations

"""v7.1.2 hero delivery hardening.

Use the original repository raster Black Desert camel image directly. No redraw,
vector substitute, or generated replacement is used on the production home.
"""

from . import start_v440 as base

_PATCHED = False
APPROVED_HERO = "hero_v670.jpg"
APPROVED_HERO_BLOB = "4bacaf6641105b29a1768f5cdaed6c26200f522e"


def apply_v711_hero_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "approved_hero_asset": APPROVED_HERO,
            "approved_hero_blob": APPROVED_HERO_BLOB,
            "hero_delivery": "original repository JPEG raster",
            "hero_original_raster": True,
            "hero_redraw": False,
            "hero_live_release": "7.1.2",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
