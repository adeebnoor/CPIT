from __future__ import annotations

"""ISCARB Faculty Studio v4.0.4 source-safe release normalization.

This layer repairs provenance/channel metadata after model generation without
inventing weekly-source technical claims. It is deliberately conservative:
unsupported technical specificity is moved out of pedagogy into explicitly
hypothetical enrichment, while P1-supported content remains authoritative.
"""

import re

from .gate_v10 import normalize_blueprint_for_gate as normalize_v10
from .gate_v9 import normalize_blueprint_for_output_lab
from .models import Blueprint, SourceProfile

HYP_BASIS = "HYPOTHETICAL — no external factual claim; design exploration only."

SESSION_WATCHED = [
    "row-level encryption", "immutable logging", "penetration test", "penetration testing",
    "intrusion detection system", "ids", "zero trust", "proxy gateway", "token-based",
    "container image", "infrastructure-as-code", "configuration drift", "cryptographic",
    "tamper-resistant", "tamper resistant", "bypass authentication", "session timeout",
    "automated resilience orchestrator", "automated resilience orchestrators",
]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _has_phrase(text: str, phrase: str) -> bool:
    needle = _norm(phrase)
    if not needle:
        return False
    return f" {needle} " in f" {_norm(text)} "


def _source_has(source_text: str, phrase: str) -> bool:
    return _has_phrase(source_text, phrase)


def _append_bounded(items: list[str], text: str, limit: int) -> None:
    if not text or text in items:
        return
    if len(items) < limit:
        items.append(text)
    elif items:
        if text not in items[-1]:
            items[-1] = items[-1] + " | " + text


def _move_to_pedagogy(unit, predicate) -> None:
    kept: list[str] = []
    for bullet in unit.core_content:
        if predicate(bullet):
            _append_bounded(unit.pedagogy_content, "ISCARB METHOD — " + bullet, 8)
        else:
            kept.append(bullet)
    unit.core_content = kept
    if not kept:
        unit.source_anchor = ""


def _fix_reserved_channel_purity(out: Blueprint, source_text: str) -> None:
    u15 = out.units[14]
    _move_to_pedagogy(
        u15,
        lambda b: bool(re.search(r"\bai\b|artificial intelligence", b, flags=re.I))
        and not (_source_has(source_text, "artificial intelligence") or _source_has(source_text, "ai")),
    )

    u19 = out.units[18]
    _move_to_pedagogy(
        u19,
        lambda b: any(x in b.lower() for x in ["distinguished", "not yet ready", "rubric", "four-level"]),
    )

    u20 = out.units[19]
    _move_to_pedagogy(
        u20,
        lambda b: any(x in b.lower() for x in ["top-level bounded claim", "subclaim", "final authorization", "assurance case"]),
    )


def _fix_domain_spine(out: Blueprint, profile: SourceProfile | None) -> None:
    if profile is None or not profile.topic_families:
        return
    names = [x.name.strip() for x in profile.topic_families if x.name.strip()]
    if not names:
        return
    u2 = out.units[1]
    blob = " ".join([u2.title, u2.engineering_question, *u2.core_content, *u2.pedagogy_content])
    missing = [name for name in names if not _has_phrase(blob, name)]
    if missing:
        _append_bounded(u2.pedagogy_content, "DOMAIN SPINE — " + " | ".join(names), 8)


def _fix_bundle_anchors(out: Blueprint) -> None:
    for unit in out.units:
        if not unit.core_content:
            continue
        anchor = (unit.source_anchor or "").strip()
        ids = set(re.findall(r"\[([PS]\d+)\]", anchor.upper()))
        if not ids:
            unit.source_anchor = "[P1] " + (anchor or "weekly primary lecture")


def _replace_phrase(text: str, phrase: str) -> str:
    if not text:
        return text
    p = phrase.strip()
    if p.lower() == "ids":
        return re.sub(r"\bids\b", "candidate detection control", text, flags=re.I)
    return re.sub(re.escape(p), "candidate technical control", text, flags=re.I)


def _neutralize_sentence(unit, sentence: str, source_text: str) -> str:
    if not sentence:
        return sentence
    unsupported = [
        term for term in SESSION_WATCHED
        if _has_phrase(sentence, term) and not _source_has(source_text, term)
    ]
    if not unsupported:
        return sentence

    if len(unit.enrichment_content) < 6:
        candidate = "HYPOTHETICAL DESIGN EXPLORATION — Evaluate rather than assume: " + sentence
        _append_bounded(unit.enrichment_content, candidate, 6)
        _append_bounded(unit.enrichment_basis, HYP_BASIS, 6)
        unit.contextual_enrichment = True

    revised = sentence
    for term in sorted(unsupported, key=len, reverse=True):
        revised = _replace_phrase(revised, term)
    return revised


def _fix_noncore_technology_leakage(out: Blueprint, source_text: str) -> None:
    for unit in out.units:
        unit.pedagogy_content = [_neutralize_sentence(unit, x, source_text) for x in unit.pedagogy_content]
        unit.scenario_assumptions = [_neutralize_sentence(unit, x, source_text) for x in unit.scenario_assumptions]
        unit.student_action = _neutralize_sentence(unit, unit.student_action, source_text)
        unit.takeaway = _neutralize_sentence(unit, unit.takeaway, source_text)
        unit.evidence = _neutralize_sentence(unit, unit.evidence, source_text)


def _fix_unit16_readiness_trace(out: Blueprint) -> None:
    if not out.readiness_alignment:
        return
    u16 = out.units[15]
    parts: list[str] = []
    for row in out.readiness_alignment[:2]:
        refs = ", ".join(row.slo_refs)
        # Two rows carrying the same unverified placeholder printed it twice.
        entry = f"{row.sku} ({refs})"
        if entry not in parts:
            parts.append(entry)
    target = "ETEC READINESS TARGET — " + " | ".join(parts) + "."
    blob = " ".join([*u16.pedagogy_content, *u16.enrichment_content, u16.student_action]).lower()
    if "etec" not in blob or not any(row.sku.lower() in blob or any(s.lower() in blob for s in row.slo_refs) for row in out.readiness_alignment):
        _append_bounded(u16.pedagogy_content, target, 8)


def _finalize_enrichment_contract(out: Blueprint) -> None:
    for unit in out.units:
        if unit.enrichment_content:
            unit.contextual_enrichment = True
            if not unit.enrichment_basis:
                unit.enrichment_basis = [HYP_BASIS]
        else:
            unit.contextual_enrichment = False
            unit.enrichment_basis = []


def normalize_source_backed_v404(
    bp: Blueprint,
    source_text: str = "",
    profile: SourceProfile | None = None,
) -> Blueprint:
    out = normalize_v10(bp, source_text=source_text, profile=profile)
    _fix_reserved_channel_purity(out, source_text)
    _fix_domain_spine(out, profile)
    _fix_bundle_anchors(out)
    _fix_noncore_technology_leakage(out, source_text)
    _fix_unit16_readiness_trace(out)
    _finalize_enrichment_contract(out)
    note = (
        "v4.0.4 release normalization applied: authoritative Domain Spine, explicit P1 technical anchors, "
        "reserved-unit channel purity, source-safe noncore technology handling, and explicit minimum-sufficient ETEC trace."
    )
    if note not in out.release_notes:
        out.release_notes.append(note)
    return out


def normalize_output_lab_v404(bp: Blueprint) -> Blueprint:
    out = normalize_blueprint_for_output_lab(bp)
    _fix_reserved_channel_purity(out, "")
    _fix_bundle_anchors(out)
    _fix_unit16_readiness_trace(out)
    _finalize_enrichment_contract(out)
    return out
