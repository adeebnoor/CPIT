from __future__ import annotations

"""v7.2.5 — lock the production lecture grammar to the user-approved v6.6 Balanced30 Golden Master.

The v6.6 model is not merely a dark theme.  It keeps exactly twenty learner-visible
core cognitive jobs and preserves source depth in up to eight *semantic* SOURCE
EXPANSION pages.  Later releases accidentally treated expansions mostly as text
overflow; that moved source teaching into U11-U15 and changed the approved story.

This patch restores the v6.6 contract while retaining later source parsing, generic
IT intake, hero, and public-image safety fixes.
"""

import json
import re
from typing import Iterable

from . import main as engine
from . import start_v440 as base
from . import v670_contract as contract
from . import presenter_v67_prod as presenter

_PATCHED = False
_NOTE_PREFIX = "ISCARB_GOLDEN_V660_EXPANSIONS="
_GOLDEN_AFTER = [6, 7, 8, 10, 11, 12, 14, 15]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


def _slide_no(anchor: str) -> int | None:
    m = re.search(r"\bSLIDE\s+(\d{1,3})\b", str(anchor or ""), re.I)
    return int(m.group(1)) if m else None


def _parts(text: str) -> list[str]:
    vals=[]
    for raw in re.split(r"\s*[·•▪■◆]\s*|(?<=[.!?])\s+", str(text or "")):
        s=re.sub(r"\s+", " ", raw).strip(" ·•-–—:;")
        if not s: continue
        if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", s): continue
        if re.search(r"^chapter\s+\d+\b", s, re.I): continue
        if s.lower() in {"example", "examples", "topics covered"}: continue
        if s not in vals: vals.append(s)
    return vals


def _short_source_lines(items: Iterable, max_items: int = 6) -> list[str]:
    out=[]
    for item in items:
        label=str(getattr(item, "label", "") or "").strip()
        chunks=_parts(getattr(item, "why_important", ""))
        for s in chunks:
            if _norm(s)==_norm(label): continue
            # Keep source statements legible on a projected slide.
            if len(s)>220:
                sent=re.split(r"(?<=[.!?;])\s+", s)[0].strip()
                s=sent if len(sent)>=20 else s[:217].rstrip()+"…"
            if len(s.split())>=4 and s not in out:
                out.append(s)
            if len(out)>=max_items: return out
    return out


def _items_in(profile, lo: int, hi: int):
    rows=[]
    for item in list(getattr(profile, "coverage_items", []) or []):
        n=_slide_no(getattr(item, "source_anchor", ""))
        if n is not None and lo<=n<=hi: rows.append(item)
    return rows


def _topics_covered_nodes(profile) -> list[str]:
    for item in list(getattr(profile, "coverage_items", []) or []):
        if _norm(getattr(item, "label", "")) != "topics covered": continue
        vals=[]
        for s in _parts(getattr(item, "why_important", "")):
            if _norm(s) in {"topics covered"}: continue
            if 1<=len(s.split())<=7 and not re.search(r"\d", s): vals.append(s)
        vals=list(dict.fromkeys(vals))
        if 3<=len(vals)<=8: return vals
    return []


def _source_anchor(lo: int, hi: int) -> str:
    return f"[P1] SLIDE {lo}" if lo==hi else f"[P1] SLIDES {lo}–{hi}"


def _ch10_signature(profile) -> bool:
    labels={_norm(getattr(x, "label", "")) for x in list(getattr(profile, "coverage_items", []) or [])}
    required={
        "dependability properties", "sociotechnical systems", "redundancy and diversity",
        "dependable processes", "formal methods and dependability",
    }
    return required.issubset(labels)


