from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]/'lectures'/'iscarb'
FILES={
'12':'Ch12-Safety-Engineering.html','13':'Ch13-Security-Engineering.html','14':'Ch14-Resilience-Engineering.html','15':'Ch15-Software-Reuse.html','16':'Ch16-Component-Based-Software-Engineering.html','17':'Ch17-Distributed-Software-Engineering.html','20':'Ch20-Systems-of-Systems.html'}
# Coverage anchors derived from the supplied Sommerville 10e chapter structure / key points.
ANCHORS={
'12':['safety-critical','safety requirement','safety case','hazard'],
'13':['security and dependability','security requirement','secure systems','security testing'],
'14':['cybersecurity','sociotechnical','resilient systems','critical service'],
'15':['reuse landscape','application framework','product line','application system reuse'],
'16':['component model','cbse','component composition','component'],
'17':['distributed systems','client','architectural patterns','software as a service'],
'20':['complexity','classification','reductionism','systems of systems engineering','architecture']}
SEQUENCE=[
'You sign before you know','The five-step engineering flow','Five outcomes you must prove','The source spine','The reveal','Mechanism before vocabulary','Map the system before you judge','The attractive answer still has a cost','What would another professional inspect?','Known, unknown, and monitored are not the same thing','Why this chapter matters here','A worked example of bounded judgment','AI in the assurance chain','What change would break your solution','Ready for After-Class?','What we covered — and what comes next','Your learning route this session','What you should leave with']
errors=[]
report=[]
for ch,name in FILES.items():
 p=ROOT/name
 if not p.exists(): errors.append(f'Ch{ch}: missing {name}'); continue
 s=p.read_text(encoding='utf-8',errors='ignore')
 low=s.lower()
 slides=re.findall(r'<section class="slide"',s)
 titles=re.findall(r'data-title="([^"]+)"',s)
 svgs=len(re.findall(r'<svg\b',s,re.I))
 missing=[a for a in ANCHORS[ch] if a not in low]
 if len(slides)!=20: errors.append(f'Ch{ch}: expected 20 slides, found {len(slides)}')
 if missing: errors.append(f'Ch{ch}: missing source coverage anchors: {missing}')
 pos=[]
 for title in SEQUENCE:
  try: pos.append(titles.index(title))
  except ValueError: errors.append(f'Ch{ch}: missing standard unit: {title}')
 if pos and pos!=sorted(pos): errors.append(f'Ch{ch}: standard learning sequence is out of order')
 if svgs<3: errors.append(f'Ch{ch}: only {svgs} inline diagrams; minimum is 3 before runtime visual enhancement')
 # Baseline type sizes in source; runtime layer can enlarge but not rescue tiny authoring.
 for label,pat,minv in [('h1',r'h1\{[^}]*font-size:(\d+)px',42),('card',r'\.card \.txt\{font-size:(\d+)px',20),('body',r' p\{font-size:(\d+)px',17)]:
  m=re.search(pat,s)
  if m and int(m.group(1))<minv: errors.append(f'Ch{ch}: {label} baseline {m.group(1)}px < {minv}px')
 report.append(f'Ch{ch}: slides={len(slides)} source_svgs={svgs} anchors={len(ANCHORS[ch])-len(missing)}/{len(ANCHORS[ch])}')

# Shared runtime visual/fit layer must exist and be explicitly versioned by deployment.
for fn in ['lecture-standard-v3.css','lecture-standard-v3.js']:
 if not (ROOT/fn).exists(): errors.append(f'missing shared standard layer: {fn}')

print('\n'.join(report))
if errors:
 print('\nAUDIT FAILED:',file=sys.stderr)
 print('\n'.join(' - '+e for e in errors),file=sys.stderr)
 sys.exit(1)
print('ISCARB lecture consistency audit: PASS')
