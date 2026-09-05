from __future__ import annotations

"""v7.2.8 - operational peer-review and source-expansion decision boxes.

Keeps the user-approved v6.6 Balanced30 grammar intact, but fixes two classroom
usability problems:
1) Rule 19 becomes a quick two-question peer-review card on the learner slide.
   The full 6x4 rubric remains in the Blueprint/instructor pack, not the live
   in-class cognitive task.
2) SOURCE EXPANSION pages carry a concise Decision Evidence Box so dense source
   detail is visibly tied to an engineering decision and inspectable evidence.
"""

from . import main as engine
from . import start_v440 as base
from . import v670_contract as contract
from . import presenter_v67_prod as presenter

_PATCHED = False
_ORIGINAL_DRAFT = None
_ORIGINAL_PLAN_EXPANSIONS = None

_PEER_REVIEW_NOTE = "Rule 19 operationalized: learner slide uses a two-question peer-review quick card; full 6x4 rubric remains in the instructor/blueprint layer."
_SOURCE_BOX_NOTE = "Source Expansion ergonomics locked: each expansion carries a Decision Evidence Box linking theory to decision and evidence."


def _keep_note(bp, note: str):
    notes = list(getattr(bp, "release_notes", []) or [])
    if note not in notes:
        notes = notes[:19] + [note]
    bp.release_notes = notes


def _timebox_prefix(task: str) -> tuple[str, str]:
    text = str(task or "").strip()
    if text.upper().startswith("TIMEBOX:"):
        parts = text.split("-", 1)
        if len(parts) == 2:
            return parts[0].strip() + " - ", parts[1].strip()
    return "", text


def _operationalize_rule19(bp):
    units = list(getattr(bp, "units", []) or [])
    if len(units) < 19:
        return bp
    u = units[18]
    prefix, _ = _timebox_prefix(getattr(u, "student_action", ""))
    if not prefix:
        prefix = "TIMEBOX: 3 min - "
    u.title = "Peer-review quick card"
    u.engineering_question = "Can a peer inspect your evidence, and what single change would falsify your claim?"
    u.core_content = [
        "Q1 - Is the evidence independently inspectable by someone who did not build the artifact?",
        "Q2 - What variable, counter-example, or failure condition would make this claim fall?",
    ]
    u.pedagogy_content = [
        "IN-CLASS ONLY - answer two peer-review questions, not the full rubric.",
        "FULL RUBRIC - retained for instructor scoring and post-class revision.",
    ]
    u.student_action = prefix + "Exchange artifacts with one peer; answer Q1 and Q2 only."
    u.takeaway = "A quick review tests inspectability and falsifiability before formal scoring."
    _keep_note(bp, _PEER_REVIEW_NOTE)
    return bp


def _decision_box_for_spec(spec: dict) -> str:
    title = str(spec.get("title", "source detail"))
    anchor = str(spec.get("source_anchor", "P1"))
    topic = title.split(" - ")[0].split(" — ")[0].strip() or "this source detail"
    return f"DECISION EVIDENCE BOX - Decision: what does {topic} change? Evidence: cite {anchor} and name the artifact or test that would prove it."


def _add_decision_box_to_specs(specs):
    rows = []
    for spec in list(specs or []):
        d = dict(spec)
        content = [str(x).strip() for x in list(d.get("content", []) or []) if str(x).strip()]
        box = _decision_box_for_spec(d)
        if not any(str(x).upper().startswith("DECISION EVIDENCE BOX") for x in content):
            content = [box] + content
        d["content"] = content[:7]
        d["objective"] = "Decision Evidence Box: convert dense source detail into a concrete engineering decision and inspectable evidence."
        d["visual_evidence_role"] = "Decision Evidence Box - source detail must change a decision, evidence request, or verification plan."
        rows.append(d)
    return rows


def apply_v728_peer_review_decision_boxes_patch(app):
    global _PATCHED, _ORIGINAL_DRAFT, _ORIGINAL_PLAN_EXPANSIONS
    if _PATCHED:
        return
    _PATCHED = True
    _ORIGINAL_DRAFT = engine._source_preserving_draft
    _ORIGINAL_PLAN_EXPANSIONS = contract.plan_expansions

    def draft(profile, bundle):
        bp = _ORIGINAL_DRAFT(profile, bundle)
        _operationalize_rule19(bp)
        _keep_note(bp, _SOURCE_BOX_NOTE)
        return bp

    def expansions(bp, *args, **kwargs):
        return _add_decision_box_to_specs(_ORIGINAL_PLAN_EXPANSIONS(bp, *args, **kwargs))

    engine._source_preserving_draft = draft
    base.engine._source_preserving_draft = draft
    contract.plan_expansions = expansions
    for mod in (presenter, base):
        if hasattr(mod, "plan_expansions"):
            setattr(mod, "plan_expansions", expansions)

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "peer_review_quick_card": "Rule 19 learner slide shows two questions: inspectable evidence + falsifier; full 6x4 rubric stays in instructor/blueprint layer.",
            "source_expansion_decision_box": "Every SOURCE EXPANSION includes a Decision Evidence Box linking dense P1 detail to a decision and inspectable evidence.",
            "visual_ergonomics_version": "v7.2.8",
        })
        return data
    base._health_v440 = health
    base.engine.health = health
