from __future__ import annotations

import re

from .gate import deterministic_gate as legacy_deterministic_gate
from .models import Blueprint, SourceProfile


PEDAGOGY_ONLY_TERMS = [
    "cognitive load", "operator fatigue", "artificial intelligence", "ai may assist",
    "senior design review", "counter-evidence", "residual uncertainty", "four-level rubric",
]
TECHNICAL_WATCHED_TERMS = [
    "zero trust", "microservice", "container", "infrastructure-as-code", "token-based",
    "proxy gateway", "encrypted payload", "decryption performance",
]
ALL_WATCHED_TERMS = TECHNICAL_WATCHED_TERMS + PEDAGOGY_ONLY_TERMS


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _phrase_present(text: str, phrase: str) -> bool:
    """Whole-phrase match after punctuation/hyphen normalization.

    The legacy gate used substring matching, which could create false positives
    such as matching `container` inside a longer unrelated token.
    """
    hay = f" {_norm(text)} "
    needle = f" {_norm(phrase)} "
    return needle in hay


def _profile_blob(profile: SourceProfile | None) -> str:
    if profile is None:
        return ""
    return " ".join([
        profile.lecture_title,
        profile.weekly_focus,
        *[f"{x.name} {x.why_important}" for x in profile.topic_families],
        *profile.technical_boundaries,
        *profile.source_warnings,
    ])


def _term_supported(term: str, source_text: str, profile: SourceProfile | None) -> bool:
    evidence = f"{source_text or ''} {_profile_blob(profile)}"
    return _phrase_present(evidence, term)


def _ledger_semantically_complete(text: str) -> bool:
    low = _norm(text)
    known = any(x in low for x in [
        "known", "confirmed fact", "established fact", "observed fact", "known evidence",
    ])
    unknown = any(x in low for x in [
        "unknown", "uncertain", "uncertainty", "unresolved", "not yet known",
    ])
    decision_sensitive = any(x in low for x in [
        "decision sensitive unknown", "decision sensitive uncertainty", "decision critical uncertainty",
        "uncertainty that would change the decision", "unknown that would change the decision",
        "decision changing uncertainty",
    ])
    monitor = any(x in low for x in [
        "what we monitor", "monitor", "telemetry", "observe", "observation", "track", "instrument",
        "evidence to collect", "watch condition",
    ])
    return known and unknown and decision_sensitive and monitor


def _bounded_assurance_ok(text: str) -> bool:
    """Reject unbounded promises, but do not punish explicit negation/bounds."""
    low = _norm(text)
    if not low:
        return False

    # Explicitly bounded language is expected in a real assurance case.
    bounded_cues = [
        "within the stated", "within this scenario", "under the stated", "subject to", "residual uncertainty",
        "conditional", "conditionally", "current evidence", "available evidence", "reduces", "mitigates",
        "supports", "addresses", "designed to maintain", "does not guarantee", "cannot guarantee",
        "does not eliminate", "cannot eliminate", "does not prevent all", "cannot prevent all",
    ]

    # Positive absolute promises remain prohibited. Negated phrases are handled
    # before this test so we do not fail a sentence such as "does not guarantee".
    stripped = low
    negated = [
        "does not guarantee", "cannot guarantee", "not guarantee",
        "does not eliminate", "cannot eliminate", "not eliminate",
        "does not prevent all", "cannot prevent all", "cannot prevent every",
    ]
    for phrase in negated:
        stripped = stripped.replace(phrase, " bounded limitation ")

    absolute_patterns = [
        r"\bguarantee(?:s|d)?\b",
        r"\beliminate(?:s|d)?\b",
        r"\bprevent(?:s|ed)?\b",
        r"\bprove(?:s|d)? secure\b",
        r"\bzero risk\b",
        r"\balways secure\b",
        r"\bimpossible to breach\b",
    ]
    has_absolute = any(re.search(p, stripped) for p in absolute_patterns)
    has_bound = any(cue in low for cue in bounded_cues)
    return (not has_absolute) and has_bound


def deterministic_gate(
    bp: Blueprint,
    profile: SourceProfile | None = None,
    source_text: str = "",
) -> dict[str, bool]:
    """ISCARB Gate v8.

    Retains every legacy hard gate, then replaces three brittle string checks
    with semantically stricter-but-fair checks. No criterion is removed.
    """
    checks = legacy_deterministic_gate(bp, profile, source_text)

    # 1) Core purity: whole phrase matching + source profile evidence.
    unsupported: list[tuple[int, str]] = []
    for unit in bp.units:
        core = " ".join(unit.core_content)
        for term in ALL_WATCHED_TERMS:
            if _phrase_present(core, term) and not _term_supported(term, source_text, profile):
                unsupported.append((unit.number, term))
    checks["no_obvious_unsourced_terms_in_core"] = not unsupported

    # 2) Unit 10: assess the four information states by meaning, not one exact label string.
    unit10 = bp.units[9]
    u10_text = " ".join([
        unit10.title, unit10.engineering_question, *unit10.pedagogy_content,
        unit10.student_action, unit10.takeaway, unit10.evidence,
    ])
    checks["unit10_known_unknown_monitoring"] = _ledger_semantically_complete(u10_text)

    # 3) Unit 20: only bounded, evidence-proportionate assurance may pass.
    unit20 = bp.units[19]
    u20_text = " ".join([
        unit20.title, unit20.engineering_question, *unit20.pedagogy_content,
        unit20.student_action, unit20.takeaway, unit20.evidence,
    ])
    bounded = _bounded_assurance_ok(u20_text)
    checks["unit20_assurance_language"] = bounded
    checks["unit20_uses_bounded_assurance_language"] = bounded

    return checks


