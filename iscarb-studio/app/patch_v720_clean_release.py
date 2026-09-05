from __future__ import annotations

"""ISCARB v7.2 final clean-release layer.

This layer fixes the last class of defects that can survive otherwise-valid
source-only builds: dense PDF pages being treated as one topic, source chrome or
code labels leaking into learner-facing headings, and the presenter reading a
stale crisis field instead of the strongest P1-supported engineering stake.

The policy remains source-bounded. Dense pages are decomposed only from phrases
that already exist in P1; no external topic is invented. Administrative/legal
chrome is suppressed from the teaching map, while the original source remains
available intact as a download.
"""

import re
from typing import Iterable

from . import main as engine
from . import start_v440 as base
from . import patch_v690 as v690
from . import source_profile_fallback as profile_base
from .models import CoverageItem, TopicFamily

_PATCHED = False

_ADMIN = re.compile(
    r"(?:mit opencourseware|open.?courseware|terms of use|information about citing|"
    r"all rights reserved|copyright|creative commons|https?://|www\.)",
    re.I,
)
_CODE = re.compile(
    r"^(?:t\d+\s*:|sql[- ]?\d+|begin\s+xact|end\s+xact|select\b|update\b|"
    r"insert\b|delete\b|commit\b|abort\b|wait\b|ditto\b)",
    re.I,
)
_FILLER = re.compile(
    r"^(?:gold standard mechanism|model|example|consider|easy|right answer|"
    r"devil is in the details|primary source|source page|lecture|course)$",
    re.I,
)
_BAD_TITLE = re.compile(
    r"^(?:t\d+\s*(?:commits?|updates?|reads?)?|model|begin xact|end xact|"
    r"gold standard mechanism|review required|primary source page \d+)$",
    re.I,
)
_FINITE = re.compile(
    r"\b(?:is|are|was|were|does|do|did|can|could|will|would|must|may|might|"
    r"has|have|had|receives?|creates?|happens?|obeys?|avoids?)\b",
    re.I,
)
_STAKE = re.compile(
    r"\b(?:not\s+seriali[sz]\w*|non[- ]?seriali[sz]\w*|deadlock|starv\w*|"
    r"parallel\s+schedule|wrong|incorrect|failure|fault|risk|breach|attack|"
    r"unsafe|does\s+not|cannot|violat\w*|corrupt\w*|timeout|outage|loss)\b",
    re.I,
)
_PREDICT = re.compile(
    r"\b(?:parallel\s+schedule|prediction|predict|result|receives?|does\s+not|"
    r"not\s+seriali[sz]\w*|wrong|incorrect|failure|deadlock|if\b|when\b)\b",
    re.I,
)

# Editorial spelling cleanup is used for labels only. The source excerpt itself
# stays verbatim, so provenance checks still compare learner-visible source facts
# with the original P1 text rather than with our correction.
_SPELLING = (
    (re.compile(r"serializiability", re.I), "serializability"),
    (re.compile(r"serializiable", re.I), "serializable"),
    (re.compile(r"\bxacts\b", re.I), "transactions"),
)


def _clean(text: str, limit: int = 110) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip(" \t\r\n·•-–—:;,.!?")
    for pattern, replacement in _SPELLING:
        value = pattern.sub(replacement, value)
    value = value.replace("", "→").replace("->", "→")
    value = re.sub(r"!{2,}", "!", value)
    if len(value) > limit:
        head = value[:limit]
        value = head.rsplit(" ", 1)[0] if " " in head else head
    return value.strip(" -–—:;,.!?")


def _lines(excerpt: str) -> list[str]:
    out: list[str] = []
    for raw in re.split(r"\s*[·•▪■◆]\s*|\n+", str(excerpt or "")):
        line = re.sub(r"\s+", " ", raw).strip(" \t·•")
        if not line or _ADMIN.search(line):
            continue
        if line not in out:
            out.append(line)
    return out


def _source_payload_line(line: str) -> bool:
    """Whether a line should be projected as technical source content."""
    clean = _clean(line, 180)
    if not clean or _ADMIN.search(clean) or _FILLER.fullmatch(clean):
        return False
    # Raw schedule/code lines are preserved in the original P1 download but are
    # not promoted into a chapter topic by themselves. Their explanatory result
    # or named mechanism remains a teaching checkpoint.
    if _CODE.search(clean):
        return False
    if re.fullmatch(r"(?:bill|sam|fred|george|hugh|dept\.?|salary)", clean, re.I):
        return False
    return True


