"""Finalize the student-submission release without changing assessment identity or hidden STRESS.
Rebuilds the nine offline packages with the current shared runtime and refreshes release hashes.
"""
import hashlib, io, json, zipfile
from pathlib import Path
VERSION='20260922-student-submit-v1'
R=Path(__file__).resolve().parents[1]
RUNTIME='lectures/iscarb/runtime/classroom-v3.js'
CSS='lectures/iscarb/runtime/classroom-v3.css'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pubp=R/'curriculum/publication.json';pub=json.loads(pubp.read_text())
assignp=R/'curriculum/learning-path/assignments.json';assign=json.loads(assignp.read_text())
assert [a['chapter'] for a in assign][:2]==[10,11]
# These are identity contracts for students who may already have drafts.
contracts={a['chapter']:{k:a[k] for k in ['path','stress_path','edition','version','storage_key','access_key','points']} for a in assign if a['chapter'] in [10,11]}
expected={
10:{'path':'lectures/iscarb/Ch10-FBR-Student-Assignment.html','stress_path':'lectures/iscarb/reveal/r10-mastery-v2.json','edition':'mastery-v2','version':'2026-09-ch10-mastery-v2','storage_key':'fbr:cpit455:ch10:mastery:v2','access_key':'fbr:access:ch10:v4','points':4},
11:{'path':'lectures/iscarb/Ch11-FBR-Student-Assignment.html','stress_path':'lectures/iscarb/reveal/r11-mastery-v2.json','edition':'mastery-v2','version':'2026-09-ch11-mastery-v2','storage_key':'fbr:cpit455:ch11:mastery:v2','access_key':'fbr:access:ch11:a2:v1','points':5}
}
assert contracts==expected,contracts
stress_hashes={a['chapter']:sha(R/a['stress_path']) for a in assign if a['chapter'] in [10,11]}
# Rebuild every offline package so the embedded runtime matches the live lecture.
for c in pub['lectures']:
    ch=c['chapter'];name=c['path'];pn=c['offline_package'];buf=io.BytesIO();seen=set()
    with zipfile.ZipFile(R/pn) as src,zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as out:
        for info in src.infolist():
            b=src.read(info.filename)
            if info.filename==name:
                b=(R/name).read_bytes().replace(b'href="../../',b'href="https://adeebnoor.github.io/CPIT/');seen.add(name)
            elif info.filename==RUNTIME:
                b=(R/RUNTIME).read_bytes().replace(b'../../fbr-submission.html',b'https://adeebnoor.github.io/CPIT/fbr-submission.html');seen.add(RUNTIME)
            elif info.filename==CSS:
                b=(R/CSS).read_bytes();seen.add(CSS)
            elif info.filename=='README.txt':
                b+=f'\nStudent-submission alignment: {VERSION}. The 20 iSCARB rules remain available; evidence/accountability/bounded-decision discipline is embedded in the normal classroom path. Assignment 1/2 identities and hidden STRESS are unchanged.\n'.encode()
            out.writestr(info,b)
    assert seen=={name,RUNTIME,CSS},(ch,seen)
    (R/pn).write_bytes(buf.getvalue())
    with zipfile.ZipFile(R/pn) as z: assert z.testzip() is None
# Refresh declared delivery hashes.
for c in pub['lectures']:
    pub['delivery_asset_sha256'][c['path']]=sha(R/c['path'])
    pub['delivery_asset_sha256'][c['offline_package']]=sha(R/c['offline_package'])
pub['delivery_asset_sha256'][RUNTIME]=sha(R/RUNTIME)
pub['delivery_asset_sha256'][CSS]=sha(R/CSS)
for ch in [10,11]:
    p=expected[ch]['path']
    if p in pub.get('delivery_asset_sha256',{}):pub['delivery_asset_sha256'][p]=sha(R/p)
pub['student_submission_version']=VERSION
pubp.write_text(json.dumps(pub,ensure_ascii=False,indent=2)+'\n')
manifest={
 'version':VERSION,
 'assessment_contracts':contracts,
 'stress_sha256':stress_hashes,
 'assignment_sha256':{ch:sha(R/expected[ch]['path']) for ch in [10,11]},
 'runtime_sha256':sha(R/RUNTIME),
 'offline_packages':{c['chapter']:sha(R/c['offline_package']) for c in pub['lectures']},
 'guarantee':'Assignment 1/2 storage keys, access keys, editions, versions, raw points and hidden STRESS files are unchanged.'
}
(R/'curriculum/student-submit-v1-review.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
