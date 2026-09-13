"""Idempotent authoring update for hub and existing assessed FBR pages.

Preserves identity, persistence keys, rubric and the Part A commitment protocol.
Warm-ups use a separate practice case; assessed STRESS is never loaded here.
"""
from pathlib import Path
import re, sys, html
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'curriculum'))
from chapters import CHAPTERS
e=lambda s:html.escape(str(s),quote=True)

ASSIGNMENT_CSS='''<style id="learning-scaffold-style">
body{font-size:18px;line-height:1.65}.w{max-width:1040px}h1{line-height:1.2;overflow-wrap:anywhere}.lab,.ey,.chip,.st,.hint,.foot{font-size:14px}.rubric div{font-size:16px}.card,.rule{overflow-wrap:anywhere}button,.linkbtn,input,summary{min-height:44px}input,textarea{font-size:18px}button:focus-visible,a:focus-visible,summary:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid #79d9da;outline-offset:3px}.scaffold{border:1px solid #66516f;border-radius:14px;margin:20px 0;padding:20px;background:#16131e;color:#f6f1eb}.scaffold h2{font-size:27px;line-height:1.25;margin:8px 0 12px}.scaffold p{margin:8px 0}.scaffold ol{padding-left:25px}.scaffold li{padding:5px 0}.scaffold small{font-size:14px;color:#bdb3c4}.scaffold summary{color:#79d9da;cursor:pointer;font-weight:700;padding:9px 0}.scaffold details{border-top:1px solid #473c53;margin-top:12px}.scaffold .answer-text{padding:10px 0}.scaffold a{color:#79d9da}.support-stems{border-left:3px solid #edbf82;padding:0 0 0 14px}.form-label{display:block;font-size:15px;font-weight:700;margin-top:8px}@media(max-width:600px){.scaffold{padding:15px}.w{padding:18px 14px 40px}h1{font-size:30px}.buttons{gap:10px}.buttons button{flex:1 1 150px}.scaffold h2{font-size:24px}}@media print{.scaffold{display:none!important}}
</style>'''

def scaffold(ch,d,i):
    q,a=d['practice']
    # Early assignments provide explicit sentence frames; later ones offer only optional prompts.
    stems=''.join(f'<p>{e(s)}</p>' for s in d['stems'])
    if i<=3:
        support='<div class="support-stems">'+stems+'</div>'
    else:
        support='<details><summary>Optional planning prompts</summary>'+stems+'</details>'
    return f'''<section class="scaffold" id="assignment-learning-path"><small>ASSIGNMENT {i} / 9 · {e(d['stage']).upper()}</small><h2>Start simple. Build a defensible decision.</h2><p>{e(d['support'])}</p><ol><li><b>Recognize:</b> revisit the worked example and answer the short transfer question below.</li><li><b>Apply:</b> complete FIT → BOUND → ACT + EVIDENCE for the assessed scenario.</li><li><b>Adapt:</b> commit Part A, read STRESS, then justify RETAIN, REVISE or REPLACE.</li></ol><p><a href="Ch{ch}-{e(d['slug'])}.html#unit-10">Revisit the worked example</a></p><p><b>Warm-up · not graded:</b> {e(q)}</p><details class="warmup-answer"><summary>Show / hide warm-up answer</summary><div class="answer-text">{e(a)}</div></details>{support}<p><small>Warm-up practice and planning prompts are not submitted or graded. The existing four-point rubric applies to FIT, BOUND, ACT + EVIDENCE and REFIT.</small></p></section>'''

for i,(ch,d) in enumerate(CHAPTERS.items(),1):
    p=ROOT/f'lectures/iscarb/Ch{ch}-FBR-Student-Assignment.html'
    s=p.read_text()
    s=re.sub(r'<style id="learning-scaffold-style">.*?</style>','',s,flags=re.S)
    s=s.replace('</head>',ASSIGNMENT_CSS+'</head>',1)
    s=re.sub(r'<!-- learning-scaffold-start -->.*?<!-- learning-scaffold-end -->','',s,flags=re.S)
    block='<!-- learning-scaffold-start -->'+scaffold(ch,d,i)+'<!-- learning-scaffold-end -->'
    s=s.replace('<div class="integrity">',block+'<div class="integrity">',1)
    # Existing ids are stable and are reused by the application. Add real labels.
    labels={'student':'Name (optional)','sid':'Student ID','section':'Section / group','date':'Date'}
    for id,label in labels.items():
        if f'for="{id}"' not in s:
            s=s.replace(f'<input id="{id}"',f'<label class="form-label" for="{id}">{label}</label><input id="{id}"',1)
    for id,label in {'fit':'FIT reasoning','bound':'Applicability boundary','act':'Professional action','evidence':'Evidence and owner','refitwhy':'REFIT justification','revised':'Final professional artifact'}.items():
        s=s.replace(f'<textarea id="{id}"',f'<textarea aria-label="{label}" id="{id}"') if f'aria-label="{label}"' not in s else s
    p.write_text(s)