def _ch10_expansions(profile) -> list[dict]:
    """Reference regression generated directly from P1 slide ranges in the approved v6.6 deck."""
    specs=[
        (6, 8,10, "Dependability properties — precise definitions",
         "Keep source definitions visible; the diagram is the map, not the whole lesson.",
         "Pick one property that could conflict with another and give the deployment consequence."),
        (7,11,13, "How dependability is actually achieved",
         "Dependability is built before deployment and sustained during operation.",
         "Name one prevention action and one recovery action for your local system."),
        (8,19,22, "Sociotechnical systems — the full stack",
         "A software decision can fail because the problem lives above or below the application layer.",
         "Trace one regulatory change from society down to the application layer."),
        (10,23,25, "Regulation and compliance — evidence is part of the system",
         "Critical-system approval is not a software-only decision.",
         "For the Saudi/local case, name the evidence an external regulator would need before approval."),
        (11,26,30, "Redundancy and diversity — useful, but not automatically safe",
         "Independence is the assumption that makes redundancy and diversity valuable.",
         "Choose redundancy or diversity for one failure mode, then name the common-mode failure that could defeat it."),
        (12,31,36, "Dependable processes — what ‘good process’ means",
         "Repeatability is necessary, but assurance also requires evidence outsiders can inspect.",
         "Pick two process attributes and explain what evidence would prove they exist in practice."),
        (14,37,38, "Dependable processes and agility — where the tension really is",
         "Agile can be used, but pure agile is difficult when certification needs evidence.",
         "Choose one agile practice to keep and one assurance activity that must remain non-negotiable."),
        (15,39,45, "Formal methods — mechanism, benefits, adoption limits",
         "Do not reduce formal methods to ‘mathematics = safe’; keep the source qualifications.",
         "Name one class of error formal methods can expose and one reason an organization may still reject their use."),
    ]
    out=[]
    for idx,(after,lo,hi,title,obj,task) in enumerate(specs,1):
        rows=_items_in(profile,lo,hi)
        content=_short_source_lines(rows,6)
        # A heading-only source range is never allowed to produce an empty expansion.
        if not content:
            content=[str(getattr(x,"label","") or "").strip() for x in rows if str(getattr(x,"label","") or "").strip()][:5]
        out.append({
            "after_unit":after,"title":title,"objective":obj,"content":content[:6],
            "source_anchor":_source_anchor(lo,hi),"student_task":task,
            "reason":"golden-v660-semantic-source-preservation","expansion_id":f"X{idx:02d}",
        })
    return out


def _generic_high_level_nodes(profile) -> list[str]:
    nodes=_topics_covered_nodes(profile)
    if nodes: return nodes[:8]
    rows=[]
    for item in list(getattr(profile,"topic_families",[]) or []):
        name=str(getattr(item,"name","") or "").strip()
        if not name or len(name.split())>8: continue
        key=_norm(name)
        if key and key not in {_norm(x) for x in rows}: rows.append(name)
    # A readable map is deliberately curated, never a heading dump.
    if len(rows)>8:
        idx=[round(i*(len(rows)-1)/7) for i in range(8)]
        rows=[rows[i] for i in dict.fromkeys(idx)]
    return rows[:8]


def _generic_expansions(profile) -> list[dict]:
    major=[x for x in list(getattr(profile,"coverage_items",[]) or [])
           if str(getattr(x,"importance","") or "")=="major" and _slide_no(getattr(x,"source_anchor","")) is not None]
    if not major: return []
    major.sort(key=lambda x:_slide_no(getattr(x,"source_anchor","")) or 10**6)
    nodes=_generic_high_level_nodes(profile)
    starts=[]
    for node in nodes:
        nn=_norm(node); hits=[x for x in major if _norm(getattr(x,"label",""))==nn]
        if hits: starts.append((node,_slide_no(getattr(hits[0],"source_anchor",""))))
    starts=[x for x in starts if x[1] is not None]
    starts.sort(key=lambda x:x[1])
    if not starts:
        # Fall back to source quartiles, preserving meaning instead of arbitrary text overflow.
        spans=[]; n=len(major); groups=min(8,max(1,round(n/5)))
        for i in range(groups):
            a=round(i*n/groups); b=round((i+1)*n/groups); chunk=major[a:b]
            if chunk: spans.append((str(getattr(chunk[0],"label","Source detail")),_slide_no(getattr(chunk[0],"source_anchor","")),_slide_no(getattr(chunk[-1],"source_anchor",""))))
    else:
        last=max(_slide_no(getattr(x,"source_anchor","")) or 0 for x in major)
        spans=[]
        for i,(name,lo) in enumerate(starts):
            hi=(starts[i+1][1]-1) if i+1<len(starts) else last
            spans.append((name,lo,hi))
    # v6.6 gives long source families two semantic pages and short families one.
    expanded=[]
    for name,lo,hi in spans:
        length=max(1,hi-lo+1); count=2 if length>=8 else 1
        if count==1: expanded.append((name,lo,hi))
        else:
            mid=(lo+hi)//2; expanded += [(name,lo,mid),(name,mid+1,hi)]
    # Preserve the maximum physical budget: cover + 20 core + <=8 expansions + close.
    if len(expanded)>8:
        # Evenly retain chapter-wide coverage rather than dropping the tail.
        ids=[round(i*(len(expanded)-1)/7) for i in range(8)]
        expanded=[expanded[i] for i in dict.fromkeys(ids)]
    out=[]
    for idx,(name,lo,hi) in enumerate(expanded[:8],1):
        rows=_items_in(profile,lo,hi); content=_short_source_lines(rows,6)
        if not content: continue
        after=_GOLDEN_AFTER[min(idx-1,len(_GOLDEN_AFTER)-1)]
        title=f"{name} — source detail" if idx==1 or name not in [x["title"].split(" — ")[0] for x in out] else f"{name} — continued"
        out.append({"after_unit":after,"title":title,
                    "objective":"Preserve source detail that is necessary for the engineering decision.",
                    "content":content[:6],"source_anchor":_source_anchor(lo,hi),
                    "student_task":"Use one source detail on this page to strengthen or challenge the current decision.",
                    "reason":"golden-v660-semantic-source-preservation","expansion_id":f"X{idx:02d}"})
    return out


