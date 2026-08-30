from __future__ import annotations

"""Quota-safe, source-bounded draft builder.

This is deliberately NOT a release generator.  It exists so a faculty upload is
never lost when the semantic model quota is unavailable.  It uses only the
SourceProfile's P1 checkpoints/excerpts, covers every major checkpoint by Unit
15, exposes no fabricated ETEC mapping, and must remain BLOCKED until the normal
semantic generation/audit path succeeds.
"""

from itertools import cycle

from .models import (
    Blueprint, CLO, CoverageLedgerEntry, LectureUnit, ReadinessAlignment,
    RubricCriterion, SourceProfile, TopicCoverage, VisualPlan,
)

# One-word competency labels give a learner nothing to act on. Each entry names
# the competency and what its absence costs in this decision.
_HSTACK = [
    "Analytical reasoning — decompose the chapter mechanism until each step can be checked on its own.",
    "Engineering judgment — choose between defensible options when the source does not decide for you.",
    "Evidence-based reasoning — state which source statement supports each claim, and which does not.",
    "Socio-technical thinking — account for the people and processes the mechanism actually runs through.",
    "Risk-aware design — identify the failure that would be least recoverable and design against it first.",
    "Ethical responsibility — refuse to present an unverified result as if it were established.",
]


def _clip(text: str, n: int = 220) -> str:
    text = " ".join(str(text or "").split()).strip()
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0]


def _major(profile: SourceProfile):
    rows = [x for x in profile.coverage_items if x.importance == "major"]
    return rows or profile.coverage_items[:1]


