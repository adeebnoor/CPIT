from __future__ import annotations

"""Source-verbatim definition extraction for the ISCARB knowledge anchor.

The extractor is deliberately conservative. It only returns text found in P1's
local extracted corpus and never asks an LLM to invent or paraphrase a
"definition". If no defensible definition is found, the term is omitted.
"""

import re
from pathlib import Path
from typing import Any

from .source_text import extract_source_text
from .storage import upload_path

_PAGE_RE = re.compile(r"^--- Page\s+(\d+)\s+---$", re.I)
_BULLET_RE = re.compile(r"^[\s\u2022\u25aa\u25cf\uf0b2\uf0a7\u00b7\-–—]+")
_TERM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 /&+()'’.-]{1,62}$")
_STRONG_DEFINITION_STARTS = (
    "the probability ", "the ability ", "the extent ", "a judgment ",
    "an assessment ", "reflects ", "refers to ", "is the ", "is a ",
    "are approaches ", "are methods ", "a process ", "a system ",
)
_DEFINITION_STARTS = _STRONG_DEFINITION_STARTS + (
    "provides ", "provide ", "keep ", "the process ", "the system ",
)
_TERM_VERBS = re.compile(r"\b(is|are|was|were|covers|fails|failed|should|has|have|can|will|may|must|means|depends|includes|include)\b", re.I)
_CACHE: dict[str, tuple[float, list[dict[str, Any]]]] = {}


def _clean_line(value: str) -> str:
    value = _BULLET_RE.sub("", str(value or "").strip())
    return " ".join(value.split())


def _candidate_names(job: Any) -> list[str]:
    profile = getattr(job, "source_profile", None)
    names: list[str] = []
    if profile is not None:
        for item in getattr(profile, "coverage_items", []) or []:
            label = _clean_line(getattr(item, "label", ""))
            if label and label.lower() not in {x.lower() for x in names}:
                names.append(label)
        for item in getattr(profile, "topic_families", []) or []:
            label = _clean_line(getattr(item, "name", ""))
            if label and label.lower() not in {x.lower() for x in names}:
                names.append(label)
    return names[:80]


def _pages(text: str) -> list[tuple[int, list[str]]]:
    pages: list[tuple[int, list[str]]] = []
    number = 1
    lines: list[str] = []
    for raw in str(text or "").splitlines():
        marker = _PAGE_RE.match(raw.strip())
        if marker:
            if lines:
                pages.append((number, lines))
            number = int(marker.group(1))
            lines = []
            continue
        line = _clean_line(raw)
        if line:
            lines.append(line)
    if lines:
        pages.append((number, lines))
    return pages


def _looks_like_term(line: str) -> bool:
    if not _TERM_RE.match(line):
        return False
    words = line.split()
    if not 1 <= len(words) <= 5:
        return False
    low = line.lower()
    if low.startswith(("chapter ", "page ", "key points", "topics covered")):
        return False
    if re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", line):
        return False
    if line.endswith((".", ";", ":", ",")) or low.endswith((" of", " the", " and", " or", " to")):
        return False
    first_alpha = next((c for c in line if c.isalpha()), "")
    if first_alpha and not first_alpha.isupper():
        return False
    if _TERM_VERBS.search(line):
        return False
    return True


def _looks_like_definition(text: str) -> bool:
    low = text.lower().strip()
    if len(text.split()) < 6 or len(text) > 620:
        return False
    if low.startswith(_DEFINITION_STARTS):
        return True
    return bool(re.search(r"\b(is|are|means|reflects|refers to|defined as|probability|judgment|ability|extent)\b", low))


def _definition_strength(text: str) -> int:
    low = text.lower().strip()
    if low.startswith(_STRONG_DEFINITION_STARTS):
        return 0
    if low.startswith(("provides ", "provide ", "keep ")):
        return 1
    return 2


def _join_definition(lines: list[str], start: int) -> str:
    if start < len(lines) and _looks_like_term(lines[start]) and not _looks_like_definition(lines[start]):
        return ""
    parts: list[str] = []
    for idx in range(start, min(len(lines), start + 5)):
        part = lines[idx]
        if idx > start and _looks_like_term(part) and not part.endswith((".", ";", ":")):
            break
        parts.append(part)
        joined = " ".join(parts)
        if joined.endswith((".", ";")) and len(joined.split()) >= 7:
            break
        if len(joined) > 520:
            break
    return " ".join(parts).strip()[:620]


def _priority(term: str, wanted: list[str]) -> int:
    low = term.lower()
    for item in wanted:
        w = item.lower()
        if low == w or low in w or w in low:
            return 0
    return 1


def extract_definitions_from_text(
    text: str,
    candidate_names: list[str] | None = None,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Return source-verbatim term/definition pairs with page provenance."""
    wanted = [x.strip() for x in (candidate_names or []) if x and x.strip()]
    found: list[dict[str, Any]] = []
    seen: set[str] = set()

    for page_no, lines in _pages(text):
        for i, line in enumerate(lines):
            same = re.match(r"^(.{2,60}?)(?:\s*[:—–]\s+)(.{20,620})$", line)
            if same:
                term, definition = _clean_line(same.group(1)), _clean_line(same.group(2))
                key = term.lower()
                if _looks_like_term(term) and _looks_like_definition(definition) and key not in seen:
                    seen.add(key)
                    found.append({"term": term, "definition": definition, "source_anchor": f"[P1] Page {page_no}", "page": page_no, "verbatim": True, "strength": _definition_strength(definition), "priority": _priority(term, wanted)})
                continue

            if not _looks_like_term(line) or i + 1 >= len(lines):
                continue
            definition = _join_definition(lines, i + 1)
            if not _looks_like_definition(definition):
                continue
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            found.append({"term": line, "definition": definition, "source_anchor": f"[P1] Page {page_no}", "page": page_no, "verbatim": True, "strength": _definition_strength(definition), "priority": _priority(line, wanted)})

    # Explicit source definitions outrank descriptive headings. Source-profile
    # relevance breaks ties, then original source order is preserved.
    found.sort(key=lambda item: (int(item.get("strength", 2)), int(item.get("priority", 1)), int(item.get("page", 9999))))
    return [{k: v for k, v in item.items() if k not in {"priority", "strength"}} for item in found[: max(0, limit)]]


def extract_job_definitions(job: Any, limit: int = 12) -> list[dict[str, Any]]:
    """Extract and cache definitions from the job's local P1 upload."""
    filename = str(getattr(job, "filename", "") or "")
    if not filename:
        return []
    path: Path = upload_path(str(getattr(job, "id", "")), filename)
    if not path.exists() or not path.is_file():
        return []
    try:
        stamp = path.stat().st_mtime
    except OSError:
        return []
    cached = _CACHE.get(str(getattr(job, "id", "")))
    if cached and cached[0] == stamp:
        return cached[1][:limit]
    corpus = extract_source_text(path)
    if not corpus.strip():
        return []
    definitions = extract_definitions_from_text(corpus, _candidate_names(job), limit=max(limit, 12))
    _CACHE[str(getattr(job, "id", ""))] = (stamp, definitions)
    return definitions[:limit]
