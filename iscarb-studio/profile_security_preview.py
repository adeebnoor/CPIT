from __future__ import annotations

import base64, cProfile, io, lzma, pstats, time
from pathlib import Path
from fastapi.testclient import TestClient

ROOT=Path(__file__).resolve().parent
PRESENTER=ROOT/'app'/'presenter_v67_prod.py'
if not PRESENTER.exists():
    chunks=sorted(ROOT.glob('presenter_v67_prod.xz.b64.*'))
    payload=''.join(p.read_text(encoding='ascii').strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

from app.home_v670 import app

client=TestClient(app)
source=ROOT.parent/'lectures'/'cimt'/'CPIT455-class5-NooR.pdf'
assert source.is_file()
with source.open('rb') as fh:
    r=client.post('/api/compile',files={'primary_lecture':(source.name,fh,'application/pdf')},data={
        'primary_url':'','supporting_urls':'','lecture_focus':'Security Engineering','model':'source-only','repair_rounds':'0','free_tier_confirmed':'false'})
assert r.status_code==200,r.text
job_id=r.json()['job_id']
for _ in range(400):
    j=client.get(f'/api/jobs/{job_id}').json()
    if j['status'] in {'blocked','ready','error'}: break
    time.sleep(.1)
assert j['status']=='blocked',j.get('error')

prof=cProfile.Profile()
t0=time.perf_counter(); prof.enable()
resp=client.get(f'/api/jobs/{job_id}/presenter')
prof.disable(); elapsed=time.perf_counter()-t0
assert resp.status_code==200,(resp.status_code,resp.text[:500])
print(f'SECURITY PREVIEW ELAPSED={elapsed:.3f}s bytes={len(resp.content)}')
s=io.StringIO(); pstats.Stats(prof,stream=s).sort_stats('cumulative').print_stats(60)
print(s.getvalue())
