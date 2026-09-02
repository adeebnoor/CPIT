from __future__ import annotations

"""Gate v16: ISCARB cross-topic master guidelines."""

from .gate_v15 import deterministic_gate as gate_v15
from .models import Blueprint, SourceProfile
from .master_guidelines_v470 import master_gate_checks


def deterministic_gate(bp: Blueprint, profile: SourceProfile | None = None, source_text: str = "") -> dict[str, bool]:
    checks = gate_v15(bp, profile, source_text)
    checks.update(master_gate_checks(bp))
    checks["v16_master_guidelines_pass"] = all(
        value for key, value in checks.items() if key.startswith("v16_") and key != "v16_master_guidelines_pass"
    )
    return checks
