from __future__ import annotations

"""ISCARB v7.0.3 web-source structure + source-specific crisis repair.

Public HTML lectures used to be flattened into anonymous paragraphs. The local
fallback profiler then promoted the first N words of prose into checkpoint labels,
which could end on "and", "or", "in", etc. Gate v15 correctly blocked those
fragments. This patch keeps the gate strict: it restores section structure from
the heading markers written by url_source.py, sanitizes only display metadata,
and derives the opening engineering crisis from actual P1 topic families.
"""

import re

from . import main as engine
from . import source_profile_fallback as profile_mod
from . import start_v440 as base

_PATCHED = False
WEB_HEADING_PREFIX = "SOURCE HEADING: "
_DANGLING = re.compile(
    r"\b(of|for|to|the|a|an|and|or|but|in|on|at|by|with|from|that|which|is|are|"
    r"was|were|be|been|as|it|its|their|this|these|those|than|then|so|if|when)$",
    re.IGNORECASE,
)
_RISK_TERMS = re.compile(r"\b(risk|failure|threat|hazard|attack|loss|vulnerab|error|anomal|constraint)\w*\b", re.I)
_DESIGN_TERMS = re.compile(r"\b(design|architecture|strategy|policy|control|mechanism|implementation|decomposition|routing|model|evaluation)\w*\b", re.I)


def _strip_dangling(text: str, minimum_words: int = 3) -> str:
    words = str(text or "").strip(" ,;:-").split()
    while len(words) > minimum_words and _DANGLING.search(words[-1].rstrip(" ,;:-")):
        words.pop()
    return " ".join(words).rstrip(" ,;:-")


def _display_label(value: str, max_chars: int = 92) -> str:
    text = " ".join(str(value or "").split()).strip(" -•·:;,.")
    text = re.sub(r"\s*\(part \d+\)$", "", text, flags=re.I)
    if len(text) > max_chars:
        # Prefer an author-supplied clause boundary. A raw width cut is a last resort.
        candidates = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\s+[—–-]\s+|:\s+", text) if x.strip()]
        if candidates and 2 <= len(candidates[0].split()) <= 14:
            text = candidates[0]
        else:
            words = text.split()[:12]
            text = " ".join(words)
    return _strip_dangling(text) or "Source checkpoint"


def _structured_web_chunks(path):
    """Group a materialized web lecture by its original h1-h4 structure."""
    text = profile_mod.extract_source_text(path, limit=500_000)
    if "SOURCE TYPE: public web page" not in text or WEB_HEADING_PREFIX not in text:
        return None

    paras = [profile_mod._clean(x, 4000) for x in re.split(r"\n{1,}", text) if profile_mod._clean(x, 4000)]
    source_title = next((p.split(":", 1)[1].strip() for p in paras if p.startswith("SOURCE TITLE:") and ":" in p), "Web lecture")
    sections: list[tuple[str, list[str]]] = []
    current_label = _display_label(source_title)
    current_body: list[str] = []

    def close() -> None:
        nonlocal current_body
        if current_body:
            sections.append((current_label, current_body))
        current_body = []

    for para in paras:
        if para.startswith(("SOURCE URL:", "SOURCE TITLE:", "SOURCE TYPE:")):
            continue
        if para.startswith(WEB_HEADING_PREFIX):
            close()
            current_label = _display_label(para[len(WEB_HEADING_PREFIX):])
            continue
        current_body.append(para)
    close()

    out = []
    for label, body in sections[:80]:
        excerpt = " · ".join(dict.fromkeys(x for x in body if x))
        if not excerpt:
            continue
        if len(excerpt) > profile_mod.MAX_EXCERPT_CHARS:
            clipped = excerpt[:profile_mod.MAX_EXCERPT_CHARS]
            excerpt = clipped.rsplit(" · ", 1)[0] if " · " in clipped else clipped.rsplit(" ", 1)[0]
        idx = len(out) + 1
        out.append(profile_mod.Chunk(idx, label, excerpt, (idx,)))
    return out or None


