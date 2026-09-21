"""Apply an authored nine-chapter learning organizer without changing assessed work.
The existing MAP moves to position two; subject slides, rules, objectives, readings,
case data and all assessment bytes are preserved. No automatic content generation.
"""
import argparse, copy, hashlib, io, json, re, zipfile
from pathlib import Path
VERSION='20260921-mindmap-v1'
BASE='57c792e6508e345177acc0da964f3d89aee3d17b'
RUNTIME='lectures/iscarb/runtime/classroom-v3.js'
CSS='lectures/iscarb/runtime/classroom-v3.css'
DATA=re.compile(r'(<script id="lecture-data" type="application/json">)([\s\S]*?)(</script>)')
def sha(b): return hashlib.sha256(b).hexdigest()
def once(s,a,b):
    assert s.count(a)==1, 'Expected one reviewed patch location: '+a[:120]
    return s.replace(a,b,1)
def apply(root):
    cfg=root/'tools/mindmap-v1'; maps=json.loads((cfg/'maps.json').read_text())
    pub=json.loads((root/'curriculum/publication.json').read_text())
    assert 'mindmap_version' not in pub, 'Already applied: review a fresh baseline rather than stacking edits.'
    assert [c['chapter'] for c in pub['lectures']]==[10,11,12,13,14,15,16,17,20]
    changed=[]; preserved={}
    def write(name,data):
        data=data.encode() if isinstance(data,str) else data
        (root/name).write_bytes(data); changed.append(name)
    for c in pub['assignments']:
        for name in [c['path'],c['stress_path']]:preserved[name]=sha((root/name).read_bytes())
    old=(root/RUNTIME).read_text(); assert sha(old.encode())==pub['delivery_asset_sha256'][RUNTIME]
    s=old
    lines=s.splitlines()
    i=next(i for i,l in enumerate(lines) if l.startswith("else if(s.id==='MAP')"))
    lines[i]="else if(s.id==='MAP'){renderMindMap();}"
    s='\n'.join(lines)+'\n'
    s=once(s,"s.id==='TITLE'?'A decision you can explain':s.title", "s.id==='TITLE'?'A decision you can explain':s.id==='MAP'?'Chapter mind map':s.title")
    s=once(s,"jumpButton('START','Start the case')", "jumpButton('MAP','See the chapter map →')")
    s=once(s,"${D.slides[index].title}`;save();}", "${D.slides[index].title}`;updateMapLocation();save();}")
    s=once(s,"function tools(){modal(","function legacyTools(){modal(")
    s=once(s,'TOOLS:tools,CARD:card', 'TOOLS:studyTools,OBJECTIVES:mapObjectives,CARD:card')
    s=once(s,"function open(k){",(cfg/'render.js').read_text()+"\nfunction open(k){")
    s=once(s,"<table><tr><th>Enter / Backspace", "<p>Start at the cover, then the Chapter mind map on slide 2. Use Chapter map to return, Slides to jump, and Study &amp; tools for required review, your card, methodology and display settings.</p><table><tr><th>Enter / Backspace")
    write(RUNTIME,s)
    oldcss=(root/CSS).read_bytes();assert sha(oldcss)==pub['delivery_asset_sha256'][CSS]
    write(CSS,oldcss+b'\n'+(cfg/'layout.css').read_bytes())
    lecture_paths={}
    for c in pub['lectures']:
        name=c['path'];before=(root/name).read_text();assert sha(before.encode())==c['source_sha256']
        d=json.loads(DATA.search(before).group(2));original=copy.deepcopy(d)
        r=maps[str(c['chapter'])];ids={x['id'] for x in d['slides']}
        assert len(r['branches'])==5 and all(b['target'] in ids and set(b['units'])<=ids for b in r['branches'])
        d['slides']=[d['slides'][0],next(x for x in d['slides'] if x['id']=='MAP')]+[x for x in d['slides'][1:] if x['id']!='MAP']
        d['roadmap']=r
        assert d['slides'][0]['id']=='TITLE' and d['slides'][1]['id']=='MAP' and len(d['slides'])==20
        check=copy.deepcopy(d);check.pop('roadmap');check['slides']=sorted(check['slides'],key=lambda x:x['id'])
        source=copy.deepcopy(original);source['slides']=sorted(source['slides'],key=lambda x:x['id']);assert check==source
        out=DATA.sub(lambda m:m.group(1)+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+m.group(3),before,count=1)
        out=once(out,'data-navigation="20260921-navigation-v1"','data-navigation="20260921-navigation-v1" data-mindmap="'+VERSION+'"')
        out=out.replace('classroom-v3.css?v=20260921-navigation-v1','classroom-v3.css?v='+VERSION).replace('classroom-v3.js?v=20260921-navigation-v1','classroom-v3.js?v='+VERSION)
        top='<div class="topnav"><button id="mapBtn" class="map-shortcut" data-jump="MAP">Chapter map</button><button data-open="UNITS">Slides</button><button data-open="TOOLS">Study &amp; tools</button></div>'
        out,n=re.subn(r'<div class="topnav">.*?</div>',lambda m:top,out,count=1);assert n==1
        foot='<footer class="footerbar"><div class="footer-left"><span id="topic-location"></span><button id="viewBtn" aria-pressed="false">Reading view</button></div><div class="footer-right"><span id="progress" class="progress"></span><button id="helpBtn" aria-label="Help">?</button><button id="prevBtn" class="arrow" aria-label="Previous slide">‹</button><button id="nextBtn" class="arrow" aria-label="Next slide">›</button></div></footer>'
        out,n=re.subn(r'<footer class="footerbar">.*?</footer>',lambda m:foot,out,count=1);assert n==1
        write(name,out);c['source_sha256']=sha(out.encode());c['core_keys']=[x['id'] for x in d['slides']];lecture_paths[c['chapter']]=name
    hub=(root/'iscarb.html').read_text()
    for ch,name in lecture_paths.items():
        hub=hub.replace(name+'#START',name+'#TITLE')
        hub=hub.replace('href="'+name+'#C01">Source map','href="'+name+'#MAP">Chapter mind map')
    notice='<section class="notice" id="mindmap-release"><h2>See how the ideas connect before you start.</h2><p>Each chapter now opens with its cover, then a chapter-specific mind map and three-step student roadmap. Follow the main slides; use <b>Chapter map</b> to orient yourself and <b>Study &amp; tools</b> for required review and supporting tools. The 20 rules, five objectives and assessed assignments are preserved.</p><p class="small">Mind-map update '+VERSION+'. Download a new offline ZIP to get the same map and navigation.</p></section>'
    hub,n=re.subn(r'<section class="notice" id="classroom-v3-release">.*?</section>',lambda m:notice,hub,count=1);assert n==1
    write('iscarb.html',hub)
    guide=(root/'student-guide.html').read_text()
    guide=guide.replace('<b>Start with the case.</b> Identify the decision and what remains unknown.','<b>Start with the chapter map.</b> Connect the concepts and check your role, then move to the classroom case.')
    guide=guide.replace('Select Classroom · 20 or press O to open the slide index.','Select Slides or press O to open the slide index. Use Chapter map to return to the overview.')
    start=guide.index('<section class="section"><h2>Controls and saved work</h2>')
    end=guide.index('<p><b>Offline use:</b>',start)
    guide=guide[:start]+'''<section class="section"><h2>Controls and saved work</h2><p><b>Chapter map</b> returns to the mind map on slide 2. <b>Slides</b> opens the index. <b>Study &amp; tools</b> groups the Decision card, five objectives, required self-study and practice, assignment link, 20 rules, source coverage, AI gate and display settings. Your current topic appears beside the navigation controls.</p><p>Use <b>Reading view</b> or browser zoom when you need larger text. Small screens reflow the map as a readable branching outline rather than shrinking the desktop diagram. The arrow controls and question-mark Help remain visible.</p>'''+guide[end:]
    guide=guide.replace('Select <b>Classroom · 20</b>','Select <b>Slides</b>')
    note='''<section class="panel" id="chapter-mindmap"><h2>Cover → mind map → learning</h2><p>The second slide connects the chapter concepts around one question. Its labeled branches open the related lesson. Below, the student roadmap separates your instructor’s role from your work: learn and build one card in class; complete the exact required source slides and five practice questions; then apply the method to the separate assignment and submit through Blackboard.</p><p><b>Five objectives</b> opens the unchanged chapter outcomes and original section outline. The map is a learning organizer, not a replacement for the required source. The controls are reduced, not the content. The 20 iSCARB rules remain in Study &amp; tools and in relevant classroom activities.</p></section>'''
    write('student-guide.html',once(guide,'</main>',note+'</main>'))
    instructor=(root/'instructor-guide.html').read_text()
    note='''<section class="panel" id="chapter-mindmap"><h2>Use the map as a shared learning agreement</h2><p>Open the cover and move to slide 2. Explain the relationships between the five concept branches, then distinguish your role and the learner’s work in the three roadmap stages. Show the unchanged five objectives when setting the scope. After each station, use Chapter map to reconnect the current concept to the whole chapter; return through the branch or Slides.</p><p>Do not teach the toolkit as another syllabus. The three stations build the same practice card. Exact source selections and the separate assessed artifact remain required; deadlines, raw points, draft identities and the commitment-before-STRESS sequence are unchanged.</p></section>'''
    write('instructor-guide.html',once(instructor,'</main>',note+'</main>'))
    template=(root/'iSCARB-Teaching-Template.md').read_text()
    write('iSCARB-Teaching-Template.md',template+'\n\n## Opening organizer: page 2\n- Keep the cover first, then move the existing MAP to second. Do not remove a subject slide.\n- Author five concise concept branches with relationship verbs, source-derived terms and real lesson targets.\n- Under the map, state instructor/student roles for in-class practice, exact required review and the existing assignment artifact.\n- Retain the five full objectives and source outline through the map.\n- Keep Chapter map, Slides and Study & tools as the main controls; disclose additional tools when relevant.\n- Test the cover-to-map route, branch targets, mobile reflow, keyboard input and newly extracted offline ZIPs.\n')
    for ch,name in lecture_paths.items():
        pn=f'lectures/iscarb/packages/Ch{ch}-iSCARB.zip';dest=io.BytesIO();seen=set()
        with zipfile.ZipFile(root/pn) as src,zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
            for info in src.infolist():
                b=src.read(info.filename)
                if info.filename==name:b=(root/name).read_bytes().replace(b'href="../../',b'href="https://adeebnoor.github.io/CPIT/');seen.add(name)
                elif info.filename==RUNTIME:b=(root/RUNTIME).read_bytes().replace(b'../../fbr-submission.html',b'https://adeebnoor.github.io/CPIT/fbr-submission.html');seen.add(RUNTIME)
                elif info.filename==CSS:b=(root/CSS).read_bytes();seen.add(CSS)
                elif info.filename=='README.txt':b+=b'\nMind-map update: '+VERSION.encode()+b'. Open START-HERE.html: cover, then the chapter mind map and student roadmap. Chapter map / Slides / Study & tools replace the crowded toolbar. Source reading and assessments are unchanged.\n'
                out.writestr(info,b)
        assert seen=={name,RUNTIME,CSS}
        with zipfile.ZipFile(io.BytesIO(dest.getvalue())) as z:assert z.testzip() is None
        write(pn,dest.getvalue())
    for name in changed:
        if name in pub['delivery_asset_sha256']:pub['delivery_asset_sha256'][name]=sha((root/name).read_bytes())
    pub['mindmap_version']=VERSION
    write('curriculum/publication.json',json.dumps(pub,ensure_ascii=False,indent=2)+'\n')
    assert all(sha((root/n).read_bytes())==digest for n,digest in preserved.items())
    report={'version':VERSION,'base_commit':BASE,'changed':{n:sha((root/n).read_bytes()) for n in changed},'preserved_assessments':preserved,'content_invariants':'Existing slide records, cases, readings, five objectives and canonical 20 rules unchanged; MAP order only.','navigation_schema':'20260921-navigation-v1 preserved','storage_schema':'iscarb-classroom-v3 unchanged'}
    (root/'mindmap-change-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'version':VERSION,'chapters':len(lecture_paths),'changed_files':len(changed)},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);apply(p.parse_args().root.resolve())
