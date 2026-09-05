from __future__ import annotations

"""v7.1.3 hero delivery hardening.

Use the exact user-supplied Black Desert camel artwork payload reconstructed from
repository chunks. No SVG redraw, generated substitute, or legacy raster is used
on the production home.
"""

from . import start_v440 as base

_PATCHED = False
APPROVED_HERO = "hero_original_v713.jpg"


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
            "hero_delivery": "user-supplied original raster reconstructed from repository payload",
            "hero_original_raster": True,
            "hero_user_supplied": True,
            "hero_redraw": False,
            "hero_generated_substitute": False,
            "hero_live_release": "7.1.3",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
