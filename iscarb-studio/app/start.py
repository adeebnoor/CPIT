from __future__ import annotations

"""ISCARB process bootstrap.

Applies Gate v8 at process start without destabilizing the proven compiler module.
The compiler still owns source analysis, generation, audit and repair; this layer
only upgrades deterministic normalization/checking before Faculty Studio imports it.
"""

from . import main as engine
from .gate_v8 import deterministic_gate as gate_v8, normalize_blueprint_for_gate


_original_timebox = engine.apply_90_minute_timebox
_original_health = engine.health


def _timebox_v8(bp, profile, bundle):
    bp = _original_timebox(bp, profile, bundle)
    try:
        source_text = bundle.combined_local_text()
    except Exception:
        source_text = ""
    return normalize_blueprint_for_gate(bp, source_text=source_text, profile=profile)


def _health_v8():
    data = _original_health()
    data.update({
        "deterministic_gate": "v8-semantic-aliases-bounded-assurance",
        "local_pre_gate_normalizer": True,
        "local_normalizer_scope": [
            "core/pedagogy/enrichment provenance channel cleanup",
            "Unit 10 KNOWN/UNKNOWN/DECISION-SENSITIVE UNKNOWN/WHAT WE MONITOR ledger",
            "Unit 20 bounded assurance language with residual uncertainty",
        ],
    })
    return data


# main._compile resolves these globals at runtime, so patching here upgrades both
# initial generation and every post-repair pass while preserving the rest of the
# compiler implementation.
engine.deterministic_gate = gate_v8
engine.apply_90_minute_timebox = _timebox_v8
engine.health = _health_v8

from .faculty_main import app  # noqa: E402  (import only after engine patching)