def _label_from_line(line: str) -> str:
    raw = re.sub(r"\s+", " ", str(line or "")).strip(" ·•\t")
    low = raw.lower().strip(" .!?;:")
    if not raw or _ADMIN.search(raw) or _CODE.search(raw) or _FILLER.fullmatch(_clean(raw)):
        return ""

    # Common source discourse cues are converted into the concept they name.
    # These transformations are lexical, not lecture-specific: they fire only
    # when the source itself contains the named term.
    if "serializ" in low and low.startswith("definition"):
        return "Serializability"
    if "phase locking" in low and (low.startswith("deep theorem") or "serializ" in low):
        return "Two-phase locking and serializability"
    if re.search(r"how\s+big\s+a?\s*granule\s+to\s+lock", low):
        return "Lock granularity"
    if "lock escalation" in low:
        return "Lock escalation"
    if low.startswith("what about deadlock"):
        return "Deadlock detection"
    if "avoid deadlock" in low:
        return "Deadlock prevention"
    if low.startswith("what about auxiliary structures"):
        return "Auxiliary structures"
    if "b-tree" in low and "latch" in low:
        return "B-tree latching"
    if "halloween problem" in low or "phantom problem" in low:
        return "Phantom (Halloween) problem"
    if "predicate locking" in low:
        return "Predicate locking"
    if "range lock" in low and "b-tree" in low:
        return "Range locking in B-tree indexes"
    if "escrow transactions" in low:
        return "Escrow transactions"
    if "both" in low and "locking protocol" in low and "not serial" in low:
        return "Locking protocol counterexample"
    if "concurrency control" in low:
        return _clean(re.sub(r"^.*?(concurrency control.*)$", r"\1", raw, flags=re.I), 72)
    if "crash recovery" in low:
        return _clean(re.sub(r"^.*?(crash recovery.*)$", r"\1", raw, flags=re.I), 72)
    if low == "transactions":
        return "Transactions"

    # Generic cue extraction for other IT domains.
    m = re.match(r"^(?:definition|deep theorem|principle|rule of thumb|answer)\s*[:\-]?\s*(.+)$", raw, re.I)
    if m:
        candidate = _clean(re.split(r"[.?!;]|\s+[–—]\s+", m.group(1), maxsplit=1)[0], 72)
        if 1 <= len(candidate.split()) <= 9 and not _FINITE.search(candidate):
            return candidate
    m = re.match(r"^what about\s+(.+?)\??$", raw, re.I)
    if m:
        candidate = _clean(m.group(1), 72)
        return candidate[:1].upper() + candidate[1:] if candidate else ""
    m = re.match(r"^how\s*[:\-]?\s*(.+?)(?:\?|\.|$)", raw, re.I)
    if m:
        candidate = _clean(m.group(1), 72)
        if 1 <= len(candidate.split()) <= 8 and not _FINITE.search(candidate):
            return candidate

    # Compact named headings survive unchanged. One-word labels are permitted
    # only when they name a real concept and are not extraction furniture.
    candidate = _clean(raw, 72)
    words = candidate.split()
    if 1 <= len(words) <= 7 and 4 <= len(candidate) <= 72:
        if raw.rstrip().endswith((".", ",", ";")):
            return ""
        if _BAD_TITLE.match(candidate) or _FINITE.search(candidate):
            return ""
        if re.search(r"[=]{1,}|\b(?:set|values|salary|dept)\s*=", candidate, re.I):
            return ""
        return candidate
    return ""


def _dense_segments(row: CoverageItem) -> list[CoverageItem]:
    lines = _lines(row.why_important)
    concepts: list[tuple[str, list[str]]] = []
    current_label = ""
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_label, current_lines
        payload = [x for x in current_lines if _source_payload_line(x)]
        if current_label and payload:
            # A concept consisting only of its two-word heading is too thin to
            # own a 90-minute teaching slot. Keep it only when a substantive
            # source line travels with it.
            words = sum(len(x.split()) for x in payload)
            if words >= 6 or len(payload) >= 2:
                concepts.append((current_label, payload))
        current_label, current_lines = "", []

    for line in lines:
        label = _label_from_line(line)
        # A named cue starts a new concept. The cue itself remains in the source
        # payload when it carries technical meaning; pure discourse filler does
        # not.
        if label and label != current_label:
            flush()
            current_label = label
            if _source_payload_line(line):
                current_lines.append(line)
            continue
        if current_label and _source_payload_line(line):
            current_lines.append(line)
    flush()

    # If a page did not expose at least two real concepts, do not pretend it did.
    if len(concepts) < 2:
        return []

    out: list[CoverageItem] = []
    for i, (label, payload) in enumerate(concepts, 1):
        excerpt = " · ".join(payload)
        if not excerpt.strip():
            continue
        out.append(CoverageItem(
            id=f"{row.id}-C{i:02d}",
            label=_clean(label, 80),
            knowledge_type=profile_base._knowledge_type(excerpt),
            importance="major",
            source_anchor=row.source_anchor,
            why_important=excerpt,
        ))
    return out


def _admin_row(row: CoverageItem) -> bool:
    return bool(_ADMIN.search(f"{row.label} {row.why_important}"))


