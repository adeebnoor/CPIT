"""Narrow navigation-only patch; preserve lecture data and assessed assignments."""
from pathlib import Path
import argparse, hashlib, io, json, re, zipfile
VERSION = '20260921-navigation-v1'
CHAPTERS = [10,11,12,13,14,15,16,17,20]
RUNTIME = 'lectures/iscarb/runtime/classroom-v3.js'
CSS = 'lectures/iscarb/runtime/classroom-v3.css'
NAV = r'''
// Navigation v1: native controls/editing win over presentation shortcuts.
const navControl='input,textarea,select,button,a[href],label,summary,audio,video,iframe,[role="button"],[role="textbox"],[role="combobox"],[role="slider"],[data-no-slide-nav]';
function navInteractive(target){return !(target instanceof Element)||target.isContentEditable||!!target.closest(navControl);}
function selectedText(){const s=window.getSelection();return !!(s&&!s.isCollapsed);}
function mousePresentation(){return !stationMode&&$('#modal').hidden&&!document.body.classList.contains('reading')&&matchMedia('(min-width:1001px)').matches;}
let navPointer=null,lastMouseSlide=-Infinity;
$('#chapter-main').addEventListener('pointerdown',e=>{
 navPointer=null;
 if(e.pointerType!=='mouse'||e.button!==0||e.ctrlKey||e.altKey||e.metaKey||!mousePresentation()||navInteractive(e.target))return;
 navPointer={x:e.clientX,y:e.clientY,index,selected:selectedText()};
});
$('#chapter-main').addEventListener('pointercancel',()=>{navPointer=null;});
$('#chapter-main').addEventListener('click',e=>{
 const p=navPointer;navPointer=null;
 if(!p||e.defaultPrevented||e.button!==0||e.detail!==1||e.ctrlKey||e.altKey||e.metaKey||!mousePresentation()||navInteractive(e.target))return;
 if(p.index!==index||p.selected||selectedText()||Math.hypot(e.clientX-p.x,e.clientY-p.y)>8||performance.now()-lastMouseSlide<260)return;
 lastMouseSlide=performance.now();e.preventDefault();go(index+(e.shiftKey?-1:1));
});
$('#prevBtn').title='Previous slide · Backspace or Left arrow';
$('#nextBtn').title='Next slide · Enter or Right arrow';
$('#chapter-main').setAttribute('aria-keyshortcuts','Enter Backspace ArrowLeft ArrowRight Home End');
'''
HELP_OLD='<tr><th>← / →</th><td>Previous / next classroom slide.</td></tr>'
HELP_NEW='<tr><th>Enter / Backspace</th><td>Next / previous classroom slide. On a focused button or link, Enter activates that control.</td></tr><tr><th>Mouse click / Shift + click</th><td>Next / previous on non-interactive slide content in desktop presentation mode. Dragging to select text does not navigate.</td></tr>'+HELP_OLD
GUIDE='''<section class="panel" id="navigation-shortcuts"><h2>Move between slides without searching for the arrows</h2><p><b>Enter:</b> next slide. <b>Backspace:</b> previous slide. In desktop presentation mode, a single mouse click on non-interactive slide content advances; <b>Shift + click</b> goes back. The existing arrow keys and arrow buttons remain available.</p><p>Buttons, links, enlarged figures, input fields and dialogs keep their normal behavior. Enter and Backspace remain editing keys while you write; Enter activates a focused button or link. Mouse slide navigation pauses in classroom stations, Reading view and narrow/mobile layouts, so interaction and text selection do not skip slides. Keyboard navigation still works outside controls in Reading view.</p><p>The same controls are included in new offline ZIP downloads. Previously downloaded packages do not update themselves: download the current ZIP and export a backup of any existing card before switching copies.</p></section>'''
def sha(b):return hashlib.sha256(b).hexdigest()
def once(s,a,b):
 if s.count(a)!=1:raise ValueError('Expected one patch target: '+a[:100])
 return s.replace(a,b,1)
def shell(s):
 s=once(s,'runtime/classroom-v3.js?v=20260921-classroom-v3','runtime/classroom-v3.js?v='+VERSION)
 s=once(s,'runtime/classroom-v3.css?v=20260921-classroom-v3','runtime/classroom-v3.css?v='+VERSION)
 s=once(s,'data-course-release="20260921-classroom-v3"','data-course-release="20260921-classroom-v3" data-navigation="'+VERSION+'"')
 return s
