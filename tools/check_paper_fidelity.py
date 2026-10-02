"""Fail publication when the live iSCARB course drifts from the preprint contract.

The preprint allows presentation/UX changes, but pins the scientific lecture data,
formal objectives/readings/self-checks and Mastery-v2 assessed assignments.
"""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
from course_shell import strip_assessment_presentation

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "curriculum/iscarb-paper-fidelity.json").read_text(encoding="utf-8"))
PUB = json.loads((ROOT / "curriculum/publication.json").read_text(encoding="utf-8"))

def sha_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()

def lecture_data(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'<script id="lecture-data" type="application/json">([\s\S]*?)</script>', text)
    if not m:
        raise ValueError(f"Missing lecture-data in {path}")
    data = json.loads(m.group(1))
    for k in ("version", "release", "presentationMode"):
        data.pop(k, None)
    return data

def lecture_hash(data: dict) -> str:
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def main() -> int:
    errors: list[str] = []
    ref = CONTRACT["reference"]
    claims = CONTRACT["claims"]

    if PUB.get("release") != ref["release"]:
        errors.append(f"Release drift: {PUB.get('release')} != {ref['release']}")
    if PUB.get("student_submission_version") != ref["student_submission_version"]:
        errors.append("Student submission version drifted from the preprint release.")
    if PUB.get("assignment_release"):
        errors.append("Post-preprint assignment_release must not be active in the paper-fidelity release.")

    pub_lectures = {str(x["chapter"]): x for x in PUB["lectures"]}
    for ch, spec in CONTRACT["lectures"].items():
        if ch not in pub_lectures:
            errors.append(f"Missing Chapter {ch} lecture metadata.")
            continue
        path = ROOT / spec["path"]
        try:
            data = lecture_data(path)
        except Exception as exc:
            errors.append(f"Chapter {ch} lecture parse error: {exc}")
            continue
        if lecture_hash(data) != spec["lecture_data_sha256"]:
            errors.append(f"Chapter {ch} scientific lecture-data changed from the preprint contract.")
        ids = [x["id"] for x in data.get("slides", [])]
        if ids != spec["core_keys"]:
            errors.append(f"Chapter {ch} slide grammar/order changed.")
        if len(ids) != claims["slides_per_chapter"]:
            errors.append(f"Chapter {ch} no longer has exactly 20 slides.")
        if len(data.get("objectives", [])) != claims["objectives_per_chapter"]:
            errors.append(f"Chapter {ch} objective count changed.")
        if len(data.get("stations", [])) != claims["stations_per_chapter"]:
            errors.append(f"Chapter {ch} station count changed.")
        if len(data.get("rules", [])) != claims["rules_per_chapter"]:
            errors.append(f"Chapter {ch} 20-rule grammar changed.")
        if not data.get("aiAssignment"):
            errors.append(f"Chapter {ch} lost its embedded AI transfer/practice challenge.")

    pub_assignments = {str(x["chapter"]): x for x in PUB["assignments"]}
    for ch, spec in CONTRACT["assignments"].items():
        a = pub_assignments.get(ch)
        if not a:
            errors.append(f"Missing Chapter {ch} assessed assignment metadata.")
            continue
        for key in ("path", "stress_path", "edition", "version"):
            if a.get(key) != spec[key]:
                errors.append(f"Chapter {ch} assignment {key} drifted: {a.get(key)!r} != {spec[key]!r}")
        if a.get("edition") != claims["assessed_assignment_edition"]:
            errors.append(f"Chapter {ch} assessed assignment is not Mastery v2.")
        ap, sp = ROOT / spec["path"], ROOT / spec["stress_path"]
        # Only the exact shared header/footer and CSS preference loader are new.
        # Keep the original preprint hash for ALL other bytes, including every script.
        try:
            original = strip_assessment_presentation(ap.read_text(encoding="utf-8"))
            assignment_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()
        except (OSError, ValueError):
            assignment_hash = None
        if assignment_hash != spec["assignment_sha256_lf"]:
            errors.append(f"Chapter {ch} assessed assignment content changed.")
        if spec.get("stress_delivery") == "lms":
            # Same pinned STRESS, delivered through the LMS: the page carries its text fingerprint.
            if a.get("stress_text_sha256") != spec.get("stress_text_sha256") or f'"sha": "{spec.get("stress_text_sha256")}"' not in ap.read_text(encoding="utf-8"):
                errors.append(f"Chapter {ch} LMS STRESS fingerprint drifted.")
        elif not sp.is_file() or sha_lf(sp) != spec["stress_sha256_lf"]:
            errors.append(f"Chapter {ch} STRESS payload changed.")

    public_files = PUB.get("iscarb_public_files", [])
    for pat in CONTRACT["forbidden_public_patterns"]:
        if any(pat in p for p in public_files):
            errors.append(f"Post-preprint experimental path is still public: {pat}")

    for name in CONTRACT["official_guidance"]:
        path = ROOT / name
        if not path.is_file():
            errors.append(f"Missing official guidance page: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in CONTRACT["forbidden_official_phrases"]:
            if phrase.lower() in text.lower():
                errors.append(f"{name} still presents post-preprint assessment identity: {phrase}")

    hub = (ROOT / "iscarb.html").read_text(encoding="utf-8")
    if "transfer/practice layer" not in hub:
        errors.append("Course hub must state that AI is a transfer/practice layer.")
    if "separate AI-only outcome" not in hub:
        errors.append("Course hub must state that the assessed assignment is not a separate AI-only outcome.")
    for ch, label in CONTRACT.get("hub_assignment_labels", {}).items():
        if label not in hub:
            errors.append(f"Course hub assignment label drifted for Chapter {ch}: {label}")
    for phrase in CONTRACT.get("forbidden_hub_phrases", []):
        if phrase.lower() in hub.lower():
            errors.append(f"Course hub still contains post-preprint workflow language: {phrase}")
    builder = (ROOT / "tools/build_public_site.py").read_text(encoding="utf-8")
    for name in CONTRACT.get("forbidden_public_root_files", []):
        if repr(name) in builder or f'"{name}"' in builder:
            errors.append(f"Post-preprint root file is still staged publicly: {name}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        "PASS: iSCARB matches preprint contract "
        "(20/5/3/20 lecture grammar; scientific lecture-data pinned; "
        "AI transfer/practice layer; Mastery-v2 assignments and STRESS pinned)."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