def _encode_specs(bp, specs: list[dict]):
    notes=[x for x in list(getattr(bp,"release_notes",[]) or []) if not str(x).startswith(_NOTE_PREFIX)]
    notes.append(_NOTE_PREFIX+json.dumps(specs,ensure_ascii=False,separators=(",",":")))
    bp.release_notes=notes[:20]


def _decode_specs(bp) -> list[dict]:
    for note in list(getattr(bp,"release_notes",[]) or []):
        text=str(note)
        if text.startswith(_NOTE_PREFIX):
            try:
                rows=json.loads(text[len(_NOTE_PREFIX):])
                if isinstance(rows,list): return rows[:8]
            except Exception: return []
    return []


def _restore_core_jobs(bp, profile):
    """Restore the v6.6 twenty-job spine without deleting any P1 evidence.

    Technical overflow is carried by the semantic expansions; U11-U15 therefore
    return to the engineering judgment jobs shown in the approved Golden Master.
    """
    units=list(getattr(bp,"units",[]) or [])
    if len(units)!=20: return bp
    nodes=_topics_covered_nodes(profile) or _generic_high_level_nodes(profile)
    if 3<=len(nodes)<=8:
        bp.source_topic_families=nodes
        u2=units[1]; u2.title="Domain spine"; u2.core_content=nodes
        u2.pedagogy_content=["MAP — see the chapter as a decision map before reading details."]
        u2.student_action="Use the map to explain which source family controls the decision."
        u2.takeaway="The Domain Spine is a readable source map, not a heading dump."
    structural={
        3:("Five learning outcomes","Every outcome requires visible evidence, not recognition alone.","Choose the outcome you expect to find hardest and explain why."),
        4:("Six engineering capabilities","The learner is evaluated as an engineer, not a note-taker.","Identify which capability would fail first if the source evidence were misunderstood."),
        5:("Prediction gate","Do the reasoning before naming the principle.","Commit to a prediction, constraint, derivation, and principle before seeing the worked answer."),
        10:("Known, unknown, monitor","Separate evidence from uncertainty before approval.","Separate known facts from unknowns, then monitor the decision-sensitive risk."),
        11:("Saudi/local application","Apply the source mechanism to a realistic local system.","State the Saudi case while naming the source mechanism and the decision boundary."),
        12:("Owner, evidence, sign-off","A dependable answer names who owns the evidence.","Name the owner, evidence owner, and sign-off point for the design decision."),
        13:("Stress test: change one source variable","Find the first assumption that fails.","Change one source variable and state which assumption fails first."),
        14:("Practitioner workload","The decision has a human operating cost as well as a technical cost.","Name the practitioner workload and explain whether the design reduces or increases it."),
        15:("AI assist, human sign-off","AI may assist; accountable human sign-off remains explicit.","Say where AI may assist and where human sign-off is mandatory."),
        16:("Build the decision artifact","The artifact must make the trade-off and evidence visible.","Submit one artifact that shows trade-off, evidence, readiness probe, and uncertainty."),
        17:("Change one constraint","A strong decision survives mutation — or explains why it changes.","Mutate one constraint, redesign the decision, then exchange critiques."),
        18:("Defend the decision","An answer becomes engineering only when the argument is inspectable.","Defend one decision with claim, evidence, warrant, counter-evidence, and residual uncertainty."),
        19:("Rubric: six criteria × four levels","Score evidence honestly; unsupported claims remain weak claims.","Score your artifact across all six criteria and four levels."),
        20:("Take-home decision","Close with a bounded verdict, not a slogan.","Deliver the bounded verdict with one P1 anchor, one artifact, counter-evidence, and next verification."),
    }
    for n,(title,q,task) in structural.items():
        u=units[n-1]; u.title=title; u.engineering_question=q; u.student_action=task
    # Source-only deterministic drafts used U11-U15 to carry chapter overflow.
    # The Golden Master moves that detail to X-pages, so replace only generated
    # source-only scaffolding; AI-authored/core evidence is never silently erased.
    if str(getattr(bp,"generation_mode","") or "").lower() in {"source-only","source_only","deterministic","quota-safe-draft","legacy"}:
        u11=units[10]; u11.core_content=[]; u11.pedagogy_content=["LOCAL CASE — hypothetical Saudi context.","DECISION QUESTION — which source mechanism controls approval?","BOUNDARY — use only mechanisms already taught from P1."]
        u12=units[11]; u12.core_content=[]; u12.pedagogy_content=["OWNER — accountable for the decision.","EVIDENCE — maintains the inspectable artifact.","SIGN-OFF — accepts residual risk."]
        u13=units[12]; u13.core_content=[]; u13.pedagogy_content=["CHANGE VARIABLE — alter one source-grounded condition.","FAILS FIRST — name the first broken assumption.","REDESIGN — update the decision and evidence plan."]
        u14=units[13]; u14.core_content=[]; u14.pedagogy_content=["ENGINEERING BURDEN — implementation and verification work.","OPERATIONAL BURDEN — monitoring, documentation, coordination.","TRADE-OFF — evidence quality versus delivery/operating load."]
        u15=units[14]; u15.core_content=[]; u15.pedagogy_content=["AI MAY PREPARE EVIDENCE — candidate tests, summaries, alternatives.","AI MUST NOT OWN ASSURANCE — no autonomous approval.","HUMAN SIGN-OFF — accountable engineer accepts the decision boundary."]
    return bp


