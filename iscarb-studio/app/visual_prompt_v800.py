from __future__ import annotations

"""Prompt addendum for ISCARB v8 visual evidence use.

The generator describes how a source visual should be used pedagogically. It
never grants the model authority to invent a figure, caption, numeric scale, or
P1 provenance.
"""

VISUAL_PROMPT_ADDENDUM = r"""

14. HYBRID VISUAL-NARRATIVE EVIDENCE — HARD
The runtime may extract figures, diagrams, graphs and tables directly from P1.
When the source bundle contains an information-bearing visual:
- Treat the visual as evidence, not decoration.
- Make the learner action depend on READING / MARKING / COMPARING / FALSIFYING something visible in the visual.
- Never invent a figure number, caption, axis value, threshold, percentage, cost difference, or numeric scale that is not visible in the supplied source.
- For a graph with no usable numeric scale, explicitly say that a numeric break-even cannot be calculated from P1 alone; ask the learner to mark the decision region and name the measurement/data required.
- For a diagram, ask the learner to identify the node/layer/relation whose failure or change would alter the decision.
- For a table, identify the decision-relevant row/criterion; the runtime may convert source rows into interactive cards without changing their wording.
- If a source visual is unavailable but a redraw would aid reasoning, describe only a SOURCE-DERIVED ISCARB REDRAW and keep it clearly labelled as a redraw. Never call a redraw a P1 figure.
- Keep source visual provenance visible in the learner task and evidence chain.
- Prefer 3–5 critical source visuals per 90-minute lecture rather than decorating every Unit.
"""


def apply_v800_visual_prompt_patch() -> None:
    from . import prompts
    from . import gemini_service

    if VISUAL_PROMPT_ADDENDUM.strip() not in prompts.MASTER_PROMPT:
        prompts.MASTER_PROMPT = prompts.MASTER_PROMPT.rstrip() + VISUAL_PROMPT_ADDENDUM
    # GeminiService imports MASTER_PROMPT by value at module import time.
    if VISUAL_PROMPT_ADDENDUM.strip() not in gemini_service.MASTER_PROMPT:
        gemini_service.MASTER_PROMPT = gemini_service.MASTER_PROMPT.rstrip() + VISUAL_PROMPT_ADDENDUM
