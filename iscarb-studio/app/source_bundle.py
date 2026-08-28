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
            f"LIVE SESSION TIMEBOX: {self.session_minutes} minutes",
            "SOURCE HIERARCHY: the PRIMARY source sets lecture scope, terminology, and conflict precedence; SUPPORTING sources may clarify, evidence, or enrich the SAME lecture focus but must not silently expand it into another lecture.",
            "SOURCE ANCHORS in the blueprint must use these source IDs (for example: [P1] SLIDES 7-12, [S2] p.4).",
        ]
        if self.lecture_focus.strip():
            lines.append(f"FACULTY-SUPPLIED LECTURE FOCUS: {self.lecture_focus.strip()}")
        lines.append("SOURCES:")
        lines.extend(self.manifest_lines())
        return "\n".join(lines)

    def combined_local_text(self, per_source_limit: int = 260_000) -> str:
        chunks: list[str] = [self.manifest_text()]
        for item in self.items:
            text = extract_source_text(item.path, limit=per_source_limit)
            chunks.append(f"\n===== {item.label} =====\n{text}")
        return "\n".join(chunks)
