"""Verify story-led student experience, duplication, responsive layout and offline packages."""
import argparse, asyncio, functools, hashlib, json, os, re, threading, zipfile
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
VERSION='20260922-story-v2'
DATA=re.compile(r'(<script id="lecture-data" type="application/json">)([\s\S]*?)(</script>)')
SPECIAL={'TITLE','MAP','START','END'}
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def norm(s):
    return set(re.sub(r'[^a-z0-9 ]+',' ',str(s).lower()).split())
def sim(a,b):
    A,B=norm(a),norm(b)
    return len(A&B)/len(A|B) if A|B else 0

def data_from(path):
    m=DATA.search(path.read_text())
    assert m,path
    return json.loads(m.group(2))

def static_audit(root,pub):
    report=[]
    for c in pub['lectures']:
        ch=c['chapter'];d=data_from(root/c['path']);slides=d['slides'];ids=[x['id'] for x in slides]
        assert len(slides)==20,(ch,len(slides))
        assert ids[:3]==['TITLE','MAP','START'],(ch,ids[:3])
        assert ids[-1]=='END',(ch,ids[-3:])
        assert len(d['roadmap']['branches'])==5 and all(b.get('caseLens') for b in d['roadmap']['branches'])
        if ch==11:
            assert 'CHECK' not in ids and 'DECIDE' not in ids
        duplicates=[]
        for i in range(len(slides)-1):
            a,b=slides[i],slides[i+1]
            if a['id'] in SPECIAL or b['id'] in SPECIAL:continue
            va=json.dumps([a.get('title'),a.get('takeaway'),a.get('question'),a.get('bullets')],sort_keys=True)
            vb=json.dumps([b.get('title'),b.get('takeaway'),b.get('question'),b.get('bullets')],sort_keys=True)
            score=sim(va,vb)
            if score>=.72:duplicates.append((a['id'],b['id'],round(score,2)))
            if a.get('bullets') and a.get('bullets')==b.get('bullets'):duplicates.append((a['id'],b['id'],'identical bullets'))
        assert not duplicates,(ch,duplicates)
        report.append({'chapter':ch,'count':20,'opening':ids[:3],'closing':ids[-1],'duplicate_adjacent':duplicates})
    return report

async def no_overflow(page):
    return await page.evaluate("""()=>{const m=document.getElementById('chapter-main'),f=document.querySelector('.footerbar')?.getBoundingClientRect();if(innerWidth<=1000)return [];return [...m.querySelectorAll('h1,h2,h3,p,button,section,span')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&(r.left<-2||r.right>innerWidth+2||(f&&r.bottom>f.top+3));}).map(e=>e.textContent.trim().slice(0,100));}""")

