from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .source_text import extract_source_text


@dataclass(frozen=True)
class SourceItem:
    role: str  # primary | supporting
    source_id: str  # P1, S1, S2...
    display_name: str
    path: Path
    origin: str = ""

    @property
    def label(self) -> str:
        kind = "PRIMARY" if self.role == "primary" else "SUPPORTING"
        return f"[{self.source_id}] {kind}: {self.display_name}"


@dataclass
class SourceBundle:
    items: list[SourceItem]
    lecture_focus: str = ""
    session_minutes: int = 90

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("A lecture bundle needs at least one source.")
        primary = [x for x in self.items if x.role == "primary"]
        if len(primary) != 1:
            raise ValueError("A lecture bundle must have exactly one primary lecture source.")
        if len(self.items) > 8:
            raise ValueError("Use at most 8 sources for one 90-minute lecture (1 primary + up to 7 supporting).")

    @property
    def primary(self) -> SourceItem:
        return next(x for x in self.items if x.role == "primary")

    @property
    def supporting(self) -> list[SourceItem]:
        return [x for x in self.items if x.role == "supporting"]

    def manifest_lines(self) -> list[str]:
        return [x.label for x in self.items]

    def manifest_text(self) -> str:
        lines = [
            "ISCARB LECTURE SOURCE BUNDLE",
            f"LIVE SESSION TIMEBOX: {self.session_minutes} minutes — FIXED.",
            "PRIMARY FULL-COVERAGE CONTRACT: the PRIMARY lecture source defines the complete lecture scope. Every major technical topic family in P1 MUST appear in the 20-unit session. No P1 topic may be deferred, omitted, replaced, or moved to another lecture because the source is large.",
            "COMPRESSION RULE: if P1 is dense, compress intelligently inside the same 90 minutes by grouping related concepts, reducing repetition, and varying depth. Preserve every major topic family and all decision-critical mechanisms. Use FIT for normal density and COMPRESS for high density; never solve overload by dropping primary content.",
            "SUPPORTING-SOURCE RULE: SUPPORTING sources may clarify, evidence, exemplify, contextualize, or verify the SAME lecture, but they do not expand the mandatory technical scope. Material found only in supporting sources may be ignored when it does not help teach P1.",
            "SOURCE HIERARCHY: P1 controls lecture scope, terminology, and conflict precedence. If a supporting source conflicts with P1, preserve P1 and record the conflict rather than silently reconciling them.",
            "SOURCE ANCHORS in the blueprint must use source IDs (for example: [P1] SLIDES 7-12, [S2] p.4). Every primary topic-family coverage entry should include a [P1] anchor.",
        ]
        if self.lecture_focus.strip():
            lines.append(
                "FACULTY-SUPPLIED LECTURE FOCUS: " + self.lecture_focus.strip()
                + " — use this to emphasize and organize the lecture, NOT to remove other major P1 topics."
            )
        lines.append("SOURCES:")
        lines.extend(self.manifest_lines())
        return "\n".join(lines)

    def combined_local_text(self, per_source_limit: int = 260_000) -> str:
        chunks: list[str] = [self.manifest_text()]
        for item in self.items:
            text = extract_source_text(item.path, limit=per_source_limit)
            chunks.append(f"\n===== {item.label} =====\n{text}")
        return "\n".join(chunks)