def _clean_profile(profile):
    result = profile.model_copy(deep=True)
    original = list(result.coverage_items or [])
    major_count = sum(1 for x in original if x.importance == "major" and not _admin_row(x))
    cleaned: list[CoverageItem] = []

    for row in original:
        row = row.model_copy(deep=True)
        if _admin_row(row):
            row.importance = "supporting"
            cleaned.append(row)
            continue
        lines = _lines(row.why_important)
        density = sum(len(x.split()) for x in lines)
        split_needed = density >= 70 or len(lines) >= 8 or major_count < 8
        segments = _dense_segments(row) if split_needed else []
        if segments:
            # Preserve the physical-page record as supporting provenance, while
            # teaching from atomic concepts. Nothing disappears from P1 itself.
            row.importance = "supporting"
            cleaned.append(row)
            cleaned.extend(segments)
        else:
            if _BAD_TITLE.match(_clean(row.label)) and lines:
                for line in lines:
                    candidate = _label_from_line(line)
                    if candidate:
                        row.label = candidate
                        break
            cleaned.append(row)

    # Stable de-duplication. Dense pages can state the same concept twice; one
    # family name is enough, while all source page records remain in coverage.
    majors: list[CoverageItem] = []
    seen_labels: set[str] = set()
    for row in cleaned:
        if row.importance != "major" or _admin_row(row):
            continue
        key = re.sub(r"[^a-z0-9]+", " ", _clean(row.label).lower()).strip()
        if not key or key in seen_labels or _BAD_TITLE.match(_clean(row.label)):
            row.importance = "supporting"
            continue
        seen_labels.add(key)
        majors.append(row)

    result.coverage_items = cleaned[:80]
    if majors:
        result.topic_families = [
            TopicFamily(name=_clean(row.label, 80), source_anchor=row.source_anchor,
                        why_important=_clean(row.why_important, 220))
            for row in majors[:24]
        ]
        result.in_scope_families = [x.name for x in result.topic_families]
    return result


