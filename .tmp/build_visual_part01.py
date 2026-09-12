     'trade':['Local optimization, weaker whole-system coherence','More coordination, slower change','Better integration, less owner autonomy'],
     'evidence':['Shared operating picture','Interface and escalation agreements','Cross-system drill evidence','Named inter-organizational authority'],
     'ai':'AI may summarise signals across systems or forecast strain, but it must not replace inter-agency authority or public-risk sign-off.',
     'saudi':'For large-scale Saudi services and events, the engineering challenge is often no longer one system. It is the governed behavior of many semi-autonomous systems together.',
     'after':'After-Class: capstone judgment across independently owned systems.'}
}

ETEC=[
 ('KLO2 · Problem Analysis','Use evidence to reach a supportable conclusion.'),
 ('KLO3 · Design / Development','Choose a solution while respecting safety, security, or reliability constraints.'),
 ('KLO5 · Team Work','Coordinate engineering work across roles and responsibilities.'),
 ('KLO7 · Communication','Present a decision and its evidence clearly.'),
 ('GKU7 / SKU7.2 · Quality Assurance','Show how the claim is checked, tested, or monitored.')
]


def card_grid(items, cols=3):
    html=f'<div class="grid g{cols}">' 
    for lab,txt in items:
        html += f'<div class="card"><div class="lab">{escape(lab)}</div><div class="txt">{escape(txt)}</div></div>'
    html += '</div>'
    return html

def build_svg_spine(title, items, accent='#4FC6CB'):
    n=len(items)
    boxes=[]
    x=40; w=230 if n<=4 else 170; gap=18; y=90; h=78
    total=n*w+(n-1)*gap
    start=(1250-total)/2
    line=f'<line x1="625" y1="52" x2="625" y2="92" stroke="#DDB27E" stroke-width="4"/>'
    boxes.append(f'<rect x="535" y="14" rx="12" ry="12" width="180" height="42" fill="#15121C" stroke="#DDB27E" stroke-width="2"/><text x="625" y="40" fill="#F5F0EA" font-size="22" font-family="Inter" text-anchor="middle">{escape(title)}</text>')
    for i,it in enumerate(items):
        bx=start+i*(w+gap)
        boxes.append(f'<rect x="{bx}" y="{y}" rx="16" ry="16" width="{w}" height="{h}" fill="#15121C" stroke="{accent}" stroke-width="2"/>')
        boxes.append(f'<text x="{bx+w/2}" y="{y+32}" fill="#F5F0EA" font-size="18" font-weight="700" font-family="Inter" text-anchor="middle">{escape(it)}</text>')
        if i<n-1:
            boxes.append(f'<line x1="{bx+w}" y1="{y+h/2}" x2="{bx+w+gap}" y2="{y+h/2}" stroke="#DDB27E" stroke-width="2.5" stroke-dasharray="6 6"/>')
    return f'<div class="illus"><svg viewBox="0 0 1250 200" xmlns="http://www.w3.org/2000/svg">{line}{"".join(boxes)}</svg><div class="cap">{escape(title)} · source spine visual</div></div>'

def build_svg_flow():
    steps=['Crisis','Map','Trade-off','Evidence','Verdict']
    html=['<div class="illus"><svg viewBox="0 0 1250 220" xmlns="http://www.w3.org/2000/svg">']
    start=90; w=180; h=86; gap=52; y=62
    for i,s in enumerate(steps):
        x=start+i*(w+gap)
        stroke=['#F0189A','#4FC6CB','#DDB27E','#8E7DEA','#4FBF8B'][i]
        html.append(f'<rect x="{x}" y="{y}" rx="18" ry="18" width="{w}" height="{h}" fill="#15121C" stroke="{stroke}" stroke-width="3"/>')
        html.append(f'<text x="{x+w/2}" y="{y+32}" fill="{stroke}" font-size="18" font-weight="700" font-family="Inter" text-anchor="middle">{i+1}</text>')
        html.append(f'<text x="{x+w/2}" y="{y+58}" fill="#F5F0EA" font-size="22" font-weight="700" font-family="Inter" text-anchor="middle">{s}</text>')
        if i<len(steps)-1:
