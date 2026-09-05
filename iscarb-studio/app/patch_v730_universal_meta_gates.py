from __future__ import annotations

"""v7.3.0 - reusable Universal Meta-Gates for every course.

The universal layer is deliberately domain-agnostic. It does not rewrite P1
source content and does not force dependability-specific tools into unrelated
subjects. Domain profiles (for example assurance/reliability) may add stricter
checks on top of these gates.

Submission contract:
- every mandatory gate is answered in a structured field;
- conditional AI/data gates may be marked N/A only with a reason;
- missing/too-thin answers return RETURN_FOR_REVISION;
- visual lecture grammar remains Golden v6.6.
"""

import re
from typing import Any

from . import main as engine
from . import start_v440 as base

_PATCHED = False
_ORIGINAL_DRAFT = None

UNIVERSAL_RULES = [
    {
        "id": "U01",
        "name": "Global Breaking Variable",
        "question": "What single variable, if changed, would break the solution or reverse the decision?",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U02",
        "name": "Quantify vs Qualify",
        "question": "What number, metric, probability, threshold, or measurable indicator supports the claim?",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U03",
        "name": "Verification vs Validation",
        "question": "What evidence verifies the implementation, and what separate evidence validates that the right problem is being solved?",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U04",
        "name": "Ownership & Accountability",
        "question": "Who specifically owns the decision and who signs off on it?",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U05",
        "name": "Data Layer",
        "question": "How could data bias or data drift change the result? If data are not material, state N/A and justify why.",
        "kind": "submission",
        "conditional": True,
    },
    {
        "id": "U06",
        "name": "AI Assist + Continuous Monitoring",
        "question": "What may AI automate or prepare, what must it never own, and what will be monitored after deployment or execution?",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U07",
        "name": "Human-in-the-Loop",
        "question": "If AI influences a decision, when must a human reject, override, or escalate it? If AI has no decision role, state N/A and why.",
        "kind": "submission",
        "conditional": True,
    },
    {
        "id": "U08",
        "name": "Evidence Chain",
        "question": "Provide Claim -> Evidence -> Warrant -> Counter-evidence -> Residual Uncertainty -> Verdict.",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U09",
        "name": "Tool Standardization",
        "question": "Name the analytical tool or method used and show one concrete output from it.",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U10",
        "name": "Inspectable Artifact",
        "question": "Can another team inspect the artifact and reproduce the decision without your oral explanation? Point to the inspectable evidence.",
        "kind": "submission",
        "conditional": False,
    },
    {
        "id": "U11",
        "name": "Timebox Consistency",
        "question": "Engine self-check: every interactive task uses exactly TIMEBOX: X min (or a bounded range) with no malformed label.",
        "kind": "engine",
        "conditional": False,
    },
    {
        "id": "U12",
        "name": "Local Transfer",
        "question": "Transfer the concept to a Saudi/local case and name the accountable local owner; if AI is added, state its bounded role.",
        "kind": "submission",
        "conditional": False,
    },
]

GOLDEN_RULE = (
    "The editor accepts a decision protected by an evidence chain, grounded in data or measurable indicators, "
    "signed by an accountable owner, and explicit about the variable that could break it."
)

NOTE = "Universal Meta-Gates v7.3.0: 12 reusable gates across courses; domain profiles may add stricter checks without changing the Golden lecture grammar."


def _clean(v: Any) -> str:
    return " ".join(str(v or "").split())


def _unit(bp, n: int):
    rows = list(getattr(bp, "units", []) or [])
    return rows[n - 1] if len(rows) >= n else None


def _append_requirement(u, text: str):
    if not u:
        return
    rows = [_clean(x) for x in list(getattr(u, "elite_requirements", []) or []) if _clean(x)]
    if text not in rows:
        rows.append(text)
    u.elite_requirements = rows[:20]


def _append_pedagogy(u, text: str):
    if not u:
        return
    rows = [_clean(x) for x in list(getattr(u, "pedagogy_content", []) or []) if _clean(x)]
    if text not in rows:
        rows.append(text)
    u.pedagogy_content = rows[:16]


