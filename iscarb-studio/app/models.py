from __future__ import annotations

from typing import Literal
import time
from pydantic import BaseModel, Field, field_validator

Phase = Literal["IFHAM", "MARIS", "ATQAN", "MAYYIZ"]
CIMTLens = Literal["C", "I", "M", "T", "N/A"]
AlignmentStrength = Literal["direct", "supporting"]
ScopeFit = Literal["FIT", "COMPRESS", "MIXED"]
KnowledgeType = Literal[
    "CONCEPT", "ALGORITHM", "CODE", "ARCHITECTURE", "EQUATION", "PROTOCOL",
    "PROCESS", "DATA_MODEL", "SYSTEM_BEHAVIOR", "DESIGN_PRINCIPLE", "TRADE_OFF",
    "EMPIRICAL_RESULT", "EXAMPLE", "OTHER",
]
CoverageImportance = Literal["major", "supporting"]
CoverageDepth = Literal["DEEP", "CONCISE", "INTEGRATED"]
VisualReuseMode = Literal["USE", "ADAPT", "REDRAW", "NEW"]


class TopicFamily(BaseModel):
    name: str
    source_anchor: str = ""
    why_important: str = ""


class CoverageItem(BaseModel):
    """Atomic chapter/source element used to prove computing-wide coverage."""
    id: str
    label: str
    knowledge_type: KnowledgeType = "CONCEPT"
    importance: CoverageImportance = "major"
    source_anchor: str
    why_important: str = ""


class SourceProfile(BaseModel):
    lecture_title: str
    course_or_level: str = ""
    weekly_focus: str
    topic_families: list[TopicFamily] = Field(min_length=1)
    coverage_items: list[CoverageItem] = Field(default_factory=list)
    technical_boundaries: list[str] = Field(default_factory=list)
    source_warnings: list[str] = Field(default_factory=list)

    # One live lecture is always 90 minutes. All major PRIMARY elements remain
    # in scope; COMPRESS means intelligent synthesis, never omission.
    session_minutes: int = 90
    scope_fit: ScopeFit = "FIT"
    in_scope_families: list[str] = Field(default_factory=list)
    deferred_topics: list[str] = Field(default_factory=list)
    source_conflicts: list[str] = Field(default_factory=list)
    source_manifest: list[str] = Field(default_factory=list)

    @field_validator("coverage_items", mode="before")
    @classmethod
    def cap_coverage_items(cls, value):
        if isinstance(value, list):
            seen = set()
            out = []
            for item in value:
                key = str(item.get("id", "") if isinstance(item, dict) else item).strip()
                if key and key not in seen:
                    seen.add(key)
                    out.append(item)
            return out[:80]
        return value

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


class CoverageLedgerEntry(BaseModel):
    coverage_id: str
    label: str
    knowledge_type: KnowledgeType = "CONCEPT"
    source_anchor: str
    first_taught_unit: int = Field(ge=1, le=20)
    reinforced_units: list[int] = Field(default_factory=list)
    depth: CoverageDepth = "CONCISE"
    representation: str = ""

    @field_validator("reinforced_units", mode="before")
    @classmethod
    def trim_reinforcement(cls, value):
        if isinstance(value, list):
            return list(dict.fromkeys(value))[:10]
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


class VisualPlan(BaseModel):
    visual_type: str = "concept-map"
    teaching_purpose: str = ""
    source_visual_available: bool = False
    source_page_or_slide: str = ""
    source_url: str = ""
    reuse_mode: VisualReuseMode = "NEW"
    citation: str = "ISCARB visualization"
    focal_elements: list[str] = Field(default_factory=list)
    annotation_plan: list[str] = Field(default_factory=list)
    visual_evidence_role: str = ""

    @field_validator("focal_elements", "annotation_plan", mode="before")
    @classmethod
    def cap_visual_lists(cls, value):
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()][:8]
        return value


class CoverageEvidence(BaseModel):
    coverage_id: str
    source_anchor: str
    # Exact excerpt from this unit's visible core, not a claim in a ledger.
    visible_excerpt: str = Field(min_length=20)


class LectureUnit(BaseModel):
    number: int = Field(ge=1, le=20)
    phase: Phase
    title: str
    engineering_question: str

    # TRIPLE PROVENANCE
    # core_content: ONLY technical content demonstrably supported by the user-supplied lecture bundle.
    # pedagogy_content: ISCARB instructional/assessment scaffolding.
    # enrichment_content: external/current/cultural/contextual extensions not present in the lecture bundle.
    core_content: list[str] = Field(default_factory=list, max_length=64)
    pedagogy_content: list[str] = Field(default_factory=list, max_length=16)
    enrichment_content: list[str] = Field(default_factory=list, max_length=6)
    enrichment_basis: list[str] = Field(default_factory=list, max_length=6)
    scenario_assumptions: list[str] = Field(default_factory=list, max_length=5)

    knowledge_types: list[KnowledgeType] = Field(default_factory=list)
    visual_suggestion: str
    visual_plan: VisualPlan | None = None
    student_action: str
    takeaway: str
    cimtlens: list[CIMTLens] = Field(min_length=1, max_length=4)
    clo_ids: list[Literal["CLO1", "CLO2", "CLO3", "CLO4", "CLO5"]] = Field(min_length=1)
    source_anchor: str = ""
    coverage_evidence: list[CoverageEvidence] = Field(default_factory=list)
    inherited_requirements: list[str] = Field(default_factory=list)
    elite_requirements: list[str] = Field(default_factory=list)
    evidence: str = ""
    contextual_enrichment: bool = False
    verify_before_release: bool = False
    planned_minutes: int = Field(default=0, ge=0, le=15)

    @field_validator("knowledge_types", mode="before")
    @classmethod
    def cap_knowledge_types(cls, value):
        if isinstance(value, list):
            return list(dict.fromkeys(value))[:5]
        return value

    @field_validator("core_content", "pedagogy_content", mode="before")
    @classmethod
    def cap_main_lists(cls, value):
        if isinstance(value, list):
            # Reject an oversized response explicitly via field validation;
            # never silently throw away source facts after the eighth item.
            return [x for x in value if str(x).strip()]
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


class BlueprintPlan(BaseModel):
    lecture_title: str
    engineering_thesis: str
    central_engineering_crisis: str
    named_ethical_purpose: str
    clOs: list[CLO] = Field(alias="clos", min_length=5, max_length=5)
    source_topic_families: list[str] = Field(min_length=1)
    topic_coverage: list[TopicCoverage] = Field(min_length=1)
    coverage_ledger: list[CoverageLedgerEntry] = Field(default_factory=list)
    readiness_alignment: list[ReadinessAlignment] = Field(default_factory=list)
    rubric_criteria: list[RubricCriterion] = Field(min_length=6)
    release_notes: list[str] = Field(default_factory=list)

    session_minutes: int = 90
    source_manifest: list[str] = Field(default_factory=list)
    deferred_topics: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    @field_validator("coverage_ledger", mode="before")
    @classmethod
    def cap_coverage_ledger(cls, value):
        if isinstance(value, list):
            return value[:80]
        return value

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


class Blueprint(BlueprintPlan):
    units: list[LectureUnit] = Field(min_length=20, max_length=20)
    generation_mode: str = "legacy"


class UnitBatch(BaseModel):
    units: list[LectureUnit] = Field(min_length=1, max_length=4)


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
    created_at: float = Field(default_factory=time.time)
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
