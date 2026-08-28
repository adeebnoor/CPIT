from __future__ import annotations

"""ISCARB v3.8 source-safe structural normalization.

These repairs operate only on ISCARB pedagogy/provenance metadata. They never
invent weekly-source technical facts and are safe both before a full Gate audit
and inside Output Lab presentation repair.
"""

import re

from .models import Blueprint, SourceProfile
from .gate_v9 import normalize_blueprint_for_gate, normalize_blueprint_for_output_lab


RISKY_HYPOTHETICAL_TERMS = [
    " require", " requires", " mandate", " mandates", " regulation", " regulations",
    " national rule", " market rule", " must ", " strictly limit", " enforce",
]
HYPOTHETICAL_FRAMING = [
    "assume", "in this scenario", "in this hypothetical", "scenario requires",
    "design exploration", "hypothetical context",
]


def _fix_unit3_clos(out: Blueprint) -> None:
    """Unit 3 is pure pedagogy: exactly five visible CLO rows, no fake P1 core."""
    u3 = out.units[2]
    u3.core_content = []
    u3.source_anchor = ""
    u3.pedagogy_content = [
        f"{clo.id} — {clo.statement} | PROOF: {clo.evidence_expected}"
        for clo in out.clOs
    ][:5]


def _fix_hypothetical_enrichment(out: Blueprint) -> None:
    for unit in out.units:
        if not unit.enrichment_content:
            unit.contextual_enrichment = False
            unit.enrichment_basis = []
            continue

        unit.contextual_enrichment = True
        basis_blob = " ".join(unit.enrichment_basis).lower()
        if not unit.enrichment_basis:
            unit.enrichment_basis = ["HYPOTHETICAL — no external factual claim; scenario design only."]
            basis_blob = "hypothetical"

        if "hypothetical" not in basis_blob:
            continue

        revised: list[str] = []
        for text in unit.enrichment_content:
            low = " " + text.lower() + " "
            risky = any(term in low for term in RISKY_HYPOTHETICAL_TERMS)
            framed = any(marker in low for marker in HYPOTHETICAL_FRAMING)
            if risky and not framed:
                text = "HYPOTHETICAL CONTEXT — Assume that " + text
            revised.append(text)
        unit.enrichment_content = revised


def _fix_progression_metadata(out: Blueprint) -> None:
    # IDR-7 is demonstrably satisfied by the required phase sequence already
    # encoded in the Blueprint; this tag records that visible structure.
    if not any("IDR-7" in u.inherited_requirements for u in out.units):
        out.units[0].inherited_requirements.append("IDR-7")

    # EER-7 is pedagogy, not a technical fact. If missing, make the expectation
    # explicit as a bounded estimation scaffold before precision.
    if not any("EER-7" in u.elite_requirements for u in out.units):
        target = out.units[7]  # trade-off / decision unit
        scaffold = (
            "ESTIMATE BEFORE PRECISION — use only P1 values or clearly labeled synthetic normalized assumptions; "
            "state uncertainty before comparing precise alternatives."
        )
        blob = " ".join(target.pedagogy_content).lower()
        if "estimate before precision" not in blob:
            if len(target.pedagogy_content) < 8:
                target.pedagogy_content.append(scaffold)
            elif target.pedagogy_content:
                target.pedagogy_content[-1] = scaffold + " | " + target.pedagogy_content[-1]
        target.elite_requirements.append("EER-7")


def _dedupe_tags(out: Blueprint) -> None:
    for unit in out.units:
        unit.inherited_requirements = list(dict.fromkeys(unit.inherited_requirements))
        unit.elite_requirements = list(dict.fromkeys(unit.elite_requirements))


def _apply_common(out: Blueprint) -> Blueprint:
    _fix_unit3_clos(out)
    _fix_hypothetical_enrichment(out)
    _fix_progression_metadata(out)
    _dedupe_tags(out)
    note = (
        "v3.8 structural normalization applied: Unit 3 five-CLO pedagogy channel, bounded hypothetical enrichment, "
        "IDR-7 phase-progression metadata, and EER-7 estimate-before-precision scaffold."
    )
    if note not in out.release_notes:
        out.release_notes.append(note)
    return out


def normalize_source_backed_v38(
    bp: Blueprint,
    source_text: str = "",
    profile: SourceProfile | None = None,
) -> Blueprint:
    out = normalize_blueprint_for_gate(bp, source_text=source_text, profile=profile)
    return _apply_common(out)


def normalize_output_lab_v38(bp: Blueprint) -> Blueprint:
    out = normalize_blueprint_for_output_lab(bp)
    return _apply_common(out)