async def check_page(browser,url,ch,mode,out):
    ctx=await browser.new_context(viewport={'width':1440,'height':900},offline=mode=='offline')
    page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.goto(url,wait_until='load');await page.wait_for_function('!!window.iscarb')
    d=await page.evaluate('iscarb.data')
    assert d['chapter']==ch and len(d['slides'])==20
    assert await page.locator('html').get_attribute('data-story')==VERSION
    assert [x['id'] for x in d['slides'][:3]]==['TITLE','MAP','START'] and d['slides'][-1]['id']=='END'

    # Map is a simple five-step reasoning path with scenario lenses.
    await page.evaluate('iscarb.go(1)')
    assert await page.locator('.concept-path .map-step').count()==5
    assert await page.locator('.mind-wires').count()==0
    for b in d['roadmap']['branches']:
        assert b['caseLens'] in await page.locator('.concept-path').inner_text()
    assert not await no_overflow(page)

    # Story is immediately after the map and does not reveal the mutation.
    await page.evaluate('iscarb.go(2)')
    story=await page.locator('#chapter-main').inner_text()
    assert d['case']['headline'] in story and d['case']['text'] in story and d['case']['question'] in story
    assert d['case']['mutation'] not in story
    assert 'One story, five lenses' in story
    assert not await no_overflow(page)

    # Every ordinary subject screen is explicitly tied back to the same case.
    for i,s in enumerate(d['slides']):
        if s['id'] in SPECIAL:continue
        await page.evaluate(f'iscarb.go({i})')
        if s.get('banner'):
            assert await page.locator('.ai-banner').count()==1,(ch,s['id'])
            text=await page.locator('.ai-banner').inner_text()
            assert 'AI SEGMENT' in text,(ch,s['id'])
        else:
            assert await page.locator('.case-thread').count()==1,(ch,s['id'])
            text=await page.locator('.case-thread').inner_text()
            assert 'CASE THREAD' in text,(ch,s['id'])
        assert not await no_overflow(page),(ch,s['id'])

    # The ending is unmistakable and tells the learner exactly what remains.
    await page.evaluate('iscarb.go(19)')
    end=await page.locator('#chapter-main').inner_text()
    for phrase in ['COMPLETE','Required review','Check yourself',f'Assignment {d["assignment"]}']:
        assert phrase in end,(ch,phrase,end[:500])
    assert await page.locator('.end-hero').count()==1
    assert not await no_overflow(page)

    # Mobile: map/story/end reflow, not shrink into an unreadable canvas.
    await page.set_viewport_size({'width':390,'height':844})
    for i,name in [(1,'map'),(2,'story'),(19,'end')]:
        await page.evaluate(f'iscarb.go({i})')
        assert await page.evaluate("document.documentElement.scrollWidth<=innerWidth+2"),(ch,mode,name)
    if ch in (11,16):
        await page.screenshot(path=str(out/f'ch{ch}-{mode}-mobile-end.png'),full_page=True)
    if mode=='online' and ch in (11,14):
        await page.set_viewport_size({'width':1440,'height':900});await page.evaluate('iscarb.go(1)')
        await page.screenshot(path=str(out/f'ch{ch}-map.png'),full_page=True)
        await page.evaluate('iscarb.go(2)');await page.screenshot(path=str(out/f'ch{ch}-story.png'),full_page=True)
        await page.evaluate('iscarb.go(19)');await page.screenshot(path=str(out/f'ch{ch}-end.png'),full_page=True)
    assert not errors,errors
    await ctx.close()
    return {'chapter':ch,'mode':mode,'map_steps':5,'story_after_map':True,'case_thread':True,'explicit_end':True,'errors':errors}

async def main(a):
    root=a.root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    pub=json.loads((root/'curriculum/publication.json').read_text())
    report={'version':VERSION,'static':static_audit(root,pub),'browser':[],'packages':[]}
    server=None
    if a.base:base=a.base.rstrip('/')+'/'
    else:
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root/'_site' if (root/'_site').exists() else root)))
        threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
    try:
        async with async_playwright() as p:
            browser=await p.chromium.launch(headless=True)
            for c in pub['lectures']:
                ch=c['chapter'];url=urljoin(base,c['path']+'#TITLE')
                report['browser'].append(await check_page(browser,url,ch,'online',out))
                pn=root/c['offline_package'];assert pn.exists()
                assert hashlib.sha256(pn.read_bytes()).hexdigest()==pub['delivery_asset_sha256'][c['offline_package']]
                ext=out/f'extracted-{ch}'
                with zipfile.ZipFile(pn) as z:
                    assert z.testzip() is None;z.extractall(ext)
                report['browser'].append(await check_page(browser,(ext/'START-HERE.html').as_uri(),ch,'offline',out))
                report['packages'].append({'chapter':ch,'sha256':hashlib.sha256(pn.read_bytes()).hexdigest(),'offline_opened':True})
                print('PASS story/map/end/duplicate/offline CH',ch,flush=True)
            await browser.close()
        report['status']='passed'
    finally:
        (out/'story-v2-proof.json').write_text(json.dumps(report,indent=2))
        if server:server.shutdown()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--base',default=os.environ.get('COURSE_BASE_URL'));p.add_argument('--output',type=Path,default=Path('test-results/story-v2'));asyncio.run(main(p.parse_args()))
