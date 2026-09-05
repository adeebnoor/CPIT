from __future__ import annotations

"""ISCARB v7.1.7 deterministic source-intelligence hardening.

The quota-safe path must not confuse a code/example line with the topic of a
page, nor promote copyright/host chrome into the Domain Spine.  This patch stays
source-bounded: it only re-labels material with phrases already present in P1
and extracts multiple compact concept headings from dense pages.
"""

import re

from . import main as engine
from . import start_v440 as base
from . import patch_v690 as v690
from .models import TopicFamily

_PATCHED = False

_ADMIN = re.compile(
    r"(?:for information about citing|terms of use|all rights reserved|copyright|"
    r"open.?courseware\s+https?://|further reading|references only)", re.I)
_CODE_LABEL = re.compile(
    r"^(?:t\d+\s*:|sql[- ]?\d+|begin\s+xact|end\s+xact|insert\b|update\b|"
    r"select\b|from\b|where\b|commit\b|abort\b)", re.I)
_GENERIC_LABEL = re.compile(
    r"^(?:gold standard mechanism|mechanism|model|example|consider|overview|"
    r"introduction|course|lecture|database systems|primary source page \d+)$", re.I)
_COURSE_CODE = re.compile(r"^\s*\d{1,3}(?:\.\d+)+\s*/?.*systems?\s*$", re.I)
_URL = re.compile(r"https?://|www\.", re.I)

# Source-native failure/stake vocabulary across computing domains.  Expanding
# the old generic-risk matcher lets a real P1 example such as an inconsistent
# concurrent schedule, deadlock, race, timeout or wrong result become the hook.
_SOURCE_STAKE = re.compile(
    r"\b(?:risk|threat|attack|failure|fault|hazard|harm|loss|breach|vulnerab\w*|"
    r"compromis\w*|unauthori[sz]\w*|damage|outage|unsafe|exploit\w*|intrusion|"
    r"constraint|trade[- ]?off|problem|challenge|difficult|cost|must|cannot|"
    r"require\w*|deadlock|starv\w*|abort\w*|wrong|incorrect|inconsisten\w*|"
    r"race|collision|overflow|timeout|latency|parallel\s+schedule|does\s+not|"
    r"not\s+seriali[sz]\w*|violat\w*|corrupt\w*|unavailable|unrecover\w*)\b", re.I)

_GENERIC_PREFIX = re.compile(
    r"^(?:definition|deep theorem|answer|how|issue|alternative|rule of thumb|"
    r"what about|aka)\s*[:\-]?\s*", re.I)
_BAD_CANDIDATE = re.compile(
    r"^(?:devil is in the details|gold standard mechanism|model|consider|example|"
    r"fall \d{4}|mit opencourseware|primary source|source page)\b", re.I)


def _clean(text: str, limit: int = 78) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip(" \t\r\n·•-–—:;,.!?")
    text = re.sub(r"\(\s*(?:urban myth|tried\b).*", "", text, flags=re.I).strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) > limit:
        head = text[:limit]
        text = head.rsplit(" ", 1)[0] if " " in head else head
    return text.strip(" -–—:;,.!?")


def _is_admin(label: str, excerpt: str) -> bool:
    blob = f"{label} {excerpt}"
    if _ADMIN.search(blob):
        # A terms/citation page is host/legal furniture even if the course name
        # contains a technical word such as "Systems".
        if re.search(r"terms of use|information about citing|all rights reserved|copyright", blob, re.I):
            return True
    return False


def _bad_label(label: str) -> bool:
    text = _clean(label, 120)
    return bool(
        not text or _CODE_LABEL.search(text) or _GENERIC_LABEL.match(text)
        or _COURSE_CODE.match(text) or _URL.search(text) or "!!!" in text
    )


def _candidate_from_line(line: str) -> str:
    raw = re.sub(r"\s+", " ", str(line or "")).strip(" ·•\t")
    if not raw or _URL.search(raw) or _CODE_LABEL.search(raw) or _ADMIN.search(raw):
        return ""

    # Explicit source cues often carry the concept after the cue:
    # "Deep theorem: 2 phase locking -> serializability", "How: predicate locking".
    if _GENERIC_PREFIX.match(raw):
        rest = _GENERIC_PREFIX.sub("", raw, count=1)
        rest = re.split(r"[.?!;]|\s+[–—]\s+|\s+\(", rest, maxsplit=1)[0]
        value = _clean(rest)
        if 1 <= len(value.split()) <= 9 and len(value) >= 4 and not _BAD_CANDIDATE.match(value):
            return value[:1].upper() + value[1:]

    # A source-authored heading ending in ':' is stronger than prose.
    if raw.endswith(":"):
        value = _clean(raw[:-1])
        if 1 <= len(value.split()) <= 9 and len(value) >= 4 and not _BAD_CANDIDATE.match(value):
            return value

    # "What about deadlock?" -> "Deadlock"; "How range locks in a B-tree..."
    m = re.match(r"^what about\s+(.+?)\??$", raw, re.I)
    if m:
        return _clean(m.group(1)).capitalize()
    m = re.match(r"^how\s+(.+?)(?:\s+\(|\.|$)", raw, re.I)
    if m and 1 <= len(m.group(1).split()) <= 9:
        return _clean(m.group(1))

    # Named compact concepts survive as standalone source lines. One-word
    # headings are allowed here: "Transactions", "Normalization", "Routing".
    value = _clean(raw)
    words = value.split()
    if 1 <= len(words) <= 7 and 4 <= len(value) <= 64:
        if raw.rstrip().endswith((".", ",", ";")):
            return ""
        if _BAD_CANDIDATE.match(value) or _COURSE_CODE.match(value):
            return ""
        if re.search(r"[=]{1,}|\b(?:set|values|salary|dept)\s*=", value, re.I):
            return ""
        # Sentence-like finite clauses are not headings.
        if len(words) >= 4 and re.search(r"\b(?:is|are|was|were|does|do|did|can|must|will|has|have)\b", value, re.I):
            return ""
        return value
    return ""


