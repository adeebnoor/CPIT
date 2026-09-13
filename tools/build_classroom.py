"""Generate the nine self-contained, accessible classroom editions.

Edit curriculum/chapters.py, classroom.css and classroom.js, then run this file.
The generated HTML keeps reading, diagrams and answer toggles usable offline.
"""
from pathlib import Path
import html
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'curriculum'))
from chapters import CHAPTERS

OUT = ROOT / 'lectures' / 'iscarb'
CSS = (ROOT / 'curriculum/classroom.css').read_text()
JS = (ROOT / 'curriculum/classroom.js').read_text()
VERSION = '20260913-classroom6'
BASE = 'https://adeebnoor.github.io/CPIT/'
ORDER = list(CHAPTERS)
TOPIC_UNITS = [4, 5, 7, 8, 9, 12, 14, 17]
MINUTES = [2, 1, 1, 3, 3, 2, 3, 3, 3, 4, 3, 3, 2, 3, 2, 4, 3, 1, 1, 3]
esc = lambda value: html.escape(str(value), quote=True)

def filename(ch):
    return f'Ch{ch}-{CHAPTERS[ch]["slug"]}.html'

def diagram(items, kind='columns', caption='', center=''):
    nodes = []
    for i, item in enumerate(items):
        title, _, description = item.partition('|')
        nodes.append(f'<div class="node"><span class="node-num" aria-hidden="true">{i+1:02}</span><strong>{esc(title)}</strong><p>{esc(description)}</p></div>')
    middle = f'<div class="hub-center">{esc(center)}</div>' if kind == 'hub' else ''
    note = f'<figcaption>{esc(caption)}</figcaption>' if caption else ''
    return f'<figure class="diagram {esc(kind)}">{middle}<div class="nodes">{"".join(nodes)}</div>{note}</figure>'

def question(q, answer, label='Pause & discuss', options=None, correct=None):
    extra = f' data-correct="{correct}"' if options is not None else ''
    buttons = ''
    if options is not None:
        buttons = '<div class="poll-options" role="group" aria-label="Answer options">' + ''.join(f'<button class="poll-option" data-option="{i}" aria-pressed="false"><span class="poll-letter">{chr(65+i)}.</span><span>{esc(o)}</span></button>' for i, o in enumerate(options)) + '</div><div class="poll-feedback" hidden></div>'
        answer = f'{chr(65+correct)}. {options[correct]} — {answer}'
    return f'<section class="question"{extra}><div class="question-label">{esc(label)}</div><p class="question-prompt">{esc(q)}</p>{buttons}<details class="answer"><summary>Show answer &amp; explanation</summary><div class="answer-body">{esc(answer)}</div></details></section>'