def _bound_text(text: str) -> str:
    """Conservatively rewrite non-core assurance wording without altering P1 core."""
    if not text:
        return text
    replacements = [
        (r"\bguarantees\b", "supports"),
        (r"\bguarantee\b", "support"),
        (r"\bguaranteed\b", "supported"),
        (r"\beliminates\b", "reduces"),
        (r"\beliminate\b", "reduce"),
        (r"\beliminated\b", "reduced"),
        (r"\bprevents\b", "reduces the likelihood of"),
        (r"\bprevent\b", "reduce the likelihood of"),
        (r"\bprevented\b", "reduced"),
        (r"\bprove secure\b", "support a bounded security claim for"),
        (r"\bproves secure\b", "supports a bounded security claim for"),
        (r"\bzero risk\b", "bounded residual risk"),
        (r"\balways secure\b", "secure within the stated scenario and current evidence"),
        (r"\bimpossible to breach\b", "resistant to the stated threat within current evidence"),
    ]
    out = text
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.I)
    return out


def normalize_blueprint_for_gate(
    bp: Blueprint,
    source_text: str = "",
    profile: SourceProfile | None = None,
) -> Blueprint:
    """Deterministic, content-conservative pre-gate normalizer.

    It fixes channel leakage and reserved-unit structure without inventing new
    technical mechanisms. Source-supported core is never rewritten.
    """
    out = bp.model_copy(deep=True)

    # Move obvious ISCARB scaffolding out of core. Technical contemporary terms
    # are moved only when they are demonstrably unsupported by P1/profile, and
    # are then labeled hypothetical rather than asserted as fact.
    for unit in out.units:
        kept: list[str] = []
        for bullet in unit.core_content:
            pedagogy_hits = [t for t in PEDAGOGY_ONLY_TERMS if _phrase_present(bullet, t) and not _term_supported(t, source_text, profile)]
            tech_hits = [t for t in TECHNICAL_WATCHED_TERMS if _phrase_present(bullet, t) and not _term_supported(t, source_text, profile)]
            if pedagogy_hits and len(unit.pedagogy_content) < 8:
                unit.pedagogy_content.append(bullet)
                continue
            if tech_hits and len(unit.enrichment_content) < 6:
                unit.enrichment_content.append("HYPOTHETICAL DESIGN EXPLORATION — " + bullet)
                if "HYPOTHETICAL — no external factual claim; design exploration only." not in unit.enrichment_basis:
                    unit.enrichment_basis.append("HYPOTHETICAL — no external factual claim; design exploration only.")
                unit.contextual_enrichment = True
                continue
            kept.append(bullet)
        unit.core_content = kept
        if not unit.core_content:
            unit.source_anchor = ""

    # Unit 10 must visibly implement the four-quadrant MARIS information ledger.
    u10 = out.units[9]
    u10_blob = " ".join([*u10.pedagogy_content, u10.student_action, u10.takeaway])
    if not _ledger_semantically_complete(u10_blob):
        required = [
            "KNOWN — list only source-supported facts already established in the lecture.",
            "UNKNOWN — list unresolved facts or uncertainties that remain after analysis.",
            "DECISION-SENSITIVE UNKNOWN — identify the uncertainty that could change the engineering decision.",
            "WHAT WE MONITOR — specify the evidence, observation, or telemetry that would reduce that uncertainty.",
        ]
        existing = " ".join(u10.pedagogy_content).lower()
        for item in required:
            label = item.split(" — ", 1)[0].lower()
            if label not in existing and len(u10.pedagogy_content) < 8:
                u10.pedagogy_content.append(item)

    # Unit 20: bound non-core verdict language and make residual uncertainty explicit.
    u20 = out.units[19]
    u20.pedagogy_content = [_bound_text(x) for x in u20.pedagogy_content]
    u20.student_action = _bound_text(u20.student_action)
    u20.takeaway = _bound_text(u20.takeaway)
    u20.evidence = _bound_text(u20.evidence)
    joined20 = " ".join([*u20.pedagogy_content, u20.takeaway, u20.evidence]).lower()
    if not any(x in joined20 for x in ["residual uncertainty", "within the stated", "subject to", "current evidence"]):
        if len(u20.pedagogy_content) < 8:
            u20.pedagogy_content.append(
                "RESIDUAL UNCERTAINTY — the final authorization is bounded by the stated scenario, current evidence, and explicitly unresolved uncertainty."
            )

    note = "Gate v8 deterministic normalization applied: provenance channels, Unit 10 information ledger, and bounded Unit 20 assurance."
    if note not in out.release_notes:
        out.release_notes.append(note)
    return out
