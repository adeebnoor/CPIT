from __future__ import annotations

"""v7.3.6 — Narrative Learning Experience Engine.

Adds stateful student/instructor surfaces without changing the Golden v6.6
technical grammar. Also exposes a small narrative bridge in presenter headers so
major conceptual transitions read as a story rather than a disconnected list.
"""

from . import main as engine
from . import start_v440 as base
from . import presenter_v67_prod as presenter
from .learning_experience import TRANSITIONS, health_fragment, install_learning_experience

_PATCHED = False


def _bridge(number: int) -> str:
    text = TRANSITIONS.get(number, "")
    if not text:
        return ""
    # Presenter must stay projection-readable; keep only the connective lead.
    return text.split(" — ", 1)[0].strip()


def apply_v736_narrative_learning_patch(app):
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True
    install_learning_experience(app)

    # Add connective words to presenter headers without adding slides, changing
    # source content, or weakening the 20-unit contract.
    original_ppt_header = presenter._ppt_header
    def ppt_header(slide, u, page_idx, total):
        original_ppt_header(slide, u, page_idx, total)
        cue = _bridge(getattr(u, "number", 0))
        if cue:
            presenter._ppt_text(slide, 10.35, .50, 2.55, .22, cue, 6.8, presenter.GOLD, True, presenter.PP_ALIGN.RIGHT)
    presenter._ppt_header = ppt_header

    original_pdf_header = presenter._pdf_header
    def pdf_header(c, u, page_idx, total):
        original_pdf_header(c, u, page_idx, total)
        cue = _bridge(getattr(u, "number", 0))
        if cue:
            presenter._pdf_text(c, 730, 530, 190, 15, cue, 5.8, presenter.GOLD, True, "right", 1)
    presenter._pdf_header = pdf_header

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update(health_fragment())
        data["build_id"] = "7.3.6-narrative-learning-experience"
        return data
    base._health_v440 = health
    base.engine.health = health
