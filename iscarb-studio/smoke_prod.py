from __future__ import annotations

"""Build-time smoke test for the production ISCARB presenter.

This intentionally exercises the exact surfaces that have regressed in the past:
- production patch import order
- current LectureUnit schema vs. Balanced30 planning
- presenter HTML/PPTX/PDF rendering
- source-native visual policy / public-web fallback block
- curated Domain Spine
- generic-crisis block
- exact user-supplied original Black Desert camel PNG hero payload
- single-language UI, clean multi-source intake and source-figures-first policy

The Docker image must not deploy if any of these checks fail.
"""

import base64
import hashlib
import lzma
import os
import tempfile
import zipfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app"
PRESENTER = APP / "presenter_v67_prod.py"

if not PRESENTER.exists():
    chunks = sorted(ROOT.glob("presenter_v67_prod.xz.b64.*"))
    assert chunks, "presenter_v67_prod payload chunks are missing"
    payload = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

os.environ["ISCARB_DISABLE_PUBLIC_IMAGES"] = "1"
os.environ["ISCARB_VISUAL_POLICY"] = "p1-source>native>local-context>text-first"

from app.home_v670 import faculty_studio_v670_home  # noqa: E402
from app import master_guidelines_v470 as master  # noqa: E402
from app import patch_v690  # noqa: E402
from app import presenter_v67_prod as presenter  # noqa: E402
from app.models import Blueprint, CLO, LectureUnit, RubricCriterion, TopicCoverage  # noqa: E402


def _phase(n: int) -> str:
    if n <= 4:
        return "IFHAM"
    if n <= 9:
        return "MARIS"
    if n <= 17:
        return "ATQAN"
    return "MAYYIZ"


def _unit(n: int) -> LectureUnit:
    if n == 2:
        core = [f"13.{i} Security engineering domain node {i}" for i in range(1, 11)]
        anchor = "[P1] Slide 2"
    elif n == 6:
        core = [f"Source-backed security mechanism statement {i} with sufficient teaching detail." for i in range(1, 10)]
        anchor = "[P1] Slide 6"
    else:
        core = [
            f"Source-backed technical statement for unit {n} explaining the engineering mechanism.",
            f"A second source-bounded point for unit {n} preserves technical teaching density.",
        ]
        anchor = f"[P1] Slide {n}"
    return LectureUnit(
        number=n,
        phase=_phase(n),
        title=f"Unit {n}",
        engineering_question=f"What engineering decision is controlled by mechanism {n}?",
        core_content=core,
        pedagogy_content=["DECISION — select a defensible design response.", "EVIDENCE — state what would reverse the decision."],
        enrichment_content=[],
        enrichment_basis=[],
        scenario_assumptions=[],
        knowledge_types=["CONCEPT"],
        visual_suggestion="Use a native diagram when it clarifies the mechanism; otherwise text-first.",
        student_action="State the decision and evidence.",
        takeaway="Source fidelity controls the decision.",
        cimtlens=["N/A"],
        clo_ids=["CLO1"],
        source_anchor=anchor,
        planned_minutes=4,
    )


def _blueprint() -> Blueprint:
    clos = [
        CLO(id=f"CLO{i}", statement=f"Evaluate source-grounded security decision {i}.", evidence_expected="A defensible decision with source evidence.")
        for i in range(1, 6)
    ]
    rubrics = [
        RubricCriterion(
            criterion=f"Criterion {i}",
            distinguished="Technically precise and source-grounded.",
            ready="Correct with adequate evidence.",
            developing="Partially correct or weak evidence.",
            not_yet_ready="Unsupported or technically incorrect.",
        )
        for i in range(1, 7)
    ]
    families = [f"13.{i} Security engineering family {i}" for i in range(1, 13)]
    return Blueprint(
        lecture_title="Security Engineering — Production Smoke Test",
        engineering_thesis="Security engineering must connect mechanisms, policy, evidence and accountable design decisions.",
        central_engineering_crisis="A credential reuse attack can compromise a dependent service unless authentication boundaries and recovery controls are designed explicitly.",
        named_ethical_purpose="Protect users from preventable security harm while preserving accountable system operation.",
        clos=clos,
        source_topic_families=families,
        topic_coverage=[TopicCoverage(topic_family=families[0], source_anchor="[P1] Slide 1", first_taught_unit=1)],
        coverage_ledger=[],
        readiness_alignment=[],
        rubric_criteria=rubrics,
        release_notes=[],
        session_minutes=90,
        source_manifest=[],
        deferred_topics=[],
        units=[_unit(i) for i in range(1, 21)],
        generation_mode="production-smoke",
    )


