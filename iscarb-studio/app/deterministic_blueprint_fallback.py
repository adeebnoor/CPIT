from __future__ import annotations

"""Quota-safe, source-bounded draft builder.

This is deliberately NOT a release generator.  It exists so a faculty upload is
never lost when the semantic model quota is unavailable.  It uses only the
SourceProfile's P1 checkpoints/excerpts, covers every major checkpoint by Unit
15, exposes no fabricated ETEC mapping, and must remain BLOCKED until the normal
semantic generation/audit path succeeds.
"""

import re
from itertools import cycle

from .models import (
    Blueprint, CLO, CoverageLedgerEntry, LectureUnit, ReadinessAlignment,
    RubricCriterion, SourceProfile, TopicCoverage, VisualPlan,
)
from .unit_contract import TAG_OWNERS

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


# CIMT is the intellectual spine: Concept -> Implementation -> Measurement ->
# Trend. Every unit used to be stamped "C", so three quarters of the compass was
# missing from a deck that actually performs all four jobs - the mechanism units
# implement, the measurement/review units measure, and the evolution, AI-audit
# and verdict units read the trend. The lens follows the slot's contracted job.
_CIMT_BY_UNIT = {
    1: ["C"], 2: ["C"], 3: ["C"], 4: ["C"], 5: ["C"],
    6: ["C", "I"], 7: ["I"], 8: ["I"], 9: ["M"], 10: ["M"],
    11: ["I"], 12: ["I", "M"], 13: ["T"], 14: ["M", "T"], 15: ["T"],
    16: ["I"], 17: ["T"], 18: ["M"], 19: ["M"], 20: ["T"],
}


def _obligations(unit_number: int) -> tuple[list[str], list[str]]:
    """The IDR/EER tags this slot owns under the shared unit contract.

    The slots are built to the same contract the tag map describes, so the
    obligations were being performed and simply never recorded. Recording them
    is bookkeeping, not proof: the role checks in Gate v15 are what test whether
    the work is actually visible to the learner.
    """
    owned = [tag for tag, owner in TAG_OWNERS.items() if owner == unit_number]
    return (
        sorted([x for x in owned if x.startswith("IDR")], key=lambda t: int(t.split("-")[1])),
        sorted([x for x in owned if x.startswith("EER")], key=lambda t: int(t.split("-")[1])),
    )


def _clip(text: str, n: int = 220) -> str:
    text = " ".join(str(text or "").split()).strip()
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0]


def _major(profile: SourceProfile):
    rows = [x for x in profile.coverage_items if x.importance == "major"]
    # A source-significant example can be essential teaching material even when
    # it is not itself a numbered chapter section.  Use such examples to fill a
    # teaching slot before recycling an earlier checkpoint; administrative
    # recap/assignment slides remain excluded.
    if len(rows) < 10:
        excluded = ("assignment", "to master", "take-home", "class", "contents")
        examples = [
            x for x in profile.coverage_items
            if x.importance != "major"
            and (x.knowledge_type == "EXAMPLE" or re.search(r"\bAI\b|contemporary|trend", x.label, re.I))
            and not any(term in x.label.lower() for term in excluded)
        ]
        rows.extend(x for x in examples if x.id not in {r.id for r in rows})
    return rows or profile.coverage_items[:1]


