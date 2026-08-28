from __future__ import annotations

import re

from .gate_v8 import deterministic_gate as gate_v8, normalize_blueprint_for_gate as normalize_v8
from .models import Blueprint, SourceProfile
from .readiness import ETEC_IT_READINESS
from .readiness_map import SLO_KLO_MAP, expected_klos
from .readiness_atomic import unsupported_atomic_slos

READINESS_ORIENTATION_URL = "https://gulf.edu.sa/standardized-exams-readiness"

HUMAN_FACTORS_TERMS = [
    "cognitive overload", "cognitive load", "operator fatigue", "operator stress",
    "burnout", "practitioner wellbeing", "practitioner well-being", "incident resolution times",
]

UNSUPPORTED_TECH_CLAIM_TERMS = [
    "tamper-resistant", "tamper resistant", "bypass authentication", "session timeout",
    "configuration drift", "automated resilience orchestrator", "automated resilience orchestrators",
]

AUTHORITY_CLAIM_PATTERNS = [
    r"\bmandate(?:s|d)?\b", r"\brequire(?:s|d)?\b", r"\bregulat(?:ion|ions|ory)\b",
    r"\bstandard(?:s)? emphasize\b", r"\bstrictly limit(?:s|ed)?\b",
    r"\bmust account for\b", r"\benforce(?:s|d)? strict\b",
]

PRECISION_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:\d+(?:\.\d+)?\s*%|\d+(?:\.\d+)?\s*(?:ms|milliseconds?|seconds?|requests?/s|ops/s|transactions?/s))(?![A-Za-z0-9])",
    re.I,
)

SAFE_EXERCISE_MARKERS = [
    "synthetic exercise value", "synthetic constraint", "illustrative value", "normalized exercise",
    "hypothetical", "assume that", "in this scenario", "design exploration", "testable claim",
]

TRACEABLE_BASIS_MARKERS = ["[s", "http://", "https://", "doi:", "official source"]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9%./:-]+", " ", (text or "").lower()).strip()


def _source_has(source_text: str, phrase: str) -> bool:
    return _norm(phrase) in _norm(source_text)


def _traceable_basis(unit) -> bool:
    blob = " ".join(unit.enrichment_basis).lower()
    return any(marker in blob for marker in TRACEABLE_BASIS_MARKERS)


def _safe_exercise_sentence(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in SAFE_EXERCISE_MARKERS)


def _has_external_authority_claim(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in AUTHORITY_CLAIM_PATTERNS)


def _unsourced_precision(bp: Blueprint, source_text: str) -> list[tuple[int, str]]:
    bad: list[tuple[int, str]] = []
    for unit in bp.units:
        fields = [
            *unit.pedagogy_content,
            *unit.enrichment_content,
            *unit.scenario_assumptions,
            unit.student_action,
            unit.takeaway,
            unit.evidence,
        ]
        for sentence in fields:
            for match in PRECISION_RE.findall(sentence or ""):
                if not _source_has(source_text, match) and not _safe_exercise_sentence(sentence):
                    bad.append((unit.number, match))
    return bad


def _external_claims_without_basis(bp: Blueprint) -> list[int]:
    bad: list[int] = []
    for unit in bp.units:
        if not unit.enrichment_content:
            continue
        traceable = _traceable_basis(unit)
        for sentence in unit.enrichment_content:
            if _has_external_authority_claim(sentence) and not traceable and not _safe_exercise_sentence(sentence):
                bad.append(unit.number)
                break
    return bad


def _human_factors_core_leakage(bp: Blueprint, source_text: str) -> list[tuple[int, str]]:
    bad: list[tuple[int, str]] = []
    for unit in bp.units:
        core = " ".join(unit.core_content).lower()
        for term in HUMAN_FACTORS_TERMS:
            if term in core and not _source_has(source_text, term):
                bad.append((unit.number, term))
    return bad


def _unsupported_noncore_claims(bp: Blueprint, source_text: str) -> list[tuple[int, str]]:
    bad: list[tuple[int, str]] = []
    for unit in bp.units:
        noncore = " ".join([
            *unit.pedagogy_content, *unit.scenario_assumptions,
            unit.student_action, unit.takeaway, unit.evidence,
        ]).lower()
        for term in UNSUPPORTED_TECH_CLAIM_TERMS:
            if term in noncore and not _source_has(source_text, term):
                sentences = [x for x in re.split(r"(?<=[.!?])\s+|\n+", noncore) if term in x]
                if any(not _safe_exercise_sentence(s) and not any(m in s for m in ["propose", "candidate", "evaluate", "could", "might", "would"]) for s in sentences):
                    bad.append((unit.number, term))
    return bad


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    checks = gate_v8(bp, profile, source_text)

    checks["no_unsourced_precision_in_noncore"] = not _unsourced_precision(bp, source_text)
    checks["external_authority_claims_have_traceable_basis"] = not _external_claims_without_basis(bp)
    checks["human_factors_not_misattributed_to_p1_core"] = not _human_factors_core_leakage(bp, source_text)
    checks["unsupported_noncore_technical_claims_are_framed_as_exercises"] = not _unsupported_noncore_claims(bp, source_text)

    u16 = " ".join([*bp.units[15].pedagogy_content, *bp.units[15].enrichment_content, bp.units[15].student_action])
    u17 = " ".join([*bp.units[16].pedagogy_content, *bp.units[16].enrichment_content, bp.units[16].student_action])
    checks["unit16_has_readiness_orientation_reference"] = READINESS_ORIENTATION_URL in u16
    checks["unit17_has_readiness_orientation_reference"] = READINESS_ORIENTATION_URL in u17

    return checks