def _apply_universal_scaffold(bp):
    # Keep prompts distributed across the existing 20-unit grammar rather than
    # creating extra slides or dumping all gates onto one page.
    mapping = {
        5: ["U01 Global Breaking Variable"],
        9: ["U02 Quantify vs Qualify", "U03 Verification vs Validation"],
        10: ["U01 Global Breaking Variable", "U02 Quantify vs Qualify"],
        11: ["U12 Local Transfer", "U04 Ownership & Accountability"],
        12: ["U04 Ownership & Accountability"],
        13: ["U01 Global Breaking Variable", "U09 Tool Standardization"],
        14: ["U06 AI Assist + Continuous Monitoring"],
        15: ["U05 Data Layer", "U06 AI Assist + Continuous Monitoring", "U07 Human-in-the-Loop"],
        16: ["U08 Evidence Chain", "U09 Tool Standardization", "U10 Inspectable Artifact"],
        18: ["U08 Evidence Chain", "U10 Inspectable Artifact"],
        19: ["U10 Inspectable Artifact"],
        20: ["U01 Global Breaking Variable", "U08 Evidence Chain", "U12 Local Transfer"],
    }
    rule_by_label = {f"{r['id']} {r['name']}": r for r in UNIVERSAL_RULES}
    for n, labels in mapping.items():
        u = _unit(bp, n)
        for label in labels:
            r = rule_by_label[label]
            _append_requirement(u, f"UNIVERSAL GATE {r['id']} - {r['name']}: {r['question']}")

    # Only surface the most useful short prompts to learners; the full gate set
    # belongs to the editor/submission layer.
    _append_pedagogy(_unit(bp, 10), "UNIVERSAL CHECK - name the breaking variable and a measurable monitor/threshold.")
    _append_pedagogy(_unit(bp, 11), "UNIVERSAL CHECK - transfer locally and name the accountable owner/sign-off.")
    _append_pedagogy(_unit(bp, 16), "UNIVERSAL CHECK - build a complete evidence chain in an inspectable artifact.")
    _append_pedagogy(_unit(bp, 20), "UNIVERSAL CHECK - no verdict until the breaking variable, evidence chain, and local owner are explicit.")

    notes = list(getattr(bp, "release_notes", []) or [])
    for item in (NOTE, "GOLDEN RULE - " + GOLDEN_RULE):
        if item not in notes:
            notes = notes[:18] + [item]
    bp.release_notes = notes[:20]
    return bp


def _meaningful(text: str, conditional: bool) -> bool:
    t = _clean(text)
    if len(t.split()) >= 4:
        return True
    if conditional and re.match(r"(?i)^n\s*/?\s*a\b", t) and len(t.split()) >= 3:
        return True
    return False


def evaluate_universal_gate_responses(payload: dict[str, Any]) -> dict[str, Any]:
    """Deterministic completeness gate for a structured student submission.

    Expected shape: {"answers": {"U01": "...", ...}}. U11 is an engine
    self-check and is never required from the student. Conditional gates accept
    a reasoned N/A. Semantic quality can still be reviewed by the instructor or
    a model, but structural omissions are rejected deterministically.
    """
    answers = dict(payload.get("answers") or {})
    failures = []
    passed = []
    for rule in UNIVERSAL_RULES:
        if rule["kind"] == "engine":
            continue
        rid = rule["id"]
        answer = _clean(answers.get(rid, ""))
        if _meaningful(answer, bool(rule["conditional"])):
            passed.append(rid)
        else:
            failures.append({
                "id": rid,
                "name": rule["name"],
                "question": rule["question"],
                "problem": "Missing or non-inspectable answer",
            })
    status = "ACCEPT_FOR_REVIEW" if not failures else "RETURN_FOR_REVISION"
    return {
        "status": status,
        "overall_pass": not failures,
        "passed": passed,
        "failed": failures,
        "golden_rule": GOLDEN_RULE,
    }


def _install_api(app):
    existing = {getattr(route, "path", None) for route in getattr(app, "routes", [])}
    if "/api/editor-gates/universal" not in existing:
        @app.get("/api/editor-gates/universal")
        def universal_gate_schema():
            return {"version": "v7.3.0", "count": len(UNIVERSAL_RULES), "rules": UNIVERSAL_RULES, "golden_rule": GOLDEN_RULE}

    if "/api/editor-gates/evaluate" not in existing:
        @app.post("/api/editor-gates/evaluate")
        def universal_gate_evaluate(payload: dict[str, Any]):
            return evaluate_universal_gate_responses(payload)


def apply_v730_universal_meta_gates_patch(app):
    global _PATCHED, _ORIGINAL_DRAFT
    if _PATCHED:
        return
    _PATCHED = True
    _ORIGINAL_DRAFT = engine._source_preserving_draft

    def draft(profile, bundle):
        return _apply_universal_scaffold(_ORIGINAL_DRAFT(profile, bundle))

    engine._source_preserving_draft = draft
    base.engine._source_preserving_draft = draft
    _install_api(app)

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "universal_meta_gates_version": "v7.3.0",
            "universal_meta_gates_count": 12,
            "universal_meta_gates": UNIVERSAL_RULES,
            "universal_gate_feedback_loop": "Missing structured gate answers => RETURN_FOR_REVISION before acceptance.",
            "universal_gate_architecture": "Universal meta-layer first; domain-specific profiles add stricter checks only when applicable.",
            "golden_rule": GOLDEN_RULE,
        })
        return data
    base._health_v440 = health
    base.engine.health = health
