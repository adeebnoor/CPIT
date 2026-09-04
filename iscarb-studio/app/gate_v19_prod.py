from __future__ import annotations
"""Gate v19 production automated-template checks on top of deployed Gate v16."""
from .gate_v16 import deterministic_gate as gate_v16
from .models import Blueprint, SourceProfile
from .v670_contract import automated_checks

def deterministic_gate(bp: Blueprint, profile: SourceProfile | None = None, source_text: str = "") -> dict[str, bool]:
    checks = gate_v16(bp, profile, source_text)
    checks.update(automated_checks(bp))
    return checks
