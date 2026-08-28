from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, field_validator

Phase = Literal["IFHAM", "MARIS", "ATQAN", "MAYYIZ"]
CIMTLens = Literal["C", "I", "M", "T", "N/A"]
AlignmentStrength = Literal["direct", "supporting"]
ScopeFit = Literal["FIT", "COMPRESS", "MIXED"]


class TopicFamily(BaseModel):
    name: str
    source_anchor: str = ""
    why_important: str = ""


class SourceProfile(BaseModel):
    lecture_title: str
    course_or_level: str = ""
    weekly_focus: str
    topic_families: list[TopicFamily] = Field(min_length=1)
    technical_boundaries: list[str] = Field(default_factory=list)
    source_warnings: list[str] = Field(default_factory=list)

    # One live lecture is always 90 minutes. In v1.8 all major PRIMARY topic
    # families remain in scope; COMPRESS means smart compression, not deferral.
    session_minutes: int = 90
    scope_fit: ScopeFit = "FIT"
    in_scope_families: list[str] = Field(default_factory=list)
    deferred_topics: list[str] = Field(default_factory=list)
    source_conflicts: list[str] = Field(default_factory=list)
    source_manifest: list[str] = Field(default_factory=list)

    @field_validator("in_scope_families", "deferred_topics", "source_conflicts", "source_manifest", mode="before")
    @classmethod
    def clean_scope_lists(cls, value):
        if isinstance(value, list):
            result = []
            for item in value:
                text = str(item).strip()
                if text and text not in result:
                    result.append(text)
            return result[:20]
        return value


class CLO(BaseModel):
    id: Literal["CLO1", "CLO2", "CLO3", "CLO4", "CLO5"]
    statement: str
    evidence_expected: str


class TopicCoverage(BaseModel):
    topic_family: str
    source_anchor: str
    # Structural parsing accepts any Unit 1-20 so a semantically bad draft can
    # still reach Content Gate. The hard pedagogical rule remains in gate.py:
    # every major topic MUST first be taught by Unit 15. If a model returns 16-20,
    # the Gate fails it and the repair loop must move the actual teaching earlier.
    first_taught_unit: int = Field(ge=1, le=20)
    reinforced_units: list[int] = Field(default_factory=list)

    @field_validator("reinforced_units", mode="before")
    @classmethod
    def trim_reinforced_units(cls, value):
        if isinstance(value, list):
            seen = []
            for item in value:
                if item not in seen:
                    seen.append(item)
            return seen[:10]
        return value


class ReadinessAlignment(BaseModel):
    standard: str = "ETEC Academic Standards for Information Technology Programs 2025 v2.0"
    gku: str
    sku: str
    slo_refs: list[str] = Field(min_length=1)
    klo_refs: list[str] = Field(min_length=1)
    strength: AlignmentStrength
    rationale: str
    atomicity_evidence: str
    clo_ids: list[Literal["CLO1", "CLO2", "CLO3", "CLO4", "CLO5"]] = Field(min_length=1)
    evidence_units: list[int] = Field(min_length=1)
    standard_source_pages: list[int] = Field(min_length=1)

    @field_validator("slo_refs", "klo_refs", "clo_ids", "evidence_units", "standard_source_pages", mode="before")
    @classmethod
    def dedupe_alignment_lists(cls, value):
        if isinstance(value, list):
            result = []
            for item in value:
                if item not in result:
                    result.append(item)
            return result[:10]
        return value


class RubricCriterion(BaseModel):
    criterion: str
    distinguished: str
    ready: str
    developing: str
    not_yet_ready: str
    readiness_refs: list[str] = Field(default_factory=list)

    @field_validator("readiness_refs", mode="before")
    @classmethod
    def trim_readiness_refs(cls, value):
        if isinstance(value, list):
            return list(dict.fromkeys(value))[:8]
        return value