def main() -> None:
    bp = _blueprint()
    assert not hasattr(bp.units[0], "overflow_content"), "Smoke fixture unexpectedly has legacy overflow_content"
    plan = presenter._physical_plan(bp)
    assert plan[0][0] == "cover" and plan[-1][0] == "close"
    assert sum(1 for kind, *_ in plan if kind == "unit") == 20, "Physical plan lost a core unit"
    assert len(plan) <= 30, f"Balanced30 exceeded physical limit: {len(plan)}"
    assert not any(kind == "expansion" and getattr(unit, "number", None) == 2 for kind, unit, _ in plan), "Domain Spine expanded into a heading dump"
    assert any(kind == "expansion" and getattr(unit, "number", None) == 6 for kind, unit, _ in plan), "Genuine source overflow was not expanded"

    assert os.environ.get("ISCARB_DISABLE_PUBLIC_IMAGES") == "1"
    assert getattr(master, "PUBLIC_VISUAL_UNITS", frozenset()) == frozenset(), "Public visual units were re-enabled"
    assert patch_v690._GENERIC_CRISIS.search("A team must make a consequential decision under uncertainty."), "Generic crisis guard regressed"
    nodes = patch_v690.curated_domain_nodes([f"13.{i} Topic {i}" for i in range(1, 21)], 8)
    assert 5 <= len(nodes) <= 8, f"Domain Spine returned {len(nodes)} nodes instead of 5–8"
    blocked = patch_v690._safe_local_asset(SimpleNamespace(source_kind="public-web", source_url="https://en.wikipedia.org/wiki/Second_Amendment", image_url=""))
    assert blocked is None, "Wikipedia/public-web visual was not blocked"
    if hasattr(presenter, "_public_candidates"):
        assert presenter._public_candidates(bp, bp.units[0]) == [], "Presenter public candidate fallback is active"

    hero = APP / "static" / "hero_user_original.png"
    assert hero.exists(), "Exact user-supplied original hero PNG is missing"
    hero_bytes = hero.read_bytes()
    assert len(hero_bytes) == 2_315_610, f"Exact hero byte length changed: {len(hero_bytes)}"
    assert hero_bytes.startswith(b"\x89PNG\r\n\x1a\n"), "Exact user-supplied hero is not PNG"
    assert hashlib.sha256(hero_bytes).hexdigest() == "8967fa14fe910e5831531a6b74c64bcd650c965ad691697dd2d705d450b6e50d", "Exact hero checksum changed"

    response = faculty_studio_v670_home()
    html = bytes(response.body).decode("utf-8", "replace")
    assert response.status_code == 200
    assert "hero_user_original.png?v=7.1.4" in html, "Production home is not using the exact user-supplied original hero"
    for legacy in ("hero_v670.jpg", "hero_v671.svg", "hero_v672.webp", "hero_original_v713.jpg"):
        assert legacy not in html, f"Legacy/substitute hero is still referenced: {legacy}"
    assert 'data-lang="en"' in html, "Production home must start in one language, not bilingual mode"
    assert "site_v701_i18n.js?v=single-language-v1" in html, "Single-language localization surface is missing"
    assert "site_v710_sources.js?v=clean-multisource-v1" in html, "Clean multi-source intake patch is missing"
    assert "SOURCE FIGURES FIRST" in html, "Source-figures-first policy badge regressed"
    assert "7.1.4" in html, "Production home UI version stamp regressed"

    with tempfile.TemporaryDirectory(prefix="iscarb-smoke-") as td:
        root = Path(td)
        preview = presenter.render_presenter_preview(bp, "BLOCKED", source_root=root)
        assert isinstance(preview, str) and len(preview) > 10_000, "Presenter HTML preview is unexpectedly empty"
        low = preview.lower()
        for forbidden in ("wikipedia.org", "wikimedia.org", "second amendment", "down syndrome"):
            assert forbidden not in low, f"Forbidden/public fallback content leaked into presenter preview: {forbidden}"

        pptx = root / "smoke.pptx"
        pdf = root / "smoke.pdf"
        presenter.export_presenter_pptx(bp, pptx, source_root=root, release_state="blocked")
        presenter.export_presenter_pdf(bp, pdf, source_root=root, release_state="blocked")
        assert pptx.exists() and pptx.stat().st_size > 20_000, "PPTX export failed or is implausibly small"
        assert pdf.exists() and pdf.stat().st_size > 10_000, "PDF export failed or is implausibly small"
        with zipfile.ZipFile(pptx) as zf:
            names = set(zf.namelist())
            assert "ppt/presentation.xml" in names, "PPTX archive is structurally invalid"
            assert len([n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")]) >= 22, "PPTX lost expected core slides"
        assert pdf.read_bytes()[:4] == b"%PDF", "PDF export signature is invalid"

    print(f"ISCARB production smoke PASS: {len(plan)} physical slides; public fallback disabled; source figures first; exact user-supplied original hero PNG + single-language + multi-source UI; HTML/PPTX/PDF renderers healthy")


if __name__ == "__main__":
    main()
