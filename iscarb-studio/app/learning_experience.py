from __future__ import annotations

"""ISCARB v7.3.6 — narrative learning experience layer.

This module intentionally sits *above* the source-locked 20-unit compiler. It does
not rewrite technical claims. It turns a compiled Blueprint into a stateful
student journey with prediction, falsification, evidence and bounded-verdict
gates, plus an instructor progress view.

Persistence uses SQLite by default so the API has real transactional storage.
On Render free services without a persistent disk the database survives only
for the lifetime of the container; set ISCARB_LEARNING_DB_PATH to a mounted
persistent path for durable pilots.
"""

import hashlib
import hmac
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any

from fastapi import Body, Header, HTTPException, Query
from fastapi.responses import HTMLResponse

from . import main as engine

VERSION = "7.3.6"
_DB_PATH = Path(os.getenv("ISCARB_LEARNING_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "learning_experience.sqlite3")))
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_STUDENT_RE = re.compile(r"^[A-Za-z0-9._:-]{8,96}$")
_MAX_STATE_BYTES = 220_000

STATIONS = [
    {"id": "crisis", "label": "Crisis & Prediction", "units": [1, 2, 3, 4, 5]},
    {"id": "analysis", "label": "Analysis & Falsification", "units": [6, 7, 8, 9, 10]},
    {"id": "design", "label": "Design & Accountability", "units": [11, 12, 13, 14, 15]},
    {"id": "evidence", "label": "Evidence & Challenge", "units": [16, 17, 18, 19]},
    {"id": "verdict", "label": "Bounded Verdict", "units": [20]},
]

TRANSITIONS = {
    2: "BECAUSE — the crisis needs a map before a solution.",
    3: "THEREFORE — convert the source map into measurable capability.",
    4: "BUT — outcomes alone do not prove engineering judgment.",
    5: "SO — commit to a prediction before the mechanism is revealed.",
    6: "BECAUSE — prediction is useful only when first principles can test it.",
    7: "THEREFORE — turn the mechanism into an inspectable implementation structure.",
    8: "BUT — a working design still competes with alternatives.",
    9: "SO — quantify what matters and name what would falsify the choice.",
    10: "YET — measurement never removes uncertainty; separate known, unknown and monitored variables.",
    11: "THEREFORE — transfer the reasoning to the local operating context.",
    12: "BUT — a design without an accountable owner is not operationally complete.",
    13: "SO — stress the decision by changing the variable most likely to break it.",
    14: "IN CONTRAST — optimize for the people who must operate the design, not only the diagram.",
    15: "THEREFORE — bound AI assistance and keep human sign-off explicit.",
    16: "NOW — assemble the reasoning into an inspectable decision artifact.",
    17: "BUT — evidence must survive a changed constraint.",
    18: "THEREFORE — defend the claim with evidence, warrant and counter-evidence.",
    19: "YET — your own confidence is insufficient; expose the artifact to peer critique.",
    20: "FINALLY — issue only the verdict the evidence can actually support.",
}


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(_DB_PATH, timeout=8)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    return con


def _init_db() -> None:
    with _connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS learning_state (
              job_id TEXT NOT NULL,
              student_id TEXT NOT NULL,
              display_name TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL,
              updated_at REAL NOT NULL,
              PRIMARY KEY(job_id, student_id)
            );
            CREATE TABLE IF NOT EXISTS learning_audit (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              job_id TEXT NOT NULL,
              student_id TEXT NOT NULL,
              action TEXT NOT NULL,
              payload_json TEXT NOT NULL DEFAULT '{}',
              created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_learning_audit_job ON learning_audit(job_id, created_at);
            CREATE TABLE IF NOT EXISTS learning_settings (
              job_id TEXT PRIMARY KEY,
              ai_evidence_allowed INTEGER NOT NULL DEFAULT 0,
              manual_recalculation_required INTEGER NOT NULL DEFAULT 1,
              instructor_key_hash TEXT NOT NULL DEFAULT '',
              updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS peer_feedback (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              job_id TEXT NOT NULL,
              from_student_id TEXT NOT NULL,
              to_student_id TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_peer_feedback_target ON peer_feedback(job_id, to_student_id, created_at);
            """
        )
        cols = {r["name"] for r in con.execute("PRAGMA table_info(learning_settings)").fetchall()}
        if "instructor_key_hash" not in cols:
            con.execute("ALTER TABLE learning_settings ADD COLUMN instructor_key_hash TEXT NOT NULL DEFAULT ''")


_init_db()


def _load_job(job_id: str):
    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, engine.JOB_MISSING_MESSAGE)
    if job.blueprint is None:
        raise HTTPException(409, "The lecture Blueprint is not available yet. Finish compilation first.")
    return job


def _student_id(value: str) -> str:
    value = str(value or "").strip()
    if not _STUDENT_RE.match(value):
        raise HTTPException(400, "student_id must be an opaque 8–96 character identifier using letters, numbers, dot, underscore, colon or hyphen.")
    return value


def _safe_text(value: Any, cap: int = 4000) -> str:
    return " ".join(str(value or "").split())[:cap]


def _rubric(payload: dict[str, Any]) -> dict[str, Any]:
    prediction = _safe_text(payload.get("prediction"))
    falsifications = payload.get("falsifications") or {}
    accountability = payload.get("accountability") or {}
    evidence = payload.get("evidence_chain") or {}
    verdict = payload.get("verdict") or {}
    risks = payload.get("risks") or []
    tradeoffs = payload.get("tradeoffs") or {}
    completed = {int(x) for x in (payload.get("completed_units") or []) if str(x).isdigit() and 1 <= int(x) <= 20}

    dimensions = {
        "prediction": min(4, 1 + int(len(prediction) >= 35) + int(len(prediction) >= 90) + int(bool(payload.get("prediction_revisited")))),
        "falsification": min(4, 1 + int(bool(falsifications)) + int(any(len(_safe_text(v)) >= 45 for v in falsifications.values())) + int(len(falsifications) >= 2)),
        "quantification": min(4, 1 + int(bool(tradeoffs)) + int(any(_safe_text(v.get("measure") if isinstance(v, dict) else v) for v in tradeoffs.values())) + int(any(_safe_text(v.get("source_basis") if isinstance(v, dict) else "") for v in tradeoffs.values()))),
        "accountability": min(4, 1 + int(bool(accountability.get("owner"))) + int(bool(accountability.get("verifier"))) + int(bool(accountability.get("signoff")))),
        "risk": min(4, 1 + int(len(risks) >= 1) + int(len(risks) >= 3) + int(any(_safe_text(r.get("mitigation")) for r in risks if isinstance(r, dict)))),
        "evidence": min(4, 1 + sum(int(bool(_safe_text(evidence.get(k)))) for k in ("claim", "evidence", "warrant")) + int(bool(_safe_text(evidence.get("counter_evidence"))))),
        "verdict": min(4, 1 + int(verdict.get("choice") in {"accept", "conditional", "redesign", "reject"}) + int(len(_safe_text(verdict.get("reasoning"))) >= 70) + int(bool(_safe_text(verdict.get("residual_uncertainty"))))),
        "completion": 1 if len(completed) < 5 else 2 if len(completed) < 12 else 3 if len(completed) < 20 else 4,
    }
    avg = sum(dimensions.values()) / max(1, len(dimensions))
    if avg >= 3.5 and len(completed) >= 18:
        level = "Leader"
    elif avg >= 2.8 and len(completed) >= 14:
        level = "Expert"
    elif avg >= 2.0:
        level = "Practitioner"
    else:
        level = "Emerging"
    return {"level": level, "score": round(avg, 2), "dimensions": dimensions, "scale": {"1": "Emerging", "2": "Practitioner", "3": "Expert", "4": "Leader"}}


def _adaptive_suggestions(job, payload: dict[str, Any]) -> list[dict[str, str]]:
    bp = job.blueprint
    out: list[dict[str, str]] = []
    if len(_safe_text(payload.get("prediction"))) < 35:
        out.append({"gate": "Prediction", "action": "Re-read the crisis and identify one constraint, failure mode or decision variable before advancing.", "source": "U1–U5 · ISCARB prediction scaffold"})
    if not payload.get("falsifications"):
        u = bp.units[8] if len(bp.units) >= 9 else bp.units[-1]
        out.append({"gate": "Falsification", "action": "Use the source-backed mechanism around Unit 9 and name one observable result that would force redesign.", "source": _safe_text(getattr(u, "source_anchor", "P1"), 160) or "P1"})
    ev = payload.get("evidence_chain") or {}
    if not all(_safe_text(ev.get(k)) for k in ("claim", "evidence", "warrant")):
        u = bp.units[15] if len(bp.units) >= 16 else bp.units[-1]
        out.append({"gate": "Evidence chain", "action": "Complete Claim → Evidence → Warrant before adding counter-evidence and residual uncertainty.", "source": _safe_text(getattr(u, "source_anchor", "ISCARB evidence policy"), 160) or "ISCARB evidence policy"})
    return out[:4]


def _key_hash(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _claim_instructor_key(job_id: str, key: str) -> bool:
    key = str(key or "").strip()
    if len(key) < 24 or len(key) > 180:
        raise HTTPException(400, "Instructor key must be a 24–180 character random token.")
    digest = _key_hash(key)
    _settings(job_id)
    with _connect() as con:
        row = con.execute("SELECT instructor_key_hash FROM learning_settings WHERE job_id=?", (job_id,)).fetchone()
        current = str(row["instructor_key_hash"] or "") if row else ""
        if current and not hmac.compare_digest(current, digest):
            raise HTTPException(409, "This lecture already has an instructor access key. Use the browser that created the learning experience.")
        if not current:
            con.execute("UPDATE learning_settings SET instructor_key_hash=?,updated_at=? WHERE job_id=?", (digest, time.time(), job_id))
    return True


def _require_instructor_key(job_id: str, key: str) -> None:
    key = str(key or "").strip()
    if not key:
        raise HTTPException(401, "Instructor access key required.")
    with _connect() as con:
        row = con.execute("SELECT instructor_key_hash FROM learning_settings WHERE job_id=?", (job_id,)).fetchone()
    if not row or not row["instructor_key_hash"] or not hmac.compare_digest(str(row["instructor_key_hash"]), _key_hash(key)):
        raise HTTPException(403, "Invalid instructor access key.")


def _settings(job_id: str) -> dict[str, Any]:
    with _connect() as con:
        row = con.execute("SELECT * FROM learning_settings WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            now = time.time()
            con.execute("INSERT INTO learning_settings(job_id,updated_at) VALUES(?,?)", (job_id, now))
            row = con.execute("SELECT * FROM learning_settings WHERE job_id=?", (job_id,)).fetchone()
    return {
        "ai_evidence_allowed": bool(row["ai_evidence_allowed"]),
        "manual_recalculation_required": bool(row["manual_recalculation_required"]),
        "updated_at": row["updated_at"],
    }


def _load_state(job_id: str, student_id: str) -> dict[str, Any]:
    with _connect() as con:
        row = con.execute("SELECT payload_json,display_name,updated_at FROM learning_state WHERE job_id=? AND student_id=?", (job_id, student_id)).fetchone()
    if not row:
        return {"student_id": student_id, "display_name": "", "payload": {}, "updated_at": None}
    try:
        payload = json.loads(row["payload_json"])
    except Exception:
        payload = {}
    return {"student_id": student_id, "display_name": row["display_name"], "payload": payload, "updated_at": row["updated_at"]}


def _save_state(job_id: str, student_id: str, body: dict[str, Any]) -> dict[str, Any]:
    display_name = _safe_text(body.get("display_name"), 120)
    payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > _MAX_STATE_BYTES:
        raise HTTPException(413, "Learning state is too large. Keep evidence concise and attach large artifacts outside this form.")
    now = time.time()
    with _connect() as con:
        previous = con.execute("SELECT payload_json FROM learning_state WHERE job_id=? AND student_id=?", (job_id, student_id)).fetchone()
        con.execute(
            "INSERT INTO learning_state(job_id,student_id,display_name,payload_json,updated_at) VALUES(?,?,?,?,?) "
            "ON CONFLICT(job_id,student_id) DO UPDATE SET display_name=excluded.display_name,payload_json=excluded.payload_json,updated_at=excluded.updated_at",
            (job_id, student_id, display_name, encoded, now),
        )
        action = "state_created" if not previous else "state_autosaved"
        con.execute("INSERT INTO learning_audit(job_id,student_id,action,payload_json,created_at) VALUES(?,?,?,?,?)", (job_id, student_id, action, json.dumps({"completed": len(payload.get("completed_units") or []), "current_unit": payload.get("current_unit")}, ensure_ascii=False), now))
    return {"saved": True, "updated_at": now, "rubric": _rubric(payload)}


def _public_blueprint(job) -> dict[str, Any]:
    bp = job.blueprint
    units = []
    for u in bp.units:
        units.append({
            "number": u.number,
            "phase": u.phase,
            "title": u.title,
            "engineering_question": u.engineering_question,
            "core_content": list(u.core_content or []),
            "pedagogy_content": list(u.pedagogy_content or []),
            "enrichment_content": list(u.enrichment_content or []),
            "student_action": u.student_action,
            "takeaway": u.takeaway,
            "source_anchor": u.source_anchor,
            "planned_minutes": u.planned_minutes,
            "transition": TRANSITIONS.get(u.number, ""),
        })
    return {
        "lecture_title": bp.lecture_title,
        "engineering_thesis": bp.engineering_thesis,
        "central_engineering_crisis": bp.central_engineering_crisis,
        "source_topic_families": list(bp.source_topic_families or []),
        "units": units,
    }


def _student_page(job_id: str) -> str:
    return f"""<!doctype html><html lang='en' dir='ltr' data-theme='dark'><head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>ISCARB Learning Experience</title>
<link rel='stylesheet' href='/static/learning_v736.css?v={VERSION}'>
</head><body data-job='{job_id}' data-role='student'>
<div id='app'><div class='boot'>Loading the engineering journey…</div></div>
<script src='/static/learning_v736.js?v={VERSION}' defer></script></body></html>"""


def _instructor_page(job_id: str) -> str:
    return f"""<!doctype html><html lang='en' dir='ltr' data-theme='dark'><head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>ISCARB Instructor Dashboard</title>
<link rel='stylesheet' href='/static/learning_v736.css?v={VERSION}'>
</head><body data-job='{job_id}' data-role='instructor'>
<div id='app'><div class='boot'>Loading instructor evidence dashboard…</div></div>
<script src='/static/learning_v736.js?v={VERSION}' defer></script></body></html>"""


def install_learning_experience(app) -> None:
    existing = {getattr(r, "path", None) for r in getattr(app, "routes", [])}

    if "/learn/{job_id}" not in existing:
        @app.get("/learn/{job_id}", include_in_schema=False)
        def student_experience(job_id: str):
            _load_job(job_id)
            return HTMLResponse(_student_page(job_id), headers={"Cache-Control": "no-store", "X-ISCARB-Learning": VERSION})

    if "/instructor/{job_id}" not in existing:
        @app.get("/instructor/{job_id}", include_in_schema=False)
        def instructor_dashboard(job_id: str, key: str = Query(...)):
            _load_job(job_id)
            _require_instructor_key(job_id, key)
            return HTMLResponse(_instructor_page(job_id), headers={"Cache-Control": "no-store", "X-ISCARB-Learning": VERSION, "Referrer-Policy": "no-referrer"})

    if "/api/learning/{job_id}/bootstrap" not in existing:
        @app.get("/api/learning/{job_id}/bootstrap")
        def learning_bootstrap(job_id: str, student_id: str = Query(...)):
            sid = _student_id(student_id)
            job = _load_job(job_id)
            state = _load_state(job_id, sid)
            payload = state.get("payload") or {}
            return {
                "version": VERSION,
                "job_id": job_id,
                "release_state": job.status,
                "blueprint": _public_blueprint(job),
                "stations": STATIONS,
                "settings": _settings(job_id),
                "state": state,
                "rubric": _rubric(payload),
                "suggestions": _adaptive_suggestions(job, payload),
                "persistence": {"backend": "sqlite", "path_configurable": True, "durability": "persistent only when ISCARB_LEARNING_DB_PATH points to a mounted persistent disk"},
            }

    if "/api/learning/{job_id}/state" not in existing:
        @app.put("/api/learning/{job_id}/state")
        def save_learning_state(job_id: str, body: dict[str, Any] = Body(default_factory=dict)):
            _load_job(job_id)
            sid = _student_id(body.get("student_id", ""))
            return _save_state(job_id, sid, body)

    if "/api/learning/{job_id}/peer-critique" not in existing:
        @app.post("/api/learning/{job_id}/peer-critique")
        def peer_critique(job_id: str, body: dict[str, Any] = Body(default_factory=dict)):
            _load_job(job_id)
            frm = _student_id(body.get("from_student_id", ""))
            to = _student_id(body.get("to_student_id", ""))
            critique = {
                "inspectable_evidence": _safe_text(body.get("inspectable_evidence"), 1000),
                "counter_evidence": _safe_text(body.get("counter_evidence"), 1000),
                "single_change": _safe_text(body.get("single_change"), 1000),
            }
            if not all(len(v) >= 8 for v in critique.values()):
                raise HTTPException(400, "Peer critique requires inspectable evidence, counter-evidence and one falsifying change.")
            now = time.time()
            with _connect() as con:
                con.execute("INSERT INTO peer_feedback(job_id,from_student_id,to_student_id,payload_json,created_at) VALUES(?,?,?,?,?)", (job_id, frm, to, json.dumps(critique, ensure_ascii=False), now))
                con.execute("INSERT INTO learning_audit(job_id,student_id,action,payload_json,created_at) VALUES(?,?,?,?,?)", (job_id, frm, "peer_critique_submitted", json.dumps({"target": to}), now))
            return {"saved": True, "created_at": now}

    if "/api/learning/{job_id}/peer-feedback" not in existing:
        @app.get("/api/learning/{job_id}/peer-feedback")
        def get_peer_feedback(job_id: str, student_id: str = Query(...)):
            _load_job(job_id)
            sid = _student_id(student_id)
            with _connect() as con:
                rows = con.execute("SELECT from_student_id,payload_json,created_at FROM peer_feedback WHERE job_id=? AND to_student_id=? ORDER BY created_at DESC LIMIT 20", (job_id, sid)).fetchall()
            return {"feedback": [{"from": r["from_student_id"], "created_at": r["created_at"], **json.loads(r["payload_json"])} for r in rows]}

    if "/api/instructor/{job_id}/claim" not in existing:
        @app.post("/api/instructor/{job_id}/claim")
        def claim_instructor_access(job_id: str, body: dict[str, Any] = Body(default_factory=dict)):
            _load_job(job_id)
            _claim_instructor_key(job_id, str(body.get("key") or ""))
            return {"claimed": True}

    if "/api/instructor/{job_id}/settings" not in existing:
        @app.put("/api/instructor/{job_id}/settings")
        def instructor_settings(job_id: str, body: dict[str, Any] = Body(default_factory=dict), x_iscarb_instructor_key: str = Header(default="")):
            _load_job(job_id)
            _require_instructor_key(job_id, x_iscarb_instructor_key)
            ai = bool(body.get("ai_evidence_allowed", False))
            manual = bool(body.get("manual_recalculation_required", True))
            now = time.time()
            with _connect() as con:
                con.execute(
                    "INSERT INTO learning_settings(job_id,ai_evidence_allowed,manual_recalculation_required,updated_at) VALUES(?,?,?,?) "
                    "ON CONFLICT(job_id) DO UPDATE SET ai_evidence_allowed=excluded.ai_evidence_allowed,manual_recalculation_required=excluded.manual_recalculation_required,updated_at=excluded.updated_at",
                    (job_id, int(ai), int(manual), now),
                )
                con.execute("INSERT INTO learning_audit(job_id,student_id,action,payload_json,created_at) VALUES(?,?,?,?,?)", (job_id, "INSTRUCTOR", "settings_changed", json.dumps({"ai_evidence_allowed": ai, "manual_recalculation_required": manual}), now))
            return {"saved": True, **_settings(job_id)}

    if "/api/instructor/{job_id}/summary" not in existing:
        @app.get("/api/instructor/{job_id}/summary")
        def instructor_summary(job_id: str, x_iscarb_instructor_key: str = Header(default="")):
            job = _load_job(job_id)
            _require_instructor_key(job_id, x_iscarb_instructor_key)
            with _connect() as con:
                rows = con.execute("SELECT student_id,display_name,payload_json,updated_at FROM learning_state WHERE job_id=? ORDER BY updated_at DESC", (job_id,)).fetchall()
                audit_count = con.execute("SELECT COUNT(*) AS n FROM learning_audit WHERE job_id=?", (job_id,)).fetchone()["n"]
            students = []
            for row in rows:
                try:
                    payload = json.loads(row["payload_json"])
                except Exception:
                    payload = {}
                completed = {int(x) for x in (payload.get("completed_units") or []) if str(x).isdigit() and 1 <= int(x) <= 20}
                verdict = payload.get("verdict") or {}
                students.append({
                    "student_id": row["student_id"],
                    "display_name": row["display_name"],
                    "updated_at": row["updated_at"],
                    "completed_units": len(completed),
                    "current_unit": int(payload.get("current_unit") or 1),
                    "prediction_complete": len(_safe_text(payload.get("prediction"))) >= 20,
                    "falsification_complete": bool(payload.get("falsifications")),
                    "evidence_complete": all(_safe_text((payload.get("evidence_chain") or {}).get(k)) for k in ("claim", "evidence", "warrant")),
                    "verdict": verdict.get("choice") or "",
                    "rubric": _rubric(payload),
                })
            return {
                "version": VERSION,
                "lecture_title": job.blueprint.lecture_title,
                "job_id": job_id,
                "settings": _settings(job_id),
                "students": students,
                "audit_events": audit_count,
                "student_url": f"/learn/{job_id}",
                "security_note": "Instructor evidence is protected by a per-lecture access key. For high-stakes deployment, add institutional SSO/course membership before using this as a formal gradebook.",
            }


def health_fragment() -> dict[str, Any]:
    return {
        "learning_experience_version": VERSION,
        "learning_journey": "Prediction -> Analysis/Falsification -> Design/Accountability -> Evidence/Peer challenge -> Bounded Verdict",
        "learning_persistence": "SQLite transactional store; set ISCARB_LEARNING_DB_PATH to mounted persistent storage for durable pilots.",
        "learning_autorubric": "Deterministic structural rubric only; no semantic grade is fabricated by AI.",
        "learning_numeric_policy": "Quantitative trade-offs require learner/source basis; missing numbers remain explicitly unmeasured.",
    }
