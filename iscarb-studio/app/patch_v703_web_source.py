from __future__ import annotations

"""ISCARB v7.0.4 web-source fidelity repair.

Old university lecture pages are often semantically structured by short headings
followed by lists/definition lists rather than modern h1-h6 markup. A flat local
profile can therefore classify the heading as major and its essential members as
supporting; the 10 teaching slots then teach the heading while silently dropping
its members (CIA dimensions, threat types, risk-assessment steps, etc.).

This patch never invents subject matter and never weakens Gate v15. For public
web P1 only it:
- removes extraction metadata from the teaching profile,
- restores a real lecture title,
- carries later source blocks beyond the legacy 80-item inventory ceiling,
- folds supporting members into a preceding heading-only major checkpoint,
- derives the opening crisis from real P1 families,
- keeps learner-visible labels free of width-cut sentence fragments.
"""

import re

from . import main as engine
from . import source_profile_fallback as profile_mod
from . import start_v440 as base
from .models import CoverageItem, TopicFamily

_PATCHED = False
WEB_HEADING_PREFIX = "SOURCE HEADING: "
MAX_WEB_PROFILE_ITEMS = 160
MAX_CHILDREN_PER_HEADING = 10
_METADATA_PREFIXES = ("SOURCE URL:", "SOURCE TITLE:", "SOURCE TYPE:")
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
    if text.startswith(WEB_HEADING_PREFIX):
        text = text[len(WEB_HEADING_PREFIX):].strip()
    text = re.sub(r"\s*\(part \d+\)$", "", text, flags=re.I)
    if len(text) > max_chars:
        candidates = [x.strip() for x in re.split(r"(?<=[.!?])\s+|\s+[—–-]\s+|:\s+", text) if x.strip()]
        if candidates and 2 <= len(candidates[0].split()) <= 14:
            text = candidates[0]
        else:
            text = " ".join(text.split()[:12])
    return _strip_dangling(text) or "Source checkpoint"


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _row_number(row) -> int:
    match = re.search(r"(\d+)$", str(getattr(row, "id", "") or ""))
    return int(match.group(1)) if match else 10_000


def _is_web_profile(profile, bundle=None) -> bool:
    rows = getattr(profile, "coverage_items", []) or []
    if any(str(getattr(r, "label", "")).startswith("SOURCE TYPE: public web page") for r in rows):
        return True
    if bundle is not None:
        try:
            text = profile_mod.extract_source_text(bundle.primary.path, limit=5000)
            return "SOURCE TYPE: public web page" in text
        except Exception:
            return False
    return False


def _expanded_web_rows(bundle, existing_ids: set[str]) -> list[CoverageItem]:
    """Recover web blocks after the legacy 80-item profile boundary.

    The materialized TXT still contains the full public page. We mirror the
    deterministic section inventory for items 81..160, using only P1 text and
    the same local knowledge/importance classifiers as the base profiler.
    """
    text = profile_mod.extract_source_text(bundle.primary.path, limit=500_000)
    if "SOURCE TYPE: public web page" not in text:
        return []
    paras = [profile_mod._clean(x, 520) for x in re.split(r"\n{1,}", text) if profile_mod._clean(x, 520)]
    out: list[CoverageItem] = []
    for i, para in enumerate(paras[:MAX_WEB_PROFILE_ITEMS], 1):
        if re.match(r"^recommended\b", para, flags=re.I):
            break
        cid = f"P1-S{i:02d}"
        if cid in existing_ids:
            continue
        raw = para[len(WEB_HEADING_PREFIX):].strip() if para.startswith(WEB_HEADING_PREFIX) else para
        words = raw.split()
        if not words:
            continue
        label = _display_label(" ".join(words[:12]), 110)
        lines = profile_mod._meaningful_lines(raw)
        importance = profile_mod._page_importance(label, lines, i)
        out.append(CoverageItem(
            id=cid,
            label=label,
            knowledge_type=profile_mod._knowledge_type(raw),
            importance=importance,
            source_anchor=f"[P1] SECTION {i}",
            why_important=raw,
        ))
    return out


