"""Release gate: chapter-specific coverage, answers, links and artifact parity."""
from pathlib import Path
from html.parser import HTMLParser
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'curriculum'))
from chapters import CHAPTERS
from build_classroom import render, filename, MINUTES
REQUIRED={10:['availability','reliability','safety','security','resilience','fault','sociotechnical','redundancy','diversity','formal'],11:['pofod','rocof','mttf','mttr','operational profile','n-version','43.2'],12:['hazard','safety requirement','fault tree','safety case','inhibited'],13:['confidentiality','integrity','authorization','security requirement','penetration'],14:['critical service','resistance','recognition','recovery','reinstatement','sociotechnical'],15:['inversion of control','product line','application system reuse','fit-gap','lifecycle'],16:['provided interface','required interface','component model','sequential','hierarchical','additive','adapter'],17:['partial failure','thin client','layers','tiers','peer-to-peer','software as a service','idempotency'],20:['operational independence','managerial independence','acknowledged','collaborative','virtual','reductionism','emergence']}
class Parse(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.questions=0;self.answers=0;self.open_answers=0;self.units=0;self.visuals=0;self.skip=0;self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);cls=a.get('class','').split()
        if tag in ['script','style']:self.skip+=1
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='section' and 'question' in cls:self.questions+=1
        if tag=='section' and 'lesson-slide' in cls:self.units+=1
        if tag=='figure' and 'diagram' in cls:self.visuals+=1
        if tag=='details' and 'answer' in cls:self.answers+=1;self.open_answers+='open' in a
    def handle_endtag(self,tag):
        if tag in ['script','style']:self.skip-=1
    def handle_data(self,data):
        if not self.skip:self.text.append(data)
errors=[]
assert sum(MINUTES)==50
for ch,d in CHAPTERS.items():
    p=ROOT/'lectures/iscarb'/filename(ch);s=p.read_text();parser=Parse();parser.feed(s)
    text=' '.join(parser.text).lower()
    for anchor in REQUIRED[ch]:
        if anchor not in text:errors.append(f'Ch{ch}: missing own chapter coverage: {anchor}')
    if len(parser.ids)!=len(set(parser.ids)):errors.append(f'Ch{ch}: duplicate ids')
    for href in parser.links:
        if href.startswith('#') and href[1:] not in parser.ids:errors.append(f'Ch{ch}: unresolved fragment {href}')
    if (parser.units,parser.questions,parser.answers,parser.open_answers)!=(20,19,19,0):errors.append(f'Ch{ch}: incomplete units/answers or visible answer on load')
    if s!=render(ch,d):errors.append(f'Ch{ch}: generated page differs from authored curriculum; rebuild')
    if len(d['outcomes'])!=5 or len(d['topics'])!=8:errors.append(f'Ch{ch}: incomplete concept sequence')
    for t in d['topics']:
        if len(t['answer'].split())<15:errors.append(f'Ch{ch}: answer lacks an explanation: {t["title"]}')
    assignment=(ROOT/f'lectures/iscarb/Ch{ch}-FBR-Student-Assignment.html').read_text()
    if 'assignment-learning-path' not in assignment or 'warmup-answer' not in assignment:errors.append(f'Ch{ch}: missing warm-up scaffold')
    if f"keyBase:'fbr:cpit455:ch{ch}:prod:v4'" not in assignment:errors.append(f'Ch{ch}: original storage identity changed')
    print(f'Ch{ch}: {parser.units} units · {parser.visuals} figures · {parser.questions}/{parser.answers} questions/hidden answers')
assert abs((1-30/(30*24*60))*100-99.93055556)<1e-7
assert abs((1-60/(30*24*60))*100-99.86111111)<1e-7
assert abs(30*24*60*.001-43.2)<1e-9
if errors:print('\n'.join(errors),file=sys.stderr);sys.exit(1)
print('PASS: 180 units, 171 paired answers, chapter-specific coverage and independent numerical checks.')
