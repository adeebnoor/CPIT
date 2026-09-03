from __future__ import annotations

"""ISCARB v4.7 master guidelines.

These rules are intentionally discipline-agnostic. They constrain how a weekly
advanced software-engineering source is transformed into a 20-unit live lecture
without replacing the PRIMARY source or turning the presenter into a reading
pack.
"""

import json
import os
import re
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .models import Blueprint, LectureUnit
from . import source_visuals as sv
from . import source_visuals_v42 as sv42

MAX_CORE_ITEM_WORDS = 26
MAX_CORE_ITEMS = 3
MAX_CORE_WORDS = 58
MAX_PEDAGOGY_ITEM_WORDS = 32
PUBLIC_WEB_KIND = "public-web"
PUBLIC_VISUAL_UNITS = frozenset({1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15})
_MUTATION_UNIT = 17


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _words(text: str) -> list[str]:
    return _clean(text).split()


def _short(text: str, limit: int) -> str:
    bits = _words(text)
    return " ".join(bits[:limit])


def _keywords(text: str) -> set[str]:
    stop = {
        "engineering", "software", "system", "systems", "source", "unit", "lecture",
        "which", "what", "when", "where", "this", "that", "with", "from", "into",
        "using", "used", "their", "your", "about", "before", "after", "current",
    }
    return {
        w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text)
        if w.lower() not in stop
    }


def _best_clause(text: str, focus: str, limit: int = MAX_CORE_ITEM_WORDS) -> str:
    """Extract one short, source-grounded maxim without inventing content."""
    text = _clean(text)
    if len(text.split()) <= limit:
        return text
    focus_words = _keywords(focus)
    candidates: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+|\s*[;•▪]\s*", text):
        sentence = _clean(sentence).strip(" -;:")
        if 5 <= len(sentence.split()) <= limit:
            candidates.append(sentence)
    if candidates:
        return max(candidates, key=lambda c: (len(_keywords(c) & focus_words), -abs(len(c.split()) - 16)))
    # Printed textbook sentences can be very long. A comma-delimited clause is
    # still a complete proposition more often than a blind word truncation.
    for clause in re.split(r"\s*,\s*", text):
        clause = _clean(clause).strip(" -;:")
        if 6 <= len(clause.split()) <= limit:
            return clause
    # Last resort for the zero-API review draft only. Overflow remains preserved
    # in notes, so the presenter is concise without pretending detail vanished.
    return _short(text, limit).rstrip(" ,;:-") + "…"


def _append_overflow(unit: LectureUnit, text: str) -> None:
    text = _clean(text)
    if not text:
        return
    marker = "MASTER GUIDELINE SOURCE DETAIL (speaker notes): "
    existing = str(unit.evidence or "")
    if text not in existing:
        unit.evidence = (existing.strip() + " " + marker + text).strip()


def _focus(unit: LectureUnit) -> str:
    core = " ".join(unit.core_content[:2])
    return _clean(unit.title or core or unit.engineering_question)


def _stress_prompt(unit: LectureUnit) -> tuple[str, str]:
    blob = " ".join([unit.title, *unit.core_content]).lower()
    focus = _focus(unit)
    if any(x in blob for x in ("throughput", "transaction", "request", "load", "operation", "latency")):
        variable = "100 to 100,000 operations per second"
        question = f"STRESS TEST: Which assumption in {focus} fails first when load moves from {variable}?"
    elif any(x in blob for x in ("central", "database", "architecture", "node", "distributed", "replica")):
        variable = "one centralized deployment to a multi-node distributed deployment"
        question = f"STRESS TEST: Which assumption in {focus} fails first when the structure moves from {variable}?"
    else:
        variable = "one controlled deployment to many independently configured deployments"
        question = f"STRESS TEST: Which assumption in {focus} fails first when scope moves from {variable}?"
    return question, variable