def _groups(rows, count: int = 10):
    buckets = [[] for _ in range(count)]
    for i, row in enumerate(rows):
        buckets[min(count - 1, (i * count) // max(1, len(rows)))].append(row)
    return buckets


def _anchors(rows) -> str:
    return "; ".join(dict.fromkeys(x.source_anchor for x in rows if x.source_anchor)) or "[P1]"


def _visual(kind: str, purpose: str, rows=()) -> VisualPlan:
    return VisualPlan(
        visual_type=kind,
        teaching_purpose=purpose,
        source_visual_available=False,
        reuse_mode="NEW",
        citation="ISCARB deterministic source-bounded draft",
        focal_elements=[_clip(x.label, 42) for x in list(rows)[:6]],
        annotation_plan=[_clip(x.why_important, 130) for x in list(rows)[:6] if x.why_important],
        visual_evidence_role="Draft representation; faculty review required before release.",
    )


# A learner activity that reads the same on all twenty slides teaches nothing.
# The knowledge type already says what kind of thinking the checkpoint demands,
# so the activity is derived from it and names the checkpoint out loud.
_ACTION_BY_KNOWLEDGE = {
    "PROCESS": "Walk {focus} step by step, then mark the step that fails first under pressure and say why.",
    "ALGORITHM": "Trace {focus} on one small input, then state the case that breaks it.",
    "CODE": "Read {focus} line by line and name the assumption the code depends on.",
    "ARCHITECTURE": "Redraw {focus} from memory, then mark the interface that carries the most risk.",
    "EQUATION": "Substitute one realistic value into {focus} and state what the result would have to be to change the decision.",
    "PROTOCOL": "Play both sides of {focus} and identify the message whose loss is unrecoverable.",
    "TRADE_OFF": "State both sides of {focus}, then commit to one and name the cost you accept.",
    "DESIGN_PRINCIPLE": "Apply {focus} to the central decision, then describe a case where following it would be wrong.",
    "SYSTEM_BEHAVIOR": "Predict how {focus} behaves under load, then name the observation that would refute you.",
    "DATA_MODEL": "Populate {focus} with one realistic record and find the field that cannot be filled honestly.",
    "RESULT": "State what {focus} establishes, then name the condition under which it would not hold.",
    "CONCEPT": "Define {focus} in your own words, then give one example and one non-example.",
}


# When a source yields fewer checkpoints than teaching slots, the old code reused
# the last checkpoint for every remaining unit and produced ten identical slides.
# The source cannot be invented, but the teaching move can differ: each slot asks
# a different question of the same material. These live in the pedagogy channel,
# so triple provenance stays intact - nothing here is presented as source content.
_TEACHING_MOVES = [
    ("mechanism", "How does {focus} actually work, step by step?",
     ["Name each step and what it consumes and produces.",
      "Mark the step you could not perform from the source alone."]),
    ("boundary", "Where does {focus} stop applying?",
     ["State the condition under which the mechanism no longer holds.",
      "Name one system this would be the wrong choice for, and why."]),
    ("failure", "What is the first thing to fail in {focus}, and how would you notice?",
     ["Describe the failure signal a practitioner would actually observe.",
      "Say which failure is recoverable and which is not."]),
    ("alternative", "What would you use instead of {focus}, and what would it cost?",
     ["Name one defensible alternative and the property it trades away.",
      "State the condition that decides between them."]),
    ("evidence", "What evidence would show {focus} is working as intended?",
     ["Name the observation that supports the claim.",
      "Name the observation that would refute it."]),
    ("application", "Apply {focus} to the central decision of this lecture.",
     ["Carry the mechanism through to a concrete choice, not a restatement.",
      "State what the decision would be if the mechanism did not exist."]),
    ("misconception", "What is commonly misunderstood about {focus}?",
     ["State the plausible-but-wrong reading and why it is wrong.",
      "Give the source statement that settles it."]),
    ("scale", "What changes about {focus} as the system grows?",
     ["Describe the behaviour at small scale and at large scale.",
      "Identify the assumption that breaks first."]),
    ("dependency", "What must already be true for {focus} to be usable?",
     ["List the preconditions the source assumes without stating them.",
      "Say what happens when one precondition is absent."]),
    ("verification", "How would you verify {focus} before relying on it?",
     ["Define the check and the result that would pass it.",
      "Say what remains unverified after the check succeeds."]),
]

# Below this, a slide is a blank minute rather than a taught one. Items are
# counted as well as words: one long sentence is still one box on the slide.
_MIN_UNIT_WORDS = 14
_MIN_UNIT_ITEMS = 3


def _teaching_move(idx: int, focus: str):
    """The move for teaching slot `idx` (6..15)."""
    name, question, scaffold = _TEACHING_MOVES[(idx - 6) % len(_TEACHING_MOVES)]
    short = focus if len(focus) <= 70 else focus[:70].rsplit(" ", 1)[0]
    return name, question.format(focus=short), list(scaffold)


def _student_action_for(bucket, labels) -> str:
    focus = labels[0] if labels else "this source mechanism"
    if len(focus) > 70:
        focus = focus[:70].rsplit(" ", 1)[0]
    kinds = [x.knowledge_type for x in bucket] or ["CONCEPT"]
    template = _ACTION_BY_KNOWLEDGE.get(kinds[0], _ACTION_BY_KNOWLEDGE["CONCEPT"])
    return template.format(focus=focus)


def _readiness_trail(profile: SourceProfile, clos, rows) -> list[ReadinessAlignment]:
    """A traceable readiness trail, explicitly not an approved ETEC mapping.

    Faculty need to see what this lecture can and cannot evidence. An empty list
    shows nothing; inventing SLO codes would claim an alignment nobody approved.
    So every entry links a real source family to the units that actually produce
    an artifact, and marks the standardized references UNVERIFIED in place.
    """
    families = [x.name for x in profile.topic_families[:5]] or [x.label for x in rows[:5]]
    trail: list[ReadinessAlignment] = []
    for i, family in enumerate(families):
        trail.append(ReadinessAlignment(
            gku=f"Computing knowledge exercised by: {family}",
            sku=f"UNVERIFIED — locally derived from P1 family '{family}'; no approved ETEC SKU mapping was produced in this pass.",
            slo_refs=["UNVERIFIED-NO-APPROVED-SLO-MAPPING"],
            klo_refs=["UNVERIFIED-NO-APPROVED-KLO-MAPPING"],
            strength="supporting",
            rationale=(
                f"Units 16-20 produce artifacts that exercise '{family}', so the capability is evidenced locally. "
                "Standardized readiness stays unverified because semantic alignment did not run, and no page of the "
                "ETEC standard is cited in this deterministic pass."
            ),
            atomicity_evidence=(
                f"One family, one claim: '{family}' is evidenced only by the listed units, each of which records its own "
                "artifact and learner action."
            ),
            clo_ids=[clos[min(i, len(clos) - 1)].id],
            evidence_units=[16, 18, 19],
            standard_source_pages=[0],
        ))
    return trail


def build_deterministic_blueprint(profile: SourceProfile) -> Blueprint:
    rows = _major(profile)
    groups = _groups(rows, 10)
    family_names = [x.name for x in profile.topic_families] or [x.label for x in rows[:6]]
    title = profile.lecture_title

    clos = [
        CLO(id="CLO1", statement=f"Explain the source-defined foundations of {title}.", evidence_expected="Source-anchored concept map or explanation."),
        CLO(id="CLO2", statement=f"Apply source-defined mechanisms from {title} to a bounded engineering task.", evidence_expected="Worked application using only P1 mechanisms."),
        CLO(id="CLO3", statement="Compare defensible alternatives and justify an engineering trade-off.", evidence_expected="Decision comparison with explicit trade-off."),
        CLO(id="CLO4", statement="Evaluate evidence, uncertainty, and a falsification condition for the decision.", evidence_expected="Evidence note with counter-evidence and residual uncertainty."),
        CLO(id="CLO5", statement="Defend a bounded professional decision and identify what must be verified next.", evidence_expected="Short decision record with source anchors and review status."),
    ]

    units: list[LectureUnit] = []
    mins = [4,5,4,4,5] + [5]*10 + [4,4,4,3,3]
    phases = ["IFHAM"]*5 + ["MARIS"]*5 + ["ATQAN"]*5 + ["MAYYIZ"]*5

    def add(n, title_, q, core, ped, action, takeaway, kind, anchor="N/A — ISCARB PEDAGOGY", evidence=""):
        units.append(LectureUnit(
            number=n, phase=phases[n-1], title=title_, engineering_question=q,
            core_content=[_clip(x, 250) for x in core], pedagogy_content=[_clip(x, 220) for x in ped],
            enrichment_content=[], enrichment_basis=[], scenario_assumptions=[],
            knowledge_types=list(dict.fromkeys([x.knowledge_type for x in (groups[n-6] if 6 <= n <= 15 else [])])) or ["CONCEPT"],
            visual_suggestion=kind, visual_plan=_visual(kind, q, groups[n-6] if 6 <= n <= 15 else []),
            student_action=action, takeaway=takeaway, cimtlens=["C"],
            clo_ids=[clos[min(4, max(0, (n-1)//4))].id], source_anchor=anchor,
            inherited_requirements=[], elite_requirements=[], evidence=evidence,
            contextual_enrichment=False, verify_before_release=True, planned_minutes=mins[n-1],
        ))

    add(1, f"{title}: the engineering decision", "What can we responsibly decide before the missing evidence is resolved?", [],
        ["Start from the source and an evidence gap; do not reveal the diagnosis first."],
        "Write one prediction and one piece of evidence you would need before committing.",
        "A defensible decision begins by separating what the source supports from what remains unknown.", "title")
    add(2, "Domain spine", "What are the major source families that structure this chapter?", [*family_names[:8]],
        ["Connect the chapter families before studying mechanisms in isolation."], "Sketch the source spine and mark the family you expect to be most decision-sensitive.",
        "The chapter is one connected engineering argument, not a list of slides.", "concept-map", "[P1]")
    add(3, "Five outcomes for this lecture", "What should you be able to explain, apply, compare, evaluate, and defend?", [],
        [f"{c.id}: {c.statement}" for c in clos], "Choose the CLO that will be hardest to prove and state why.",
        "Every outcome requires visible evidence, not recognition alone.", "table")
    add(4, "Engineering judgment stack", "Which competencies are required to turn chapter knowledge into a decision?", [], _HSTACK,
        "Identify which competency would fail first if the source were misunderstood.", "Judgment combines technical reasoning, evidence, risk, people, and responsibility.", "concept-map")
    first = rows[:2]
    add(5, "Prediction gate", "PREDICT before seeing the full mechanism: what result follows from the source constraints?",
        [_clip(x.why_important or x.label, 240) for x in first], ["PREDICT → CONSTRAINT → DERIVE → NAME"],
        "Commit to a prediction, then identify the source statement that could overturn it.", "Prediction must precede explanation.", "process", _anchors(first))

    visual_cycle = cycle(["concept-map", "process", "comparison", "timeline", "architecture", "table"])
    for idx, bucket in enumerate(groups, start=6):
        # A thin source leaves teaching slots without their own checkpoint.
        reused = not bucket
        if reused:
            bucket = rows[-1:]
        labels = [x.label for x in bucket]
        core = [x.why_important or x.label for x in bucket]
        kind = next(visual_cycle)
        if any(x.knowledge_type == "PROCESS" for x in bucket): kind = "process"
        elif any(x.knowledge_type == "ARCHITECTURE" for x in bucket): kind = "architecture"
        elif any(x.knowledge_type == "TRADE_OFF" for x in bucket): kind = "comparison"
        if idx == 8: kind = "comparison"
        if idx == 9: kind = "table"
        title_ = " / ".join(labels[:2]) if labels else f"Source mechanism {idx-5}"
        move_name, move_question, move_scaffold = _teaching_move(idx, labels[0] if labels else "this mechanism")
        if reused:
            # Same material, a different question of it - never the same slide twice.
            title_ = f"{title_}: {move_name}"
        ped = []
        if idx == 8: ped = ["Compare at least two source-derived alternatives; make the trade-off explicit."]
        elif idx == 9: ped = ["State the measure and the observation that would falsify the current decision."]
        elif idx == 10: ped = ["KNOWN", "UNKNOWN", "DECISION-SENSITIVE UNKNOWN", "WHAT WE MONITOR"]
        elif idx == 11: ped = ["Use a Saudi/Gulf constraint only as an explicit hypothetical unless P1 supports it."]
        elif idx == 12: ped = ["Name the responsible role, evidence owner, and sign-off point without adding new technology."]
        elif idx == 13: ped = ["Ask what changes next while keeping the source mechanism dominant."]
        elif idx == 14: ped = ["Identify the practitioner/operational consequence implied by the source mechanism; do not invent psychology claims."]
        elif idx == 15: ped = ["AI MAY ASSIST", "AI MUST NOT BE TRUSTED AUTONOMOUSLY", "Claim → Assumption → Source Check → Test → Failure Search → Human Sign-off"]
        question = move_question if reused else (
            f"How does {labels[0] if labels else 'this source mechanism'} change the engineering decision?")
        action = move_scaffold[0] if reused else _student_action_for(bucket, labels)
        # Every teaching slot carries its move. A thin source gives one checkpoint
        # line, and one line is a single oversized box on the slide - the move is
        # what makes that checkpoint workable, so it always ships beside it.
        ped = [*ped, *move_scaffold]
        if len([x for x in (*core, *ped) if str(x).strip()]) < _MIN_UNIT_ITEMS:
            ped = [*ped, f"Name what {labels[0] if labels else 'this mechanism'} would cost if it were absent."]
        add(idx, title_, question, core, ped, action,
            f"Source checkpoint(s) covered: {', '.join(labels)}",
            kind, _anchors(bucket), evidence=f"P1 checkpoint evidence: {', '.join(x.id for x in bucket)}")

    add(16, "Build the decision artifact", "Can you integrate the chapter mechanisms into one coherent engineering response?", [],
        ["Use only mechanisms already taught from P1; nothing new may be introduced here.",
         "State the decision, then the chapter mechanism that drives it.",
         "Name one alternative you rejected and the trade-off that decided it.",
         "Attach the evidence that supports the choice and the uncertainty that remains."],
        "Build one decision artifact that connects mechanism, alternative, trade-off, evidence, and uncertainty.",
        "Integration is where chapter knowledge becomes professional capability.", "portfolio",
        evidence="Learner-produced decision artifact integrating the chapter mechanisms.")
    add(17, "Change one constraint", "What changes when one decision-sensitive constraint changes?", [],
        ["Pick the constraint whose change would most alter the decision, and say why it is that one.",
         "Rerun the chapter mechanism under the changed constraint rather than adjusting the conclusion.",
         "Record which part of the original reasoning survived and which part did not.",
         "Peer critique must challenge the revised reasoning, not merely agree with it."],
        "Mutate one constraint, redesign the decision, then exchange critiques.",
        "Robust understanding survives a changed constraint.", "mutation",
        evidence="Redesigned decision plus the peer critique exchanged on it.")
    add(18, "Defend the decision", "What evidence justifies the claim, and what evidence would weaken it?", [],
        ["CLAIM — the decision you are defending, stated in one sentence.",
         "EVIDENCE — the specific source statement or artifact that supports it.",
         "WARRANT — why that evidence licenses this claim rather than a weaker one.",
         "COUNTER-EVIDENCE — the strongest source-supported case against your claim.",
         "RESIDUAL UNCERTAINTY — what remains unresolved, and what would resolve it."],
        "Write the five-part evidence argument and identify the weakest link.",
        "A strong engineering answer is auditable and falsifiable.", "argument", evidence="Learner-generated evidence argument.")
    add(19, "What you can prove", "Which capabilities can you demonstrate from this lecture, and which remain unverified?", [],
        ["Technical correctness + source fidelity", "Mechanism reasoning", "Alternatives + trade-offs", "Evidence + falsification", "Constraint adaptation", "Professional accountability", "ETEC readiness is UNVERIFIED in quota-safe fallback mode."],
        "Attach one artifact to each capability you claim; do not claim readiness without an approved SLO mapping.",
        "Capability claims require evidence. Standardized readiness remains unverified until semantic alignment runs.", "rubric",
        evidence="Capability-to-artifact index naming which claims are evidenced and which remain unverified.")
    add(20, "Take-home decision", "APPROVE, CONDITIONALLY APPROVE, REDESIGN, or REJECT — what does the evidence support?", [],
        ["APPROVE — the evidence supports the decision as it stands.",
         "CONDITIONALLY APPROVE — it holds only if a named condition is verified first.",
         "REDESIGN — the mechanism is sound but this application of it is not.",
         "REJECT — the evidence contradicts the decision or is too thin to support it.",
         "Keep residual uncertainty visible and state what must be verified next."],
        "Choose the bounded verdict and write the next verification action.",
        "No release claim is allowed from fallback mode; this draft requires semantic review.", "verdict",
        evidence="Bounded verdict with the named next verification action.")

    # Map every major source checkpoint to a teaching unit no later than Unit 15.
    ledger = []
    row_to_unit = {}
    for unit_no, bucket in enumerate(groups, start=6):
        for row in bucket:
            row_to_unit[row.id] = unit_no
    for row in rows:
        unit_no = row_to_unit.get(row.id, 6)
        ledger.append(CoverageLedgerEntry(
            coverage_id=row.id, label=row.label, knowledge_type=row.knowledge_type,
            source_anchor=row.source_anchor, first_taught_unit=unit_no,
            reinforced_units=[16,18], depth="CONCISE" if len(rows) > 12 else "DEEP",
            representation=f"Unit {unit_no}: source checkpoint + learner application",
        ))

    topic_coverage = [
        TopicCoverage(topic_family=x.name, source_anchor=x.source_anchor, first_taught_unit=min(15, 6+i), reinforced_units=[16,18])
        for i, x in enumerate(profile.topic_families[:10])
    ] or [TopicCoverage(topic_family=rows[0].label, source_anchor=rows[0].source_anchor, first_taught_unit=6, reinforced_units=[16,18])]

    rubric_names = [
        "Technical correctness + source fidelity", "First-principles / mechanism reasoning",
        "Alternatives + trade-off engineering judgment", "Evidence + falsification / verification quality",
        "Constraint adaptation + risk-aware redesign", "Professional accountability + readiness discipline",
    ]
    rubric = [RubricCriterion(
        criterion=name,
        distinguished="Source-anchored, complete, precise, and transferable.",
        ready="Correct and supported with a clear artifact.",
        developing="Partly correct or incompletely evidenced.",
        not_yet_ready="Unsupported, incomplete, or contradicted by P1.",
        readiness_refs=["UNVERIFIED — evidenced by Units 16, 18 and 19; no approved ETEC SLO mapping in this pass."],
    ) for name in rubric_names]

    return Blueprint(
        lecture_title=title,
        engineering_thesis=f"Use the complete primary-source chapter to make a bounded engineering decision about {title}.",
        central_engineering_crisis=f"A team must make a consequential decision about {title} while distinguishing source-supported knowledge from unresolved assumptions.",
        named_ethical_purpose="Make an evidence-proportionate professional decision without overstating what the source or the learner artifact proves.",
        clos=clos, units=units, source_topic_families=family_names[:20], topic_coverage=topic_coverage,
        coverage_ledger=ledger, readiness_alignment=_readiness_trail(profile, clos, rows), rubric_criteria=rubric,
        release_notes=["QUOTA-SAFE DRAFT ONLY: semantic generation/audit unavailable; readiness unverified; release forbidden."],
        session_minutes=90, source_manifest=profile.source_manifest, deferred_topics=[],
    )
