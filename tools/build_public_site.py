"""Stage the public site with identical classroom source and published behavior."""
from pathlib import Path
import shutil, os, sys
from sanitize_static_site import main as sanitize
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'_site'
VERSION='20260913-classroom6'
PUBLIC=['index.html','cimt.html','imam.html','iscarb.html','iscarb-students.html','fbr-submission.html','download.html','download-stats.html','student-guide.html','course-resources.html','methodology.html','style.css','iscarb-theme.css','iscarb-theme.js']
def main():
    if DEST.exists():shutil.rmtree(DEST)
    DEST.mkdir()
    for name in PUBLIC:shutil.copy2(ROOT/name,DEST/name)
    for name in ['slides','lectures','wealth-os']:shutil.copytree(ROOT/name,DEST/name)
    image='iscarb-studio/app/static/hero_user_original.png'
    (DEST/image).parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/image,DEST/image)
    for p in DEST.rglob('*.html'):
        if p==DEST/'index.html' or 'wealth-os' in p.parts:continue
        s=p.read_text()
        if 'data-iscarb-lesson="6"' in s or p.name=='InClass-Presenter.html':continue
        prefix=os.path.relpath(DEST,p.parent).replace('\\','/')
        prefix='' if prefix=='.' else prefix+'/'
        if 'iscarb-theme.css' not in s:s=s.replace('</head>',f'<link rel="stylesheet" href="{prefix}iscarb-theme.css?v={VERSION}"></head>',1)
        if 'iscarb-theme.js' not in s:s=s.replace('</body>',f'<script src="{prefix}iscarb-theme.js?v={VERSION}" defer></script></body>',1)
        p.write_text(s)
    old=sys.argv;sys.argv=['sanitize_static_site.py',str(DEST)]
    try:result=sanitize()
    finally:sys.argv=old
    if result:raise SystemExit(result)
    print('Public site staged. Classroom pages match validated source.')
if __name__=='__main__':main()