class LectureUnit(BaseModel):
    number: int = Field(ge=1, le=20)
    phase: Phase
    title: str
    engineering_question: str

    # TRIPLE PROVENANCE
    # core_content: ONLY technical content demonstrably supported by the user-supplied lecture bundle.
    # pedagogy_content: ISCARB instructional/assessment scaffolding.
    # enrichment_content: external/current/cultural/contextual extensions not present in the lecture bundle.
    core_content: list[str] = Field(default_factory=list, max_length=8)
    pedagogy_content: list[str] = Field(default_factory=list, max_length=8)
    enrichment_content: list[str] = Field(default_factory=list, max_length=6)
    enrichment_basis: list[str] = Field(default_factory=list, max_length=6)
    scenario_assumptions: list[str] = Field(default_factory=list, max_length=5)

    visual_suggestion: str
    student_action: str
    takeaway: str
    cimtlens: list[CIMTLens] = Field(min_length=1, max_length=4)
    clo_ids: list[Literal["CLO1", "CLO2", "CLO3", "CLO4", "CLO5"]] = Field(min_length=1)
    source_anchor: str = ""
    inherited_requirements: list[str] = Field(default_factory=list)
    elite_requirements: list[str] = Field(default_factory=list)
    evidence: str = ""
    contextual_enrichment: bool = False
    verify_before_release: bool = False
    planned_minutes: int = Field(default=0, ge=0, le=15)

    @field_validator("core_content", "pedagogy_content", mode="before")
    @classmethod
    def cap_main_lists(cls, value):
        if isinstance(value, list):
            return [x for x in value if str(x).strip()][:8]
        return value

    @field_validator("enrichment_content", "enrichment_basis", mode="before")
    @classmethod
    def cap_enrichment_lists(cls, value):
        if isinstance(value, list):
            return [x for x in value if str(x).strip()][:6]
        return value

    @field_validator("scenario_assumptions", mode="before")
    @classmethod
    def cap_assumptions(cls, value):
        if isinstance(value, list):
            return [x for x in value if str(x).strip()][:5]
        return value

    @field_validator("cimtlens", mode="before")
    @classmethod
    def cap_cimt(cls, value):
        if isinstance(value, list):
            return list(dict.fromkeys(value))[:4]
        return value

    @field_validator("clo_ids", "inherited_requirements", "elite_requirements", mode="before")
    @classmethod
    def dedupe_tags(cls, value):
        if isinstance(value, list):
            return list(dict.fromkeys(value))
        return value


class Blueprint(BaseModel):
    lecture_title: str
    engineering_thesis: str
    central_engineering_crisis: str
    named_ethical_purpose: str
    clOs: list[CLO] = Field(alias="clos", min_length=5, max_length=5)
    units: list[LectureUnit] = Field(min_length=20, max_length=20)
    source_topic_families: list[str] = Field(min_length=1)
    topic_coverage: list[TopicCoverage] = Field(min_length=1)
    readiness_alignment: list[ReadinessAlignment] = Field(min_length=1)
    rubric_criteria: list[RubricCriterion] = Field(min_length=6)
    release_notes: list[str] = Field(default_factory=list)

    session_minutes: int = 90
    source_manifest: list[str] = Field(default_factory=list)
    deferred_topics: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    @field_validator("release_notes", "source_manifest", "deferred_topics", mode="before")
    @classmethod
    def trim_blueprint_lists(cls, value):
        if isinstance(value, list):
            result = []
            for item in value:
                text = str(item).strip()
                if text and text not in result:
                    result.append(text)
            return result[:20]
        return value


class AuditIssue(BaseModel):
    severity: Literal["critical", "major", "minor"]
    unit_numbers: list[int] = Field(default_factory=list)
    requirement: str
    problem: str
    repair_instruction: str


class AuditReport(BaseModel):
    overall_pass: bool
    source_fidelity_pass: bool
    engineering_rigor_pass: bool
    cumulative_fidelity_pass: bool
    readiness_alignment_pass: bool
    provenance_separation_pass: bool
    issues: list[AuditIssue] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class JobState(BaseModel):
    id: str
    status: Literal["queued", "analyzing", "generating", "auditing", "repairing", "ready", "blocked", "error"]
    progress: int = Field(ge=0, le=100)
    message: str
    filename: str = ""
    model: str = ""
    source_manifest: list[str] = Field(default_factory=list)
    lecture_focus: str = ""
    source_profile: SourceProfile | None = None
    blueprint: Blueprint | None = None
    audit: AuditReport | None = None
    deterministic_checks: dict[str, bool] = Field(default_factory=dict)
    error: str | None = None
