from __future__ import annotations

import re

# Conservative lexical requirements for composite ETEC SLOs that are easy to
# overclaim from partial topic overlap. Each inner tuple is an OR-group; ALL
# groups must be represented in the weekly source for the SLO to be eligible.
# These do not replace semantic audit; they only prevent obvious over-alignment.
ATOMIC_SOURCE_REQUIREMENTS: dict[str, list[tuple[str, ...]]] = {
    "SLO3.1.2": [
        ("vulnerability", "vulnerabilities"),
        ("threat", "threats"),
        ("risk", "risks"),
    ],
    "SLO7.1.3": [
        ("use case", "use cases"),
        ("event flow", "event flows"),
        ("functional requirement", "functional requirements"),
    ],
    "SLO7.2.2": [
        ("acceptance test", "acceptance testing"),
        ("evaluate", "evaluation"),
    ],
    "SLO8.1.5": [
        ("version control",),
        ("project hosting",),
        ("deployment", "deployment services"),
    ],
    "SLO9.1.2": [
        ("validat",),
        ("client", "client-side"),
        ("server", "server-side"),
        ("cookie", "cookies"),
        ("javascript",),
    ],
    "SLO9.1.3": [
        ("server-side database", "server side database"),
        ("read", "reads"),
        ("modify", "modifies"),
    ],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def slo_source_atomicity_ok(slo: str, source_text: str) -> bool:
    requirements = ATOMIC_SOURCE_REQUIREMENTS.get(slo)
    if not requirements:
        return True
    hay = _normalize(source_text)
    if not hay:
        # If extraction fails, do not create a false negative; semantic audit remains.
        return True
    return all(any(term in hay for term in group) for group in requirements)


def unsupported_atomic_slos(slo_refs: list[str], source_text: str) -> list[str]:
    return [slo for slo in slo_refs if not slo_source_atomicity_ok(slo, source_text)]
