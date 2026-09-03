from __future__ import annotations

"""ISCARB Faculty Studio v4.8.1 — real-lecture regression release.

This module is a thin release layer on top of v4.7.0. The generation
pipeline, the 20-unit contract and every Gate v16 Master Guideline check
are inherited unchanged from ``start_v470``; only the public release
identity moves forward. Keeping the bump in its own module means the
version that ``/api/health`` reports can never drift from the module the
ASGI entry point actually loads.
"""

from .start_v470 import app  # noqa: F401  (re-exported ASGI application)
from . import start_v470 as prev
from . import start_v440 as base

PUBLIC_VERSION = "4.8.1"
PIPELINE_ID = "faculty-studio-v4.8.1-real-lecture-visual-output"

# The landing route stamps X-ISCARB-Version from start_v440's module global,
# so the release identity has to be rebound there as well as in the health
# payload. Both surfaces must agree or a stale Render image is indetectable.
base.PUBLIC_VERSION = PUBLIC_VERSION
base.PIPELINE_ID = PIPELINE_ID
prev.PUBLIC_VERSION = PUBLIC_VERSION
prev.PIPELINE_ID = PIPELINE_ID

_prev_health = base._health_v440


def _health_v480():
    data = _prev_health()
    data.update({
        "version": PUBLIC_VERSION,
        "pipeline": PIPELINE_ID,
        "public_experience": (
            "ISCARB Faculty Studio v4.8.1 — approved Arabic-first RTL landing page "
            "with the CIMT visual-first presenter surface"
        ),
    })
    return data


base._health_v440 = _health_v480
base.engine.health = _health_v480
