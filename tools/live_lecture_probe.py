#!/usr/bin/env python3
"""Compile one lecture on the live Faculty Studio and bring the deck back.

Written as a script rather than an inline workflow heredoc so it can be read,
reviewed and run locally, and so YAML quoting cannot corrupt it.

Outputs are saved before any quality judgement is made: a deck that fails a gate
is exactly the deck a reviewer needs to look at.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
import zipfile
from pathlib import Path

import requests
from pypdf import PdfReader

EXPORTS = {
    "Visual_Presenter.pptx": "export/pptx",
    "Visual_Presenter.pdf": "export/presenter-pdf",
    "Faculty_Reading_Pack.pdf": "export/pdf",
    "Instructor_Guide.docx": "export/docx",
    "Student_Activity_Pack.docx": "export/student",
    "Blueprint.json": "export/json",
}
TERMINAL = {"ready", "blocked", "error"}


def download_outputs(session, base, job: str, out: Path) -> dict:
    """Save every output a finished job exposes, tolerating the ones it lacks."""
    out.mkdir(parents=True, exist_ok=True)
    saved: dict[str, int] = {}
    preview = session.get(f"{base}/api/jobs/{job}/presenter", timeout=180)
    if preview.status_code == 200 and len(preview.content) > 500:
        (out / "Presenter_Preview.html").write_bytes(preview.content)
        saved["Presenter_Preview.html"] = len(preview.content)
        print(f"  saved Presenter_Preview.html: {len(preview.content)/1024:.0f} KB", flush=True)
    for name, path in EXPORTS.items():
        try:
            rr = session.get(f"{base}/api/jobs/{job}/{path}", timeout=300)
        except requests.RequestException as exc:
            print(f"  {name}: request failed ({exc})", flush=True)
            continue
        if rr.status_code == 200 and len(rr.content) > 500:
            (out / name).write_bytes(rr.content)
            saved[name] = len(rr.content)
            print(f"  saved {name}: {len(rr.content)/1024:.0f} KB", flush=True)
        else:
            print(f"  {name}: HTTP {rr.status_code} ({len(rr.content)} bytes)", flush=True)
    return saved


def capture_existing(session, base, job: str, out: Path) -> dict:
    health = session.get(f"{base}/api/health", timeout=90)
    health.raise_for_status()
    q = session.get(f"{base}/api/jobs/{job}", timeout=120)
    q.raise_for_status()
    final = q.json()
    out.mkdir(parents=True, exist_ok=True)
    (out / "job.json").write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")
    saved = download_outputs(session, base, job, out) if final.get("blueprint") else {}
    return {"job_id": job, "version": health.json().get("version"), "origin": f"existing job {job}",
            "final": final, "saved": saved}


def compile_lecture(session, base, args, out: Path) -> dict:
    health = session.get(f"{base}/api/health", timeout=90)
    health.raise_for_status()
    version = health.json().get("version")
    print(f"live version: {version}", flush=True)

    data = {"repair_rounds": str(args.repair_rounds), "lecture_focus": args.lecture_focus, "model": "auto"}
    if args.source_file:
        path = Path(args.source_file)
        with path.open("rb") as fh:
            r = session.post(f"{base}/api/compile", files={"primary_lecture": (path.name, fh, "application/pdf")},
                             data=data, timeout=300)
        origin = path.name
    else:
        r = session.post(f"{base}/api/compile", data={**data, "primary_url": args.source_url}, timeout=300)
        origin = args.source_url
    r.raise_for_status()
    job = r.json()["job_id"]
    print(f"job {job} compiling from {origin}", flush=True)

    final, last = None, ""
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        q = session.get(f"{base}/api/jobs/{job}", timeout=120)
        q.raise_for_status()
        final = q.json()
        line = f"{final.get('status')} {final.get('progress')} {(final.get('message') or '')[:150]}"
        if line != last:
            print(line, flush=True)
            last = line
        if final.get("status") in TERMINAL:
            break
        time.sleep(10)

    out.mkdir(parents=True, exist_ok=True)
    (out / "job.json").write_text(json.dumps(final or {}, indent=2, ensure_ascii=False), encoding="utf-8")

    saved = download_outputs(session, base, job, out) if final and final.get("blueprint") else {}
    return {"job_id": job, "version": version, "origin": origin, "final": final or {}, "saved": saved}


def quality_report(result: dict, out: Path) -> list[str]:
    """Describe the deck a reviewer is about to open. Never raises."""
    findings: list[str] = []
    final = result["final"]
    bp = final.get("blueprint") or {}
    units = bp.get("units") or []
    profile = final.get("source_profile") or {}
    checks = final.get("deterministic_checks") or {}

    report = {
        "live_version": result["version"],
        "job_id": result["job_id"],
        "source": result["origin"],
        "status": final.get("status"),
        "message": final.get("message"),
        "error": final.get("error"),
        "lecture_title": bp.get("lecture_title"),
        "units": len(units),
        "minutes": sum(int(u.get("planned_minutes") or 0) for u in units),
        "clos": len(bp.get("clOs") or bp.get("CLOs") or bp.get("clos") or []),
        "readiness_entries": len(bp.get("readiness_alignment") or []),
        "major_checkpoints": len([x for x in profile.get("coverage_items", []) if x.get("importance") == "major"]),
        "gate_pass": sum(1 for v in checks.values() if v),
        "gate_total": len(checks),
        "gate_failed": sorted(k for k, v in checks.items() if not v),
        "saved_files": result["saved"],
        "unit_titles": [f"{u.get('number')}. {u.get('title')}" for u in units],
    }

    if not units:
        findings.append("no blueprint was produced")
    else:
        if len(units) != 20:
            findings.append(f"{len(units)} units instead of 20")
        if report["minutes"] != 90:
            findings.append(f"{report['minutes']} planned minutes instead of 90")

    # The defects the live review found, checked directly on the returned deck.
    leaked = [t for t in report["unit_titles"] if "slide " in t.lower()]
    if leaked:
        findings.append(f"extractor slide coordinates in {len(leaked)} headings: {leaked[:3]}")
    glyphs = [t for t in report["unit_titles"] if any(g in t for g in "■▪●◆▶◼")]
    if glyphs:
        findings.append(f"bullet-glyph residue in {len(glyphs)} headings: {glyphs[:3]}")
    if units and not report["readiness_entries"]:
        findings.append("readiness trail is empty")

    thin = [
        u.get("number") for u in units
        if sum(len(str(x).split()) for x in (u.get("core_content") or []) + (u.get("pedagogy_content") or [])) < 12
    ]
    if thin:
        findings.append(f"near-empty units: {thin}")

    report["findings"] = findings
    (out / "qa_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== LIVE LECTURE QA ===", flush=True)
    for key in ("live_version", "status", "lecture_title", "units", "minutes", "clos",
                "readiness_entries", "major_checkpoints"):
        print(f"  {key:<20} {report[key]}", flush=True)
    print(f"  {'gate':<20} {report['gate_pass']}/{report['gate_total']} passing", flush=True)
    if report["gate_failed"]:
        print(f"  failed checks       {', '.join(report['gate_failed'][:12])}", flush=True)
    print("  findings            " + ("; ".join(findings) if findings else "none"), flush=True)
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://iscarb-lecture-studio.onrender.com")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--source-file", default="")
    ap.add_argument("--lecture-focus", default="")
    ap.add_argument("--repair-rounds", default="1")
    ap.add_argument("--timeout", type=int, default=1500)
    ap.add_argument("--out", default="live-lecture")
    ap.add_argument("--job-id", default="", help="capture a job that already ran instead of compiling")
    args = ap.parse_args()
    if not args.job_id and not args.source_url and not args.source_file:
        ap.error("give --job-id, --source-url or --source-file")

    session = requests.Session()
    session.headers.update({"User-Agent": "ISCARB-live-lecture-probe/1.0"})
    out = Path(args.out)
    base = args.base_url.rstrip("/")
    result = capture_existing(session, base, args.job_id, out) if args.job_id else compile_lecture(session, base, args, out)
    findings = quality_report(result, out)

    status = (result["final"] or {}).get("status")
    if status not in {"ready", "blocked"}:
        print(f"\nFAILED: compilation ended as {status}", flush=True)
        return 1
    # A BLOCKED deck is a legitimate outcome to review, so findings are reported
    # rather than treated as a run failure.
    return 0


if __name__ == "__main__":
    sys.exit(main())