def _prefix_once(text: str, prefix: str) -> str:
    if not text:
        return text
    if text.lower().startswith(prefix.lower()):
        return text
    return f"{prefix}{text}"


def _normalize_enrichment_flags(out: Blueprint) -> None:
    """Make the enrichment flag, content and basis internally coherent.

    Missing provenance is never invented as fact. If content exists without a
    traceable basis, it is explicitly bounded as hypothetical enrichment.
    """
    for unit in out.units:
        if not unit.enrichment_content:
            unit.contextual_enrichment = False
            unit.enrichment_basis = []
            continue

        unit.contextual_enrichment = True
        basis_blob = " ".join(unit.enrichment_basis).lower()
        traceable_or_hyp = any(m in basis_blob for m in ["[s", "http://", "https://", "doi:", "official source", "hypothetical"])
        if not traceable_or_hyp:
            unit.enrichment_content = [
                _prefix_once(x, "HYPOTHETICAL CONTEXT — ") for x in unit.enrichment_content
            ]
            unit.enrichment_basis = ["HYPOTHETICAL — no external factual claim; scenario design only."]


def _normalize_unit5_first_principles(out: Blueprint) -> None:
    """Guarantee the visible first-principles sequence without inventing technical facts."""
    u5 = out.units[4]
    blob = " ".join(u5.pedagogy_content).lower()
    required = ["predict", "constraint", "deriv", "principle"]
    if all(k in blob for k in required):
        return
    scaffold = (
        "PREDICT → CONSTRAINT → DERIVATION → PRINCIPLE — predict the behavior; "
        "state only source-supported constraints; derive the mechanism step by step; "
        "then name the engineering principle."
    )
    if len(u5.pedagogy_content) < 8:
        u5.pedagogy_content.append(scaffold)
    elif u5.pedagogy_content:
        u5.pedagogy_content[-1] = scaffold + " | " + u5.pedagogy_content[-1]


def _normalize_readiness_alignment(out: Blueprint, source_text: str) -> None:
    """Conservatively repair exact ETEC mappings and keep only minimal supported targets."""
    valid_skus = ETEC_IT_READINESS["skus"]
    repaired = []

    for alignment in out.readiness_alignment:
        if alignment.sku not in valid_skus or alignment.sku not in SLO_KLO_MAP:
            continue

        official = valid_skus[alignment.sku]
        valid_slos = [
            slo for slo in alignment.slo_refs
            if slo in official["slos"] and slo in SLO_KLO_MAP[alignment.sku]
        ]
        unsupported = set(unsupported_atomic_slos(valid_slos, source_text))
        valid_slos = [slo for slo in valid_slos if slo not in unsupported]
        if not valid_slos:
            continue

        alignment.gku = official["gku"]
        alignment.slo_refs = valid_slos
        alignment.klo_refs = list(expected_klos(alignment.sku, valid_slos))

        official_pages = list(official["source_pages"])
        retained_pages = [p for p in alignment.standard_source_pages if p in official_pages]
        alignment.standard_source_pages = retained_pages or official_pages[:1]

        if not alignment.atomicity_evidence.strip():
            alignment.atomicity_evidence = (
                "Deterministic source-atomicity check: retained SLOs are supported by the weekly source boundary."
            )
        repaired.append(alignment)

    # Never fabricate a readiness target. If nothing survives conservative
    # filtering, leave the original alignment in place so the Gate blocks it.
    if repaired:
        repaired.sort(key=lambda x: (0 if x.strength == "direct" else 1, -len(x.evidence_units)))
        out.readiness_alignment = repaired[:2]


def normalize_blueprint_for_output_lab(bp: Blueprint) -> Blueprint:
    """Presentation-safe local repair for an imported Blueprint.

    This intentionally does NOT re-audit source fidelity or ETEC atomicity,
    because Output Lab does not have the original source bundle.
    """
    out = bp.model_copy(deep=True)
    _normalize_enrichment_flags(out)
    _normalize_unit5_first_principles(out)
    readiness_line = (
        f"READINESS ORIENTATION REFERENCE — {READINESS_ORIENTATION_URL} "
        "(orientation gateway only; ETEC Academic Standards remain the assessment authority)."
    )
    for idx in [15, 16]:
        unit = out.units[idx]
        blob = " ".join([*unit.pedagogy_content, *unit.enrichment_content, unit.student_action])
        if READINESS_ORIENTATION_URL not in blob and len(unit.pedagogy_content) < 8:
            unit.pedagogy_content.append(readiness_line)

    note = (
        "Output Lab local normalization applied: enrichment-state consistency, visible Unit 5 first-principles scaffold, "
        "and readiness orientation references. Source-dependent release checks were not re-audited."
    )
    if note not in out.release_notes:
        out.release_notes.append(note)
    return out


