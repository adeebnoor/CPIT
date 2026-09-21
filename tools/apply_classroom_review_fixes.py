"""Explicit review corrections for the pinned 20260921 payload; no content generation.
Fix legacy-entry routing and a DOM test expecting bullet lists on title/map screens.
Preserve assessed assignment bytes and all source files.
"""
from pathlib import Path
import hashlib,io,json,zipfile
R=Path(__file__).resolve().parents[1]
def patch(name,before,after):
    p=R/name;s=p.read_text(encoding='utf-8')
    if before in s:
        assert s.count(before)==1,name
        p.write_text(s.replace(before,after),encoding='utf-8')
    else:assert after in s,name+' does not match the reviewed correction'
patch('lectures/iscarb/runtime/classroom-v3.js',
      'function open(k){if(D.slides.some(s=>s.id===k))',
      'function open(k){k=(D.aliases||{})[k]||k;if(D.slides.some(s=>s.id===k))')
patch('tools/learning-path-tests/check-visual.cjs',
      'if(s.bullets){assert(x.d.querySelectorAll',
      "if(!['TITLE','START','MAP','END'].includes(s.id)){assert(x.d.querySelectorAll")
patch('tools/classroom-v3-tests/check-classroom-http.py',
      "response=await page.goto(urljoin(BASE,c['path']),wait_until='networkidle');assert response.status==200",
      "response=await page.goto(urljoin(BASE,c['path'])+'#START',wait_until='networkidle');assert response.status==200")
patch('tools/classroom-v3-tests/check-classroom-http.py',
      "assert D['release']==PUB['release'] and len(D['slides'])==20",
      "assert D['release']==PUB['release'] and len(D['slides'])==20\n     assert 'This earlier unit' not in await page.locator('#modal-body').inner_text(),'Existing hub entry must resolve'\n     await page.evaluate('iscarb.closeModal()')")
for p in (R/'lectures/iscarb/packages').glob('Ch*-iSCARB.zip'):
    out=io.BytesIO()
    with zipfile.ZipFile(p) as src,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data=src.read(info.filename)
            if info.filename.endswith('/runtime/classroom-v3.js'):
                data=data.replace(b'function open(k){if(D.slides.some(s=>s.id===k))',b'function open(k){k=(D.aliases||{})[k]||k;if(D.slides.some(s=>s.id===k))')
            dst.writestr(info,data)
    p.write_bytes(out.getvalue())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'curriculum/publication.json';pub=json.loads(p.read_text())
for name in pub['delivery_asset_sha256']:pub['delivery_asset_sha256'][name]=sha(R/name)
p.write_text(json.dumps(pub,ensure_ascii=False,indent=2)+'\n')
p=R/'curriculum/classroom-v3-review.json';review=json.loads(p.read_text())
review['review_corrections']=['Resolve legacy START entry through explicit chapter aliases.','Keep bullet-list assertions on concept screens; title/map screens have separate structure checks.','Exercise existing hub anchors in the real-origin test.']
p.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
m=Path('/tmp/classroom-manifest.json')
if m.is_file():
    d=json.loads(m.read_text());d['review_fix_script_sha256']=sha(Path(__file__))
    for name in d['files']:d['files'][name]=sha(R/name)
    m.write_text(json.dumps(d))
print('Applied explicit routing/test corrections; refreshed exact runtime and offline-package hashes.')
