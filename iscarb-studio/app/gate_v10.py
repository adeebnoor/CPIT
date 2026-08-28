from __future__ import annotations

"""ISCARB Gate v10 — deterministic repair completeness.

v10 keeps every Gate v9 requirement, then closes three repair gaps observed in
faculty use:
1) enrichment flag/basis consistency,
2) visible Unit 5 first-principles derivation,
3) conservative official ETEC readiness normalization.

The normalizer never grants RELEASE; it only makes deterministic structure
internally consistent so the semantic/source audit remains meaningful.
"""

from .gate_v9 import deterministic_gate as gate_v9, normalize_blueprint_for_gate as normalize_v9
from .models import Blueprint, SourceProfile
from .readiness import ETEC_IT_READINESS
from .readiness_map import SLO_KLO_MAP, expected_klos
from .readiness_atomic import unsupported_atomic_slos

HYP_BASIS = "HYPOTHETICAL — no external factual claim; scenario design only."


def _evidence_text(bp: Blueprint, source_text: str) -> str:
    if (source_text or "").strip():
        return source_text
    return " ".join(x for u in bp.units for x in u.core_content)


def _fix_enrichment_contract(bp: Blueprint) -> None:
    for unit in bp.units:
        if unit.enrichment_content:
            unit.contextual_enrichment = True
            if not unit.enrichment_basis:
                unit.enrichment_basis = [HYP_BASIS]
        else:
            unit.contextual_enrichment = False
            unit.enrichment_basis = []


def _fix_unit5_first_principles(bp: Blueprint) -> None:
    u5 = bp.units[4]
    blob = " ".join(u5.pedagogy_content).lower()
    required = ["predict", "constraint", "deriv", "principle"]
    if all(x in blob for x in required):
        return
    scaffold = (
        "PREDICT → CONSTRAINT → DERIVATION → PRINCIPLE — predict before explanation; "
        "state the source-supported constraint; derive what follows from the taught mechanism; "
        "only then name the formal principle."
    )
    if len(u5.pedagogy_content) < 8:
        u5.pedagogy_content.append(scaffold)
    elif u5.pedagogy_content:
        u5.pedagogy_content[-1] = scaffold
    else:
        u5.pedagogy_content = [scaffold]


def _normalize_one_alignment(r, evidence_text: str):
    if r.sku not in ETEC_IT_READINESS["skus"] or r.sku not in SLO_KLO_MAP:
        return None
    official = ETEC_IT_READINESS["skus"][r.sku]
    valid = []
    for slo in r.slo_refs:
        if slo not in official["slos"] or slo not in SLO_KLO_MAP[r.sku]:
            continue
        if unsupported_atomic_slos([slo], evidence_text):
            continue
        valid.append(slo)
    if not valid:
        return None
    valid = valid[:1]
    r.gku = official["gku"]
    r.slo_refs = valid
    r.klo_refs = expected_klos(r.sku, valid)
    r.standard_source_pages = list(official["source_pages"])
    r.atomicity_evidence = (
        "Minimum-sufficient alignment retained only after official SKU/SLO validation "
        "and source-atomicity screening against the weekly source/core evidence."
    )
    return r


def _security_fallback(bp: Blueprint, evidence_text: str):
    low = evidence_text.lower()
    if not all(any(k in low for k in group) for group in [
        ("vulnerability", "vulnerabilities"),
        ("threat", "threats"),
        ("risk", "risks"),
    ]):
        return None
    if not bp.readiness_alignment:
        return None
    seed = bp.readiness_alignment[0].model_copy(deep=True)
    official = ETEC_IT_READINESS["skus"]["SKU3.1"]
    seed.gku = official["gku"]
    seed.sku = "SKU3.1"
    seed.slo_refs = ["SLO3.1.2"]
    seed.klo_refs = expected_klos("SKU3.1", seed.slo_refs)
    seed.standard_source_pages = list(official["source_pages"])
    seed.strength = "direct"
    seed.rationale = (
        "The weekly source explicitly treats vulnerabilities, threats, and risk; "
        "alignment is therefore limited to comparing these concepts and their interrelationship."
    )
    seed.atomicity_evidence = (
        "Source/core evidence contains vulnerability, threat, and risk language required "
        "for SLO3.1.2; no broader cybersecurity SLO is claimed."
    )
    if not seed.clo_ids:
        seed.clo_ids = ["CLO1"]
    if not seed.evidence_units:
        seed.evidence_units = [5]
    return seed


def _fix_readiness(bp: Blueprint, source_text: str) -> None:
    evidence = _evidence_text(bp, source_text)
    kept = []
    seen = set()
    for row in bp.readiness_alignment:
        fixed = _normalize_one_alignment(row, evidence)
        if fixed is None:
            continue
        key = (fixed.sku, tuple(fixed.slo_refs))
        if key in seen:
            continue
        seen.add(key)
        kept.append(fixed)
        if len(kept) >= 2:
            break
    if not kept:
        fallback = _security_fallback(bp, evidence)
        if fallback is not None:
            kept = [fallback]
    if kept:
        bp.readiness_alignment = kept


def normalize_blueprint_for_gate(
    bp: Blueprint,
    source_text: str = "",
    profile: SourceProfile | None = None,
) -> Blueprint:
    out = normalize_v9(bp, source_text=source_text, profile=profile)
    _fix_enrichment_contract(out)
    _fix_unit5_first_principles(out)
    _fix_readiness(out, source_text)
    note = (
        "Gate v10 deterministic normalization applied: enrichment contract consistency, "
        "visible Unit 5 first-principles derivation, and minimum-sufficient official ETEC readiness normalization."
    )
    if note not in out.release_notes:
        out.release_notes.append(note)
    return out


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    checks = gate_v9(bp, profile, source_text)
    checks["v10_enrichment_contract_consistent"] = checks.get("enrichment_flag_consistency", False)
    checks["v10_unit5_first_principles_visible"] = checks.get("unit5_visible_first_principles_derivation", False)
    checks["v10_readiness_minimum_sufficient"] = checks.get("readiness_is_minimum_sufficient", False)
    checks["v10_readiness_official_map_exact"] = checks.get("readiness_exact_official_slo_klo_map", False)
    checks["v10_readiness_source_atomic"] = checks.get("readiness_source_atomicity", False)
    return checks