def normalize_blueprint_for_gate(
    bp: Blueprint,
    source_text: str = "",
    profile: SourceProfile | None = None,
) -> Blueprint:
    out = normalize_v8(bp, source_text=source_text, profile=profile)

    # 0) Structural/provenance repairs that are source-safe.
    _normalize_enrichment_flags(out)
    _normalize_unit5_first_principles(out)

    # 1) Human-factors concepts belong in ISCARB pedagogy unless explicitly in P1.
    for unit in out.units:
        kept: list[str] = []
        for bullet in unit.core_content:
            low = bullet.lower()
            leaked = any(term in low and not _source_has(source_text, term) for term in HUMAN_FACTORS_TERMS)
            if leaked and len(unit.pedagogy_content) < 8:
                unit.pedagogy_content.append(
                    "ISCARB HUMAN-FACTORS INTERPRETATION — " + bullet
                )
            else:
                kept.append(bullet)
        unit.core_content = kept
        if not unit.core_content:
            unit.source_anchor = ""

    # 2) Exact/quantitative exercise values that are not in P1 must never masquerade as evidence.
    for unit in out.units:
        for attr in ["pedagogy_content", "enrichment_content", "scenario_assumptions"]:
            values = list(getattr(unit, attr))
            revised: list[str] = []
            for sentence in values:
                matches = PRECISION_RE.findall(sentence or "")
                if matches and any(not _source_has(source_text, m) for m in matches) and not _safe_exercise_sentence(sentence):
                    sentence = _prefix_once(sentence, "SYNTHETIC EXERCISE VALUE — ")
                revised.append(sentence)
            setattr(unit, attr, revised)

        for attr in ["student_action", "takeaway", "evidence"]:
            sentence = getattr(unit, attr)
            matches = PRECISION_RE.findall(sentence or "")
            if matches and any(not _source_has(source_text, m) for m in matches) and not _safe_exercise_sentence(sentence):
                setattr(unit, attr, _prefix_once(sentence, "SYNTHETIC EXERCISE VALUE — "))

    # 3) Unreferenced authority/market claims are converted to explicit hypotheticals.
    for unit in out.units:
        if not unit.enrichment_content or _traceable_basis(unit):
            continue
        unit.enrichment_content = [
            _prefix_once(x, "HYPOTHETICAL CONTEXT — Assume that ")
            if _has_external_authority_claim(x) and not _safe_exercise_sentence(x)
            else x
            for x in unit.enrichment_content
        ]
        if any(x.startswith("HYPOTHETICAL CONTEXT") for x in unit.enrichment_content):
            marker = "HYPOTHETICAL — no external factual claim; scenario design only."
            if marker not in unit.enrichment_basis and len(unit.enrichment_basis) < 6:
                unit.enrichment_basis.append(marker)
            unit.contextual_enrichment = True

    # 4) Unsupported technical examples in non-core are reframed as things to test/design, not facts.
    for unit in out.units:
        revised: list[str] = []
        for sentence in unit.pedagogy_content:
            low = sentence.lower()
            hits = [t for t in UNSUPPORTED_TECH_CLAIM_TERMS if t in low and not _source_has(source_text, t)]
            if hits and not _safe_exercise_sentence(sentence) and not any(m in low for m in ["propose", "candidate", "evaluate", "could", "might", "would"]):
                sentence = _prefix_once(sentence, "TESTABLE DESIGN HYPOTHESIS — ")
            revised.append(sentence)
        unit.pedagogy_content = revised

    # 5) Readiness orientation reference is mandatory in BOTH Portfolio/Mutation units.
    readiness_line = (
        f"READINESS ORIENTATION REFERENCE — {READINESS_ORIENTATION_URL} "
        "(orientation gateway only; ETEC Academic Standards remain the assessment authority)."
    )
    for idx in [15, 16]:
        unit = out.units[idx]
        blob = " ".join([*unit.pedagogy_content, *unit.enrichment_content, unit.student_action])
        if READINESS_ORIENTATION_URL not in blob:
            if len(unit.pedagogy_content) < 8:
                unit.pedagogy_content.append(readiness_line)
            elif len(unit.enrichment_content) < 6:
                unit.enrichment_content.append(readiness_line)
                unit.enrichment_basis.append("HYPOTHETICAL — user-required orientation reference; not used as ETEC authority.")
                unit.contextual_enrichment = True

    # 6) Repair readiness mappings conservatively against the official bundled map.
    _normalize_readiness_alignment(out, source_text)

    # Re-run flag normalization because steps above may have added enrichment.
    _normalize_enrichment_flags(out)

    note = (
        "Gate v9 claim-level normalization applied: enrichment-state consistency, visible first-principles derivation, "
        "synthetic precision labeling, external-authority claim bounding, human-factors provenance, testable non-core "
        "technical hypotheses, readiness orientation references, and conservative exact readiness mapping."
    )
    if note not in out.release_notes:
        out.release_notes.append(note)

    return out
