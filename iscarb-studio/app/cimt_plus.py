from __future__ import annotations

import re

from .models import Blueprint, SourceProfile, VisualPlan, KnowledgeType

VISUAL_GRAMMAR: dict[str, str] = {
    "CONCEPT": "causal-concept-map",
    "ALGORITHM": "algorithm-trace",
    "CODE": "code-state-trace",
    "ARCHITECTURE": "system-architecture",
    "EQUATION": "derivation-sensitivity",
    "PROTOCOL": "protocol-sequence",
    "PROCESS": "process-flow",
    "DATA_MODEL": "data-model-schema",
    "SYSTEM_BEHAVIOR": "state-timeline",
    "DESIGN_PRINCIPLE": "principle-application-boundary",
    "TRADE_OFF": "decision-matrix",
    "EMPIRICAL_RESULT": "evidence-result-uncertainty",
    "EXAMPLE": "annotated-example",
    "OTHER": "concept-map",
}


def _blob(unit) -> str:
    return " ".join([
        unit.title,
        unit.engineering_question,
        *unit.core_content,
        *unit.pedagogy_content,
        unit.student_action,
        unit.takeaway,
        unit.visual_suggestion,
    ]).lower()


def infer_knowledge_types(text: str) -> list[KnowledgeType]:
    low = " " + re.sub(r"[^a-z0-9+/#.-]+", " ", (text or "").lower()) + " "
    rules: list[tuple[KnowledgeType, list[str]]] = [
        ("ALGORITHM", [" algorithm ", " pseudocode ", " complexity ", " big-o ", " sorting ", " searching "]),
        ("CODE", [" code ", " class ", " function ", " method ", " variable ", " statement ", " compile ", " debug "]),
        ("EQUATION", [" equation ", " formula ", " calculate ", " probability ", " mttf ", " mtbf ", " availability =", " reliability ="]),
        ("PROTOCOL", [" protocol ", " packet ", " message sequence ", " tcp ", " udp ", " request response "]),
        ("DATA_MODEL", [" schema ", " entity ", " relation ", " relational ", " database ", " table ", " normalization "]),
        ("ARCHITECTURE", [" architecture ", " component ", " subsystem ", " layer ", " client server ", " distributed system "]),
        ("PROCESS", [" process ", " workflow ", " lifecycle ", " stage ", " activity ", " pipeline "]),
        ("SYSTEM_BEHAVIOR", [" state ", " transition ", " event ", " scheduler ", " deadlock ", " concurrency ", " timing "]),
        ("TRADE_OFF", [" trade-off ", " tradeoff ", " alternative ", " versus ", " vs ", " cost ", " compromise "]),
        ("EMPIRICAL_RESULT", [" experiment ", " result ", " measured ", " benchmark ", " dataset ", " observation "]),
        ("DESIGN_PRINCIPLE", [" principle ", " guideline ", " design rule ", " heuristic "]),
    ]
    out: list[KnowledgeType] = []
    for ktype, markers in rules:
        if any(marker in low for marker in markers):
            out.append(ktype)
    return out[:5] or ["CONCEPT"]


def _ledger_types_for_unit(bp: Blueprint, unit_number: int) -> list[KnowledgeType]:
    out: list[KnowledgeType] = []
    for row in bp.coverage_ledger:
        if row.first_taught_unit == unit_number or unit_number in row.reinforced_units:
            if row.knowledge_type not in out:
                out.append(row.knowledge_type)
    return out[:5]


def _visual_type_for(types: list[KnowledgeType], unit_number: int) -> str:
    # Reserved ISCARB functions have their own cognitive job; technical Units
    # remain source-native through the knowledge-type grammar.
    reserved = {
        1: "incident-decision-scene",
        2: "domain-spine-map",
        3: "capability-evidence-path",
        4: "h-stack-radial",
        5: "predict-derive-reveal",
        11: "saudi-system-context-map",
        12: "accountability-consequence-map",
        13: "trend-engineering-timeline",
        14: "operator-load-resilience-loop",
        15: "ai-permissibility-gate",
        16: "portfolio-mission-brief",
        17: "constraint-mutation-redesign",
        18: "claim-evidence-warrant-graph",
        19: "performance-rubric-ladder",
        20: "assurance-case-verdict-tree",
    }
    if unit_number in reserved:
        return reserved[unit_number]
    return VISUAL_GRAMMAR.get((types or ["CONCEPT"])[0], "concept-map")


def normalize_cimt_plus(bp: Blueprint, profile: SourceProfile | None = None) -> Blueprint:
    """Attach source-native knowledge types and a safe dominant visual plan.

    This does not invent coverage. Missing coverage ledger entries remain a gate
    failure so the model/repair loop must explicitly restore them.
    """
    for unit in bp.units:
        if not unit.knowledge_types:
            unit.knowledge_types = _ledger_types_for_unit(bp, unit.number) or infer_knowledge_types(_blob(unit))

        expected_type = _visual_type_for(unit.knowledge_types, unit.number)
        if unit.visual_plan is None:
            unit.visual_plan = VisualPlan(
                visual_type=expected_type,
                teaching_purpose=f"Make Unit {unit.number} perform one visible cognitive job before explanation.",
                source_visual_available=False,
                reuse_mode="NEW",
                citation="ISCARB visualization based on source-locked P1 content",
                focal_elements=[x for x in [unit.title, *unit.core_content[:3]] if x][:4],
                annotation_plan=[unit.engineering_question, unit.student_action][:2],
                visual_evidence_role="Supports learner prediction, explanation, comparison, or decision evidence without replacing P1.",
            )
        else:
            vp = unit.visual_plan
            # A source visual claim must be auditable. Otherwise downgrade safely.
            if vp.source_visual_available and not (vp.source_page_or_slide.strip() or "[P1]" in (unit.source_anchor or "").upper()):
                vp.source_visual_available = False
                vp.reuse_mode = "REDRAW"
                vp.citation = "ISCARB redraw based on source-locked P1 content"
            if not vp.teaching_purpose.strip():
                vp.teaching_purpose = f"Make Unit {unit.number} perform one visible cognitive job."
            if not vp.visual_type.strip() or vp.visual_type.strip().lower() in {"generic", "boxes", "cards", "infographic"}:
                vp.visual_type = expected_type
            # Technical source-native types override obviously generic concept layouts.
            if unit.number in range(6, 11) and unit.knowledge_types and unit.knowledge_types[0] != "CONCEPT":
                if vp.visual_type in {"concept-map", "causal-concept-map", "cards", "generic-boxes"}:
                    vp.visual_type = expected_type
            if not vp.citation.strip():
                vp.citation = "ISCARB visualization based on source-locked P1 content"
            if not vp.focal_elements:
                vp.focal_elements = [x for x in [unit.title, *unit.core_content[:3]] if x][:4]
            if not vp.annotation_plan:
                vp.annotation_plan = [unit.engineering_question, unit.student_action][:2]
            if not vp.visual_evidence_role.strip():
                vp.visual_evidence_role = "Makes the source-grounded reasoning inspectable in the classroom."

    note = "CIMT+ computing visual normalization applied: source-native knowledge typing and one-dominant-visual planning across 20 Units."
    if note not in bp.release_notes:
        bp.release_notes.append(note)
    return bp
