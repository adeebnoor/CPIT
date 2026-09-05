from __future__ import annotations

"""v7.2.9 final polish.

Fixes two issues found in the rendered Ch10 proof without changing the Golden
learning grammar: long time-box labels are compacted only in the visual pill,
and Rule 11 shows an actual bounded domain-adaptive Saudi/local transfer case
rather than an instruction that merely says to transfer.
"""

import html as html_lib
import re

from . import main as engine
from . import start_v440 as base
from . import presenter_v67_prod as presenter
from . import patch_v729_ztm_theme as ztm

_PATCHED = False
_PREVIOUS_DRAFT = None
_ORIGINAL_PPT_SEMANTIC = None
_ORIGINAL_PDF_SEMANTIC = None
_ORIGINAL_PREVIEW = None


def _clean(v) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()


def _compact_timebox(value: str) -> str:
    """Compact the badge only; the full timing semantics remain in student_action."""
    s = _clean(value)
    low = s.lower()
    if "micro-case" in low and "transfer" in low:
        nums = re.findall(r"\d+(?:-\d+)?", s)
        if len(nums) >= 2:
            return f"{nums[0]} + {nums[1]} min"
    if "post-class" in low or "post class" in low:
        return "post-class"
    # Keep normal 60-90 sec / 3-4 min / 5-7 min labels unchanged.
    return s


def _taskbar_parts(task: str, timebox: str) -> tuple[str, str]:
    task = _clean(task)
    if task.upper().startswith("TIMEBOX:"):
        parsed_tb, parsed_task = ztm._timebox_parts(task, default=timebox)
        return _compact_timebox(parsed_tb), parsed_task
    return _compact_timebox(timebox), task


def _topic_blob(bp) -> str:
    vals = [getattr(bp, "lecture_title", ""), getattr(bp, "engineering_thesis", "")]
    vals += list(getattr(bp, "source_topic_families", []) or [])
    return " ".join(_clean(x) for x in vals).lower()


def _local_case(bp) -> str:
    """Bounded pedagogical transfer case. It is explicitly not represented as P1."""
    t = _topic_blob(bp)
    if any(k in t for k in ("dependab", "reliab", "redundan", "fault", "safety", "formal method")):
        return (
            "Saudi hospital — bounded hypothetical (ISCARB scaffold, not P1): two patient-monitoring "
            "services run on separate servers but share one upstream power/network dependency. Before "
            "clinical deployment, decide whether the redundancy claim is acceptable and name the evidence "
            "that would expose a common-mode failure."
        )
    if any(k in t for k in ("security", "cyber", "authentication", "access control", "threat")):
        return (
            "Saudi digital service — bounded hypothetical (ISCARB scaffold, not P1): normal login uses MFA, "
            "but account recovery uses a weaker channel. Decide whether deployment is acceptable and name "
            "the evidence needed to verify the recovery path."
        )
    if any(k in t for k in ("database", "transaction", "serializ", "sql", "concurrency")):
        return (
            "Saudi hospital scheduling service — bounded hypothetical (ISCARB scaffold, not P1): two "
            "transactions update the same appointment record under load. Decide which concurrency guarantee "
            "is required and what test evidence would demonstrate it."
        )
    if any(k in t for k in ("network", "routing", "protocol", "distributed", "cloud")):
        return (
            "Saudi public-service platform — bounded hypothetical (ISCARB scaffold, not P1): two network "
            "paths appear independent but share one upstream dependency. Decide whether the resilience claim "
            "is acceptable and what evidence would reveal the shared failure point."
        )
    return (
        "Saudi/local system — bounded hypothetical (ISCARB scaffold, not P1): one operational dependency "
        "changes and a previously valid service claim may no longer hold. Apply the taught mechanism, name "
        "the evidence required, and set the decision boundary."
    )


def _rule11_local_from_unit(bp, u) -> str:
    existing = ztm._label_value(getattr(u, "pedagogy_content", []), "LOCAL CASE")
    if existing and len(existing.split()) >= 12 and "hypothetical saudi context" not in existing.lower():
        return existing
    return _local_case(bp)


def _upgrade_rule11(bp):
    units = list(getattr(bp, "units", []) or [])
    if len(units) < 11:
        return bp
    u = units[10]
    rows = [_clean(x) for x in list(getattr(u, "pedagogy_content", []) or []) if _clean(x)]
    rows = [x for x in rows if not re.match(r"^LOCAL CASE\s*[—:-]", x, flags=re.I)]
    local = _local_case(bp)
    # Place the concrete transfer immediately after the transfer rule so the
    # blueprint and every renderer preserve the same scaffold sequence.
    pos = 2 if len(rows) >= 2 else len(rows)
    rows.insert(pos, f"LOCAL CASE — {local}")
    u.pedagogy_content = rows[:16]
    return bp