def apply_master_guidelines(bp: Blueprint) -> Blueprint:
    """Mutate a draft into the v4.7 presenter contract while preserving P1 detail."""
    # 1) Cognitive load: PRIMARY source appears as maxims, not reading paragraphs.
    for unit in bp.units:
        if not unit.core_content:
            continue
        original = [_clean(x) for x in unit.core_content if _clean(x)]
        maxims: list[str] = []
        for item in original:
            maxim = _best_clause(item, _focus(unit))
            if maxim and maxim not in maxims:
                maxims.append(maxim)
            if maxim != item:
                _append_overflow(unit, item)
        if len(maxims) > MAX_CORE_ITEMS:
            for extra in maxims[MAX_CORE_ITEMS:]:
                _append_overflow(unit, extra)
            maxims = maxims[:MAX_CORE_ITEMS]
        while sum(len(x.split()) for x in maxims) > MAX_CORE_WORDS and len(maxims) > 1:
            _append_overflow(unit, maxims.pop())
        unit.core_content = maxims

    # Opening slide: one source stake + Decision/Unknown only. The lecturer can
    # narrate the framing; it must not become a fourth paragraph-sized box.
    u1 = bp.units[0]
    if u1.core_content:
        original = u1.core_content[0]
        lean = _best_clause(original, _focus(u1), 18)
        if lean != original:
            _append_overflow(u1, original)
        u1.core_content = [lean]
    decision = next((x for x in u1.pedagogy_content if str(x).lower().startswith("decision")), "DECISION — identify the source family that controls this case before choosing a solution.")
    unknown = next((x for x in u1.pedagogy_content if str(x).lower().startswith("unknown")), "UNKNOWN — name the missing evidence that could reverse the decision.")
    u1.pedagogy_content = [decision, unknown]

    # 3) Bounded local context. Exact locality is a scenario, never a claim about
    # law/policy, and the learner may only use mechanisms already taught in P1.
    u11 = bp.units[10]
    focus11 = _focus(u11)
    u11.pedagogy_content = [
        f"HYPOTHETICAL SAUDI/LOCAL CONSTRAINT: {focus11} must operate without relying on any external service or mechanism not present in this P1 lecture.",
        "BOUNDARY: Solve only with mechanisms already taught in the current PRIMARY source; do not import a later-chapter technology.",
        "DECIDE: Change one source-taught mechanism and cite the P1 evidence that makes the change necessary.",
    ]
    u11.scenario_assumptions = ["This is a bounded instructional scenario, not a claim about Saudi law, policy, or infrastructure."]
    u11.student_action = "Resolve the bounded local constraint using only P1 mechanisms, then cite the source line that justifies your change."

    # 4) Scalability/trend must mutate a concrete variable or structure.
    u13 = bp.units[12]
    stress_q, variable = _stress_prompt(u13)
    u13.engineering_question = stress_q
    u13.pedagogy_content = [
        f"STRESS VARIABLE: {variable}.",
        "FAIL-FIRST: Identify the first source assumption that no longer holds.",
        "REDESIGN BOUNDARY: Change only mechanisms already introduced in P1 and state the cost of the change.",
    ]
    u13.student_action = "Name the fail-first assumption under the stated stress variable, redesign with P1 mechanisms only, and state the accepted cost."

    # 5) AI governance: generation is separable from professional approval.
    u15 = bp.units[14]
    u15.pedagogy_content = [
        "AI MAY ASSIST: Generate candidate test cases, failure probes, or structure a draft for human review.",
        "AI MUST NOT BE TRUSTED AUTONOMOUSLY: It may not approve the design, certify absence of defects/failure modes/vulnerabilities, or issue professional sign-off.",
        "HUMAN SIGN-OFF: The learner personally checks claims against P1, inspects or executes the evidence, searches for failure, and owns the final decision.",
    ]

    # 6) Performance-based grading: the criterion names the capability; the level
    # descriptor says what observable defense/evidence earns the level. Keep the
    # cells short enough to project at 12pt.
    # One shared descriptor repeated down every row is a table that measures
    # nothing: six criteria x four levels printed the same two sentences, so a
    # marker could not separate a learner who traced a mechanism from one who
    # recited it. Each cell now names the observable act that earns that level
    # for that capability, which is what "performance-based" has to mean.
    RUBRIC_ROWS = (
        (
            "Technical correctness + P1 fidelity",
            "Correct; quotes the bounding P1 line.",
            "Correct; points to the right P1 section.",
            "Mostly right; P1 anchor approximate.",
            "From memory; no P1 anchor.",
        ),
        (
            "Mechanism reasoning",
            "Traces a new input; predicts the break.",
            "Traces a familiar input correctly.",
            "Names steps; cannot run them.",
            "Names it; no trace attempted.",
        ),
        (
            "Alternatives + trade-offs",
            "Two options; names what each costs.",
            "A second option and one real trade-off.",
            "Alternative named; treated as free.",
            "One option, as the only possibility.",
        ),
        (
            "Evidence + falsification",
            "Names what would disprove it; looked.",
            "Names support and what would weaken it.",
            "Support only; no disconfirming test.",
            "Asserted; no evidence either way.",
        ),
        (
            "Constraint adaptation",
            "Redesigns in P1 and prices the change.",
            "Redesigns using P1 mechanisms only.",
            "Imports an untaught mechanism.",
            "Answer unchanged by the constraint.",
        ),
        (
            "Professional accountability + readiness",
            "Owns it; residual risk and next check.",
            "Owns it; states what stays unverified.",
            "Verdict given; ownership vague.",
            "Defers, or withholds nothing.",
        ),
    )
    for row, (criterion, distinguished, ready, developing, not_yet) in zip(bp.rubric_criteria, RUBRIC_ROWS):
        row.criterion = criterion
        row.distinguished = distinguished
        row.ready = ready
        row.developing = developing
        row.not_yet_ready = not_yet
    u19 = bp.units[18]
    u19.pedagogy_content = [
        "PERFORMANCE: Defend the engineering decision; recall alone does not earn capability credit.",
        "EVIDENCE: Every capability claim requires one learner artifact and one P1 source anchor.",
        "NO CREDIT: Unsupported capability claims remain unverified.",
    ]
    u19.student_action = "Defend each claimed capability with one learner artifact and one P1 source anchor; unsupported claims earn no capability credit."
    u19.takeaway = "Grades follow demonstrated engineering performance and evidence, not recall alone."
    u20 = bp.units[19]
    evidence_rule = "EVIDENCE RULE: Every final verdict must cite a P1 source anchor and a learner-produced artifact that can be challenged."
    if evidence_rule not in u20.pedagogy_content:
        u20.pedagogy_content.append(evidence_rule)
    u20.student_action = "Defend the bounded verdict with one P1 anchor, one artifact, counter-evidence, and the next verification action."

    # Visual purpose must name the unit concept so visual/text matching has an
    # explicit semantic target before any image is selected.
    for unit in bp.units:
        if unit.visual_plan is not None:
            unit.visual_plan.teaching_purpose = f"Make {_short(_focus(unit), 12)} visible for this unit's engineering decision."
    return bp


