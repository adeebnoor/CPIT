"""Return Assignments 3–9 to automatic STRESS: the new evidence opens on the page right after Part A is committed.

Instructor's decision (5 Oct 2026): one Blackboard item per assignment, for the final PDF. No Part A upload, no
Adaptive Release and no pasted evidence. This reverses tools/apply_lms_stress.py:
- restores each reveal payload (lectures/iscarb/reveal/rNN-*.json) byte for byte from the last commit that had it;
- restores the page's original reveal() (commit first, then fetch the payload) and its reveal path;
- removes the Blackboard steps from the page text;
- drops stress_delivery / stress_text_sha256 from publication.json and the paper-fidelity contract, and lists
  the payloads as public files again (refresh_release_hashes.py then re-pins them).
The commit-then-reveal order is unchanged: the page reveals only after a verified, saved Part A commitment.
Idempotent:  python3 tools/apply_auto_stress.py
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / 'curriculum/publication.json'
FID = ROOT / 'curriculum/iscarb-paper-fidelity.json'
BEFORE = 'f94ae5f^'   # the last commit before STRESS moved to Blackboard
NEW_BULLET = ('<li><b>Commit, then the new evidence.</b> Part A becomes read-only when you commit, and the new evidence opens on this page straight away. '
              'Complete Part B, export the PDF and upload it in Blackboard.</li>')
OLD_BULLET = re.compile(r'<li><b>Commit, then Blackboard\.</b>.*?</li>', re.S)
UNDO = [
    ('You then upload the Part A record to Blackboard, which releases the new evidence. Committing here does not submit anything to the LMS.',
     'STRESS will open automatically after your commitment is saved. No code is required. This does not submit anything to the LMS.'),
    ('After you commit Part A, upload the Part A record to Blackboard. Blackboard then releases the new evidence, and you paste it here to continue.',
     'The new evidence opens automatically after you commit Part A. No unlock code is required.'),
    ("note('Part A committed. Follow the Blackboard steps below to receive the new evidence.')",
     "note('Part A committed. Continue with the new evidence and REFIT.')"),
]


def old(path: str) -> str:
    return subprocess.run(['git', 'show', f'{BEFORE}:{path}'], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def patch_page(path: str) -> bool:
    p = ROOT / path; s = s0 = p.read_text(encoding='utf-8')
    if 'const LMS_STRESS=' in s:
        o = old(path)
        a, b = o.index('async function reveal(){'), o.index('async function commit(){')
        i, j = s.index('const LMS_STRESS='), s.index('async function commit(){')
        s = s[:i] + o[a:b] + s[j:]
        ref = re.search(r'("reveal": |reveal:)\s*("[^"]*"|\'[^\']*\')', o).group(2)
        s, n = re.subn(r'("reveal": |reveal:)\s*(""|\'\')', lambda m: m.group(1) + ref, s, count=1)
        if n != 1: raise SystemExit(f'{path}: empty reveal path not found')
    for new, orig in UNDO:
        s = s.replace(new, orig)
    s = OLD_BULLET.sub(NEW_BULLET, s)
    if s != s0: p.write_text(s, encoding='utf-8')
    return s != s0


def main() -> int:
    pub = json.loads(PUB.read_text(encoding='utf-8')); fid = json.loads(FID.read_text(encoding='utf-8'))
    old_fid = json.loads(old('curriculum/iscarb-paper-fidelity.json'))
    done = []
    for kind in ('assignments', 'previous_assignments'):
        for a in pub[kind]:
            if a['chapter'] < 12: continue
            sp = ROOT / a['stress_path']
            if not sp.is_file():
                sp.write_bytes(subprocess.run(['git', 'show', f'{BEFORE}:{a["stress_path"]}'], cwd=ROOT, capture_output=True, check=True).stdout)
            if a['stress_path'] not in pub['iscarb_public_files']:
                pub['iscarb_public_files'].append(a['stress_path'])
            a.pop('stress_delivery', None); a.pop('stress_text_sha256', None)
            if patch_page(a['path']): done.append(a['path'])
            if kind == 'assignments':
                spec = fid['assignments'][str(a['chapter'])]
                spec.pop('stress_delivery', None); spec.pop('stress_text_sha256', None)
                spec.setdefault('stress_sha256_lf', old_fid['assignments'][str(a['chapter'])]['stress_sha256_lf'])
    pub['iscarb_public_files'].sort()
    PUB.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    FID.write_text(json.dumps(fid, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    # keep the concise-page generator in step, so a later run does not bring the Blackboard bullet back
    gen = ROOT / 'tools/apply_assignment_concise.py'; g = gen.read_text(encoding='utf-8')
    g2 = re.sub(r"'<li><b>Commit, then Blackboard\.</b>.*?</li>'", lambda _: repr(NEW_BULLET), g, flags=re.S)
    if g2 != g: gen.write_text(g2, encoding='utf-8')
    print(f'Automatic STRESS restored for {len(done)} page(s).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
