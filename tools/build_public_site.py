"""Stage the explicit reviewed ISCARB release without modifying approved lectures."""
from pathlib import Path
import shutil, os, sys
from sanitize_static_site import main as sanitize
from audit_classroom import audit, publication
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'_site'
VERSION=publication()['release']
PUBLIC=['index.html','404.html','cimt.html','imam.html','iscarb.html','iscarb-students.html','fbr-submission.html','download.html','download-stats.html','student-guide.html','course-resources.html','methodology.html','style.css','iscarb-theme.css','iscarb-theme.js','iscarb-hub.css','iscarb-hub.js']
def main():
    spec=publication(); errors=audit(ROOT)
    if errors: raise SystemExit('\n'.join(errors))
    if DEST.exists(): shutil.rmtree(DEST)
    DEST.mkdir()
    for name in PUBLIC: shutil.copy2(ROOT/name,DEST/name)
    for name in ['slides','lectures/cimt','lectures/himma','wealth-os']:
        if (ROOT/name).exists(): shutil.copytree(ROOT/name,DEST/name)
    for name in spec['iscarb_public_files']:
        (DEST/name).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/name,DEST/name)
    image='iscarb-studio/app/static/hero_user_original.png'; (DEST/image).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/image,DEST/image)
    immutable_lectures={item['path'] for item in spec['lectures']}
    for p in DEST.rglob('*.html'):
        if p==DEST/'index.html' or 'wealth-os' in p.parts: continue
        rel=p.relative_to(DEST).as_posix(); s=p.read_text()
        if rel in immutable_lectures or 'data-iscarb-standalone="1"' in s or p.name in ('InClass-Presenter.html','Faculty-Presenter.html'): continue
        prefix=os.path.relpath(DEST,p.parent).replace('\\','/'); prefix='' if prefix=='.' else prefix+'/'
        if 'iscarb-theme.css' not in s: s=s.replace('</head>',f'<link rel="stylesheet" href="{prefix}iscarb-theme.css?v={VERSION}"></head>',1)
        if 'iscarb-theme.js' not in s: s=s.replace('</body>',f'<script src="{prefix}iscarb-theme.js?v={VERSION}" defer></script></body>',1)
        p.write_text(s)
    old=sys.argv; sys.argv=['sanitize_static_site.py',str(DEST)]
    try: result=sanitize()
    finally: sys.argv=old
    if result: raise SystemExit(result)
    errors=audit(DEST)
    if errors: raise SystemExit('\n'.join(errors))
    published={p.relative_to(DEST).as_posix() for p in (DEST/'lectures/iscarb').rglob('*') if p.is_file()}
    if published!=set(spec['iscarb_public_files']): raise SystemExit('The staged ISCARB directory does not match its explicit publication allowlist.')
    for item in spec['lectures']+spec['assignments']:
        name=item['path']
        if (ROOT/name).read_bytes()!=(DEST/name).read_bytes(): raise SystemExit(f'Staging changed approved standalone content: {name}')
    print('Public site staged: Chapters 10 and 11 with reviewed progressive assignments, identical to validated sources.')
if __name__=='__main__': main()