def _golden_plan_expansions(bp, target=30):
    specs=_decode_specs(bp)
    if specs: return specs[:max(0,min(8,int(target or 30)-22))]
    return _ORIGINAL_PLAN_EXPANSIONS(bp,target)


def _golden_physical_slide_plan(bp,target=30,strict=True):
    if strict and not contract.verdict_eligible(bp):
        raise ValueError("Bounded Verdict blocked until Rule 18 assurance and 6x4 rubric are complete")
    specs=_golden_plan_expansions(bp,target); by={}
    for s in specs: by.setdefault(int(s.get("after_unit",15)),[]).append(s)
    plan=[{"kind":"COVER"}]
    for u in bp.units:
        plan.append({"kind":"CORE","unit_number":u.number})
        for s in by.get(u.number,[]): plan.append({"kind":"SOURCE_EXPANSION",**s})
    plan.append({"kind":"CLOSE"})
    if len(plan)>30: raise ValueError(f"Golden v6.6 Balanced30 overflow: {len(plan)} physical slides")
    for i,row in enumerate(plan,1): row.update(physical_index=i,physical_total=len(plan))
    return plan


_ORIGINAL_DRAFT = None
_ORIGINAL_PLAN_EXPANSIONS = contract.plan_expansions
_ORIGINAL_PHYSICAL = contract.physical_slide_plan


def apply_v725_golden_v660_patch(app):
    global _PATCHED,_ORIGINAL_DRAFT
    if _PATCHED: return
    _PATCHED=True
    _ORIGINAL_DRAFT=engine._source_preserving_draft
    def golden_draft(profile,bundle):
        bp=_ORIGINAL_DRAFT(profile,bundle)
        bp=_restore_core_jobs(bp,profile)
        specs=_ch10_expansions(profile) if _ch10_signature(profile) else _generic_expansions(profile)
        _encode_specs(bp,specs)
        bp.release_notes=[x for x in bp.release_notes if "Golden v6.6" not in x][:19]+["Golden v6.6 Balanced30 model locked: 20 core cognitive jobs + semantic P1 source expansions + close; max 30 physical slides."]
        return bp
    engine._source_preserving_draft=golden_draft
    base.engine._source_preserving_draft=golden_draft
    contract.plan_expansions=_golden_plan_expansions
    contract.physical_slide_plan=_golden_physical_slide_plan
    for mod in (presenter,base):
        if hasattr(mod,"plan_expansions"): setattr(mod,"plan_expansions",_golden_plan_expansions)
        if hasattr(mod,"physical_slide_plan"): setattr(mod,"physical_slide_plan",_golden_physical_slide_plan)
    try:
        from . import start_v670_prod as prod
        prod.plan_expansions=_golden_plan_expansions
        prod.physical_slide_plan=_golden_physical_slide_plan
    except Exception: pass
    # Health is a release contract, not cosmetic versioning.
    previous=base._health_v440
    def health():
        data=dict(previous()); data.update({
            "golden_master":"v6.6 Balanced30 user-approved",
            "golden_master_locked":True,
            "golden_core_units":20,
            "golden_source_expansions":"semantic P1 preservation; up to 8",
            "golden_physical_max":30,
            "golden_story":"CRISIS > MAP > MECHANISM > TRADE-OFF > EVIDENCE > VERDICT",
            "golden_task_footer":"YOUR TASK on every learner-visible page",
            "golden_theme":"BlackNative/TextGold + magenta/cyan/gold",
        }); return data
    base._health_v440=health; base.engine.health=health
