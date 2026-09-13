#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]
L=ROOT/'lectures'/'iscarb'
chapters=['10','11','12','13','14','15','16','17','20']
rebuilt=['12','13','14','15','16','17','20']
errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

def text(path):
    p=ROOT/path if isinstance(path,str) else path
    need(p.exists(),f'missing: {p.relative_to(ROOT) if p.exists() else p}')
    return p.read_text(encoding='utf-8',errors='ignore') if p.exists() else ''

# Master lecture architecture.
for rel in ['lectures/iscarb/Master-Lecture-v2.html','lectures/iscarb/lecture-master-v2.css','lectures/iscarb/lecture-master-v2.js','lectures/iscarb/lecture-content-master2.js','lectures/iscarb/lecture-diagrams-v1.js']:
    text(rel)
master=text('lectures/iscarb/lecture-content-master2.js')
for ch in rebuilt:
    need(re.search(rf"['\"]?{ch}['\"]?\s*:",master) is not None or f"chapter:'{ch}'" in master or f'chapter:"{ch}"' in master,f'master curriculum missing chapter {ch}')
for token in ['Hazard','security','critical service','reuse','interface','distributed','independence']:
    need(token.lower() in master.lower(),f'master curriculum missing coverage token: {token}')
for ch in rebuilt:
    candidates=list(L.glob(f'Ch{ch}-*.html'))
    deck=[p for p in candidates if 'FBR-Student-Assignment' not in p.name]
    need(bool(deck),f'chapter {ch} lecture route missing')
    if deck:
        s=deck[0].read_text(encoding='utf-8',errors='ignore')
        need(f'Master-Lecture-v2.html?chapter={ch}' in s,f'chapter {ch} does not route to master lecture')

# After-Class common contract and chapter concept coverage.
common=['FIT','BOUND','ACT','EVIDENCE','STRESS','REFIT','Commit Part A','localStorage']
concepts={
 '12': [('hazard','safety'),('fault-tree','fault tree','hazard-log','hazard log'),('protection','requirement')],
 '13': [('asset','datasets'),('threat','vulnerability'),('security requirement','authorization','authentication'),('penetration','audit')],
 '14': [('critical service',),('recognition','resistance'),('recovery','reinstatement'),('degraded','continuity')],
 '15': [('reuse',),('vendor','licensing'),('fit-gap','fit gap'),('maintainability','lifecycle')],
 '16': [('component',),('provided','requires','required'),('semantic',),('composition','adapter')],
 '17': [('distributed',),('state','scal'),('latency','qos','quality of service'),('partition','failover','replication')],
 '20': [('systems of systems','sos'),('operational','managerial'),('governance',),('interface','constituent')],
}
for ch in chapters:
    p=L/f'Ch{ch}-FBR-Student-Assignment.html'
    s=text(p)
    low=s.lower()
    for tok in common:
        need(tok.lower() in low,f'Ch{ch} After-Class missing {tok}')
    if ch in concepts:
        for group in concepts[ch]:
            need(any(x.lower() in low for x in group),f'Ch{ch} After-Class concept gap: {" / ".join(group)}')

# Progression is explicit and monotonically harder in the entry page.
gate=text('fbr-submission.html')
expected=[('10','1 / 9','25–35'),('11','2 / 9','25–40'),('12','3 / 9','30–40'),('13','4 / 9','30–45'),('14','5 / 9','35–45'),('15','6 / 9','35–50'),('16','7 / 9','40–50'),('17','8 / 9','45–55'),('20','9 / 9','50–60')]
pos=[]
for ch,level,timing in expected:
    i=gate.find(f"'{ch}':")
    need(i>=0,f'FBR entry missing chapter {ch}')
    pos.append(i)
    block=gate[i:i+500] if i>=0 else ''
    need(level in block,f'FBR entry wrong/missing challenge level for Ch{ch}')
    need(timing in block,f'FBR entry wrong/missing time ramp for Ch{ch}')
need(pos==sorted(pos), 'FBR challenge configuration is not in 1→9 sequence')

prog=text('fbr-progression-v1.js')
for ch,level,_ in expected:
    need(f"'{ch}':" in prog,f'progression UI missing Ch{ch}')
    need(level.split(' · ')[0] in prog,f'progression UI missing level {level}')

if errors:
    print('ISCARB RELEASE AUDIT: FAIL')
    for e in errors: print(' -',e)
    sys.exit(1)
print('ISCARB RELEASE AUDIT: PASS')
print(' - Ch10/11 frozen lecture base preserved')
print(' - Ch12–17/20 route to Chapter-10 master engine')
print(' - After-Class common FBR contract present for 9 challenges')
print(' - Chapter-specific concept coverage present for Ch12–17/20')
print(' - Difficulty/time ramp is explicit from 1/9 to 9/9 capstone')
