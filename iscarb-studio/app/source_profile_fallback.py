from __future__ import annotations

"""Deterministic P1 source profiling used only when the AI profiling call is unavailable.

The fallback is deliberately conservative: it does not invent subject matter. It
extracts page/slide/section headings and short source excerpts from the PRIMARY
file and turns those into a coverage contract. Gemini still receives the full
source during blueprint generation; this module only prevents the whole compile
from dying before generation when a profiling-model quota is exhausted.
"""

import re
from pathlib import Path

from .models import CoverageItem, SourceProfile, TopicFamily
from .source_bundle import SourceBundle
from .source_text import extract_source_text


_FURNITURE = {
    "software engineering", "chapter", "contents", "copyright", "all rights reserved",
    "ian sommerville", "page", "slide", "learning objectives", "objectives",
}


def _clean(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip(" \t\r\n-|•·")
    return text[:limit].rstrip(" ,;:-")


def _meaningful_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in str(text or "").splitlines():
        line = _clean(raw, 180)
        if len(line) < 3:
            continue
        low = line.lower()
        if low.isdigit() or re.fullmatch(r"\d+[./-]?\d*", low):
            continue
        if any(low == x for x in _FURNITURE):
            continue
        if line not in lines:
            lines.append(line)
    return lines


def _knowledge_type(text: str) -> str:
    low = text.lower()
    if any(x in low for x in ("algorithm", "pseudo", "procedure", "steps:")):
        return "ALGORITHM"
    if any(x in low for x in ("equation", "formula", "probability", "pofod", "rocof", "mtbf", "mttf", "=", "%")):
        return "EQUATION"
    if any(x in low for x in ("architecture", "layer", "component", "subsystem", "client-server", "distributed")):
        return "ARCHITECTURE"
    if any(x in low for x in ("process", "activities", "workflow", "review", "inspection", "testing")):
        return "PROCESS"
    if any(x in low for x in ("protocol", "request", "response", "message", "transaction")):
        return "PROTOCOL"
    if any(x in low for x in ("trade-off", "tradeoff", "cost", "versus", " vs ", "advantage", "disadvantage")):
        return "TRADE_OFF"
    if any(x in low for x in ("example", "case study", "scenario")):
        return "EXAMPLE"
    if any(x in low for x in ("principle", "guideline", "rule", "design for")):
        return "DESIGN_PRINCIPLE"
    if any(x in low for x in ("failure", "fault", "behavior", "behaviour", "state", "recovery")):
        return "SYSTEM_BEHAVIOR"
    return "CONCEPT"


def _is_furniture_line(line: str) -> bool:
    low = _clean(line, 180).lower()
    if not low:
        return True
    exact = {
        "cpit-455 software engineering (ii)", "advanced software engineering",
        "advanced softwre engineering", "today lecture topic", "today lecture topic – part 2",
        "today lecture topic - part 2", "the cimt compass", "where academic meets business reality",
        "concept implementation measurement trend", "measurement implementation reality",
    }
    if low in exact:
        return True
    if any(low.startswith(x) for x in ("adeeb noor", "it department", "faculty of computing", "king abdulaziz university", "fall 2025")):
        return True
    return False


def _choose_label(lines: list[str], page_no: int) -> str:
    clean = [x for x in lines if not _is_furniture_line(x)]
    # Numbered chapter sections are the strongest deterministic checkpoint.
    for x in clean[:12]:
        if re.match(r"^\d{1,2}\.\d+(?:\.\d+)?\b", x):
            return _clean(x, 120)
    # Prefer compact title-like lines over body sentences.
    for x in clean[:12]:
        if 3 <= len(x.split()) <= 11 and len(x) <= 100:
            return _clean(x, 120)
    return _clean(clean[0] if clean else f"Primary source page {page_no}", 120)



def _page_importance(label: str, lines: list[str], page_no: int) -> str:
    low = label.lower()
    support_markers = (
        "class", "take-home", "to master", "your challenge", "assignment",
        "today lecture topic", "the big picture", "big picture", "cimt compass",
        "setting the stage", "our roadmap", "the core idea", "the big why",
        "key clo", "availability: system is ready", "to master today's lesson",
        "ai era", "ai revolution", "aligning with industry trends", "keeping up with trends",
        "example", "ex;", "remember", "cautionary tale", "how to show this",
        "topics covered", "key points",
    )
    slide_no = _embedded_slide_number(label)
    if page_no == 1 or slide_no == 1 or any(m in low for m in support_markers):
        return "supporting"
    blob = " ".join(lines[:18]).lower()
    if slide_no and len(blob.split()) < 12:
        return "supporting"
    major_markers = (
        "definition", "requirements", "architecture", "process", "model", "metrics",
        "measurement", "testing", "assurance", "design", "fault", "failure",
        "security", "reliability", "dependability", "resilience", "safety",
        "component", "composition", "reuse", "distributed", "client", "server",
        "middleware", "saas", "service-oriented", "risk assessment", "formal methods",
        "redundancy", "diversity", "sociotechnical", "programming for",
    )
    if re.match(r"^\d{1,2}\.\d+(?:\.\d+)?\b", label) or any(m in blob for m in major_markers):
        return "major"
    content_lines = [x for x in lines if not _is_furniture_line(x)]
    return "major" if len(content_lines) >= 4 and len(" ".join(content_lines).split()) >= 28 else "supporting"


def _pdf_chunks(path: Path) -> list[tuple[int, str, str]]:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    out: list[tuple[int, str, str]] = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        lines = _meaningful_lines(text)
        if not lines:
            continue
        label = _choose_label(lines, i)
        excerpt = _clean(" · ".join(x for x in lines[:8] if not _is_furniture_line(x)), 720)
        out.append((i, label, excerpt))
    return out


def _pptx_chunks(path: Path) -> list[tuple[int, str, str]]:
    from pptx import Presentation
    prs = Presentation(str(path))
    out: list[tuple[int, str, str]] = []
    for i, slide in enumerate(prs.slides, 1):
        raw = "\n".join(sh.text for sh in slide.shapes if hasattr(sh, "text") and sh.text)
        lines = _meaningful_lines(raw)
        if not lines:
            continue
        out.append((i, _choose_label(lines, i), _clean(" · ".join(x for x in lines[:8] if not _is_furniture_line(x)), 720)))
    return out



def _embedded_slide_number(text: str) -> int | None:
    m = re.match(r"^\s*SLIDE\s+(\d+)\s*:", str(text or ""), flags=re.I)
    return int(m.group(1)) if m else None


def _declared_slide_count(text: str) -> int | None:
    """Return the player-declared deck size before host recommendation chrome."""
    head = re.split(r"\bRecommended\b", str(text or ""), maxsplit=1, flags=re.I)[0]
    for pattern in (r"\b1\s*/\s*(\d{1,4})\b", r"\b(\d{1,4})\s+slides\b"):
        m = re.search(pattern, head, flags=re.I)
        if m:
            value = int(m.group(1))
            if 2 <= value <= 500:
                return value
    return None


def _anchor_slides(anchor: str) -> set[int]:
    """Extract explicit P1 slide coordinates from source anchors."""
    found: set[int] = set()
    for m in re.finditer(r"\bSLIDES?\s+(\d+)(?:\s*[-–—]\s*(\d+))?", str(anchor or ""), flags=re.I):
        start = int(m.group(1)); end = int(m.group(2) or start)
        if end < start:
            start, end = end, start
        if end - start <= 200:
            found.update(range(start, end + 1))
    return found



def _doc_chunks(path: Path) -> list[tuple[int, str, str]]:
    # Public presentation pages may expose `SLIDE n:` labels in extracted
    # text. Respect the deck boundary and never ingest Recommended cards.
    text = extract_source_text(path, limit=500_000)
    declared_slides = _declared_slide_count(text)
    paras = [_clean(x, 520) for x in re.split(r"\n{1,}", text) if _clean(x, 520)]
    out: list[tuple[int, str, str]] = []
    for i, para in enumerate(paras[:200], 1):
        if re.match(r"^recommended\b", para, flags=re.I):
            break
        words = para.split()
        label = _clean(" ".join(words[:12]), 110)
        slide_no = _embedded_slide_number(label) or _embedded_slide_number(para)
        if declared_slides and slide_no and slide_no > declared_slides:
            continue
        out.append((i, label, para))
    return out[:80]


def _chunks(path: Path) -> tuple[str, list[tuple[int, str, str]]]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "PAGE", _pdf_chunks(path)
    if ext == ".pptx":
        return "SLIDE", _pptx_chunks(path)
    return "SECTION", _doc_chunks(path)


def _title_from(primary_name: str, chunks: list[tuple[int, str, str]]) -> str:
    stem = Path(primary_name).stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    # Prefer a plausible first source heading over a machine filename.
    if chunks:
        first = _clean(chunks[0][1], 120)
        if 5 <= len(first) <= 120 and not re.fullmatch(r"[A-Z0-9_. -]+", first):
            return first
    return stem or "Primary lecture"


def build_deterministic_source_profile(bundle: SourceBundle, reason: str = "AI profiler unavailable") -> SourceProfile:
    primary = bundle.primary
    coordinate, chunks = _chunks(primary.path)
    if not chunks:
        # Last-resort single source item. It is intentionally explicit rather than
        # pretending that a semantic profile exists when extraction yielded nothing.
        chunks = [(1, Path(primary.display_name).stem, "Primary source supplied by faculty")]

    # Preserve source order while suppressing exact duplicate headings caused by
    # recurring lecture furniture. We still keep a page-level coverage item for
    # every content-bearing source page/slide.
    families: list[TopicFamily] = []
    seen_family: set[str] = set()
    coverage: list[CoverageItem] = []
    for idx, label, excerpt in chunks[:80]:
        clean_label = _clean(label, 120) or f"Source {coordinate.title()} {idx}"
        embedded_slide = _embedded_slide_number(clean_label)
        anchor = f"[P1] SLIDE {embedded_slide}" if embedded_slide else f"[P1] {coordinate} {idx}"
        key = re.sub(r"[^a-z0-9]+", " ", clean_label.lower()).strip()
        source_lines = _meaningful_lines(excerpt.replace(" · ", "\n"))
        importance = _page_importance(clean_label, source_lines, idx)
        is_title_like = importance == "supporting"
        coverage.append(CoverageItem(
            id=f"P1-{coordinate[0]}{idx:02d}",
            label=clean_label,
            knowledge_type=_knowledge_type(excerpt),
            importance=importance,
            source_anchor=anchor,
            why_important=_clean(excerpt, 260),
        ))
        if key and key not in seen_family and not is_title_like:
            seen_family.add(key)
            families.append(TopicFamily(
                name=clean_label,
                source_anchor=anchor,
                why_important=_clean(excerpt, 260),
            ))

    if not families:
        first = coverage[0]
        families = [TopicFamily(name=first.label, source_anchor=first.source_anchor, why_important=first.why_important)]
        coverage[0].importance = "major"

    title = _title_from(primary.display_name, chunks)
    focus = _clean(bundle.lecture_focus, 260) or title
    warning = (
        "Source profile was built deterministically because the AI profiling call was unavailable: "
        + _clean(reason, 300)
        + ". The full primary source is still supplied to blueprint generation; RELEASE still requires normal gates."
    )
    return SourceProfile(
        lecture_title=title,
        course_or_level="Faculty-supplied lecture",
        weekly_focus=focus,
        topic_families=families[:40],
        coverage_items=coverage[:80],
        technical_boundaries=[
            "P1 remains the authority for technical claims and terminology.",
            "Deterministic fallback records source coordinates; it does not add external technical claims.",
        ],
        source_warnings=[warning],
        session_minutes=90,
        scope_fit="COMPRESS" if len([x for x in coverage if x.importance == "major"]) > 16 else "FIT",
        in_scope_families=[x.name for x in families[:40]],
        deferred_topics=[],
        source_conflicts=[],
        source_manifest=bundle.manifest_lines(),
    )



def reconcile_source_profile(ai_profile: SourceProfile, bundle: SourceBundle) -> SourceProfile:
    """Add only uncovered real source slides to the semantic P1 contract."""
    deterministic = build_deterministic_source_profile(bundle, "chapter-completeness reconciliation")
    existing = {re.sub(r"[^a-z0-9]+", " ", x.label.lower()).strip() for x in ai_profile.coverage_items}
    semantic_slides: set[int] = set()
    for row in ai_profile.coverage_items:
        semantic_slides.update(_anchor_slides(row.source_anchor))

    merged = list(ai_profile.coverage_items)
    for item in deterministic.coverage_items:
        if item.importance != "major":
            continue
        item_slides = _anchor_slides(item.source_anchor)
        if item_slides and item_slides.issubset(semantic_slides):
            continue
        key = re.sub(r"[^a-z0-9]+", " ", item.label.lower()).strip()
        if key and key not in existing:
            merged.append(item)
            existing.add(key)
            semantic_slides.update(item_slides)

    ai_profile.coverage_items = merged[:80]
    ai_profile.deferred_topics = []
    ai_profile.source_warnings = list(dict.fromkeys([
        *ai_profile.source_warnings,
        "Deterministic source-coordinate reconciliation excludes duplicate semantic slides and host-page recommendation cards from mandatory P1 coverage.",
    ]))[:20]
    return ai_profile