def master_gate_checks(bp: Blueprint) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    source_units = [u for u in bp.units if u.core_content]
    checks["v16_primary_source_has_no_paragraphs"] = all(
        all(len(_words(item)) <= MAX_CORE_ITEM_WORDS for item in u.core_content)
        and len(u.core_content) <= MAX_CORE_ITEMS
        and sum(len(_words(item)) for item in u.core_content) <= MAX_CORE_WORDS
        for u in source_units
    )
    checks["v16_visual_text_alignment_target_declared"] = all(
        u.visual_plan is not None
        and bool(_keywords(u.visual_plan.teaching_purpose) & _keywords(" ".join([u.title, u.engineering_question, *u.core_content])))
        for u in bp.units
    )
    u11 = " ".join([*bp.units[10].pedagogy_content, *bp.units[10].scenario_assumptions]).lower()
    checks["v16_local_context_is_bounded"] = all(x in u11 for x in ("hypothetical", "constraint", "primary source")) and any(x in u11 for x in ("only", "do not import", "not present"))
    u13 = " ".join([bp.units[12].engineering_question, *bp.units[12].pedagogy_content]).lower()
    checks["v16_scalability_has_explicit_stress_variable"] = "stress variable" in u13 and "fails first" in u13 and any(x in u13 for x in ("100", "centralized", "deployment", "distributed", "instances"))
    u15 = " ".join(bp.units[14].pedagogy_content).lower()
    checks["v16_ai_generation_is_separate_from_signoff"] = all(x in u15 for x in ("ai may assist", "ai must not be trusted autonomously", "human sign-off", "p1")) and any(x in u15 for x in ("test cases", "failure probes"))
    u19 = bp.units[18]
    rubric_blob = " ".join(
        x for r in bp.rubric_criteria
        for x in (r.criterion, r.distinguished, r.ready, r.developing, r.not_yet_ready)
    )
    u20 = " ".join([*bp.units[19].pedagogy_content, bp.units[19].student_action]).lower()
    checks["v16_grading_requires_live_evidence_defense"] = (
        "defend" in u19.student_action.lower()
        and "p1" in u19.student_action.lower()
        and "evidence" in rubric_blob.lower()
        and "p1" in rubric_blob.lower()
        and "p1" in u20
        and "artifact" in u20
    )
    return checks


