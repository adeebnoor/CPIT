from __future__ import annotations

"""Strict end-to-end source-only tests against the actual production app.

Uses real CPIT-455 PDFs from the repository and exercises upload -> source parsing ->
20-unit draft -> Domain Spine/opening policy -> presenter preview -> all downloadable
outputs. No Gemini/API call is made.
"""

import base64
import lzma
import time
import zipfile
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent
PRESENTER = ROOT / "app" / "presenter_v67_prod.py"
if not PRESENTER.exists():
    chunks = sorted(ROOT.glob("presenter_v67_prod.xz.b64.*"))
    assert chunks, "presenter payload chunks are missing"
    payload = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

from app.home_v670 import app  # noqa: E402

client = TestClient(app)
LECTURES = [
    ("Dependable Systems", ROOT.parent / "lectures" / "cimt" / "CPIT455-class2-NooR.pdf", False),
    ("Reliability Engineering", ROOT.parent / "lectures" / "cimt" / "CPIT455-class3-NooR.pdf", False),
    ("Security Engineering", ROOT.parent / "lectures" / "cimt" / "CPIT455-class5-NooR.pdf", True),
]
FORBIDDEN = ("wikipedia.org", "wikimedia.org", "second amendment", "down syndrome")
GENERIC = ("a team must make a consequential decision", "consequential decision under uncertainty")


def _compile_source_only(title: str, source: Path) -> dict:
    assert source.is_file() and source.stat().st_size > 10_000, f"Missing real source: {source}"
    with source.open("rb") as fh:
        response = client.post(
            "/api/compile",
            files={"primary_lecture": (source.name, fh, "application/pdf")},
            data={
                "primary_url": "",
                "supporting_urls": "",
                "lecture_focus": title,
                "model": "source-only",
                "repair_rounds": "0",
                "free_tier_confirmed": "false",
            },
        )
    assert response.status_code == 200, (title, response.status_code, response.text[:1000])
    job_id = response.json().get("job_id")
    assert job_id and len(job_id) == 32, (title, response.text)

    deadline = time.time() + 90
    while time.time() < deadline:
        state = client.get(f"/api/jobs/{job_id}")
        assert state.status_code == 200, (title, state.status_code, state.text[:500])
        job = state.json()
        if job.get("status") in {"ready", "blocked", "error"}:
            break
        time.sleep(0.25)
    else:
        raise AssertionError(f"{title}: source-only compile did not finish within 90 seconds")

    assert job["status"] == "blocked", (title, job.get("status"), job.get("error"), job.get("message"))
    assert job["progress"] == 100
    assert job.get("error") in (None, ""), (title, job.get("error"))
    return job


def _assert_blueprint(title: str, job: dict, require_security_crisis: bool) -> None:
    bp = job["blueprint"]
    units = bp["units"]
    assert len(units) == 20
    assert sorted(u["number"] for u in units) == list(range(1, 21))

    # Domain Spine is a curated map, never the old heading dump.
    u2 = next(u for u in units if u["number"] == 2)
    spine = [str(x).strip() for x in u2.get("core_content", []) if str(x).strip()]
    family_count = len(bp.get("source_topic_families", []))
    assert len(spine) <= 8, (title, "Domain Spine too large", len(spine), spine)
    if family_count >= 5:
        assert len(spine) >= 5, (title, "Domain Spine too small", len(spine), spine)

    # The banned boilerplate opening must never return.
    opening_blob = " ".join([
        str(bp.get("central_engineering_crisis", "")),
        str(units[0].get("engineering_question", "")),
        " ".join(map(str, units[0].get("core_content", []))),
    ]).lower()
    for phrase in GENERIC:
        assert phrase not in opening_blob, (title, "generic opening leaked", opening_blob)

    # For Security Engineering itself we expect a source-grounded crisis, not a generic fallback.
    if require_security_crisis:
        assert "review required" not in opening_blob, (title, "security source did not yield a usable source-grounded crisis", opening_blob)
        risk_terms = ("risk", "threat", "attack", "failure", "breach", "vulnerab", "comprom", "unauthor", "damage", "harm", "security")
        assert any(term in opening_blob for term in risk_terms), (title, "opening lacks a security engineering stake", opening_blob)


