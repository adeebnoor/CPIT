"""Refresh the nine downloadable course packages from the reviewed source files.

Runs before validation/staging, so offline downloads and online runtime are identical.
Never regenerates authored lecture or assessment content.
"""
from pathlib import Path
import hashlib, io, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    # One source for the teaching models: lectures use a copy of the assignment lab engine.
    (ROOT/'lectures/iscarb/runtime/labs.js').write_bytes((ROOT/'curriculum/learning-path/labs.js').read_bytes())
    p=ROOT/'curriculum/publication.json';spec=json.loads(p.read_text())
    shared=['lectures/iscarb/runtime/classroom-v3.css','lectures/iscarb/runtime/classroom-v3.js','lectures/iscarb/runtime/readable.css','lectures/iscarb/runtime/assignment-readable.css']
    shared += ['lectures/iscarb/runtime/national-content.js','lectures/iscarb/runtime/source-figures.js','lectures/iscarb/runtime/national-alignment.css','lectures/iscarb/runtime/story-v3.js','lectures/iscarb/runtime/labs.js','lectures/iscarb/runtime/stage-v4.css','nelc-alignment.html','national-site.css','iscarb-hub.css','iscarb-hub.js','course-design.css','student-ux.js','assets/fcit-kau-logo.png','lectures/iscarb/sources/NELC-AI-Learning-Design-v1-2026.pdf']
    shared += ['course-shell.css','course-shell.js','iscarb.html','student-guide.html','course-resources.html','instructor-guide.html','methodology.html','index.html','student-ux.css','chapter-search.js']
    shared += ['fbr-submission.html']
    shared += [item['study_path'] for item in spec['lectures']]
    shared += [item['path'] for item in spec['assignments']+spec['previous_assignments']]
    shared += [item['stress_path'] for item in spec['assignments']+spec['previous_assignments'] if item.get('stress_delivery')!='lms']
    shared += [str(p.relative_to(ROOT)) for folder in ('lectures/iscarb/assets/national','lectures/iscarb/assets/source-vectors','lectures/iscarb/assets/story') for p in (ROOT/folder).glob('*') if p.is_file()]
    # STRESS delivered through the LMS must not survive inside older package contents.
    withdrawn={item['stress_path'] for item in spec['assignments']+spec['previous_assignments'] if item.get('stress_delivery')=='lms'}
    for lecture in spec['lectures']:
        name=lecture['offline_package'];path=ROOT/name
        replace=shared+[lecture['path'],next(a['path'] for a in spec['assignments'] if a['chapter']==lecture['chapter'])]
        additions={n:(ROOT/n).read_bytes() for n in replace}
        buf=io.BytesIO()
        with zipfile.ZipFile(path) as old,zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as out:
            seen=set()
            for item in old.infolist():
                if item.filename in seen or item.filename in withdrawn:continue
                seen.add(item.filename)
                out.writestr(item,additions.get(item.filename,old.read(item.filename)))
            for n,b in additions.items():
                if n not in seen:out.writestr(n,b)
        with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as check:
            assert check.testzip() is None
            for n,b in additions.items():assert check.read(n)==b
        path.write_bytes(buf.getvalue())
        spec['delivery_asset_sha256'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    p.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
    print('PASS: all 9 offline packages contain current lecture, assignment and readable runtime.')
if __name__=='__main__':main()
