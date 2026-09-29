"""Seal assignment STRESS payloads so the public site never serves new evidence in plain text.

The assignment page asks for an unlock code after Part A is committed and decrypts the
payload in the browser (PBKDF2-SHA256 -> AES-256-GCM, Web Crypto). Only the instructor
holds the codes; release each chapter's code in Blackboard when students may see STRESS.

Keep both input files OUTSIDE this repository. Never commit plaintext STRESS or codes.

  plain.json  {"lectures/iscarb/reveal/r16-mastery-v2.json": {"label": "...", "text": "...", "principle": "..."}, ...}
  codes.json  {"16": "ABCD-EFGH-JKMN", ...}   (one code per chapter)

Usage:
  python3 tools/seal_stress.py --new-codes codes.json            # create random codes (refuses to overwrite)
  python3 tools/seal_stress.py --plain plain.json --codes codes.json   # write sealed payloads
  python3 tools/seal_stress.py --verify --plain plain.json --codes codes.json

Requires the "cryptography" package (pip install cryptography). Not needed at runtime or in CI.
"""
from __future__ import annotations
import argparse, base64, json, os, secrets, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I/L
ITERATIONS = 250_000
PUBLIC_LABEL = "STRESS · new evidence"


def normalize(code: str) -> str:
    return "".join(ch for ch in code.upper() if ch.isalnum())


def new_code() -> str:
    raw = "".join(secrets.choice(ALPHABET) for _ in range(12))
    return f"{raw[:4]}-{raw[4:8]}-{raw[8:]}"


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def derive(code: str, salt: bytes, iterations: int) -> bytes:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(normalize(code).encode("utf-8"))


def seal(chapter: str, version: str, plain: dict, code: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    assert len(normalize(code)) == 12, f"Chapter {chapter}: code must have 12 characters"
    salt, iv = os.urandom(16), os.urandom(12)
    body = {k: plain[k] for k in ("label", "text", "principle") if plain.get(k)}
    assert body.get("text", "").strip(), f"Chapter {chapter}: missing STRESS text"
    ct = AESGCM(derive(code, salt, ITERATIONS)).encrypt(
        iv, json.dumps(body, ensure_ascii=False).encode("utf-8"), f"{chapter}|{version}".encode("utf-8"))
    return {"chapter": str(chapter), "version": version, "label": PUBLIC_LABEL,
            "sealed": {"v": 1, "alg": "AES-256-GCM", "kdf": "PBKDF2-SHA256", "iter": ITERATIONS,
                       "salt": b64(salt), "iv": b64(iv), "ct": b64(ct)}}


def unseal(payload: dict, code: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    s = payload["sealed"]
    key = derive(code, base64.b64decode(s["salt"]), s["iter"])
    aad = f"{payload['chapter']}|{payload['version']}".encode("utf-8")
    return json.loads(AESGCM(key).decrypt(base64.b64decode(s["iv"]), base64.b64decode(s["ct"]), aad))


def version_of(path: Path, plain: dict) -> str:
    if plain.get("version"):
        return plain["version"]
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))["version"]
    raise SystemExit(f"No version known for {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plain")
    ap.add_argument("--codes")
    ap.add_argument("--new-codes", metavar="FILE")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.new_codes:
        out = Path(args.new_codes)
        if out.exists():
            raise SystemExit(f"{out} exists; refusing to overwrite codes.")
        if out.resolve().is_relative_to(ROOT):
            raise SystemExit("Keep the codes file outside the repository.")
        chapters = ["10", "11", "12", "13", "14", "15", "16", "17", "20"]
        out.write_text(json.dumps({c: new_code() for c in chapters}, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {len(chapters)} codes to {out}. Keep it private.")
        return 0
    if not (args.plain and args.codes):
        ap.error("--plain and --codes are required")
    for f in (args.plain, args.codes):
        if Path(f).resolve().is_relative_to(ROOT):
            raise SystemExit(f"{f} is inside the repository; keep plaintext and codes outside it.")
    plain = json.loads(Path(args.plain).read_text(encoding="utf-8"))
    codes = json.loads(Path(args.codes).read_text(encoding="utf-8"))
    for rel, body in plain.items():
        path = ROOT / rel
        chapter = str(body.get("chapter") or json.loads(path.read_text(encoding="utf-8"))["chapter"])
        code = codes[chapter]
        if args.verify:
            got = unseal(json.loads(path.read_text(encoding="utf-8")), code)
            assert got["text"] == body["text"], f"{rel}: decrypted text differs"
            print(f"OK  {rel}")
            continue
        payload = seal(chapter, version_of(path, body), body, code)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Sealed {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