def _asset_signature(plan) -> str:
    asset = getattr(plan, "asset", None)
    if asset is None:
        return ""
    return "|".join([
        str(getattr(asset, "source_kind", "")),
        str(getattr(asset, "slide_number", "")),
        str(getattr(asset, "local_path", "")),
        str(getattr(asset, "image_url", "")),
        str(getattr(asset, "source_url", "")),
    ])


def _mutation_allowed(unit: LectureUnit) -> bool:
    if unit.number != _MUTATION_UNIT:
        return False
    blob = " ".join([unit.title, unit.engineering_question, *unit.pedagogy_content]).lower()
    return any(x in blob for x in ("mutation", "constraint", "changed", "change one"))


def visual_plan_checks(bp: Blueprint, plans) -> dict[str, bool]:
    seen: dict[str, int] = {}
    unique_ok = True
    aligned_ok = True
    for unit, plan in zip(bp.units, plans):
        sig = _asset_signature(plan)
        if sig:
            if sig in seen and not _mutation_allowed(unit):
                unique_ok = False
            seen.setdefault(sig, unit.number)
        asset = getattr(plan, "asset", None)
        if asset is None:
            continue
        if getattr(asset, "source_kind", "") == PUBLIC_WEB_KIND:
            if len(_keywords(getattr(asset, "alt_text", "")) & _keywords(" ".join([unit.title, unit.engineering_question, *unit.core_content]))) < 1:
                aligned_ok = False
        elif getattr(plan, "source_slide", None):
            anchors = set(sv.anchor_slides(unit.source_anchor))
            if anchors and plan.source_slide not in anchors:
                aligned_ok = False
    return {
        "v16_no_visual_reuse_without_mutation": unique_ok,
        "v16_visual_matches_unit_concept_or_p1_anchor": aligned_ok,
    }


