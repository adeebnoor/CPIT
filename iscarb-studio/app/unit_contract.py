"""One instructional contract shared by generation, audit and targeted repair.

This describes pedagogy, not source facts. Passing the local role checks never
substitutes for independent review against the original lecture.
"""
from __future__ import annotations

import json


UNIT_JOBS = {
    1: "Open ONE ill-structured crisis and professional purpose. The plan's central_engineering_crisis is displayed on this slide. Include a concrete Decision: question and an Unknown: evidence gap in pedagogy_content. Do not reveal the diagnosis. Keep technical definitions for units 6–15.",
    2: "Domain Spine: map ALL locked source topic families in at least two source-grounded core entries, with a P1 anchor. This map is not first teaching of source details.",
    3: "Exactly five CLOs: core_content=[], source_passages=[], source_anchor=''. pedagogy_content contains exactly CLO1: through CLO5:, matching the locked plan's measurable CLO statements. Never attach source facts to this outcomes page.",
    4: "Exactly six pedagogy_content entries, one applied capability each: Analytical reasoning; Engineering judgment; Evidence-based reasoning; Socio-technical thinking; Risk-aware design; Ethical responsibility. core_content=[] and source_passages=[].",
    5: "Predict before explanation. Four separate pedagogy entries, IN ORDER, labeled PREDICT:, CONSTRAINT:, DERIVE:, NAME:. Each must have at least four meaningful words after its label. NAME identifies the derived principle; DERIVE explains why the constraint changes the prediction. Do not disclose the answer in the title/question.",
    6: "Teach the assigned P1 mechanism from first principles, with at least three substantive core/pedagogy entries in total. Trace the source mechanism, not a generic instruction to think.",
    7: "Teach assigned P1 architecture/implementation structure and ask the learner to trace or apply it. Preserve source components and relationships.",
    8: "Teach P1 and compare TWO defensible alternatives using three separate pedagogy entries: Alternative A:, Alternative B:, Trade-off:. Each has at least four meaningful words after the label. Name the real alternatives and what is sacrificed; do not invent an unsupported technology.",
    9: "Teach P1 with separate pedagogy entries Measure: and Falsifier:, each at least four meaningful words. Name an observable result, test conditions and a result that would disconfirm the decision. Unsupplied test data must be explicitly hypothetical.",
    10: "Design review: four separate pedagogy entries Known:, Unknown:, Decision-sensitive unknown:, Monitor:. Each has at least four meaningful words after its label, applied to this system. A heading alone does not count.",
    11: "Teach P1, then integrate a concrete Saudi/local application under an explicitly HYPOTHETICAL bounded constraint. The learner must solve it using ONLY mechanisms already taught in the current P1 lecture; do not import later-chapter technology and do not invent a national mandate.",
    12: "Teach P1 and integrate accountability: name the responsible role/owner, the evidence they check, and the sign-off/escalation decision. Keep the title source-first.",
    13: "Teach P1 and run a bounded scalability/trend stress test. Name one explicit numeric or structural variable (for example load, node count, centralized-to-distributed, or one-to-many deployments) and ask which source assumption fails FIRST. Open-ended 'what changes?' prompts do not pass.",
    14: "Teach P1 and integrate practitioner workload/wellbeing as a bounded design question or source-supported consequence, not an invented empirical claim.",
    15: "Teach assigned P1 content (including technical AI if actually in P1). Put instructional AI-use rules ONLY in pedagogy_content: AI MAY ASSIST: may generate candidate test cases/failure probes or structure drafts; AI MUST NOT BE TRUSTED AUTONOMOUSLY: may not approve/certify the design; Human sign-off: the learner personally checks P1, evidence and failure cases and owns the final decision. Never move these rules into core_content.",
    16: "Launch one source-grounded design/portfolio artifact with a trade-off and observable evidence. Name only the locked, fully supported ETEC readiness target(s) and the artifact that demonstrates them.",
    17: "Change a constraint, require peer critique and a revised/redesigned artifact with rerun evidence. Do not pre-solve with untaught technology.",
    18: "Evidence protocol lives in pedagogy_content, NOT core_content: Claim:, Evidence:, Warrant:, Counter-evidence:, Residual uncertainty:. Apply the chain to the learner's decision. Do not cite P1 as the source of this ISCARB method.",
    19: "Use exactly six capability criteria with four substantive levels. Every credited capability must be demonstrated through performance, a learner artifact and a P1 source anchor; recall alone earns no capability credit. These are assessment pedagogy, not P1 technical core.",
    20: "Bounded assurance: Claim, Evidence, Warrant, Residual uncertainty and APPROVE / CONDITIONALLY APPROVE / REDESIGN / REJECT. The learner must DEFEND the verdict with a P1 anchor plus a learner artifact and state counter-evidence/next verification. No absolute guarantees; assurance scaffolds stay in pedagogy.",
}

