"""Re-pin integrity hashes after an intentional, reviewed content change.

The audit and paper-fidelity checks fail on ANY byte change so that drift is never silent.
After a deliberate change has been reviewed, run this tool to record the new hashes:

  python3 tools/prepare_readable_release.py            # refresh offline ZIPs first
  python3 tools/refresh_release_hashes.py --revision 20260929-review-v1 --note "what changed and why"

It updates curriculum/publication.json (delivery asset and lecture hashes) and, with
--revision, re-pins curriculum/iscarb-paper-fidelity.json and appends a revision record.
The preprint reference (release, commit, DOI) is never changed by this tool.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_classroom import canonical_sha  # noqa: E402
from check_paper_fidelity import lecture_data, lecture_hash, sha_lf  # noqa: E402
from course_shell import strip_assessment_presentation  # noqa: E402

PUB = ROOT / "curriculum/publication.json"
FID = ROOT / "curriculum/iscarb-paper-fidelity.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--revision", help="revision id to record in the paper-fidelity contract")
    ap.add_argument("--note", default="", help="one-paragraph summary of the reviewed change")
    args = ap.parse_args()

    pub = json.loads(PUB.read_text(encoding="utf-8"))
    changed = []
    for name, old in list(pub["delivery_asset_sha256"].items()):
        new = canonical_sha(ROOT / name)
        if new != old:
            pub["delivery_asset_sha256"][name] = new
            changed.append(name)
    for lecture in pub["lectures"]:
        new = hashlib.sha256((ROOT / lecture["path"]).read_bytes()).hexdigest()
        if new != lecture["source_sha256"]:
            lecture["source_sha256"] = new
            changed.append(lecture["path"] + " (source_sha256)")
    PUB.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"publication.json: {len(changed)} hash(es) updated")
    for c in changed:
        print("  ", c)

    if args.revision:
        fid = json.loads(FID.read_text(encoding="utf-8"))
        pinned = []
        for ch, spec in fid["lectures"].items():
            h = lecture_hash(lecture_data(ROOT / spec["path"]))
            if h != spec["lecture_data_sha256"]:
                spec["lecture_data_sha256"] = h
                pinned.append(f"lecture {ch}")
        for ch, spec in fid["assignments"].items():
            text = strip_assessment_presentation((ROOT / spec["path"]).read_text(encoding="utf-8"))
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if h != spec["assignment_sha256_lf"]:
                spec["assignment_sha256_lf"] = h
                pinned.append(f"assignment {ch}")
            s = sha_lf(ROOT / spec["stress_path"])
            if s != spec["stress_sha256_lf"]:
                spec["stress_sha256_lf"] = s
                pinned.append(f"stress {ch}")
        revisions = fid.setdefault("revisions", [])
        if not any(r.get("revision") == args.revision for r in revisions):
            revisions.append({"revision": args.revision, "date": datetime.date.today().isoformat(),
                              "base_release": fid["reference"]["release"], "summary": args.note,
                              "repinned": pinned})
        else:
            for r in revisions:
                if r.get("revision") == args.revision:
                    r["repinned"] = sorted(set(r.get("repinned", [])) | set(pinned))
                    if args.note:
                        r["summary"] = args.note
        FID.write_text(json.dumps(fid, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"iscarb-paper-fidelity.json: re-pinned {len(pinned)} item(s) under revision {args.revision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
