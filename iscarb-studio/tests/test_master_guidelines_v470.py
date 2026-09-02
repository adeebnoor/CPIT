from __future__ import annotations

from pathlib import Path

from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile
from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.master_guidelines_v470 import apply_master_guidelines, master_gate_checks
from app.session_gate import apply_90_minute_timebox

ROOT = Path(__file__).resolve().parents[2]
LECTURES = ROOT / "lectures" / "cimt"


def _sample():
    pdfs = sorted(LECTURES.glob("*.pdf"))
    if not pdfs:
        return None
    pdf = pdfs[0]
    bundle = SourceBundle(items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)], lecture_focus="", session_minutes=90)
    profile = build_deterministic_source_profile(bundle, "master-guideline-test")
    bp = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
    return apply_master_guidelines(bp)


def test_master_guidelines_are_executable():
    bp = _sample()
    if bp is None:
        return
    checks = master_gate_checks(bp)
    assert checks and all(checks.values()), checks


def test_source_content_is_short_maxims_not_paragraphs():
    bp = _sample()
    if bp is None:
        return
    for unit in bp.units:
        assert len(unit.core_content) <= 3
        assert all(len(x.split()) <= 26 for x in unit.core_content)


def test_ai_signoff_stays_human():
    bp = _sample()
    if bp is None:
        return
    blob = " ".join(bp.units[14].pedagogy_content).lower()
    assert "ai may assist" in blob
    assert "ai must not be trusted autonomously" in blob
    assert "human sign-off" in blob
    assert "p1" in blob


def test_grading_requires_p1_evidence_and_artifact():
    bp = _sample()
    if bp is None:
        return
    assert "p1" in bp.units[18].student_action.lower()
    assert "artifact" in bp.units[18].student_action.lower()
    assert "p1" in bp.units[19].student_action.lower()
    assert "artifact" in bp.units[19].student_action.lower()