def _atomic_source_entries(row, limit: int | None = None) -> list[str]:
    """Recover the teachable statements flattened into one source excerpt.

    Source profiling preserves slide lines with a middle-dot separator.  The
    old fallback clipped the entire excerpt to 250 characters and stored it as
    one ``core_content`` entry, dropping named list members and producing one
    oversized box.  Keep the source order, remove duplicated headings/furniture,
    and expose each remaining statement as its own learner-visible entry.
    """
    raw = str(row.why_important or row.label or "")
    parts = re.split(r"\s*[·•▪■◆❑❒❏]\s*", raw)
    label_key = re.sub(r"[^a-z0-9]+", " ", str(row.label).lower()).strip()
    furniture = ("adeeb noor", "it department", "faculty of computing", "king abdulaziz university", "fall 2025")
    out: list[str] = []
    for part in parts:
        text = " ".join(part.split()).strip(" -:;,")
        key = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
        if not text or any(x in text.lower() for x in furniture):
            continue
        if key == label_key or text in out:
            continue
        # Physical PDF line breaks are not sentence boundaries. Rejoin wrapped
        # continuations before constructing learner-facing statements.
        dangling = r"\b(of|for|to|the|a|an|and|or|in|on|at|by|with|from|that|is|are|it|as|its|be|more|high)$"
        if out and (text[:1].islower() or re.search(dangling, out[-1], re.I)):
            out[-1] += " " + text
        else:
            out.append(text)
    out = out or [str(row.why_important or row.label)]
    return out[:limit] if limit else out


def _row_weight(row) -> int:
    return sum(len(statement.split()) for statement in _atomic_source_entries(row))


def _groups(rows, count: int = 10):
    """Split the checkpoints across the teaching slots, in source order, by weight.

    Splitting by position alone gave each slot the same number of source pages
    regardless of what was on them, so a slot that drew a two-word slide became a
    hollow teaching minute while its neighbour carried three dense pages. The
    split still never reorders the chapter; it only chooses where to cut.
    """
    rows = list(rows)
    buckets = [[] for _ in range(count)]
    if not rows:
        return buckets
    weights = [max(1, _row_weight(row)) for row in rows]
    remaining_weight = sum(weights)
    index = 0
    for slot in range(count):
        slots_left = count - slot
        # Always leave one checkpoint for each slot that still has to be filled.
        available = len(rows) - index - (slots_left - 1)
        if available <= 0:
            # Fewer checkpoints than slots left: one each, in source order, so no
            # checkpoint is left out of the ledger it is supposed to be taught in.
            for spare in range(slot, count):
                if index >= len(rows):
                    break
                buckets[spare].append(rows[index])
                index += 1
            break
        if slots_left == 1:
            buckets[slot] = rows[index:]
            break
        target = remaining_weight / slots_left
        taken = 0
        while available > 0:
            buckets[slot].append(rows[index])
            taken += weights[index]
            remaining_weight -= weights[index]
            index += 1
            available -= 1
            if taken >= target:
                break
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
        annotation_plan=[
            _clip(statement, 145)
            for row in list(rows)[:6]
            for statement in _atomic_source_entries(row, 3)
        ][:8],
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


# Each teaching slot has a contracted function (prompts.py section 10). The move
# is how that function reaches the learner, so the slot -> move mapping is fixed
# here rather than rotated: slot 8 owes the learner an alternative and its
# trade-off, slot 9 owes evidence and falsification, slot 15 owes an audit. A
# modulo rotation happened to satisfy some slots and contradict others.
_MOVE_FOR_SLOT = {
    6: "mechanism",      # Mechanism deep dive
    7: "dependency",     # Implementation grounded in supplied mechanisms
    8: "alternative",    # Two defensible alternatives + trade-off
    9: "evidence",       # Measurement + falsification
    10: "boundary",      # Design review: known / unknown / decision-sensitive
    11: "application",   # Source-first application
    12: "failure",       # Accountability: what fails, who notices, who signs off
    13: "scale",         # Evolution / improvement
    14: "misconception", # Operating consequences
    15: "verification",  # Maturity / audit
}
_MOVES_BY_NAME = {name: (name, q, sc) for name, q, sc in _TEACHING_MOVES}


# Slide headings are often written as questions ("What is dependability").
# Substituted into a move template that already asks one, they produce
# "How does What is dependability actually work" - so the interrogative opener
# is dropped and only the subject is carried into the question.
_INTERROGATIVE_OPENER = re.compile(
    r"^(what(?:\s+is|\s+are|\s+do|\s+does)?|why(?:\s+is|\s+are|\s+do|\s+does)?|"
    r"how(?:\s+is|\s+are|\s+do|\s+does|\s+to)?|when(?:\s+is|\s+are)?|"
    r"where(?:\s+is|\s+are)?|who(?:\s+is|\s+are)?)\s+",
    re.IGNORECASE,
)