def _assert_outputs(title: str, job: dict) -> None:
    job_id = job["id"]

    preview = client.get(f"/api/jobs/{job_id}/presenter")
    assert preview.status_code == 200, (title, "preview", preview.status_code, preview.text[:500])
    html = preview.text.lower()
    assert len(html) > 10_000
    for forbidden in FORBIDDEN:
        assert forbidden not in html, (title, "forbidden visual/content fallback", forbidden)

    endpoints = {
        "pptx": f"/api/jobs/{job_id}/export/pptx",
        "presenter-pdf": f"/api/jobs/{job_id}/export/presenter-pdf",
        "source-pdf": f"/api/jobs/{job_id}/export/source-pdf",
        "reading-pdf": f"/api/jobs/{job_id}/export/pdf",
        "instructor-docx": f"/api/jobs/{job_id}/export/docx",
        "student-docx": f"/api/jobs/{job_id}/export/student",
        "blueprint-json": f"/api/jobs/{job_id}/export/json",
        "authoring-prompt": f"/api/jobs/{job_id}/authoring-prompt",
    }
    blobs: dict[str, bytes] = {}
    for name, endpoint in endpoints.items():
        response = client.get(endpoint)
        assert response.status_code == 200, (title, name, response.status_code, response.text[:500] if "text" in response.headers.get("content-type", "") else len(response.content))
        blobs[name] = response.content
        assert len(response.content) > (500 if name in {"blueprint-json", "authoring-prompt"} else 5_000), (title, name, len(response.content))

    assert blobs["presenter-pdf"][:4] == b"%PDF"
    assert blobs["source-pdf"][:4] == b"%PDF"
    assert blobs["reading-pdf"][:4] == b"%PDF"
    for name in ("pptx", "instructor-docx", "student-docx"):
        assert blobs[name][:2] == b"PK", (title, name, blobs[name][:8])

    # PPTX must be structurally valid and must not embed external Wikipedia/Wikimedia relationships.
    with zipfile.ZipFile(BytesIO(blobs["pptx"])) as zf:
        names = zf.namelist()
        assert "ppt/presentation.xml" in names
        slide_xmls = [n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
        assert 22 <= len(slide_xmls) <= 30, (title, "physical slide count", len(slide_xmls))
        rel_text = " ".join(
            zf.read(n).decode("utf-8", "ignore").lower()
            for n in names if n.endswith(".rels") or n.endswith(".xml")
        )
        for forbidden in FORBIDDEN:
            assert forbidden not in rel_text, (title, "forbidden relationship/content in PPTX", forbidden)


def main() -> None:
    health = client.get("/api/health")
    assert health.status_code == 200
    h = health.json()
    assert h.get("version") == "6.9.4", h
    assert h.get("public_web_image_fallback") is False, h
    assert h.get("presenter_preview_500_fix") is True, h
    assert h.get("approved_hero_asset") == "hero_v671.svg", h
    assert h.get("hero_decoder_safe") is True, h

    home = client.get("/")
    assert home.status_code == 200
    assert "hero_v671.svg?v=7.1.1" in home.text
    assert "7.1.1 · IT-wide · Multi-source · Gate v15" in home.text

    for title, source, require_security_crisis in LECTURES:
        job = _compile_source_only(title, source)
        _assert_blueprint(title, job, require_security_crisis)
        _assert_outputs(title, job)
        unit2 = next(u for u in job["blueprint"]["units"] if u["number"] == 2)
        print(f"E2E PASS — {title}: 20 units; Domain Spine {len(unit2.get('core_content', []))} nodes; preview + 8 outputs healthy")

    print("ISCARB strict real-lecture E2E PASS — Dependable, Reliability, Security + decoder-safe hero")


if __name__ == "__main__":
    main()
