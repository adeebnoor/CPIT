from __future__ import annotations

import re

from .gate_v8 import deterministic_gate as gate_v8, normalize_blueprint_for_gate as normalize_v8
from .models import Blueprint, SourceProfile

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
                # It is acceptable as a question/proposal/hypothetical, not as an asserted fact.
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

    # The user-requested readiness page is an orientation gateway, not the authority.
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


def normalize_blueprint_for_gate(
    bp: Blueprint,
    source_text: str = "",
    profile: SourceProfile | None = None,
) -> Blueprint:
    out = normalize_v8(bp, source_text=source_text, profile=profile)

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
                unit.enrichment_basis.append("User-required orientation reference; not used as ETEC authority.")
                unit.contextual_enrichment = True

    note = (
        "Gate v9 claim-level normalization applied: synthetic precision labeling, external-authority claim bounding, "
        "human-factors provenance, testable non-core technical hypotheses, and readiness orientation references."
    )
    if note not in out.release_notes:
        out.release_notes.append(note)

    return out