def _normalize_web_profile(profile, bundle):
    if not _is_web_profile(profile, bundle):
        return profile

    rows = list(getattr(profile, "coverage_items", []) or [])
    existing = {str(getattr(r, "id", "")) for r in rows}
    rows.extend(_expanded_web_rows(bundle, existing))
    rows.sort(key=_row_number)

    # Extraction provenance belongs in the manifest, not the teaching scope.
    rows = [
        row for row in rows
        if not str(getattr(row, "label", "") or "").startswith(_METADATA_PREFIXES)
    ]
    for row in rows:
        row.label = _display_label(getattr(row, "label", ""), 110)
        body = str(getattr(row, "why_important", "") or "")
        if body.startswith(WEB_HEADING_PREFIX):
            row.why_important = body[len(WEB_HEADING_PREFIX):].strip()

    # A heading-only major checkpoint owns the supporting list immediately below
    # it until the next major checkpoint. This preserves CIA, threat taxonomies,
    # risk-assessment stages, guidelines, and similar source-native enumerations
    # without inflating the 10 teaching slots or upgrading arbitrary details.
    for i, row in enumerate(rows):
        if getattr(row, "importance", "") != "major":
            continue
        label = str(getattr(row, "label", "") or "").strip()
        body = str(getattr(row, "why_important", "") or "").strip()
        if not label or _norm(label) != _norm(body):
            continue
        children: list[str] = []
        for nxt in rows[i + 1:]:
            if getattr(nxt, "importance", "") == "major":
                break
            child = str(getattr(nxt, "why_important", "") or "").strip()
            if not child or child.startswith(_METADATA_PREFIXES):
                continue
            if _norm(child) == _norm(label):
                continue
            children.append(child)
            if len(children) >= MAX_CHILDREN_PER_HEADING:
                break
        if children:
            row.why_important = " · ".join([label, *children])

    profile.coverage_items = rows[:MAX_WEB_PROFILE_ITEMS]

    families = list(getattr(profile, "topic_families", []) or [])
    # Add late heading-only major rows as source families when the legacy cap hid
    # them, while avoiding body-sentence pseudo-families.
    seen = {_norm(getattr(f, "name", "")) for f in families}
    for row in rows:
        label = str(getattr(row, "label", "") or "")
        original_body = str(getattr(row, "why_important", "") or "")
        first_piece = original_body.split(" · ", 1)[0].strip()
        if (
            getattr(row, "importance", "") == "major"
            and _norm(label) == _norm(first_piece)
            and 2 <= len(label.split()) <= 11
            and _norm(label) not in seen
        ):
            families.append(TopicFamily(
                name=_display_label(label, 64),
                source_anchor=str(getattr(row, "source_anchor", "") or "[P1]"),
                why_important=_display_label(label, 120),
            ))
            seen.add(_norm(label))
    profile.topic_families = families[:40]
    profile.in_scope_families = [getattr(f, "name", "") for f in profile.topic_families]

    # Never title a lecture after extraction metadata or a URL. Prefer the first
    # real source family, which is author-visible and already source-anchored.
    title = str(getattr(profile, "lecture_title", "") or "").strip()
    if title.startswith(_METADATA_PREFIXES) or title.lower().startswith(("http://", "https://", "source url")):
        candidate = next((getattr(f, "name", "") for f in profile.topic_families if getattr(f, "name", "")), "Primary lecture")
        profile.lecture_title = _display_label(candidate, 72)
        focus = str(getattr(profile, "weekly_focus", "") or "")
        if focus.startswith(_METADATA_PREFIXES) or "http" in focus.lower():
            profile.weekly_focus = profile.lecture_title

    return profile


def _structured_web_chunks(path):
    """Group modern web lectures when explicit heading markers are available."""
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
        if para.startswith(_METADATA_PREFIXES):
            continue
        if para.startswith(WEB_HEADING_PREFIX):
            close()
            current_label = _display_label(para[len(WEB_HEADING_PREFIX):])
            continue
        current_body.append(para)
    close()

    out = []
    for label, body in sections[:MAX_WEB_PROFILE_ITEMS]:
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
        key = _norm(clean)
        if not clean or not key or key in seen or clean.startswith(_METADATA_PREFIXES):
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
        if len(raw) > limit:
            result = _strip_dangling(result)
        return result

    def doc_chunks(path):
        structured = _structured_web_chunks(path)
        return structured if structured is not None else previous_doc_chunks(path)

    profile_mod._clean = clean
    profile_mod._doc_chunks = doc_chunks

    previous_profile_builder = engine.build_deterministic_source_profile

    def build_profile(bundle, reason: str = ""):
        profile = previous_profile_builder(bundle, reason)
        return _normalize_web_profile(profile, bundle)

    engine.build_deterministic_source_profile = build_profile
    base.engine.build_deterministic_source_profile = build_profile

    previous_draft = engine._source_preserving_draft

    def source_preserving_draft(profile, bundle):
        profile = _normalize_web_profile(profile, bundle)
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
            "web_source_structure": "v7.0.4",
            "html_headings_preserved": True,
            "legacy_html_definition_lists": True,
            "web_profile_item_ceiling": MAX_WEB_PROFILE_ITEMS,
            "source_heading_members_preserved": True,
            "source_specific_crisis": True,
            "source_fragment_gate_weakened": False,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
