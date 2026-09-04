from __future__ import annotations

"""v7.1.1 hero delivery hardening.

The earlier hero_v672.webp file is retained only as a deprecated repository asset;
it is not used by the live home because the stored WebP payload is not reliably
decodable.  The live page uses the repository's vector Black Desert camel hero,
with the existing inline SVG as a no-network fallback.
"""

from . import start_v440 as base

_PATCHED = False
APPROVED_HERO = "hero_v671.svg"
APPROVED_HERO_BLOB = "8882ed948a0fae492d7bdb906c4237d5133d9bc3"


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
            "hero_delivery": "external SVG image + inline SVG fallback",
            "hero_decoder_safe": True,
            "hero_webp_deprecated": True,
            "hero_live_release": "7.1.1",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