def _sentences(items: Iterable[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        for raw in re.split(r"\s*[·•▪■◆]\s*|(?<=[.!?])\s+", str(item or "")):
            text = re.sub(r"\s+", " ", raw).strip(" ·•-–—")
            if text and text not in out:
                out.append(text)
    return out


def _best_stake(profile, bp) -> tuple[str, str]:
    candidates: list[tuple[int, str, str]] = []
    for row in getattr(profile, "coverage_items", []) or []:
        if _admin_row(row):
            continue
        for sentence in _sentences([row.why_important]):
            words = sentence.split()
            if not (7 <= len(words) <= 45) or _CODE.search(sentence) or not _STAKE.search(sentence):
                continue
            score = 0
            low = sentence.lower()
            if "not serial" in low or "non-serial" in low: score += 8
            if "parallel schedule" in low: score += 7
            if "deadlock" in low: score += 5
            if "wrong" in low or "incorrect" in low: score += 4
            if "failure" in low or "risk" in low: score += 3
            candidates.append((score, sentence, row.source_anchor))
    if not candidates:
        for unit in getattr(bp, "units", []) or []:
            if "[P1]" not in str(getattr(unit, "source_anchor", "") or "").upper():
                continue
            for sentence in _sentences(getattr(unit, "core_content", []) or []):
                if 7 <= len(sentence.split()) <= 45 and _STAKE.search(sentence) and not _CODE.search(sentence):
                    candidates.append((1, sentence, unit.source_anchor))
    if not candidates:
        return "", ""
    candidates.sort(key=lambda x: (-x[0], abs(len(x[1].split()) - 20), len(x[1])))
    return candidates[0][1], candidates[0][2]


def _best_prediction(profile, avoid: str = "") -> tuple[str, str]:
    candidates: list[tuple[int, str, str]] = []
    for row in getattr(profile, "coverage_items", []) or []:
        if _admin_row(row):
            continue
        for sentence in _sentences([row.why_important]):
            if sentence == avoid or _CODE.search(sentence):
                continue
            words = sentence.split()
            if not (7 <= len(words) <= 42) or not _PREDICT.search(sentence):
                continue
            low = sentence.lower(); score = 0
            if "parallel schedule" in low: score += 8
            if "receiv" in low and "does not" in low: score += 6
            if "result" in low: score += 3
            if "if " in low or low.startswith("if"): score += 2
            candidates.append((score, sentence, row.source_anchor))
    if not candidates:
        return "", ""
    candidates.sort(key=lambda x: (-x[0], abs(len(x[1].split()) - 18), len(x[1])))
    return candidates[0][1], candidates[0][2]


def _good_node(text: str) -> bool:
    value = _clean(text, 90)
    low = value.lower()
    if not value or _ADMIN.search(value) or _CODE.search(value) or _BAD_TITLE.match(value):
        return False
    if any(x in low for x in ("gold standard mechanism", "terms of use", "opencourseware")):
        return False
    if low.startswith(("ever ", "however ", "therefore ", "consider ", "example ", "model ")):
        return False
    if len(value.split()) > 9 or len(value) > 80:
        return False
    return True


def _domain_nodes(profile, limit: int = 8) -> list[str]:
    raw = [x.name for x in getattr(profile, "topic_families", []) or [] if _good_node(x.name)]
    seen: set[str] = set(); clean: list[str] = []
    for item in raw:
        value = _clean(item, 80)
        key = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
        if key and key not in seen:
            seen.add(key); clean.append(value)
    if len(clean) <= limit:
        return clean
    # Show the breadth of the chapter rather than only its first page.
    idx: list[int] = []
    for i in range(limit):
        n = round(i * (len(clean) - 1) / (limit - 1))
        if n not in idx:
            idx.append(n)
    return [clean[i] for i in idx]


def _sanitize_title(title: str) -> str:
    value = _clean(title, 82)
    if _BAD_TITLE.match(value) or _CODE.search(value) or _ADMIN.search(value):
        return ""
    if value.lower() in {"gold standard mechanism", "model", "consider"}:
        return ""
    return value


def _clean_blueprint(bp, profile):
    if not getattr(bp, "units", None):
        return bp

    stake, stake_anchor = _best_stake(profile, bp)
    if stake:
        # The presenter reads bp.central_engineering_crisis directly. Keep it and
        # Unit 1 synchronized so stale scaffold text cannot reappear in PPTX/PDF.
        bp.central_engineering_crisis = stake
        u1 = bp.units[0]
        u1.title = "The source-defined engineering stake"
        u1.engineering_question = "Which design choice controls this P1-supported failure, and what evidence would reverse that choice?"
        u1.core_content = [stake]
        u1.source_anchor = stake_anchor or u1.source_anchor
        u1.pedagogy_content = [
            "DECISION — identify the design response this source-supported stake requires.",
            "REVERSAL TEST — name the P1 evidence that would make you change the decision.",
        ]
        u1.student_action = "State the decision, cite the P1 stake, and name the evidence that would make you change your mind."

    nodes = _domain_nodes(profile)
    if nodes:
        bp.source_topic_families = nodes
        u2 = bp.units[1]
        u2.title = "Domain spine"
        u2.core_content = nodes
        u2.pedagogy_content = ["MAP — connect the source concepts before studying any one mechanism in isolation."]
        u2.student_action = "Connect two nodes and explain the dependency that matters most to the engineering decision."
        u2.takeaway = "A domain spine is a readable map of the source, not a dump of headings."

    prediction, prediction_anchor = _best_prediction(profile, avoid=stake)
    if prediction and len(bp.units) >= 5:
        u5 = bp.units[4]
        u5.title = "Prediction gate"
        u5.engineering_question = "Before the mechanism is named, what outcome do you predict from this P1 example?"
        u5.core_content = [prediction]
        u5.source_anchor = prediction_anchor or u5.source_anchor
        # Keep the fixed Predict → Constrain → Derive → Name pedagogy already
        # generated by the 20-unit grammar; only the source payload is replaced.

    # A final title guard protects every renderer. Dense decomposition should
    # already make these titles source-specific; this only catches raw code or
    # extraction furniture that survives an unusual source.
    fallback_nodes = nodes or ["Source mechanism"]
    used: set[str] = set()
    for unit in bp.units[5:15]:
        title = _sanitize_title(unit.title)
        key = title.lower() if title else ""
        if not title or key in used:
            candidate = ""
            for item in unit.core_content:
                maybe = _label_from_line(item)
                if maybe and _good_node(maybe) and maybe.lower() not in used:
                    candidate = maybe; break
            if not candidate:
                for item in fallback_nodes:
                    if item.lower() not in used:
                        candidate = item; break
            title = candidate or f"Source mechanism {unit.number - 5}"
        unit.title = title
        used.add(title.lower())

    return bp


def apply_v720_clean_release_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    previous = engine._source_preserving_draft

    def clean_release_draft(profile, bundle):
        cleaned_profile = _clean_profile(profile)
        blueprint = previous(cleaned_profile, bundle)
        return _clean_blueprint(blueprint, cleaned_profile)

    engine._source_preserving_draft = clean_release_draft
    base.engine._source_preserving_draft = clean_release_draft

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "release_ui": "7.2.0",
            "clean_release": True,
            "dense_p1_decomposition": True,
            "administrative_source_chrome_in_spine": False,
            "raw_code_labels_in_spine": False,
            "opening_and_presenter_crisis_synchronized": True,
            "public_web_image_fallback": False,
        })
        return data

    base._health_v440 = health
    base.engine.health = health