def _public_candidates(bp: Blueprint, unit: LectureUnit):
    if os.getenv("ISCARB_DISABLE_PUBLIC_IMAGES", "").lower() in {"1", "true", "yes"}:
        return []
    query_terms = list(_keywords(" ".join([bp.lecture_title, unit.title, unit.engineering_question, *unit.core_content[:2]])))
    query = " ".join(query_terms[:7])
    if not query:
        return []
    cache = sv._cache_dir("wikimedia-v470:" + query)
    meta = cache / "manifest.json"
    data = None
    if meta.exists():
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            data = None
    if data is None:
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search"
            f"&gsrsearch={quote_plus(query)}&gsrlimit=10&prop=pageimages|info|extracts"
            "&piprop=thumbnail&pithumbsize=1600&inprop=url&exintro=1&explaintext=1"
        )
        try:
            req = Request(url, headers={"User-Agent": "ISCARB-Visual-Lecture-Engine/2.3", "Accept": "application/json"})
            with urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read(sv.MAX_VISUAL_BYTES).decode("utf-8", "ignore"))
            meta.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except Exception:
            try:
                meta.write_text('{"query":{"pages":{}}}', encoding="utf-8")
            except Exception:
                pass
            return []
    pages = list((((data or {}).get("query") or {}).get("pages") or {}).values())
    unit_keys = _keywords(" ".join([unit.title, unit.engineering_question, *unit.core_content]))
    ranked = []
    for page in pages:
        thumb = (page.get("thumbnail") or {}).get("source")
        if not thumb:
            continue
        title = str(page.get("title") or "")
        extract = str(page.get("extract") or "")
        overlap = len(unit_keys & _keywords(title + " " + extract))
        if overlap < 1:
            continue
        full = str(page.get("fullurl") or ("https://en.wikipedia.org/wiki/" + title.replace(" ", "_")))
        asset = sv.VisualAsset(0, str(thumb), title + (" — " + _short(extract, 20) if extract else ""), full, "", PUBLIC_WEB_KIND, 0.0, ())
        ranked.append((overlap, asset))
    return [asset for _, asset in sorted(ranked, key=lambda pair: pair[0], reverse=True)]


def plans_for_blueprint_v470(bp: Blueprint, source_root=None):
    """Source-first, semantically aligned, non-repeating visual planning."""
    registry = sv.load_registry(bp, source_root=source_root)
    used: set[str] = set()
    plans = []
    for unit in bp.units:
        purpose = (unit.visual_plan.teaching_purpose if unit.visual_plan else "") or sv.TEACHING_PURPOSE.get(unit.number, "Make the decision visible.")
        anchor = (unit.source_anchor or "").strip()
        source_backed = sv._looks_source_backed(anchor)
        visual_type = sv42._visual_type(unit)
        chosen = None
        if registry and source_backed and unit.number in sv.SOURCE_VISUAL_PRIORITY:
            anchors = set(sv.anchor_slides(anchor))
            pool = [a for a in registry.assets if (not anchors or a.slide_number in anchors)]
            ranked = sorted(pool, key=lambda a: sv42._quality_score(a, unit, anchors), reverse=True)
            ranked = sv42._prefer_source_picture(ranked, unit, anchors)
            for asset in ranked:
                sig = "|".join([asset.source_kind, str(asset.slide_number), asset.local_path, asset.image_url, asset.source_url])
                if sig in used and not _mutation_allowed(unit):
                    continue
                score = sv42._quality_score(asset, unit, anchors)
                if score >= 10.0 and not sv42._looks_like_title_only(asset) and sv42._is_presentable(asset):
                    chosen = sv.VisualPlan(visual_type, purpose, "USE", f"Source visual: [P1] Slide/Page {asset.slide_number} · {registry.source_title}", True, asset.slide_number, asset, (unit.takeaway, unit.student_action))
                    used.add(sig)
                    break
        if chosen is None and unit.number in PUBLIC_VISUAL_UNITS:
            for asset in _public_candidates(bp, unit):
                sig = _asset_signature(type("P", (), {"asset": asset})())
                if sig in used:
                    continue
                chosen = sv.VisualPlan(visual_type, purpose, "USE", f"Illustrative public image · {asset.alt_text} · {asset.source_url}", False, None, asset, (unit.takeaway, unit.student_action))
                used.add(sig)
                break
        if chosen is None:
            chosen = sv.VisualPlan(
                visual_type, purpose, "REDRAW" if source_backed else "NEW",
                anchor or "ISCARB pedagogy — original teaching visualization",
                False, None, None, (unit.takeaway, unit.student_action),
            )
        plans.append(chosen)
    return plans