def make_slides(ch, d):
    slides = []
    def add(title, phase, content, label='Explain', source=''):
        i = len(slides) + 1
        tag = 'h1' if i == 1 else 'h2'
        slides.append(dict(title=title, phase=phase, content=content, label=label, source=source, unit=i, tag=tag))
    add(d['title'], 'CRISIS', f'<p class="case-label">Constructed teaching scenario · Chapter {ch} · {MINUTES[0]} minutes</p><p class="lead">{esc(d["scenario"])}</p>'+diagram(d['stakes'])+question(*d['opening'], label='Predict · 30 seconds'), 'Start with the case', 'Teaching scenario; not a report of a real incident.')
    links = ''.join(f'<a href="#unit-{u}"><small>Unit {u:02}</small><span>{esc(t["title"])}</span></a>' for u, t in zip(TOPIC_UNITS, d['topics']))
    add('The chapter map', 'MAP', f'<p class="lead">Follow the same reasoning route used in Chapter 10. Open a topic to revisit its explanation.</p><nav class="topic-map" aria-label="Chapter concept map">{links}</nav>', 'Locate the concepts', 'Sommerville, Software Engineering, 10th edition · Chapter '+str(ch)+'.')
    add('Five things you will be able to do', 'MAP', '<ol class="targets">'+''.join(f'<li>{esc(o)}</li>' for o in d['outcomes'])+'</ol><div class="callout">Explain the mechanism, then use it to defend a decision.</div>', 'Learning outcomes')
    for n in [0,1]:
        t=d['topics'][n]
        add(t['title'], 'MAP', diagram(t['items'],t['kind'],center=d['title'])+f'<div class="callout">{esc(t["takeaway"])}</div>'+question(t['question'],t['answer']), 'Concept & visual')
    p=d['polls'][0]
    add('Check the distinction', 'MAP', '<p class="lead">Choose your answer before opening the explanation. Then explain the mechanism to a partner.</p>'+question(p['question'],p['answer'],'Poll 1 · retrieve',p['options'],p['correct']), 'Retrieval practice')
    for n in [2,3,4]:
        t=d['topics'][n]
        add(t['title'], 'MAP' if n<4 else 'TRADE-OFF', diagram(t['items'],t['kind'],center=t['title'])+f'<div class="callout">{esc(t["takeaway"])}</div>'+question(t['question'],t['answer']), 'Concept & visual')
    w=d['worked']
    add(w['title'], 'TRADE-OFF', diagram(w['given'])+question(w['question'],w['answer'],'Worked example · try, then reveal')+'<p class="source">Model reasoning for this practice case. Different choices can be defensible under different stated constraints.</p>', 'Study an example')
    add('Your turn: change one condition', 'TRADE-OFF', diagram(['Recall|Use the preceding worked example.', 'Apply|Identify the changed assumption.', 'Explain|State what evidence or action changes.'],'flow')+question(*d['practice'],label='Guided practice · 60 seconds'), 'Apply independently')
    t=d['topics'][5]
    add(t['title'], 'TRADE-OFF', diagram(t['items'],t['kind'],center=t['title'])+f'<div class="callout">{esc(t["takeaway"])}</div>'+question(t['question'],t['answer']), 'Deepen the mechanism')
    p=d['polls'][1]
    add('Challenge the attractive answer', 'TRADE-OFF', '<p class="lead">An attractive claim can hide an assumption. Choose, justify, then inspect the answer.</p>'+question(p['question'],p['answer'],'Poll 2 · analyze',p['options'],p['correct']), 'Test an assumption')
    t=d['topics'][6]
    add(t['title'], 'TRADE-OFF', diagram(t['items'],t['kind'],center=t['title'])+f'<div class="callout">{esc(t["takeaway"])}</div>'+question(t['question'],t['answer']), 'Evaluate the cost')
    add('Make the evidence inspectable', 'EVIDENCE', diagram(d['evidence'])+f'<div class="callout">{esc(d["ai"])}</div>'+question('Which evidence item would most directly support or overturn your case decision?', 'Use an artifact linked to the governing requirement and the current case boundary. '+ '; '.join(x.replace('|',': ') for x in d['evidence'])+'. Name what result would make you reopen the verdict. A document title without its relevant result is insufficient.', 'Discuss · evidence and AI'), 'Verify the claim')
    add('Stress the decision together', 'EVIDENCE', diagram(['Engineer · 45 sec|State a verdict and its applicability boundary.', 'Reviewer · 60 sec|Challenge the boundary using the changed condition.', 'Observer · 45 sec|Identify the evidence needed to settle the disagreement.'],'columns')+question(*d['stress'],label='Collaborative activity · rotate roles')+'<p class="source">Retain, revise or replace only when the reasoning warrants it. A changed fact does not mechanically require a changed verdict.</p>', 'Collaborate & defend')
    t=d['topics'][7]
    add(t['title'], 'EVIDENCE', diagram(t['items'],t['kind'],center=t['title'])+f'<div class="callout">{esc(t["takeaway"])}</div>'+question(t['question'],t['answer']), 'Bound the assurance')
    challenge=ORDER.index(ch)+1
    add(f'Assignment {challenge:02}: {d["stage"]}', 'VERDICT', f'<p class="lead">{esc(d["challenge"])}</p>'+diagram(['1 · Warm up|Retrieve one concept before writing.', '2 · Apply|Write FIT, BOUND, ACT and EVIDENCE.', '3 · Adapt|Commit Part A, inspect STRESS, then justify REFIT.'],'flow')+f'<p>{esc(d["support"])}</p><div class="rubric"><div><b>1 point</b>FIT<br><small>Select and justify.</small></div><div><b>1 point</b>BOUND<br><small>State the limit.</small></div><div><b>1 point</b>ACT + EVIDENCE<br><small>Produce and verify.</small></div><div><b>1 point</b>REFIT<br><small>Adapt with reasons.</small></div></div><div class="actions"><a class="primary-link" href="{BASE}fbr-submission.html?chapter={ch}">Open After-Class assignment</a></div><p class="source">4 points per assignment. Browser work is a draft; the LMS is the submission destination.</p>', 'Easy → complex')
    add('Check the coverage, then revisit', 'VERDICT', '<p class="lead">Core chapter sections addressed in this classroom edition:</p><div class="coverage">'+''.join(f'<div>{esc(s)}</div>' for s in d['sections'])+'</div><div class="callout">Return to the map for a missed concept. Use the textbook for full detail, extended examples and exercises.</div><p>After class: explain one diagram from memory. In 2–3 days: repeat the practice question without its answer. Next week: connect one concept to the new chapter.</p>'+f'<p><a href="https://software-engineering-book.com/slides/" target="_blank" rel="noopener">Author’s chapter presentation index</a></p>'+ ('<p><a href="Ch10-Dependable-Systems-Final100.html">Chapter 10 detailed reference edition</a></p>' if ch==10 else ''), 'Coverage & spaced review')
    add('Retrieve it without the notes', 'VERDICT', '<p class="lead">Answer first; open the explanation to check. Revisit the corresponding concept when your explanation is incomplete.</p>'+''.join(question(q,a,f'Readiness {i+1} · course-written practice') for i,(q,a) in enumerate(d['ready']))+f'<div class="actions"><a class="primary-link" href="{BASE}fbr-submission.html?chapter={ch}">Continue to After-Class</a><a class="primary-link" href="{BASE}iscarb.html">Back to lecture hub</a></div><p class="source">Self-check for this course. These are not official ETEC test items or a certification of readiness.</p>', 'Recall & explain')
    assert len(slides)==20
    return slides