def _as_noun_phrase(focus: str) -> str:
    """Reduce a heading to the subject a question template can be built on."""
    text = str(focus or "").strip().rstrip("?").strip()
    stripped = _INTERROGATIVE_OPENER.sub("", text, count=1).strip()
    # Only accept the reduction when something substantive survives.
    return stripped if len(stripped.split()) >= 1 and len(stripped) >= 3 else text


# A checkpoint label is a heading, not a sentence to be dropped whole into a
# question. Clipping it at a character budget left questions ending on "and" or
# "of", which reads as broken English and fails the mid-thought gate.
_FOCUS_DANGLING = re.compile(
    r"^(of|for|to|the|a|an|and|or|in|on|at|by|with|from|that|which|is|are|as|its|be|than|then)$",
    re.IGNORECASE,
)
MAX_FOCUS_CHARS = 70


def _short_focus(focus: str) -> str:
    text = " ".join(str(focus or "").split())
    if len(text) > MAX_FOCUS_CHARS:
        text = text[:MAX_FOCUS_CHARS].rsplit(" ", 1)[0]
    words = text.rstrip(" ,;:-").split()
    while len(words) > 2 and _FOCUS_DANGLING.match(words[-1]):
        words.pop()
    return " ".join(words).rstrip(" ,;:-") or "this source mechanism"


def _teaching_move(idx: int, focus: str):
    """The move for teaching slot `idx` (6..15)."""
    key = _MOVE_FOR_SLOT.get(idx)
    if key is None:
        name, question, scaffold = _TEACHING_MOVES[(idx - 6) % len(_TEACHING_MOVES)]
    else:
        name, question, scaffold = _MOVES_BY_NAME[key]
    short = _short_focus(_as_noun_phrase(focus))
    return name, question.format(focus=short), list(scaffold)


def _fill_rows(groups, rows) -> list:
    """Checkpoints for the teaching slots the source could not fill.

    Every empty slot used to borrow rows[-1:], so a chapter with eight
    checkpoints and ten slots showed its last checkpoint three times over -
    the learner reads the same page under three headings and the deck covers
    fewer topics than it has slides. Prefer checkpoints no slot already owns,
    richest first; only once those run out does a checkpoint appear twice, and
    then the least-used one goes next.
    """
    owned = {id(r) for bucket in groups for r in bucket}
    unowned = [r for r in rows if id(r) not in owned]
    unowned.sort(key=lambda r: len(str(r.why_important or r.label)), reverse=True)
    holes = sum(1 for bucket in groups if not bucket)
    fill = unowned[:holes]
    if len(fill) < holes and rows:
        # Not enough distinct material: repeat in source order rather than
        # hammering one checkpoint, so the repeats are at least spread out.
        pool = [r for r in rows if id(r) not in {id(x) for x in fill}] or list(rows)
        while len(fill) < holes:
            fill.append(pool[len(fill) % len(pool)])
    return fill


def _student_action_for(bucket, labels) -> str:
    focus = labels[0] if labels else "this source mechanism"
    if len(focus) > 70:
        focus = focus[:70].rsplit(" ", 1)[0]
    kinds = [x.knowledge_type for x in bucket] or ["CONCEPT"]
    template = _ACTION_BY_KNOWLEDGE.get(kinds[0], _ACTION_BY_KNOWLEDGE["CONCEPT"])
    return template.format(focus=focus)


# Publishing five readiness rows never made the trail more informative; the gate
# asks for a minimum-sufficient claim, and the draft has exactly one thing to say
# per family it can point at.
MAX_READINESS_ROWS = 2