def _profile_labels(profile) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        clean = _display_label(value, 88)
        key = re.sub(r"[^a-z0-9]+", " ", clean.lower()).strip()
        if not key or key in seen:
            return
        seen.add(key)
        labels.append(clean)

    for family in getattr(profile, "topic_families", []) or []:
        add(getattr(family, "name", ""))
    for row in getattr(profile, "coverage_items", []) or []:
        if getattr(row, "importance", "") == "major":
            add(getattr(row, "label", ""))
    return labels


def _source_specific_crisis(profile, blueprint) -> str:
    labels = _profile_labels(profile)
    title = _display_label(getattr(profile, "lecture_title", "") or getattr(blueprint, "lecture_title", "Primary lecture"), 72)
    risk = next((x for x in labels if _RISK_TERMS.search(x)), None)
    design = next((x for x in labels if _DESIGN_TERMS.search(x) and x != risk), None)

    if risk and design:
        return (
            f"The {title} decision is blocked by {risk}: before committing to {design}, "
            "the team must choose a source-backed response, make its trade-off explicit, "
            "and name the evidence that would reverse the choice."
        )
    if len(labels) >= 3:
        return (
            f"The {title} decision spans {labels[0]}, {labels[1]}, and {labels[2]}. "
            "The team must decide which source-backed mechanism governs the case, "
            "what trade-off follows, and what evidence would reverse that decision."
        )
    if labels:
        return (
            f"The {title} decision turns on {labels[0]}. The team must identify the "
            "source-backed mechanism that supports the choice and the missing evidence "
            "that would force a different decision."
        )
    return (
        f"The {title} decision cannot be released yet: the team must identify the "
        "source-backed mechanism, its trade-off, and the evidence that could reverse it."
    )


def _repair_display_fragments(blueprint, profile):
    """Repair only learner-visible source labels; never rewrite source payload."""
    by_id = {getattr(row, "id", ""): row for row in getattr(profile, "coverage_items", []) or []}
    for unit in getattr(blueprint, "units", []) or []:
        if not 6 <= getattr(unit, "number", 0) <= 15:
            continue
        values = [unit.title, unit.takeaway]
        if not any(_DANGLING.search(str(v or "").strip().rstrip("?.!;:")) for v in values):
            continue
        ids = re.findall(r"P1-[A-Z]\d+", str(getattr(unit, "evidence", "") or ""), flags=re.I)
        labels = [_display_label(getattr(by_id.get(i), "label", "")) for i in ids if i in by_id]
        labels = list(dict.fromkeys(x for x in labels if x and x != "Source checkpoint"))
        if labels:
            unit.title = " / ".join(labels[:2])
            unit.takeaway = "Source checkpoint(s) covered: " + "; ".join(labels[:4])
        else:
            unit.title = _strip_dangling(unit.title)
            unit.takeaway = _strip_dangling(unit.takeaway)
    return blueprint


def apply_v703_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    previous_clean = profile_mod._clean
    previous_doc_chunks = profile_mod._doc_chunks

    def clean(text: str, limit: int = 160) -> str:
        raw = re.sub(r"\s+", " ", str(text or "")).strip()
        result = previous_clean(text, limit)
        # Only width-driven clipping gets this repair. Complete source sentences
        # remain byte-for-byte in why_important/core content.
        if len(raw) > limit:
            result = _strip_dangling(result)
        return result

    def doc_chunks(path):
        structured = _structured_web_chunks(path)
        return structured if structured is not None else previous_doc_chunks(path)

    profile_mod._clean = clean
    profile_mod._doc_chunks = doc_chunks

    previous_draft = engine._source_preserving_draft

    def source_preserving_draft(profile, bundle):
        blueprint = previous_draft(profile, bundle)
        blueprint = _repair_display_fragments(blueprint, profile)
        blueprint.central_engineering_crisis = _source_specific_crisis(profile, blueprint)
        return engine.fit_presenter_text(blueprint)

    engine._source_preserving_draft = source_preserving_draft
    base.engine._source_preserving_draft = source_preserving_draft

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "web_source_structure": "v7.0.3",
            "html_headings_preserved": True,
            "source_specific_crisis": True,
            "source_fragment_gate_weakened": False,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
