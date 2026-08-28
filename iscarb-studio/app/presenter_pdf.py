from __future__ import annotations

import re
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape

from .models import Blueprint, LectureUnit

W, H = 960, 540
INK = colors.HexColor('#1D2921')
MUTED = colors.HexColor('#657169')
PAPER = colors.HexColor('#FAF9F6')
WHITE = colors.white
GREEN = colors.HexColor('#0C533D')
GREEN2 = colors.HexColor('#1D8B56')
TEAL = colors.HexColor('#0A353E')
PURPLE = colors.HexColor('#563C7D')
GOLD = colors.HexColor('#C4A24F')
RED = colors.HexColor('#B84D52')
SOFT_GREEN = colors.HexColor('#E7F4EC')
SOFT_TEAL = colors.HexColor('#E7F0F1')
SOFT_PURPLE = colors.HexColor('#EEE8F5')
SOFT_GOLD = colors.HexColor('#F7F1E0')
SOFT_RED = colors.HexColor('#FAEBEC')
PHASE = {'IFHAM':PURPLE,'MARIS':GREEN2,'ATQAN':GOLD,'MAYYIZ':TEAL}


def _short(text: str, n: int = 72) -> str:
    t = re.sub(r'\s+',' ',str(text or '')).strip()
    if len(t) <= n:
        return t
    cut=t[:n-1].rsplit(' ',1)[0]
    return cut+'…'


def _wrap(c, text, x, y, width, size=12, color=INK, bold=False, leading=None, max_lines=4):
    font='Helvetica-Bold' if bold else 'Helvetica'
    c.setFont(font,size); c.setFillColor(color)
    words=str(text or '').split(); lines=[]; line=''
    for word in words:
        trial=(line+' '+word).strip()
        if c.stringWidth(trial,font,size) <= width:
            line=trial
        else:
            if line: lines.append(line)
            line=word
            if len(lines) >= max_lines-1: break
    if line and len(lines)<max_lines: lines.append(line)
    if words and len(' '.join(lines)) < len(' '.join(words)):
        lines[-1]=lines[-1].rstrip(' .,:;-')+'…'
    leading=leading or size*1.25
    for i,ln in enumerate(lines): c.drawString(x,y-i*leading,ln)
    return len(lines)*leading


def _round(c,x,y,w,h,fill=WHITE,stroke=colors.HexColor('#DDE4DF'),radius=12,sw=1.2):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(sw)
    c.roundRect(x,y,w,h,radius,fill=1,stroke=1)


def _pill(c,x,y,w,text,fill):
    c.setFillColor(fill); c.roundRect(x,y,w,22,11,fill=1,stroke=0)
    c.setFillColor(WHITE if fill != GOLD else INK); c.setFont('Helvetica-Bold',8)
    c.drawCentredString(x+w/2,y+7,text)


def _base(c,u:LectureUnit):
    c.setFillColor(PAPER); c.rect(0,0,W,H,fill=1,stroke=0)
    col=PHASE[u.phase]
    _pill(c,40,494,72,f'UNIT {u.number:02d}',col); _pill(c,120,494,70,u.phase,col); _pill(c,848,494,72,f'{u.planned_minutes} MIN',col)
    _wrap(c,u.title,40,465,820,25,INK,True,max_lines=2)
    _wrap(c,u.engineering_question,40,416,850,12,MUTED,True,max_lines=2)
    c.setFillColor(INK); c.rect(0,0,W,34,fill=1,stroke=0)
    c.setFillColor(colors.HexColor('#7EE0AD')); c.setFont('Helvetica-Bold',8); c.drawString(40,13,'YOU TRY')
    _wrap(c,_short(u.student_action,110),100,13,610,8,WHITE,True,max_lines=1)
    c.setFillColor(colors.HexColor('#BDC9C1')); c.setFont('Helvetica',7); c.drawRightString(920,13,_short(u.source_anchor or 'ISCARB pedagogy',55))


def _node(c,x,y,w,h,title,body='',fill=WHITE,stroke=PURPLE):
    _round(c,x,y,w,h,fill,stroke,14,1.6)
    c.setFillColor(stroke); c.setFont('Helvetica-Bold',10); c.drawCentredString(x+w/2,y+h-22,title)
    if body: _wrap(c,_short(body,72),x+12,y+h-45,w-24,9,MUTED,False,max_lines=4)


