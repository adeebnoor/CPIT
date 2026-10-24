"""Ten-minute opener before the Chapter 15 lecture: «وطن آمن ووعي رقمي» (idempotent).

The university asked for ten minutes at the start of one lecture per section in the week from 25 October 2026.
Chapter 15 is the lecture of that week. lectures/iscarb/runtime/opener-v1.js shows a full-screen opener before the
first slide (the four themes in the course's terms, "verify before you share" with FIT, EVIDENCE, BOUND and ACT,
two fictional situations for a show of hands, and a ten-minute clock). "Start the lecture" closes it. It opens by
itself only in presenter mode (?presenter=1), once per session at the start of the lecture until 1 November 2026;
anyone can open it from #AWARENESS. The twenty lecture slides and the lecture data are unchanged.

Adds the script to the Chapter 15 lecture and registers it in the publication allowlist, the asset hashes and the
offline packages.
"""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
JS = 'lectures/iscarb/runtime/opener-v1.js'
LECTURE = ROOT / 'lectures/iscarb/Ch15-Software-Reuse.html'
TAG = '<script src="runtime/opener-v1.js?v=20261025-awareness"></script>'
ANCHOR = '<script src="runtime/classroom-v3.js?'


def main():
    t = LECTURE.read_text(encoding='utf-8')
    if TAG not in t:
        assert t.count(ANCHOR) == 1, 'classroom-v3.js tag not found once'
        t = t.replace(ANCHOR, TAG + ANCHOR)
        LECTURE.write_text(t, encoding='utf-8')
    p = ROOT / 'curriculum/publication.json'
    pub = json.loads(p.read_text(encoding='utf-8'))
    if JS not in pub['iscarb_public_files']:
        pub['iscarb_public_files'] = sorted(pub['iscarb_public_files'] + [JS])
    pub['delivery_asset_sha256'][JS] = hashlib.sha256((ROOT / JS).read_bytes()).hexdigest()
    p.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    r = ROOT / 'tools/prepare_readable_release.py'
    s = r.read_text(encoding='utf-8')
    old, new = "'lectures/iscarb/runtime/story-v3.js',", "'lectures/iscarb/runtime/story-v3.js','lectures/iscarb/runtime/opener-v1.js',"
    if new not in s:
        assert s.count(old) == 1
        r.write_text(s.replace(old, new), encoding='utf-8')
    print('Chapter 15 opener applied and registered')


if __name__ == '__main__':
    main()