def _readiness_trail(profile: SourceProfile, clos, rows) -> list[ReadinessAlignment]:
    """A traceable readiness trail, explicitly not an approved ETEC mapping.

    Faculty need to see what this lecture can and cannot evidence. An empty list
    shows nothing; printing official SKU/SLO codes would present an alignment
    nobody approved as if it were standardized. So each entry names a real source
    family, points at the units that actually produce an artifact, and keeps the
    standardized references marked UNVERIFIED in place.
    """
    families = [x.name for x in profile.topic_families[:MAX_READINESS_ROWS]] or [
        x.label for x in rows[:MAX_READINESS_ROWS]]
    trail: list[ReadinessAlignment] = []
    for i, family in enumerate(families):
        # These fields are printed on the readiness slide, so the placeholder stays
        # short and the explanation lives in the rationale beneath it. Spelling the
        # whole disclaimer into the SKU field pushed Unit 16 off its own canvas.
        # It also stays spaced rather than hyphenated: an unbreakable 34-character
        # token cannot be wrapped, and one such token overflows the column on its own.
        trail.append(ReadinessAlignment(
            gku="UNVERIFIED — no approved ETEC GKU mapping",
            sku="UNVERIFIED — no approved ETEC SKU mapping",
            slo_refs=["UNVERIFIED-NO-APPROVED-SLO-MAPPING"],
            klo_refs=["UNVERIFIED-NO-APPROVED-KLO-MAPPING"],
            strength="supporting",
            rationale=(
                f"Locally derived from P1 family '{family}'; no approved ETEC SKU mapping was produced in this pass. "
                f"Units 16-20 produce artifacts that exercise '{family}', so the capability is evidenced locally. "
                "Standardized readiness stays unverified because the source does not use enough of any published SKU "
                "vocabulary to reference it, and no semantic alignment ran in this pass."
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


# Floors the condensing pass must never cross: they are the gate's own teaching
# minimums, so trimming for legibility can never hollow a slide out.
MIN_CORE_WORDS_ON_A_TEACHING_SLIDE = 12
MIN_PAYLOAD_WORDS_ON_A_SLIDE = 28
MIN_VISIBLE_ITEMS_ON_A_SLIDE = 3
MAX_MERGED_STATEMENT_CHARS = 320
MAX_FIT_ROUNDS = 60
_CONTINUES_NOTE = "Condensed for the canvas: the slide carries the statements that fit; the rest of this checkpoint stays in the source at"


def _merge_shortest_pair(unit) -> bool:
    """Join the two adjacent source statements that cost the least to combine.

    Ten list members are ten boxes on the slide, and the box overhead - not the
    words - is what pushes the renderer below its readable floor. Merging keeps
    every source fact and buys back the space a dropped statement would have.
    """
    core = [str(x).strip() for x in unit.core_content if str(x).strip()]
    best, cost = None, None
    for i in range(len(core) - 1):
        combined = len(core[i]) + len(core[i + 1]) + 2
        if combined > MAX_MERGED_STATEMENT_CHARS:
            continue
        if cost is None or combined < cost:
            best, cost = i, combined
    if best is None:
        return False
    core[best] = core[best].rstrip(" .;,") + "; " + core[best + 1]
    del core[best + 1]
    unit.core_content = core
    return True


def _drop_last_statement(unit, teaching: bool) -> bool:
    """Stop the slide short of the excerpt, and record that in the unit's evidence."""
    core = [str(x).strip() for x in unit.core_content if str(x).strip()]
    if len(core) < 2:
        return False
    remaining = core[:-1]
    words = sum(len(x.split()) for x in remaining)
    payload = words + sum(len(str(x).split()) for x in unit.pedagogy_content)
    items = len(remaining) + len([x for x in unit.pedagogy_content if str(x).strip()])
    if teaching and (words < MIN_CORE_WORDS_ON_A_TEACHING_SLIDE
                     or payload < MIN_PAYLOAD_WORDS_ON_A_SLIDE
                     or items < MIN_VISIBLE_ITEMS_ON_A_SLIDE):
        return False
    unit.core_content = remaining
    # The note belongs in the unit's evidence record, not on the slide: the
    # presenter already prints this unit's source anchor, and spending three
    # lines of the canvas explaining the trim is what forced the next trim.
    anchor = str(unit.source_anchor or "P1").strip() or "P1"
    if _CONTINUES_NOTE not in unit.evidence:
        unit.evidence = f"{unit.evidence} {_CONTINUES_NOTE} {anchor}.".strip()
    return True


def fit_presenter_text(bp: Blueprint) -> Blueprint:
    """Condense the draft until every teaching slide is legible at the gate's floor.

    A source-preserving draft copies whole source pages into a teaching slot, and
    a slot carrying three pages cannot be projected: the renderer drops the body
    below 16pt and the release gate rejects the deck - which is what left a free
    draft with a list of unreadable-unit failures nobody could clear. Related
    statements are merged first, so no source fact is lost while the box count
    falls. Only when merging is exhausted does a slide stop short of the excerpt,
    and it then names the anchor where the checkpoint continues.
    """
    from .presenter_v44 import readability_problems

    for _round in range(MAX_FIT_ROUNDS):
        problems = [n for n in readability_problems(bp) if 5 <= n <= 15]
        if not problems:
            break
        progressed = False
        for number in problems:
            unit = bp.units[number - 1]
            if _merge_shortest_pair(unit) or _drop_last_statement(unit, teaching=number >= 6):
                progressed = True
        if not progressed:
            break
    return bp


def build_deterministic_blueprint(profile: SourceProfile) -> Blueprint:
    rows = _major(profile)
    groups = _groups(rows, 10)
    # When P1 itself contains an AI example, Unit 15 should audit that source
    # example rather than recycling an unrelated earlier checkpoint under an AI
    # heading.  This is a content move, not an enrichment: the row keeps its P1
    # anchor and the other checkpoints retain source order.
    ai_examples = [
        row for row in rows
        if row.knowledge_type == "EXAMPLE"
        and re.search(r"\bAI\b", f"{row.label} {row.why_important}", re.I)
    ]
    if ai_examples and not groups[9]:
        selected = ai_examples[-1]
        for bucket in groups:
            if selected in bucket:
                bucket.remove(selected)
        groups[9].append(selected)
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

    def add(n, title_, q, core, ped, action, takeaway, kind, anchor="N/A — ISCARB PEDAGOGY", evidence="",
            verify=False):
        inherited, elite = _obligations(n)
        units.append(LectureUnit(
            number=n, phase=phases[n-1], title=title_, engineering_question=q,
            core_content=[str(x).strip() for x in core], pedagogy_content=[str(x).strip() for x in ped],
            enrichment_content=[], enrichment_basis=[], scenario_assumptions=[],
            knowledge_types=list(dict.fromkeys([x.knowledge_type for x in (groups[n-6] if 6 <= n <= 15 else [])])) or ["CONCEPT"],
            visual_suggestion=kind, visual_plan=_visual(kind, q, groups[n-6] if 6 <= n <= 15 else []),
            student_action=action, takeaway=takeaway, cimtlens=list(_CIMT_BY_UNIT[n]),
            clo_ids=[clos[min(4, max(0, (n-1)//4))].id], source_anchor=anchor,
            inherited_requirements=inherited, elite_requirements=elite, evidence=evidence,
            # Flagging all twenty units said only "this is a draft", which the job
            # status, the audit report and the release notes already say, and it
            # left a gate failure no repair could ever clear. The flag now marks
            # the units that carry a real unresolved decision: a teaching slot the
            # source could not fill with its own checkpoint.
            contextual_enrichment=False, verify_before_release=verify, planned_minutes=mins[n-1],
        ))

    add(1, f"{title}: the engineering decision", "What can we responsibly decide before the missing evidence is resolved?", [],
        ["Start from the source and an evidence gap; do not reveal the diagnosis first."],
        "Write one prediction and one piece of evidence you would need before committing.",
        "A defensible decision begins by separating what the source supports from what remains unknown.", "title")
    add(2, "Domain spine", "What are the major source families that structure this chapter?", [*family_names],
        ["Connect the chapter families before studying mechanisms in isolation."], "Sketch the source spine and mark the family you expect to be most decision-sensitive.",
        "The chapter is one connected engineering argument, not a list of slides.", "concept-map", "[P1]")
    add(3, "Five outcomes for this lecture", "What should you be able to explain, apply, compare, evaluate, and defend?", [],
        [f"{c.id}: {c.statement}" for c in clos], "Choose the CLO that will be hardest to prove and state why.",
        "Every outcome requires visible evidence, not recognition alone.", "table")
    add(4, "Engineering judgment stack", "Which competencies are required to turn chapter knowledge into a decision?", [], _HSTACK,
        "Identify which competency would fail first if the source were misunderstood.", "Judgment combines technical reasoning, evidence, risk, people, and responsibility.", "concept-map")
    first = rows[:2]
    add(5, "Prediction gate", "PREDICT before seeing the full mechanism: what result follows from the source constraints?",
        [statement for row in first for statement in _atomic_source_entries(row)],
        ["PREDICT: State the behaviour you expect before naming the mechanism.",
         "CONSTRAINT: Identify the source-supported condition that limits that prediction.",
         "DERIVE: Trace why that condition changes the expected behaviour.",
         "NAME: Name the principle only after defending the derivation."],
        "Commit to a prediction, then identify the source statement that could overturn it.", "Prediction must precede explanation.", "process", _anchors(first))

    visual_cycle = cycle(["concept-map", "process", "comparison", "timeline", "architecture", "table"])
    seen_actions: set[str] = set()
    fill_order = _fill_rows(groups, rows)
    for idx, bucket in enumerate(groups, start=6):
        # A thin source leaves teaching slots without their own checkpoint.
        reused = not bucket
        if reused:
            bucket = [fill_order.pop(0)] if fill_order else rows[-1:]
        labels = [x.label for x in bucket]
        core = [
            statement
            for row in bucket
            for statement in _atomic_source_entries(row)
        ]
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
        if idx == 8: ped = [f"Alternative A: Apply {labels[0]} under the source's stated conditions.",
                            "Alternative B: Retain the current design until those conditions are evidenced.",
                            "Trade-off: Compare the cost of changing the design with the risk of delaying the decision."]
        elif idx == 9: ped = [f"Measure: Choose an observable result of {labels[0]} and record its test conditions.",
                              "Falsifier: Identify a result that contradicts the source-based prediction; revise the decision if observed."]
        elif idx == 10: ped = [f"Known: Identify the claims explicitly supported by {labels[0]}.",
                               "Unknown: List assumptions for which the source supplies no evidence.",
                               "Decision-sensitive unknown: Select the missing fact that would reverse your design choice.",
                               "Monitor: Define an observation, its owner, and the condition requiring a new decision."]
        elif idx == 11: ped = ["Use a Saudi/Gulf constraint only as an explicit hypothetical unless P1 supports it."]
        elif idx == 12: ped = ["Name the responsible role, evidence owner, and sign-off point without adding new technology."]
        elif idx == 13: ped = ["Ask what changes next while keeping the source mechanism dominant."]
        elif idx == 14: ped = ["Identify the practitioner/operational consequence implied by the source mechanism; do not invent psychology claims."]
        elif idx == 15: ped = ["AI MAY ASSIST: Propose test cases for the source mechanism, subject to verification.",
                               "AI MUST NOT BE TRUSTED AUTONOMOUSLY: Approve the design or certify its safety.",
                               "Human sign-off: Check each claim against the source, test it, search for failures, then record the responsible reviewer."]
        # The slot's contracted question always ships. It used to appear only on
        # the thin-source path, so a source rich enough to fill every slot got
        # ten copies of "How does X change the engineering decision?" - the
        # better the source, the more generic the grammar. Now the move states
        # what this slot asks of the learner, and the source names its focus.
        question = move_question
        action = _student_action_for(bucket, labels)
        if action in seen_actions:
            action = move_scaffold[0]
        seen_actions.add(action)
        # Every teaching slot carries its move. A thin source gives one checkpoint
        # line, and one line is a single oversized box on the slide - the move is
        # what makes that checkpoint workable, so it always ships beside it.
        ped = ped if idx in {8, 9, 10, 15} else [*ped, *move_scaffold]
        if len([x for x in (*core, *ped) if str(x).strip()]) < _MIN_UNIT_ITEMS:
            ped = [*ped, f"Name what {labels[0] if labels else 'this mechanism'} would cost if it were absent."]
        add(idx, title_, question, core, ped, action,
            f"Source checkpoint(s) covered: {', '.join(labels)}",
            kind, _anchors(bucket), evidence=f"P1 checkpoint evidence: {', '.join(x.id for x in bucket)}",
            verify=reused)

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

    # Every locked family gets a coverage row. Truncating at ten silently declared
    # a narrower lecture than the source profile locked, and the deck then failed
    # its own topic-coverage contract on any chapter with more than ten families.
    topic_coverage = [
        TopicCoverage(topic_family=x.name, source_anchor=x.source_anchor,
                      first_taught_unit=min(15, 6 + i), reinforced_units=[16, 18])
        for i, x in enumerate(profile.topic_families)
    ] or [TopicCoverage(topic_family=rows[0].label, source_anchor=rows[0].source_anchor, first_taught_unit=6, reinforced_units=[16,18])]

    # One descriptor set repeated six times told a marker nothing about which
    # capability was being judged, and its length forced the rubric table below
    # the 12pt readable floor. Each criterion now names what its own levels look
    # like, in wording short enough to project.
    rubric_levels = [
        ("Technical correctness + source fidelity",
         "Every claim traced to P1, precise and complete.",
         "Claims are correct and anchored to the source.",
         "Mostly correct; some anchors are missing.",
         "Contradicts P1 or cites no source at all."),
        ("First-principles / mechanism reasoning",
         "Derives the mechanism from its constraints.",
         "Explains the mechanism in the right order.",
         "Names the steps without connecting them.",
         "Restates the slide; no mechanism shown."),
        ("Alternatives + trade-off engineering judgment",
         "Two defensible options, each with its cost.",
         "One alternative and the trade-off it carries.",
         "An alternative named; trade-off left vague.",
         "One option only, with no trade-off."),
        ("Evidence + falsification / verification quality",
         "States the measure and what would refute it.",
         "Gives the evidence and a check on it.",
         "Evidence given; nothing could disconfirm it.",
         "Assertion offered in place of evidence."),
        ("Constraint adaptation + risk-aware redesign",
         "Reruns the decision under the new constraint.",
         "Adjusts the design to the new constraint.",
         "Notes the change but keeps the old answer.",
         "The constraint change is ignored."),
        ("Professional accountability + readiness discipline",
         "Names owner, sign-off, and what is unverified.",
         "Names the responsible role and its evidence.",
         "Accountability implied but never assigned.",
         "No owner and no review status."),
    ]
    rubric = [RubricCriterion(
        criterion=name,
        distinguished=distinguished,
        ready=ready,
        developing=developing,
        not_yet_ready=not_yet,
        readiness_refs=["UNVERIFIED — evidenced by Units 16, 18 and 19; no approved ETEC SLO mapping in this pass."],
    ) for name, distinguished, ready, developing, not_yet in rubric_levels]

    return Blueprint(
        lecture_title=title,
        engineering_thesis=f"Use the complete primary-source chapter to make a bounded engineering decision about {title}.",
        central_engineering_crisis=f"A team must make a consequential decision about {title} while distinguishing source-supported knowledge from unresolved assumptions.",
        named_ethical_purpose="Make an evidence-proportionate professional decision without overstating what the source or the learner artifact proves.",
        clos=clos, units=units, source_topic_families=family_names, topic_coverage=topic_coverage,
        coverage_ledger=ledger, readiness_alignment=_readiness_trail(profile, clos, rows), rubric_criteria=rubric,
        release_notes=["QUOTA-SAFE DRAFT ONLY: semantic generation/audit unavailable; readiness unverified; release forbidden."],
        session_minutes=90, source_manifest=profile.source_manifest, deferred_topics=[],
    )
