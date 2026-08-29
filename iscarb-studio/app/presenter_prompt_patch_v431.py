from __future__ import annotations

"""v4.3.1 prompt contract for learner-facing CIMT Presenter copy.

The Blueprint already has a visual_plan.annotation_plan field.  We use that
field as the renderer's concise, source-safe teaching copy instead of adding a
parallel presentation schema.  This keeps provenance intact: core_content is
still the technical record, while annotation_plan is only a faithful visual
compression of content already present in the Blueprint/source bundle.
"""

from . import prompts as _p

PRESENTER_COPY_CONTRACT = r"""

CIMT LEARNER-FACING PRESENTER COPY — HARD RELEASE CONTRACT
The faculty-facing Blueprint may be detailed. The learner-facing Presenter must
look and read like a taught CIMT lecture, not like a dashboard or a dump of the
Blueprint.

For EVERY Unit populate visual_plan.annotation_plan with 2–5 concise teaching
annotations that can be projected at classroom distance.

Rules for visual_plan.annotation_plan:
- Each annotation is normally 4–18 words; one complete idea only.
- Use the weekly source's vocabulary and mechanisms.
- Technical annotations MUST be faithful compressions of core_content and the
  cited P1/S# material. They may not introduce a new technical claim.
- Pure pedagogy Units may compress pedagogy_content instead.
- On source-visual Units, annotations tell the learner what to NOTICE, COMPARE,
  TRACE, PREDICT, or CHALLENGE in the figure; do not repeat a paragraph beside it.
- Prefer concrete nouns, mechanisms, contrasts, arrows, quantities, states, or
  decision criteria over generic educational prose.
- Do not emit placeholders such as "KEY POINT 1", "mechanism for unit 8",
  "decision evidence 4", "source-supported concept", or "engineering scaffold".
- Do not mechanically repeat the Unit title, engineering question, or takeaway.
- Do not use visible hard truncation tokens "..." or "…".
- Do not fabricate national requirements, standards, technologies, examples, or
  numbers merely to make a slide look richer.

CLASSROOM ACTION COPY
student_action must be a short executable classroom instruction, normally 8–24
words. It should tell the learner what to decide, calculate, trace, critique,
redesign, falsify, or defend now. Avoid long rubric language in student_action.

CIMT VISUAL DENSITY
A projected slide should normally have one dominant visual/cognitive job and
2–5 meaningful annotations. Preserve useful white space. Do not create a grid of
repeated dashboard cards merely because the Blueprint has many metadata fields.
"""

PRESENTER_AUDIT_CONTRACT = r"""

PRESENTER COPY AUDIT — RELEASE CRITICAL
Also fail cumulative fidelity when learner-facing visual_plan.annotation_plan is
missing or generic across several Units, contains unsupported technical claims,
repeats placeholder phrases, or reads like mechanically truncated metadata.
Flag repeated dashboard/card prose, visible ellipsis, and source-visual slides
whose annotations merely duplicate paragraphs instead of directing attention to
the actual figure. student_action should be brief and executable in class.
"""

PRESENTER_REPAIR_CONTRACT = r"""

PRESENTER COPY REPAIR
Rebuild visual_plan.annotation_plan for all 20 Units as 2–5 concise, source-safe
teaching annotations. Compress only claims already present in core_content or
pedagogy_content; never invent technical detail. Rewrite student_action as a
brief executable classroom move. Remove placeholders, repeated generic wording,
visible ellipsis, and dashboard-style metadata prose.
"""


def install_prompt_patch() -> None:
    if "CIMT LEARNER-FACING PRESENTER COPY — HARD RELEASE CONTRACT" not in _p.MASTER_PROMPT:
        _p.MASTER_PROMPT += PRESENTER_COPY_CONTRACT
    if "PRESENTER COPY AUDIT — RELEASE CRITICAL" not in _p.AUDIT_PROMPT:
        _p.AUDIT_PROMPT += PRESENTER_AUDIT_CONTRACT
    if "PRESENTER COPY REPAIR" not in _p.REPAIR_PROMPT:
        _p.REPAIR_PROMPT += PRESENTER_REPAIR_CONTRACT


install_prompt_patch()