def apply(root):
 changed=[]
 def write(name,b):
  (root/name).write_bytes(b);changed.append(name)
 old=(root/RUNTIME).read_bytes()
 assert hashlib.sha1(b'blob '+str(len(old)).encode()+b'\0'+old).hexdigest()=='af73a73e9374d72828a746cc0a00b2b51dbf6102','Runtime changed; review before patching'
 s=old.decode();s=once(s,"document.addEventListener('keydown',e=>{",NAV+"\ndocument.addEventListener('keydown',e=>{if(e.defaultPrevented||e.isComposing||e.ctrlKey||e.altKey||e.metaKey)return;")
 s=once(s,"if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.target.isContentEditable)return;", "if(navInteractive(e.target))return;if(e.key==='Enter'||e.key==='Backspace'){if(e.shiftKey)return;e.preventDefault();if(!e.repeat)go(index+(e.key==='Enter'?1:-1));return;}")
 s=once(s,HELP_OLD,HELP_NEW)
 s=once(s,"$('#progress').textContent=`${new Set(state.seen).size} / ${D.slides.length} visited · not mastery`;", "$('#progress').innerHTML=`${new Set(state.seen).size} / ${D.slides.length} visited · not mastery<span class=\"nav-shortcuts\">Enter → · Backspace ←</span>`;")
 write(RUNTIME,s.encode())
 css=(root/CSS).read_bytes()+b'\n/* Navigation hints do not scale or hide lesson content. */\n.nav-shortcuts{display:block;font-size:11px;line-height:1.3;white-space:nowrap;color:var(--teal)}\n'
 write(CSS,css)
 paths={}
 for ch in CHAPTERS:
  ps=list((root/'lectures/iscarb').glob('Ch'+str(ch)+'-*.html'));ps=[p for p in ps if 'data-course-release="20260921-classroom-v3"' in p.read_text()]
  assert len(ps)==1,(ch,ps)
  p=ps[0];name=p.relative_to(root).as_posix();before=p.read_text();after=shell(before)
  assert re.search(r'<script id="lecture-data"[^>]*>(.*?)</script>',before,re.S).group(1)==re.search(r'<script id="lecture-data"[^>]*>(.*?)</script>',after,re.S).group(1),'Chapter data changed'
  write(name,after.encode());paths[ch]=name
 for ch in CHAPTERS:
  name=f'lectures/iscarb/packages/Ch{ch}-iSCARB.zip';out=io.BytesIO();seen=set()
  with zipfile.ZipFile(root/name) as src,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as dst:
   for info in src.infolist():
    data=src.read(info.filename)
    if info.filename==RUNTIME:
     assert data.decode().replace('https://adeebnoor.github.io/CPIT/','../../')==old.decode();data=s.replace('../../fbr-submission.html','https://adeebnoor.github.io/CPIT/fbr-submission.html').encode();seen.add(RUNTIME)
    elif info.filename==CSS:data=css;seen.add(CSS)
    elif info.filename==paths[ch]:data=shell(data.decode()).encode();seen.add(paths[ch])
    elif info.filename=='README.txt':data+=b'\nNavigation: Enter = next; Backspace = previous. In desktop presentation mode, click slide content = next; Shift + click = previous. Editing fields, dialogs and controls keep their normal behavior.\n'
    dst.writestr(info,data)
  assert seen=={RUNTIME,CSS,paths[ch]},(ch,seen)
  with zipfile.ZipFile(io.BytesIO(out.getvalue())) as z: assert z.testzip() is None
  write(name,out.getvalue())
 guide=(root/'student-guide.html').read_text();assert 'id="navigation-shortcuts"' not in guide
 write('student-guide.html',once(guide,'</main>',GUIDE+'</main>').encode())
 cat=root/'curriculum/publication.json'
 if cat.exists():
  pub=json.loads(cat.read_text());assert pub['release']=='20260921-classroom-v3'
  for lecture in pub['lectures']:
   lecture['source_sha256']=sha((root/lecture['path']).read_bytes())
  for name in [RUNTIME,CSS]+[f'lectures/iscarb/packages/Ch{ch}-iSCARB.zip' for ch in CHAPTERS]:
   assert name in pub['delivery_asset_sha256'],name
   pub['delivery_asset_sha256'][name]=sha((root/name).read_bytes())
  write('curriculum/publication.json',(json.dumps(pub,ensure_ascii=False,indent=2)+'\n').encode())
 manifest={'navigation_version':VERSION,'changed':{n:sha((root/n).read_bytes()) for n in changed},'chapter_data':'unchanged','assessment_files':'not edited','storage_keys':'unchanged'}
 (root/'navigation-change-manifest.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps({'version':VERSION,'updated_files':len(changed),'packages':len(CHAPTERS)},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();apply(a.root.resolve())
