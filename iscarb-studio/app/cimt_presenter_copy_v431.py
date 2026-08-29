from __future__ import annotations

"""Small display-copy patch for the v4.3 CIMT-native renderer.

The technical Blueprint remains unchanged.  For learner-facing slide copy only,
visual_plan.annotation_plan is preferred when it contains useful annotations.
This prevents long source/provenance prose from being squeezed into repetitive
cards while preserving the source-backed core for audit and export JSON.
"""

from . import cimt_native_v43 as _renderer

_INSTALLED = False
_ORIGINAL_CORE = _renderer._core
_ORIGINAL_PED = _renderer._ped


def _clean_annotations(unit, n: int) -> list[str]:
    plan = getattr(unit, "visual_plan", None)
    values = list(getattr(plan, "annotation_plan", None) or [])
    out: list[str] = []
    for raw in values:
        text = _renderer.presenter_text(str(raw), 112)
        if not text:
            continue
        low = text.lower()
        # Never reward the generic placeholders that caused the old deck to
        # look machine-filled instead of taught.
        if low.startswith("key point ") or "mechanism for unit" in low or "decision evidence " in low:
            continue
        if text not in out:
            out.append(text)
        if len(out) >= n:
            break
    return out


def _core_for_presenter(unit, n: int = 7) -> list[str]:
    annotations = _clean_annotations(unit, n)
    if annotations:
        return annotations
    return _ORIGINAL_CORE(unit, n)


def _ped_for_presenter(unit, n: int = 6) -> list[str]:
    # Unit 4 is a pure H-Stack teaching slide and _spec() intentionally reads
    # pedagogy rather than core. Curated annotations are useful there too.
    if getattr(unit, "number", 0) == 4:
        annotations = _clean_annotations(unit, n)
        if annotations:
            return annotations
    return _ORIGINAL_PED(unit, n)


def install_presenter_copy_v431() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _renderer._core = _core_for_presenter
    _renderer._ped = _ped_for_presenter
    _INSTALLED = True