MASTER_GUIDELINES = """
ISCARB MASTER GUIDELINES (release conditions across all advanced software-engineering topics):
1) COGNITIVE LOAD: Never paste PRIMARY-source paragraphs into presenter slides. Use one short engineering maxim or very short bullets; keep narrative detail in P1 / speaker notes.
2) VISUAL-TEXT ALIGNMENT: Prefer a P1 figure that directly explains the Unit. If no useful P1 visual exists, use a semantically matched public visual or redraw. Never repeat the same asset in another Unit unless Unit 17 explicitly mutates/traces a variable on it.
3) BOUNDED LOCAL CONTEXT: Local scenarios are explicitly hypothetical, state a precise constraint, and may use only mechanisms already taught in this P1 lecture.
4) SCALABILITY/TREND: Name an explicit numeric or structural stress variable and ask which assumption fails first; reject generic 'what changes when it grows?' questions.
5) AI GOVERNANCE: AI may generate candidate tests/options/draft structure; accountable human engineering sign-off cannot be delegated to the model.
6) PERFORMANCE GRADING: Capability credit and final verdicts require defended learner performance, one learner artifact, and traceable P1 evidence.
"""

CHANNEL_CONTRACT = """
AUTHORITATIVE FIELD AND ROLE CONTRACT (applies to generators AND auditors):
core_content/source_passages contain source-supported technical knowledge only.
pedagogy_content contains instructional questions, reasoning steps, AI-use rules,
assessment and assurance scaffolds. Source-backed AI knowledge is not the same
as an ISCARB AI-use rule. In U15 retain the former in core, the latter in pedagogy.
U3 has no core/source passages. U18 evidence-method instructions stay in pedagogy.
Never invert these channels to satisfy an audit suggestion. Audit suggestions
are candidate advice, not authority to override these invariants or P1.
Every mandatory source ID must remain visibly taught in its locked unit 6–15.
Do not invent facts, truncate source lists, or count labels as substantive work.
Use complete concise sentences; remove repetition rather than source detail.
Keep questions/actions brief, and normally 2–5 concise teaching propositions per
technical unit. Pedagogy should be specific but short enough to project.
"""

# Tag owners make cross-batch obligations explicit; tags are not evidence of
# performance and the independent semantic audit must still inspect the work.
TAG_OWNERS = {
    "IDR-1": 6, "IDR-2": 7, "IDR-3": 16, "IDR-4": 13,
    "IDR-5": 1, "IDR-6": 11, "IDR-7": 2, "IDR-8": 12,
    "IDR-9": 14, "IDR-10": 15, "IDR-11": 18, "IDR-12": 2,
    "IDR-13": 18, "IDR-14": 16,
    "EER-1": 1, "EER-2": 5, "EER-3": 5, "EER-4": 8,
    "EER-5": 8, "EER-6": 10, "EER-7": 9, "EER-8": 9,
    "EER-9": 17, "EER-10": 17, "EER-11": 10, "EER-12": 16,
}


def contract_text(numbers=range(1, 21)):
    result = [MASTER_GUIDELINES, CHANNEL_CONTRACT]
    for n in numbers:
        tags = [tag for tag, owner in TAG_OWNERS.items() if owner == n]
        result.append(f"UNIT {n}: {UNIT_JOBS[n]} Required obligations: {', '.join(tags)}. "
                      "Demonstrate them in the learner's work and record IDR tags in inherited_requirements and EER tags in elite_requirements; labels alone never prove compliance.")
        if n == 9:
            result.append("EER-7: ask for an estimate before measurement/precision; use source values or a qualitative estimate when numerical evidence is absent. Do not invent numerical facts.")
    return "\n".join(result)


def role_problems(bp, numbers=None):
    """The SAME executable checks as the final gate, localized for correction."""
    from .gate_v15 import unit_role_checks
    selected = set(numbers if numbers is not None else range(1, 21))
    problems = {}
    for key, passed in unit_role_checks(bp, selected).items():
        if not passed:
            problems[key] = "Repair this unit's instructional job; see its authoritative contract."
    for unit in bp.units:
        if unit.number not in selected:
            continue
        if unit.number == 4 and unit.core_content:
            problems["unit04_reserved_channel"] = "H-Stack capabilities are pedagogy, not P1 core; regenerate with empty core/source_passages."
        if unit.number == 18 and any(term in " ".join(unit.core_content).lower()
                                     for term in ("warrant", "counter-evidence", "residual uncertainty", "evidence policy framework")):
            problems["unit18_reserved_channel"] = "Move evidence-method instructions to pedagogy; preserve actual technical teaching in its assigned unit."
    return problems


def repair_context(bp, numbers):
    from .presenter_v44 import readability_problems
    problems = role_problems(bp, numbers)
    problems.update({f"presenter_unit{n:02d}": reason for n, reason in readability_problems(bp).items() if n in numbers})
    return "\nAUTHORITATIVE CORRECTION TARGETS:\n" + json.dumps(problems) + contract_text(numbers)
