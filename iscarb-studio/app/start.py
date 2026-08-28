from __future__ import annotations

"""ISCARB process bootstrap.

Applies Gate v9 at process start without destabilizing the proven compiler module.
Gate v9 keeps the v8 provenance/ledger/assurance repairs and adds claim-level
fidelity controls for invented precision, unsupported authority claims, human-
factors source attribution, and mandatory readiness-orientation references.
"""

import uuid

from fastapi import HTTPException

from . import main as engine
from .gate import failed_check_names
from .gate_v9 import deterministic_gate as gate_v9, normalize_blueprint_for_gate
from .models import AuditIssue, AuditReport, JobState


_original_timebox = engine.apply_90_minute_timebox
_original_health = engine.health


def _timebox_v9(bp, profile, bundle):
    bp = _original_timebox(bp, profile, bundle)
    try:
        source_text = bundle.combined_local_text()
    except Exception:
        source_text = ""
    return normalize_blueprint_for_gate(bp, source_text=source_text, profile=profile)


def _health_v9():
    data = _original_health()
    data.update({
        "deterministic_gate": "v9-claim-level-fidelity",
        "local_pre_gate_normalizer": True,
        "local_gate_repair": True,
        "local_normalizer_scope": [
            "core/pedagogy/enrichment provenance channel cleanup",
            "Unit 10 KNOWN/UNKNOWN/DECISION-SENSITIVE UNKNOWN/WHAT WE MONITOR ledger",
            "Unit 20 bounded assurance language with residual uncertainty",
            "unsourced precise numeric/percentage claims labeled as synthetic exercises",
            "unreferenced regulatory/market authority claims bounded as hypothetical context",
            "human-factors concepts kept out of source-locked core unless P1-supported",
            "Units 16-17 readiness orientation URL present while ETEC remains authority",
        ],
    })
    return data


# main._compile resolves these globals at runtime, so patching here upgrades both
# initial generation and every post-repair pass while preserving the rest of the
# compiler implementation.
engine.deterministic_gate = gate_v9
engine.apply_90_minute_timebox = _timebox_v9
engine.health = _health_v9

from . import faculty_main as faculty  # noqa: E402  (import only after engine patching)

app = faculty.app