def _arrow(c,x1,y1,x2,y2,color=MUTED):
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(2); c.line(x1,y1,x2,y2)
    import math
    a=math.atan2(y2-y1,x2-x1); l=8
    pts=[(x2,y2),(x2-l*math.cos(a-.45),y2-l*math.sin(a-.45)),(x2-l*math.cos(a+.45),y2-l*math.sin(a+.45))]
    p=c.beginPath(); p.moveTo(*pts[0]); p.lineTo(*pts[1]); p.lineTo(*pts[2]); p.close(); c.drawPath(p,fill=1,stroke=0)


def _chain(c, labels):
    n=len(labels); gap=18; total=850; w=(total-gap*(n-1))/n; y=145; h=180
    for i,(t,b) in enumerate(labels):
        x=55+i*(w+gap); _node(c,x,y,w,h,t,b,WHITE,PHASE.get('MAYYIZ',TEAL))
        if i<n-1: _arrow(c,x+w+3,y+h/2,x+w+gap-3,y+h/2,INK)


def _render(c,bp:Blueprint,u:LectureUnit):
    core=list(u.core_content); ped=list(u.pedagogy_content)
    if u.number==1:
        _node(c,45,130,275,230,'INCIDENT',bp.central_engineering_crisis,SOFT_RED,RED)
        for i,s in enumerate(core[:3]): _node(c,345,287-i*78,260,62,f'SIGNAL {i+1}',s,WHITE,GREEN)
        _node(c,635,130,280,230,'DECISION','What evidence would change your first diagnosis?',SOFT_PURPLE,PURPLE)
    elif u.number==2:
        c.setFillColor(GREEN); c.circle(480,235,78,fill=1,stroke=0); c.setFillColor(WHITE); c.setFont('Helvetica-Bold',14); c.drawCentredString(480,242,'SECURITY'); c.drawCentredString(480,222,'ENGINEERING')
        fams=bp.source_topic_families[:6]; positions=[(170,320),(790,320),(120,220),(840,220),(190,120),(770,120)]
        for i,f in enumerate(fams): _node(c,positions[i][0]-85,positions[i][1]-25,170,50,f'FAMILY {i+1}',f,WHITE,PURPLE)
    elif u.number in {3,4,16}:
        if u.number==3: items=[(x.id,x.statement) for x in bp.clOs[:5]]
        elif u.number==4:
            names=['ANALYTICAL','JUDGMENT','EVIDENCE','SOCIO-TECH','RISK-AWARE','ETHICAL']; items=[(n,ped[i] if i<len(ped) else '') for i,n in enumerate(names)]
        else: items=[('PROBLEM','Frame it'),('RISK','Analyze it'),('ARCHITECTURE','Design it'),('TRADE-OFF','Defend it'),('EVIDENCE','Prove it'),('ASSURANCE','Bound it')]
        cols=3 if len(items)==6 else 5; rows=2 if cols==3 else 1; bw=260 if cols==3 else 160
        for i,(t,b) in enumerate(items):
            r=i//cols; cc=i%cols; _node(c,55+cc*(bw+25),180-r*135,bw,110,t,b,WHITE,PHASE[u.phase])
    elif u.number in {5,6,9,11,12,13,14,15,17,18}:
        mapping={
            5:[('PREDICT','Before explanation'),('CONSTRAIN','What cannot change?'),('DERIVE','Reason from mechanism'),('NAME','Reveal principle')],
            6:[('ASSET','Value'),('THREAT','Harm'),('VULNERABILITY','Exposure'),('CONTROL','Risk response')],
            9:[('GUIDELINE','Rule'),('MECHANISM','How'),('TEST','Evidence'),('FALSIFY','Failure threshold')],
            11:[('SAUDI CONTEXT','Hypothetical setting'),('RISK SHIFT','Environment changes risk'),('DESIGN IMPACT','Adapt controls')],
            12:[('SOFTWARE','Design'),('DEPLOYMENT','Configure'),('OPERATIONS','Monitor'),('ACCOUNTABILITY','Own consequence')],
            13:[('ENDURING','Principle'),('CURRENT','Practice'),('NEXT','Question')],
            14:[('DESIGN FRICTION','Opaque system'),('COGNITIVE LOAD','More pressure'),('RECOVERY','Clear path'),('WELLBEING','Less avoidable burden')],
            15:[('AI MAY ASSIST','Draft'),('SOURCE CHECK','Verify'),('TEST','Challenge'),('HUMAN SIGN-OFF','Own decision')],
            17:[('BEFORE','Current'),('MUTATION','Constraint changes'),('ADAPT','Redesign'),('CRITIQUE','Peer challenge')],
            18:[('CLAIM',''),('EVIDENCE',''),('WARRANT',''),('COUNTER-EVIDENCE',''),('RESIDUAL UNCERTAINTY','')],
        }
        _chain(c,mapping[u.number])
    elif u.number==7:
        _round(c,95,110,770,250,SOFT_PURPLE,PURPLE,28,2); c.setFillColor(PURPLE); c.setFont('Helvetica-Bold',12); c.drawString(120,332,'PLATFORM PROTECTION')
        _round(c,190,145,580,170,SOFT_GREEN,GREEN2,24,2); c.setFillColor(GREEN2); c.drawString(215,288,'APPLICATION PROTECTION')
        _round(c,310,180,340,90,SOFT_TEAL,TEAL,20,2); c.setFillColor(TEAL); c.drawCentredString(480,222,'RECORD / ASSET')
        c.setFillColor(MUTED); c.setFont('Helvetica-Bold',11); c.drawCentredString(480,80,'PROTECTION  ↔  DISTRIBUTION')
    elif u.number==8:
        _node(c,70,135,300,220,'ALTERNATIVE A',ped[0] if ped else 'Flexible COTS path',SOFT_PURPLE,PURPLE)
        c.setFillColor(GOLD); c.setFont('Helvetica-Bold',30); c.drawCentredString(480,250,'↔'); c.setFont('Helvetica-Bold',10); c.setFillColor(MUTED); c.drawCentredString(480,220,'USABILITY · RISK · OVERHEAD')
        _node(c,590,135,300,220,'ALTERNATIVE B',ped[1] if len(ped)>1 else 'Restricted client path',SOFT_GREEN,GREEN2)
    elif u.number==10:
        vals=[('KNOWN','Verified facts'),('UNKNOWN','Unresolved evidence'),('DECISION-SENSITIVE','Could change approval'),('MONITOR','Evidence to collect')]
        for i,(t,b) in enumerate(vals):
            rr=i//2; cc=i%2; _node(c,95+cc*395,235-rr*130,360,105,t,b,WHITE,GREEN2)
    elif u.number==19:
        headers=['CAPABILITY','4 · DIST.','3 · READY','2 · DEV.','1 · NOT YET']; xs=[60,460,570,680,790];
        c.setFont('Helvetica-Bold',8); c.setFillColor(MUTED)
        for x,h in zip(xs,headers): c.drawString(x,350,h)
        crit=[x.criterion for x in bp.rubric_criteria[:6]]
        cols=[GREEN2,PURPLE,GOLD,RED]
        for r,t in enumerate(crit):
            y=320-r*42; _wrap(c,_short(t,44),60,y,360,8,INK,True,max_lines=1)
            for j,col in enumerate(cols): c.setFillColor(col); c.roundRect(460+j*110,y-8,82,20,5,fill=1,stroke=0)
    elif u.number==20:
        _node(c,180,330,600,65,'TOP CLAIM',u.takeaway,TEAL,TEAL)
        for i,clo in enumerate(bp.clOs[:5]): _node(c,55+i*175,185,150,105,clo.id,clo.evidence_expected,WHITE,TEAL)
        labels=[('APPROVE',GREEN2),('CONDITIONAL',PURPLE),('REDESIGN',GOLD),('REJECT',RED)]
        for i,(t,col) in enumerate(labels):
            c.setFillColor(col); c.roundRect(135+i*180,95,150,34,17,fill=1,stroke=0); c.setFillColor(WHITE if col!=GOLD else INK); c.setFont('Helvetica-Bold',9); c.drawCentredString(210+i*180,107,t)
    else:
        _chain(c,[(f'{i+1:02d}',x) for i,x in enumerate((core or ped)[:4])])


def export_presenter_pdf(bp: Blueprint, out: Path) -> Path:
    out=Path(out); c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
    c.setTitle(bp.lecture_title); c.setAuthor('ISCARB Faculty Studio')
    for u in bp.units:
        _base(c,u); _render(c,bp,u); c.showPage()
    c.save(); return out