def _ppt_taskbar(slide, task: str, anchor: str = "", timebox: str = "2 min"):
    tb, clean_task = _taskbar_parts(task, timebox)
    y, h = 6.62, .79
    shadow = slide.shapes.add_shape(ztm.MSO_SHAPE.ROUNDED_RECTANGLE, ztm.Inches(.32), ztm.Inches(y+.035), ztm.Inches(12.68), ztm.Inches(h))
    shadow.fill.solid(); shadow.fill.fore_color.rgb = presenter._rgb(ztm.SHADOW); shadow.line.fill.background()
    card = slide.shapes.add_shape(ztm.MSO_SHAPE.ROUNDED_RECTANGLE, ztm.Inches(.29), ztm.Inches(y), ztm.Inches(12.68), ztm.Inches(h))
    card.fill.solid(); card.fill.fore_color.rgb = presenter._rgb(ztm.BG_SURFACE); card.line.color.rgb = presenter._rgb(ztm.BORDER); card.line.width = ztm.Pt(.8)
    for x, w, col in [(.34, 6.28, ztm.ACCENT_PRIMARY), (6.62, 6.28, ztm.ACCENT_CYAN)]:
        r = slide.shapes.add_shape(ztm.MSO_SHAPE.RECTANGLE, ztm.Inches(x), ztm.Inches(y+.025), ztm.Inches(w), ztm.Inches(.045))
        r.fill.solid(); r.fill.fore_color.rgb = presenter._rgb(col); r.line.fill.background()
    ztm._ppt_text(slide, .50, y+.18, 1.05, .20, "YOUR TASK", 7.3, ztm.ACCENT_PRIMARY, True)
    ztm._ppt_text(slide, 1.55, y+.15, 8.35, .36, presenter._short(clean_task, 34), 8.5, ztm.TEXT_HEADING, False, valign=ztm.MSO_ANCHOR.MIDDLE)
    # Wider pill prevents the Rule 11 1+5 timing from clipping.
    ztm._ppt_badge(slide, 10.02, y+.16, 1.94, f"TIMEBOX · {tb}", ztm.ROSE_BG, ztm.ALERT_URGENT, "#FECDD3")
    if anchor:
        ztm._ppt_text(slide, 12.02, y+.20, .72, .18, presenter._short(anchor, 6), 5.2, ztm.TEXT_BODY, False, ztm.PP_ALIGN.RIGHT)


def _pdf_taskbar(c, task: str, anchor: str = "", timebox: str = "2 min"):
    tb, clean_task = _taskbar_parts(task, timebox)
    c.setFillColor(ztm.HexColor(ztm.SHADOW)); c.roundRect(25, 7, 910, 54, 9, fill=1, stroke=0)
    c.setFillColor(ztm.HexColor(ztm.BG_SURFACE)); c.setStrokeColor(ztm.HexColor(ztm.BORDER)); c.setLineWidth(.7); c.roundRect(23, 9, 910, 54, 9, fill=1, stroke=1)
    c.setFillColor(ztm.HexColor(ztm.ACCENT_PRIMARY)); c.rect(28, 58, 450, 3, fill=1, stroke=0)
    c.setFillColor(ztm.HexColor(ztm.ACCENT_CYAN)); c.rect(478, 58, 450, 3, fill=1, stroke=0)
    presenter._pdf_text(c, 38, 31, 75, 15, "YOUR TASK", 6.4, ztm.ACCENT_PRIMARY, True, max_lines=1)
    presenter._pdf_text(c, 118, 23, 560, 28, presenter._short(clean_task, 36), 7.3, ztm.TEXT_HEADING, False, max_lines=2)
    ztm._pdf_badge(c, 692, 25, 156, f"TIMEBOX · {tb}", ztm.ROSE_BG, ztm.ALERT_URGENT)
    if anchor:
        presenter._pdf_text(c, 854, 28, 67, 14, presenter._short(anchor, 6), 4.7, ztm.TEXT_BODY, False, "right", 1)


def _ppt_rule11(slide, bp, u):
    micro = ztm._label_value(u.pedagogy_content, "MICRO-CASE") or "Solve one tiny mechanism-first case before adding local complexity."
    local = _rule11_local_from_unit(bp, u)
    ztm._ppt_badge(slide, .72, 1.86, 1.44, "STEP 1", ztm.PILL_BG, ztm.ACCENT_PRIMARY)
    ztm._ppt_box(slide, .72, 2.24, 5.72, 2.75, "MICRO-CASE", presenter._short(micro, 48), ztm.ACCENT_PRIMARY, ztm.BG_SURFACE, 11.0, 10.0)
    ztm._ppt_badge(slide, 6.90, 1.86, 1.44, "STEP 2", ztm.CYAN_BG, ztm.ACCENT_CYAN)
    ztm._ppt_box(slide, 6.90, 2.24, 5.72, 2.75, "SAUDI / LOCAL TRANSFER", presenter._short(local, 50), ztm.ACCENT_CYAN, ztm.BG_SURFACE, 10.5, 10.0)
    ztm._ppt_box(slide, 2.18, 5.33, 8.88, .72, "THINKING CHAIN", "Mechanism → Evidence → Decision Boundary", ztm.ACCENT_PRIMARY, ztm.PILL_BG, 8.8, 8.0)