def _concepts(label: str, excerpt: str, max_items: int = 5) -> list[str]:
    parts = [x.strip() for x in re.split(r"\s*[·•▪■◆]\s*|\n+", str(excerpt or "")) if x.strip()]
    out: list[str] = []
    if not _bad_label(label):
        out.append(_clean(label))
    for line in parts:
        cand = _candidate_from_line(line)
        if not cand:
            continue
        key = re.sub(r"[^a-z0-9]+", " ", cand.lower()).strip()
        if not key or any(key == re.sub(r"[^a-z0-9]+", " ", x.lower()).strip() for x in out):
            continue
        # Avoid tiny data values becoming a spine node.
        if re.fullmatch(r"(?:bill|sam|fred|george|hugh|easy|wait|ditto)", cand, re.I):
            continue
        out.append(cand)
        if len(out) >= max_items:
            break
    return out


def _best_title(profile, bundle) -> str:
    focus = _clean(getattr(bundle, "lecture_focus", ""), 110)
    if focus and len(focus.split()) >= 2:
        return focus
    current = _clean(getattr(profile, "lecture_title", ""), 110)
    if current and not _bad_label(current):
        return current
    for row in getattr(profile, "coverage_items", []) or []:
        if _is_admin(getattr(row, "label", ""), getattr(row, "why_important", "")):
            continue
        cs = _concepts(getattr(row, "label", ""), getattr(row, "why_important", ""), 3)
        if cs:
            return cs[0]
    return current or "Primary IT lecture"


def _normalize_profile(profile, bundle):
    rows = list(getattr(profile, "coverage_items", []) or [])
    for row in rows:
        label = str(getattr(row, "label", "") or "")
        excerpt = str(getattr(row, "why_important", "") or "")
        if _is_admin(label, excerpt):
            row.importance = "supporting"
            continue
        cs = _concepts(label, excerpt, 4)
        if cs and _bad_label(label):
            row.label = cs[0]

    profile.lecture_title = _best_title(profile, bundle)
    if not getattr(profile, "weekly_focus", "") or _bad_label(getattr(profile, "weekly_focus", "")):
        profile.weekly_focus = profile.lecture_title

    # Build the learner-visible spine from compact P1 phrases, not one arbitrary
    # first line per physical page. Coverage items themselves remain unchanged,
    # so no source material is lost from the ledger.
    families: list[TopicFamily] = []
    seen: set[str] = set()
    for row in rows:
        if getattr(row, "importance", "") != "major":
            continue
        label = str(getattr(row, "label", "") or "")
        excerpt = str(getattr(row, "why_important", "") or "")
        if _is_admin(label, excerpt):
            continue
        for concept in _concepts(label, excerpt, 4):
            key = re.sub(r"[^a-z0-9]+", " ", concept.lower()).strip()
            if not key or key in seen:
                continue
            seen.add(key)
            families.append(TopicFamily(
                name=concept,
                source_anchor=str(getattr(row, "source_anchor", "") or "[P1]"),
                why_important=_clean(excerpt, 220),
            ))
            if len(families) >= 16:
                break
        if len(families) >= 16:
            break
    if families:
        profile.topic_families = families
        profile.in_scope_families = [x.name for x in families]
    return profile


def apply_v717_source_intelligence_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    # Broaden only the source-evidence selector; generic fabricated crises remain
    # rejected by the existing v6.9 gate.
    v690._RISK = _SOURCE_STAKE

    previous = engine._source_preserving_draft

    def intelligent_draft(profile, bundle):
        return previous(_normalize_profile(profile, bundle), bundle)

    engine._source_preserving_draft = intelligent_draft
    base.engine._source_preserving_draft = intelligent_draft

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.update({
            "release_ui": "7.1.7",
            "source_intelligence": "dense-P1 concept extraction + administrative-page suppression",
            "dense_pdf_policy": "derive compact P1 concepts; never use code/example/footer line as Domain Spine node",
            "opening_crisis_selector": "P1 failure/stake sentence first; generic crisis still blocks release",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
