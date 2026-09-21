"""Student-path tests on real HTTP and newly downloaded, extracted offline packages.
Fresh contexts contain only QA drafts. No LMS submission or student data is used.
"""
import argparse, asyncio, functools, hashlib, json, os, re, threading, zipfile
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
VERSION='20260921-mindmap-v1'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
async def check_page(browser,url,ch,kind,out):
    ctx=await browser.new_context(viewport={'width':1366,'height':768},offline=kind=='offline')
    page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.goto(url,wait_until='load');await page.wait_for_function('!!window.iscarb')
    d=await page.evaluate('iscarb.data');assert d['chapter']==ch and len(d['slides'])==20
    assert await page.locator('html').get_attribute('data-mindmap')==VERSION
    assert d['slides'][0]['id']=='TITLE' and d['slides'][1]['id']=='MAP'
    assert await page.evaluate('iscarb.getIndex()')==0
    await page.locator('[data-jump="MAP"]').last.click()
    assert await page.evaluate('iscarb.getIndex()')==1
    assert await page.locator('.mind-branch').count()==5
    assert await page.locator('.student-roadmap .road-stage').count()==3
    assert await page.locator('.topnav button').count()==3
    for branch in d['roadmap']['branches']:
        await page.locator('.mind-branch[data-jump="'+branch['target']+'"]').click()
        assert await page.evaluate('iscarb.data.slides[iscarb.getIndex()].id')==branch['target']
        assert await page.locator('#topic-location').inner_text()==branch['label']
        await page.locator('#mapBtn').click();assert await page.evaluate('iscarb.getIndex()')==1
    await page.locator('[data-open="OBJECTIVES"]').click()
    assert await page.locator('.objective-list li').all_text_contents()==d['objectives']
    text=await page.locator('#modal-body').inner_text()
    assert all(s in text for s in d['sections'])
    await page.keyboard.press('Escape');await page.locator('#nextBtn').click()
    assert await page.evaluate('iscarb.getIndex()')==2
    await page.locator('#mapBtn').click()
    await page.locator('.topnav [data-open="TOOLS"]').click()
    for target in ['CARD','OBJECTIVES','READING','QUIZ','RULES','COVERAGE','READINESS','AI','PORTFOLIO']:
        assert await page.locator('#modal [data-open="'+target+'"]').count()==1,target
    await page.locator('#modal [data-open="READING"]').click()
    text=await page.locator('#modal-body').inner_text()
    assert all(x['range'] in text and x['title'] in text for x in d['readings'])
    await page.keyboard.press('Escape');await page.locator('.topnav [data-open="TOOLS"]').click()
    assignment=page.locator('#modal a.tool-link');assert 'chapter='+str(ch) in await assignment.get_attribute('href')
    await page.locator('#modal [data-open="RULES"]').click();assert await page.locator('[data-rule]').count()==20
    await page.keyboard.press('Escape')
    await page.evaluate('document.activeElement.blur()');await page.keyboard.press('Enter')
    assert await page.evaluate('iscarb.getIndex()')==2
    await page.keyboard.press('Backspace');assert await page.evaluate('iscarb.getIndex()')==1
    layouts=[]
    for w,h in [(1920,1080),(1440,900),(1366,768),(1280,720),(1024,768),(390,844)]:
        await page.set_viewport_size({'width':w,'height':h});await page.locator('#mapBtn').click()
        bad=await page.evaluate('''()=>{const m=document.getElementById('chapter-main'),f=document.querySelector('.footerbar').getBoundingClientRect();return [...m.querySelectorAll('button,p,h1,h2,h3,span,strong')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&(r.left< -2||r.right>innerWidth+2||(innerWidth>1000&&r.bottom>f.top+2));}).map(e=>e.textContent.slice(0,90))}''')
        assert not bad,(ch,kind,w,bad)
        assert await page.evaluate('innerWidth<=1000||document.getElementById("chapter-main").scrollHeight<=document.getElementById("chapter-main").clientHeight+3'),(ch,kind,w,'overflow')
        layouts.append([w,h])
        if (kind=='online' and w==1440) or (ch==11 and w==390):
            await page.screenshot(path=str(out/f'ch{ch}-{kind}-{w}.png'),full_page=True)
    assert not errors,errors
    await ctx.close();return {'chapter':ch,'mode':kind,'page_two':True,'branches':5,'unchanged_objectives':5,'reduced_primary_controls':3,'viewports':layouts,'errors':errors}
async def main(a):
    root=a.root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    pub=json.loads((root/'curriculum/publication.json').read_text());server=None
    if a.base:base=a.base.rstrip('/')+'/'
    else:
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
        threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
    report={'version':VERSION,'base':base,'chapters':[],'packages':[]}
    try:
        async with async_playwright() as p:
            options={'headless':True}
            if os.environ.get('CHROMIUM_EXECUTABLE'):options['executable_path']=os.environ['CHROMIUM_EXECUTABLE']
            browser=await p.chromium.launch(**options);hub=await browser.new_page()
            await hub.goto(urljoin(base,'iscarb.html'),wait_until='load')
            for c in pub['lectures']:
                ch=c['chapter'];entry=hub.locator(f'#chapter-{ch} .actions a.btn').first
                assert (await entry.get_attribute('href')).endswith('#TITLE'),(ch,'Hub skips the cover/map')
                lecture_url=urljoin(base,await entry.get_attribute('href'))
                report['chapters'].append(await check_page(browser,lecture_url,ch,'online',out))
                link=hub.locator(f'#chapter-{ch} a[download]');href=await link.get_attribute('href')
                assert href.split('?')[0]==c['offline_package']
                async with hub.expect_download() as pending:await link.click()
                download=await pending.value;zpath=out/f'Ch{ch}-iSCARB.zip';await download.save_as(zpath)
                digest=hashlib.sha256(zpath.read_bytes()).hexdigest();assert digest==pub['delivery_asset_sha256'][c['offline_package']]
                extracted=out/f'extracted-{ch}'
                with zipfile.ZipFile(zpath) as z:
                    assert z.testzip() is None
                    assert all((extracted/n).resolve().is_relative_to(extracted.resolve()) for n in z.namelist())
                    z.extractall(extracted)
                report['chapters'].append(await check_page(browser,(extracted/'START-HERE.html').as_uri(),ch,'offline',out))
                report['packages'].append({'chapter':ch,'sha256':digest,'downloaded':True,'extracted_and_opened_offline':True})
                print('PASS mind map / actual entry / roles / objectives / study tools / ZIP: CH',ch,flush=True)
            await browser.close()
        report['status']='passed';report['map_layout_checks']=sum(len(c['viewports']) for c in report['chapters'])
    finally:
        (out/'mindmap-proof.json').write_text(json.dumps(report,indent=2))
        if server:server.shutdown()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--base',default=os.environ.get('COURSE_BASE_URL'));p.add_argument('--output',type=Path,default=Path('test-results/mindmap'));asyncio.run(main(p.parse_args()))