p=ROOT/'iscarb.html';s=p.read_text()
s=s.replace('Teach the discipline.<em>Practise the judgment.</em>','Understand the chapter.<em>Defend the decision.</em>')
s=s.replace('Teach the discipline.','Understand the chapter.').replace('Practise the judgment.','Defend the decision.')
s=s.replace('SOURCE FIGURES FIRST · ENGINEERING DECISIONS · HUMAN SIGN-OFF','VISUAL CONCEPTS · GUIDED PRACTICE · INDEPENDENT JUDGMENT')
s=re.sub(r'<p>CPIT-455 uses split delivery:.*?</p>','<p>Start with Chapter 10. Every chapter follows the same route: understand the concepts, inspect a worked example, practise, then defend a decision. Open model answers when you are ready. Choose Reading view or enlarge the text whenever you need.</p>',s,count=1,flags=re.S)
s=s.replace('Bloom · Create</span>','Bloom · Understand → Apply → Create</span>',1)
s=re.sub(r'<style id="learning-hub-style">.*?</style>','',s,flags=re.S)
s=s.replace('</head>','''<style id="learning-hub-style">
html{scroll-padding-top:20px}.lec[hidden]{display:none!important}.wrap{max-width:1280px}.hero.iscarb-themed-hero{min-height:0!important;padding:36px!important}.hero h1{font-size:clamp(34px,5vw,62px)!important;line-height:1.16!important}.hero p{font-size:19px!important;line-height:1.65!important;max-width:68ch!important}.sectionHead{gap:20px;flex-wrap:wrap}.sectionHead p{font-size:17px;line-height:1.65}.lec h3{font-size:25px;line-height:1.25;overflow-wrap:anywhere}.lec p{font-size:17px;line-height:1.6}.lec .label,.badge,.clo,.bloom,.workload span,.checkLabel{font-size:14px}.links a{min-height:46px;font-size:15px;display:flex;align-items:center;justify-content:center}.checkLabel{min-height:44px}.checkLabel input{min-width:20px;min-height:20px}.stage-note{border-top:1px solid var(--line);padding-top:12px;margin-top:12px}.stage-note b{display:block;color:var(--gold);font-size:15px;margin-bottom:6px}.stage-note span{font-size:16px;color:var(--muted);line-height:1.5}.learning-path{margin:24px 0;padding:24px;border:1px solid var(--line);border-radius:18px;background:var(--panel)}.learning-path h2{font-size:28px;line-height:1.2;margin:0 0 12px}.learning-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.learning-steps div{padding:14px;border-left:3px solid var(--gold)}.learning-steps b{display:block;color:var(--gold);font-size:18px}.learning-steps p{font-size:17px;line-height:1.6;margin:8px 0}.hero .start-lesson{margin:20px 0 0}.nav{flex-wrap:wrap}.nav a,.nav button,.term{min-height:44px}.search{font-size:17px}.progressBox{min-width:0}.toolbar{flex-wrap:wrap}.toolbar label{min-width:0;flex:1}.grid{align-items:stretch}a:focus-visible,button:focus-visible,input:focus-visible,.lec:focus-visible{outline:3px solid var(--cyan);outline-offset:4px}.note{font-size:15px;line-height:1.6}@media(max-width:700px){.hero.iscarb-themed-hero{padding:24px!important}.learning-steps{grid-template-columns:1fr}.learning-path{padding:18px}.hero h1{font-size:36px!important}.toolbar{display:grid;grid-template-columns:1fr}.sectionHead{display:block}.nav a,.nav button{font-size:14px}.grid{grid-template-columns:1fr!important}.brand{min-width:0}.brand strong{white-space:normal}.learning-path h2{font-size:25px}.top{flex-wrap:wrap}.roadmap{grid-template-columns:1fr 1fr}.resourceGrid{grid-template-columns:1fr}.path{flex-wrap:wrap}.wrap{padding:16px}.q span{overflow-wrap:anywhere}}
</style></head>''',1)
if 'id="assignment-progression"' not in s:
    path='''<section class="learning-path" id="assignment-progression"><h2>One learning route. Increasing independence.</h2><div class="learning-steps"><div><b>01 · Guided foundations</b><p>Ch. 10–12: identify, calculate and trace. Worked examples and sentence stems help you start.</p></div><div><b>02 · Compare and justify</b><p>Ch. 13–15: evaluate threats, disruptions and alternatives. Select the evidence and justify trade-offs.</p></div><div><b>03 · Design and defend</b><p>Ch. 16–17, 20: compose, distribute and integrate. Defend your own architecture across changing conditions.</p></div></div></section>'''
    s=s.replace('<section id="lectures"',path+'<section id="lectures"',1)
if 'class="start-lesson"' not in s:
    s=s.replace('<div class="path">','<div class="start-lesson"><a class="cta" href="lectures/iscarb/InClass-Presenter.html?chapter=10">Start Chapter 10 →</a> <a class="cta alt" href="#lectures">Browse all chapters</a></div><div class="path">',1)
for i,(ch,d) in enumerate(CHAPTERS.items(),1):
    pattern=rf'(<article class="lec"[^>]*id="ch{ch}".*?)(</article>)'
    def patch(m):
        card=re.sub(r'<div class="stage-note">.*?</div>','',m[1],flags=re.S)
        card=card.replace('<div class="checks">',f'<div class="stage-note"><b>Assignment {i:02} · {e(d["stage"])}</b><span>{e(d["challenge"])}</span></div><div class="checks">',1)
        return card+m[2]
    s=re.sub(pattern,patch,s,count=1,flags=re.S)
# Retain progress when storage is available and keep the hub usable when it is not.
storage="const localPrefs={get(k){try{return window.localStorage.getItem(k)}catch{return null}},set(k,v){try{window.localStorage.setItem(k,v)}catch{}}};\n"
if 'const localPrefs=' not in s:
    s=s.replace("const root=document.documentElement",storage+"const root=document.documentElement",1)
    s=s.replace("localStorage.setItem(","localPrefs.set(").replace("localStorage.getItem(","localPrefs.get(")
    s=s.replace('window.localPrefs.set(', 'window.localStorage.setItem(').replace('window.localPrefs.get(', 'window.localStorage.getItem(')
s=s.replace("if(['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName))return;","if(['INPUT','TEXTAREA','SELECT','BUTTON','A','SUMMARY'].includes(document.activeElement.tagName))return;")
p.write_text(s)
print('Updated nine scaffolded assignments and the learning hub; storage keys and rubric preserved.')