def render(ch,d):
    slides=make_slides(ch,d)
    options=''.join(f'<option value="{n}" data-url="{filename(n)}" {"selected" if n==ch else ""}>{n} · {esc(c["title"])}</option>' for n,c in CHAPTERS.items())
    outline=''.join(f'<li><a href="#unit-{s["unit"]}">{s["unit"]:02} · {esc(s["title"])}</a></li>' for s in slides)
    body=''
    for s in slides:
        body+=f'<section class="lesson-slide" id="unit-{s["unit"]}" data-title="{esc(s["title"])}" data-phase="{s["phase"]}" aria-labelledby="heading-{s["unit"]}"><div class="eyebrow"><span>{s["phase"]} · {esc(s["label"])}</span><span class="unit">{s["unit"]:02} / 20 · {MINUTES[s["unit"]-1]} min</span></div><{s["tag"]} id="heading-{s["unit"]}" tabindex="-1">{esc(s["title"])}</{s["tag"]}>{s["content"]}<p class="source">{esc(s["source"] or f"Sommerville · Software Engineering, 10th ed. · Chapter {ch}. Explanatory diagrams and practice: CPIT-455.")}</p></section>'
    return f'''<!doctype html>
<html lang="en" data-iscarb-lesson="6"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#09080e"><meta name="description" content="Chapter {ch}: {esc(d['title'])}. Visual explanations, worked examples and answers you can reveal. CPIT-455, Professor Adeeb Noor."><meta name="iscarb-version" content="{VERSION}"><title>Chapter {ch} · {esc(d['title'])} · ISCARB In-Class</title><style>{CSS}</style><noscript><style>.toolbar,.deck-nav{{display:none}}</style></noscript></head>
<body data-chapter="{ch}" class="reading"><a class="skip" href="#main">Skip to lesson</a>
<header class="coursebar"><a class="brand" href="{BASE}iscarb.html">ISCARB / CPIT-455</a><div class="chapter-picker"><label for="chapter">Chapter</label><select id="chapter">{options}</select></div></header>
<nav class="toolbar" aria-label="Learning controls"><button id="mode" aria-pressed="false">Reading view</button><button id="font" aria-label="Change lesson text size">Text 100%</button><button id="theme">Light theme</button><button id="hide-answers">Hide all answers</button><button id="fullscreen">Full screen</button><button id="print">Print / PDF</button><button id="help-button" aria-expanded="false" aria-controls="help-panel">Help</button><button id="resume" hidden>Resume</button><a class="after" href="{BASE}fbr-submission.html?chapter={ch}">After-Class ↗</a></nav>
<div id="help-panel" class="help-panel" hidden><b>Learn at your pace.</b> In slide view use ← / →, Page Up / Page Down, Home / End. Use Tab to reach controls and Enter or Space to open an answer. Reading view shows every unit and supports browser zoom. Answers close when you change slides. Print respects which answers you have opened; use Hide all answers for a practice handout. Optional theme, text size and resume position are stored on this browser only. These are not grades.</div>
<div class="route" aria-label="The Chapter 10 learning route">{''.join(f'<span data-phase="{p}">{p}</span>' for p in ['CRISIS','MAP','TRADE-OFF','EVIDENCE','VERDICT'])}</div>
<div id="outline-panel" class="help-panel" hidden><nav aria-label="All lesson units"><ol class="outline">{outline}</ol></nav></div>
<noscript><p class="noscript">Reading edition: all units and answer toggles work without JavaScript. Use the lecture hub to change chapters.</p></noscript>
<main id="main">{body}</main><footer class="deck-nav" aria-label="Slide navigation"><button id="prev">← Previous</button><div class="slide-count"><button id="outline-button" aria-expanded="false" aria-controls="outline-panel">Units <span id="count">1 / 20</span></button><div class="progress-track" aria-hidden="true"><div id="progressFill" class="progress-fill"></div></div></div><button id="next">Next →</button></footer><div class="sr" id="announcer" role="status" aria-live="polite"></div><script>{JS}</script></body></html>'''

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for ch,d in CHAPTERS.items():
        path=OUT/filename(ch)
        path.write_text(render(ch,d),encoding='utf-8')
        print(f'Ch{ch}: 20 units, {len(d["topics"])} explained concept diagrams, 2 polls, 4 readiness answers → {path.name}')
    mapping={str(ch):filename(ch) for ch in CHAPTERS}
    # Retain every existing presenter URL and chapter query; no iframe scaling.
    presenter='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ISCARB · In-Class</title></head><body><p>Open your chapter:</p><ul>'''+''.join(f'<li><a href="{filename(ch)}">Chapter {ch} · {esc(d["title"])}</a></li>' for ch,d in CHAPTERS.items())+'''</ul><script>(()=>{const map='''+json.dumps(mapping)+''';const q=new URLSearchParams(location.search);const chapter=q.get('chapter')||'10';if(!Object.prototype.hasOwnProperty.call(map,chapter))return;const target=new URL(map[chapter],location.href);if(q.get('view')==='reading')target.searchParams.set('view','reading');target.hash=location.hash;location.replace(target.href)})();</script></body></html>'''
    (OUT/'InClass-Presenter.html').write_text(presenter)

if __name__=='__main__':
    main()
