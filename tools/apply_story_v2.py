"""Apply the 2026-09-22 story-led classroom revision.
Preserves assessed assignments and source ledgers; changes only lecture presentation,
Chapter 11's duplicated visible recap screens, guides and offline packages.
"""
import hashlib, io, json, re, zipfile
from pathlib import Path
VERSION='20260922-story-v2'
BASE='684b7c9869d680e61b3b2f7da3d5de7835653502'
RUNTIME='lectures/iscarb/runtime/classroom-v3.js'
CSS='lectures/iscarb/runtime/classroom-v3.css'
DATA=re.compile(r'(<script id="lecture-data" type="application/json">)([\s\S]*?)(</script>)')
def sha(b): return hashlib.sha256(b).hexdigest()
def once(s,a,b):
    assert s.count(a)==1, 'Expected one patch location: '+a[:120]
    return s.replace(a,b,1)
def apply(root):
    cfg=root/'tools/story-v2'
    story=json.loads((cfg/'story.json').read_text())
    maps_path=root/'tools/mindmap-v1/maps.json'
    maps=json.loads(maps_path.read_text())
    pub_path=root/'curriculum/publication.json'
    pub=json.loads(pub_path.read_text())
    assert [c['chapter'] for c in pub['lectures']]==[10,11,12,13,14,15,16,17,20]
    assert pub.get('mindmap_version')=='20260921-mindmap-v1'
    changed=[];preserved={}
    def write(name,data):
        data=data.encode() if isinstance(data,str) else data
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        if name not in changed:changed.append(name)
    for a in pub['assignments']:
        for name in [a['path'],a['stress_path']]:preserved[name]=sha((root/name).read_bytes())

    for ch,lenses in story['chapters'].items():
        assert len(lenses)==5 and len(maps[ch]['branches'])==5
        for b,lens in zip(maps[ch]['branches'],lenses): b['caseLens']=lens
    for b in maps['11']['branches']:
        b['units']=[u for u in b['units'] if u not in {'CHECK','DECIDE'}]
    write('tools/mindmap-v1/maps.json',json.dumps(maps,ensure_ascii=False,indent=2)+'\n')

    runtime=(root/RUNTIME).read_text()
    renderer=(cfg/'render.js').read_text().rstrip()
    pat=re.compile(r'function renderMindMap\(\)\{[\s\S]*?\n\}\nfunction mapObjectives\(\)\{')
    runtime,n=pat.subn(renderer+'\nfunction mapObjectives(){',runtime,count=1);assert n==1
    pat=re.compile(r"else if\(s\.id==='START'\)\{[\s\S]*?\}\nelse if\(s\.id==='END'\)\{[\s\S]*?\}\nelse\{")
    runtime,n=pat.subn("else if(s.id==='START'){renderStory();}\nelse if(s.id==='END'){renderClosing();}\nelse{",runtime,count=1);assert n==1
    old="s.id==='TITLE'?'A decision you can explain':s.id==='MAP'?'Chapter mind map':s.title"
    new="s.id==='TITLE'?'A decision you can explain':s.id==='MAP'?'Chapter mind map':s.id==='START'?'The story we will solve':s.id==='END'?'Chapter complete':s.title"
    runtime=once(runtime,old,new)
    old="else{$('#chapter-main').insertAdjacentHTML('beforeend',`<p class=\"takeaway\">${esc(s.takeaway||s.title)}</p>"
    new="else{$('#chapter-main').insertAdjacentHTML('beforeend',`${storyThread(s)}<p class=\"takeaway\">${esc(s.takeaway||s.title)}</p>"
    runtime=once(runtime,old,new)
    runtime=once(runtime,'<b>APPLY THE IDEA</b>','<b>BACK TO THE STORY</b>')
    write(RUNTIME,runtime)

    write(CSS,(root/CSS).read_bytes()+b'\n'+(cfg/'layout.css').read_bytes())

    lecture_paths={}
    for c in pub['lectures']:
        ch=c['chapter'];name=c['path'];before=(root/name).read_text()
        d=json.loads(DATA.search(before).group(2))
        if ch==11:
            keep=[x for x in d['slides'] if x['id'] not in {'CHECK','DECIDE'}]
            title=next(x for x in keep if x['id']=='TITLE');map_slide=next(x for x in keep if x['id']=='MAP')
            body=[x for x in keep if x['id'] not in {'TITLE','MAP'}]
            start={'id':'START','title':'The story we will solve','phase':'SEE','takeaway':d['case']['headline'],'question':d['case']['question'],'bullets':[]}
            end={'id':'END','title':'Chapter complete','phase':'END','takeaway':'','question':'','bullets':[]}
            d['slides']=[title,map_slide,start]+body+[end]
        else:
            ids=[x['id'] for x in d['slides']];assert {'TITLE','MAP','START','END'}<=set(ids),(ch,ids)
            title=next(x for x in d['slides'] if x['id']=='TITLE');map_slide=next(x for x in d['slides'] if x['id']=='MAP');start=next(x for x in d['slides'] if x['id']=='START');end=next(x for x in d['slides'] if x['id']=='END')
            middle=[x for x in d['slides'] if x['id'] not in {'TITLE','MAP','START','END'}]
            d['slides']=[title,map_slide,start]+middle+[end]
        d['roadmap']=maps[str(ch)]
        assert [x['id'] for x in d['slides'][:3]]==['TITLE','MAP','START']
        assert d['slides'][-1]['id']=='END' and len(d['slides'])==20
        ids={x['id'] for x in d['slides']}
        for b in d['roadmap']['branches']:
            assert b['target'] in ids and set(b['units'])<=ids
        for st in d['stations']:assert st['at'] in ids
        out=DATA.sub(lambda m:m.group(1)+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+m.group(3),before,count=1)
        out=out.replace('data-mindmap="20260921-mindmap-v1"','data-mindmap="'+VERSION+'" data-story="'+VERSION+'"')
        out=out.replace('classroom-v3.css?v=20260921-mindmap-v1','classroom-v3.css?v='+VERSION)
        out=out.replace('classroom-v3.js?v=20260921-mindmap-v1','classroom-v3.js?v='+VERSION)
        write(name,out);c['source_sha256']=sha(out.encode());c['core_keys']=[x['id'] for x in d['slides']];lecture_paths[ch]=name

    hub=(root/'iscarb.html').read_text()
    notice='<section class="notice" id="mindmap-release"><h2>Map it. Live the story. Know when the chapter is complete.</h2><p>Every chapter now follows the same student path: <b>cover → simpler concept map → one fictional story → source-grounded concepts → three short stations → explicit closing slide</b>. A CASE THREAD on each main concept explains why that idea matters to the same story.</p><p class="small">Story-led update '+VERSION+'. Required source review, five objectives, assignments, points and Blackboard submission remain unchanged. Download a new offline ZIP for the matching version.</p></section>'
    hub,n=re.subn(r'<section class="notice" id="mindmap-release">.*?</section>',lambda m:notice,hub,count=1);assert n==1
    write('iscarb.html',hub)

    guide=(root/'student-guide.html').read_text()
    note='<section class="panel" id="story-led-path"><h2>Cover → concept map → story → learning → clear finish</h2><p>Slide 2 shows the five concepts as a connected reasoning path. Slide 3 introduces one fictional case that stays with you. On each main concept, the CASE THREAD explains which part of the story that idea helps answer. The final slide clearly says <b>Chapter complete</b> and lists the required review, five-objective check and assignment.</p><p>Use the story to connect ideas, not to replace the source. The changed constraint is revealed later so that you can revise your reasoning rather than memorize a final answer.</p></section>'
    if 'id="story-led-path"' not in guide: guide=guide.replace('</main>',note+'</main>')
    write('student-guide.html',guide)

    instructor=(root/'instructor-guide.html').read_text()
    note='<section class="panel" id="story-led-path"><h2>Teach through one case thread</h2><p>After the concept map, introduce the fictional case and keep it open. Each subject slide now identifies its CASE THREAD. Use that line to reconnect the source concept to the case without inventing evidence. The final slide is an explicit stop: close the class, name the required source review and five-objective check, then point to the existing assignment.</p><p>The automated duplicate audit rejects repeated adjacent recap content. Chapter 11 removes the redundant CHECK and DECIDE display screens; their unique learning functions are already provided by the three stations and required five-objective practice. No assessed assignment field or STRESS payload is changed.</p></section>'
    if 'id="story-led-path"' not in instructor: instructor=instructor.replace('</main>',note+'</main>')
    write('instructor-guide.html',instructor)

    for ch,name in lecture_paths.items():
        pn=f'lectures/iscarb/packages/Ch{ch}-iSCARB.zip';buf=io.BytesIO();seen=set()
        with zipfile.ZipFile(root/pn) as src,zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
            for info in src.infolist():
                if info.filename==name:
                    b=(root/name).read_bytes().replace(b'href="../../',b'href="https://adeebnoor.github.io/CPIT/');seen.add(name)
                elif info.filename==RUNTIME:
                    b=(root/RUNTIME).read_bytes().replace(b'../../fbr-submission.html',b'https://adeebnoor.github.io/CPIT/fbr-submission.html');seen.add(RUNTIME)
                elif info.filename==CSS:
                    b=(root/CSS).read_bytes();seen.add(CSS)
                elif info.filename=='README.txt':
                    b+=(f'\nStory-led classroom update: {VERSION}. Open START-HERE.html. The sequence is cover, concept map, fictional story, lesson, explicit Chapter complete slide.\n').encode()
                z.writestr(info,b)
        assert seen=={name,RUNTIME,CSS}
        with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:assert z.testzip() is None
        write(pn,buf.getvalue())

    # Recompute all delivery hashes, including lectures and packages.
    for c in pub['lectures']:
        pub['delivery_asset_sha256'][c['path']]=sha((root/c['path']).read_bytes())
        pn=c.get('offline_package')
        if pn:pub['delivery_asset_sha256'][pn]=sha((root/pn).read_bytes())
    pub['delivery_asset_sha256'][RUNTIME]=sha((root/RUNTIME).read_bytes())
    pub['delivery_asset_sha256'][CSS]=sha((root/CSS).read_bytes())
    pub['mindmap_version']=VERSION;pub['story_version']=VERSION
    write('curriculum/publication.json',json.dumps(pub,ensure_ascii=False,indent=2)+'\n')
    assert all(sha((root/n).read_bytes())==h for n,h in preserved.items())

    report={'version':VERSION,'base_commit':BASE,'changed':{n:sha((root/n).read_bytes()) for n in changed},'preserved_assessments':preserved,'chapter11_removed_visible_recap':['CHECK','DECIDE'],'invariants':'Nine chapters remain 20 main slides; TITLE → MAP → START; END is last. Five objectives, readings, cases, stations and assessed assignments are preserved except the two redundant Chapter 11 classroom recap displays.','storage_schema':'iscarb-classroom-v3 unchanged'}
    (root/'story-v2-change-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'version':VERSION,'chapters':len(lecture_paths),'changed_files':len(changed)},indent=2))
if __name__=='__main__': apply(Path(__file__).resolve().parents[1])