def _pdf_rule11(c, bp, u):
    micro = ztm._label_value(u.pedagogy_content, "MICRO-CASE") or "Solve one tiny mechanism-first case before local complexity."
    local = _rule11_local_from_unit(bp, u)
    ztm._pdf_badge(c, 54, 385, 92, "STEP 1", ztm.PILL_BG, ztm.ACCENT_PRIMARY)
    ztm._pdf_box(c, 54, 185, 405, 185, "MICRO-CASE", presenter._short(micro, 48), ztm.ACCENT_PRIMARY, ztm.BG_SURFACE, 9.5, 8.0)
    ztm._pdf_badge(c, 505, 385, 92, "STEP 2", ztm.CYAN_BG, ztm.ACCENT_CYAN)
    ztm._pdf_box(c, 505, 185, 405, 185, "SAUDI / LOCAL TRANSFER", presenter._short(local, 50), ztm.ACCENT_CYAN, ztm.BG_SURFACE, 9.0, 8.0)
    ztm._pdf_box(c, 180, 98, 600, 52, "THINKING CHAIN", "Mechanism → Evidence → Decision Boundary", ztm.ACCENT_PRIMARY, ztm.PILL_BG, 7.5, 6.8)


def _preview(bp, release_state="REVIEW", source_root=None):
    text = _ORIGINAL_PREVIEW(bp, release_state=release_state, source_root=source_root)
    units = list(getattr(bp, "units", []) or [])
    if len(units) >= 11:
        u = units[10]
        old = ztm._label_value(u.pedagogy_content, "TRANSFER RULE") or "Reuse mechanism → evidence → decision boundary on the Saudi/local case."
        local = _rule11_local_from_unit(bp, u)
        text = text.replace(
            html_lib.escape(presenter._short(old, 48)),
            html_lib.escape(presenter._short(local, 50)),
            1,
        )
        # Compact the single long Rule 11 badge in the progressive presenter.
        full_tb, _ = ztm._timebox_parts(u.student_action)
        text = text.replace(
            f"TIMEBOX · {html_lib.escape(full_tb.upper())}",
            f"TIMEBOX · {html_lib.escape(_compact_timebox(full_tb).upper())}",
            1,
        )
    return text


def apply_v7291_ztm_finish_patch(app):
    global _PATCHED, _PREVIOUS_DRAFT, _ORIGINAL_PPT_SEMANTIC, _ORIGINAL_PDF_SEMANTIC, _ORIGINAL_PREVIEW
    if _PATCHED:
        return
    _PATCHED = True
    _PREVIOUS_DRAFT = engine._source_preserving_draft
    _ORIGINAL_PPT_SEMANTIC = ztm._ppt_semantic
    _ORIGINAL_PDF_SEMANTIC = ztm._pdf_semantic
    _ORIGINAL_PREVIEW = ztm.render_presenter_preview_ztm

    def draft(profile, bundle):
        return _upgrade_rule11(_PREVIOUS_DRAFT(profile, bundle))
    engine._source_preserving_draft = draft
    base.engine._source_preserving_draft = draft

    def ppt_semantic(slide, bp, u, accent):
        if u.number == 11:
            return _ppt_rule11(slide, bp, u)
        return _ORIGINAL_PPT_SEMANTIC(slide, bp, u, accent)

    def pdf_semantic(c, bp, u, accent):
        if u.number == 11:
            return _pdf_rule11(c, bp, u)
        return _ORIGINAL_PDF_SEMANTIC(c, bp, u, accent)

    ztm._ppt_taskbar = _ppt_taskbar
    ztm._pdf_taskbar = _pdf_taskbar
    ztm._ppt_semantic = ppt_semantic
    ztm._pdf_semantic = pdf_semantic
    ztm.render_presenter_preview_ztm = _preview

    presenter._ppt_semantic = ppt_semantic
    presenter._pdf_semantic = pdf_semantic
    presenter.render_presenter_preview = _preview
    base.render_presenter_preview = _preview

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "ztm_finish_version": "v7.2.9-final",
            "presenter_visual_contract": "ZTM high-contrast white surface; floating cards; indigo/cyan accents; rose reserved for CRISIS/TIMEBOX.",
            "presenter_theme": "ZTM-inspired white high-contrast source-first visual narrative",
            "presenter_contract": "ZTM visual system over Golden v6.6: 20 core units, semantic source expansions, fixed taskbar, max 30 physical slides.",
            "rule11_local_case": "Concrete bounded domain-adaptive Saudi/local case follows the micro-case; explicitly ISCARB scaffold, not P1.",
            "timebox_badge_fit": "Long compound timings are compacted in the visual pill (e.g. 1 + 5 min) while full timing remains in the task semantics.",
        })
        return data
    base._health_v440 = health
    base.engine.health = health