@app.post("/api/jobs/{job_id}/local-repair")
def local_gate_repair(job_id: str):
    """Deterministically repair a generated Blueprint without a Gemini call.

    This is deliberately NOT a release authority. It repairs structural/channel
    and claim-level issues and re-renders assets, but the result remains BLOCKED
    until a full semantic/source audit is run again.
    """
    try:
        old = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, "Job not found")
    if old.blueprint is None:
        raise HTTPException(409, "No Blueprint is available to repair")

    repaired = normalize_blueprint_for_gate(
        old.blueprint,
        source_text="",
        profile=old.source_profile,
    )
    checks = gate_v9(repaired, old.source_profile, "")
    failures = failed_check_names(checks)

    new_id = uuid.uuid4().hex
    issue = AuditIssue(
        severity="major",
        unit_numbers=[],
        requirement="Local deterministic repair — semantic audit not repeated",
        problem=(
            "Gate v9 claim-level normalization was applied locally without Gemini. "
            + ("Remaining deterministic checks: " + ", ".join(failures[:24]) if failures else "No Gate v9 deterministic failures remain in the locally repairable set.")
        ),
        repair_instruction="Use these outputs for faculty review. Re-run the full compiler/audit before assigning ISCARB Verified.",
    )
    audit = AuditReport(
        overall_pass=False,
        source_fidelity_pass=(
            checks.get("no_obvious_unsourced_terms_in_core", False)
            and checks.get("human_factors_not_misattributed_to_p1_core", False)
        ),
        engineering_rigor_pass=(
            checks.get("unit10_known_unknown_monitoring", False)
            and checks.get("unit20_assurance_language", checks.get("unit20_uses_bounded_assurance_language", False))
            and checks.get("no_unsourced_precision_in_noncore", False)
        ),
        cumulative_fidelity_pass=not any(name.startswith((
            "unit2_", "unit3_", "unit4_", "unit11_", "unit12_", "unit13_", "unit14_", "unit15_", "unit16_", "unit17_", "unit18_", "unit19_"
        )) for name in failures),
        readiness_alignment_pass=not any("readiness" in name or "etec" in name for name in failures),
        provenance_separation_pass=not any(any(k in name for k in [
            "provenance", "enrichment", "unsourced", "source_anchor", "pedagogy_channel", "external_authority", "human_factors"
        ]) for name in failures),
        issues=[issue],
        strengths=[
            "Gate v9 retains v8 whole-phrase/source-profile provenance checks.",
            "Unit 10 contains a visible four-state information ledger.",
            "Unit 20 assurance language is bounded and retains residual uncertainty.",
            "Precise non-source exercise values are labeled synthetic instead of presented as evidence.",
            "Unreferenced regulatory/market claims are converted to explicit hypothetical context.",
            "Human-factors enrichment cannot masquerade as P1 source content.",
        ],
    )
    job = JobState(
        id=new_id,
        status="blocked",
        progress=100,
        message="LOCAL REPAIR COMPLETE — Gate v9 claim-level normalization applied with 0 Gemini calls. Outputs are ready for faculty review; semantic RELEASE audit was not repeated.",
        filename=old.filename,
        model="local-gate-v9-repair",
        source_manifest=list(old.source_manifest),
        lecture_focus=old.lecture_focus,
        source_profile=old.source_profile,
        blueprint=repaired,
        audit=audit,
        deterministic_checks=checks,
        error=None,
    )
    engine.save_job(job)
    return {"job_id": new_id, "remaining_failures": failures}


# Extend the existing v3.4.1 shell without copying the homepage. The result card
# gets a prominent local-repair action whenever a Blueprint exists.
_original_shell = faculty._output_v4_shell


def _gate_v9_shell(html: str) -> str:
    html = _original_shell(html)
    html = html.replace("v3.4.1 · Output v4", "v3.4.3 · Gate v9 + Output v4")
    html = html.replace("v3.4.1 Output v4", "v3.4.3 Gate v9 + Output v4")

    marker = "${issues?`<div class=\"issues\">${issues}</div>`:''}<div class=\"assets\">"
    repair = "${issues?`<div class=\"issues\">${issues}</div>`:''}<div style=\"margin:12px 0;padding:12px;border:1px solid #d8c9e8;background:#f7f3fb;border-radius:11px\"><b>Gate v9 local repair</b><div style=\"font-size:.66rem;color:#657169;margin:4px 0 9px\">Fix provenance leakage, synthetic precision, unsupported authority claims, Unit 10 information-ledger structure, readiness references and bounded Unit 20 assurance without Gemini. The repaired copy remains REVIEW REQUIRED until semantic audit is repeated.</div><button type=\"button\" onclick=\"localRepair('${id}')\" style=\"border:0;background:#563c7d;color:white;border-radius:8px;padding:9px 12px;font-weight:900;cursor:pointer\">Repair locally · NO GEMINI →</button></div><div class=\"assets\">"
    if marker in html and "localRepair('${id}')" not in html:
        html = html.replace(marker, repair)

    js = r'''
async function localRepair(id){
  const statusMsg=document.getElementById('statusMsg');
  if(statusMsg)statusMsg.textContent='Applying Gate v9 claim-level repair — 0 Gemini calls…';
  try{
    const r=await fetch('/api/jobs/'+id+'/local-repair',{method:'POST'});
    const data=await r.json();
    if(!r.ok)throw new Error(data.detail||JSON.stringify(data));
    await poll(data.job_id);
  }catch(ex){showError(ex.message)}
}
'''
    if "async function localRepair" not in html:
        html = html.replace("</script>", js + "\n</script>")
    return html


faculty._output_v4_shell = _gate_v9_shell
