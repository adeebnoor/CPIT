from __future__ import annotations

import json

# Exact SLO -> KLO mappings transcribed from the ETEC Academic Standards for
# Information Technology Programs 2025 v2.0 tables. These mappings are used as
# a hard validation authority; the model is not allowed to infer or improvise them.
SLO_KLO_MAP: dict[str, dict[str, list[str]]] = {
    "SKU2.2": {
        "SLO2.2.1": ["KLO8", "KLO9"],
        "SLO2.2.2": ["KLO3", "KLO8", "KLO9"],
        "SLO2.2.3": ["KLO1", "KLO9"],
        "SLO2.2.4": ["KLO9"],
    },
    "SKU3.1": {
        "SLO3.1.1": ["KLO1"],
        "SLO3.1.2": ["KLO2"],
        "SLO3.1.3": ["KLO2", "KLO3", "KLO4"],
        "SLO3.1.4": ["KLO2", "KLO3"],
        "SLO3.1.5": ["KLO1"],
    },
    "SKU3.2": {
        "SLO3.2.1": ["KLO1"],
        "SLO3.2.2": ["KLO2"],
        "SLO3.2.3": ["KLO1"],
    },
    "SKU7.1": {
        "SLO7.1.1": ["KLO3"],
        "SLO7.1.2": ["KLO2"],
        "SLO7.1.3": ["KLO3"],
    },
    "SKU7.2": {
        "SLO7.2.1": ["KLO1", "KLO10"],
        "SLO7.2.2": ["KLO4"],
    },
    "SKU8.1": {
        "SLO8.1.1": ["KLO3"],
        "SLO8.1.2": ["KLO3"],
        "SLO8.1.3": ["KLO7"],
        "SLO8.1.4": ["KLO2"],
        "SLO8.1.5": ["KLO4", "KLO10"],
    },
    "SKU8.2": {
        "SLO8.2.1": ["KLO3"],
        "SLO8.2.2": ["KLO3"],
        "SLO8.2.3": ["KLO1"],
        "SLO8.2.4": ["KLO2"],
    },
    "SKU9.1": {
        "SLO9.1.1": ["KLO3", "KLO4"],
        "SLO9.1.2": ["KLO3", "KLO4"],
        "SLO9.1.3": ["KLO3", "KLO4"],
        "SLO9.1.4": ["KLO2"],
        "SLO9.1.5": ["KLO4"],
    },
}


def expected_klos(sku: str, slo_refs: list[str]) -> list[str]:
    mapping = SLO_KLO_MAP.get(sku, {})
    values: set[str] = set()
    for slo in slo_refs:
        values.update(mapping.get(slo, []))
    return sorted(values, key=lambda x: int(x.replace("KLO", "")))


READINESS_KLO_MAP_CONTEXT = json.dumps(SLO_KLO_MAP, ensure_ascii=False, indent=2)
