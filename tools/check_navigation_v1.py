"""Real keyboard/mouse regression checks on HTTP lessons and extracted offline ZIPs."""
import argparse, asyncio, functools, hashlib, json, os, threading, zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
CHAPTERS=[10,11,12,13,14,15,16,17,20]
VERSION='20260921-navigation-v1'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
async def blur(page):
 await page.evaluate("document.activeElement?.blur();window.getSelection()?.removeAllRanges()")
async def idx(page):return await page.evaluate('iscarb.getIndex()')
async def canvas_click(page,back=False):
 await page.wait_for_timeout(280)
 b=await page.locator('#chapter-main').bounding_box()
 if back:await page.keyboard.down('Shift')
 await page.mouse.click(b['x']+5,b['y']+10)
 if back:await page.keyboard.up('Shift')
async def run_case(browser,url,ch,offline,out,kind):
 context=await browser.new_context(viewport={'width':1366,'height':768},offline=offline)
 page=await context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 await page.goto(url,wait_until='load');await page.wait_for_function('!!window.iscarb')
 assert await page.locator('html').get_attribute('data-navigation')==VERSION
 passed=[]
 async def check(name,condition):
  assert condition,f'{ch} {kind}: {name}';passed.append(name)
 await blur(page);await page.keyboard.press('Enter');await check('Enter advances one slide',await idx(page)==1)
 await page.keyboard.press('Backspace');await check('Backspace returns one slide',await idx(page)==0)
 await page.keyboard.press('Backspace');await check('First slide remains in lecture',await idx(page)==0 and url.split('#')[0]==page.url.split('#')[0])
 await page.keyboard.press('End');await page.keyboard.press('Enter');await check('Last slide has no wrap or navigation away',await idx(page)==19)
 await page.keyboard.press('Home');await canvas_click(page);await check('Single mouse click advances',await idx(page)==1)
 await canvas_click(page,True);await check('Shift plus mouse click returns',await idx(page)==0)
 await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowLeft');await check('Existing arrow keys preserved',await idx(page)==0)
 await page.evaluate('iscarb.go(3)');await blur(page)
 for key,extra in [('Enter',{'repeat':True}),('Enter',{'isComposing':True}),('Backspace',{'ctrlKey':True}),('Enter',{'metaKey':True})]:
  await page.evaluate("a=>document.body.dispatchEvent(new KeyboardEvent('keydown',{key:a.key,bubbles:true,cancelable:true,...a.extra}))",{'key':key,'extra':extra})
 await check('Repeat, composition and modified shortcuts do not move',await idx(page)==3)
 await page.evaluate("document.body.addEventListener('keydown',e=>e.preventDefault(),{once:true})")
 await page.keyboard.press('Enter');await check('Previously handled keyboard event respected',await idx(page)==3)
 await page.locator('#helpBtn').focus();await page.keyboard.press('Enter')
 await check('Enter activates focused native button only',not await page.locator('#modal').is_hidden() and await idx(page)==3)
 await page.keyboard.press('Backspace');await check('Dialog does not move underlying slide',await idx(page)==3)
 await page.keyboard.press('Escape');await blur(page)
 await page.locator('[data-answer]').first.click();await check('Model answer click does not advance',await idx(page)==3)
 await page.keyboard.press('Escape');await blur(page)
 await page.evaluate("iscarb.open('CARD')")
 field=page.locator('#modal textarea[data-field]').first
 await field.fill('NAVTEST');await field.press('End');await field.press('Backspace');await field.press('Enter');await field.type('X')
 await check('Editing Backspace and Enter remain native',await field.input_value()=='NAVTES\nX' and await idx(page)==3)
 value=await field.input_value();await page.keyboard.press('Escape');await page.reload();await page.wait_for_function('!!window.iscarb');await page.evaluate("iscarb.open('CARD')")
 await check('Card draft persists through reload',await page.locator('#modal textarea[data-field]').first.input_value()==value)
 await page.keyboard.press('Escape');await blur(page);await page.evaluate('iscarb.go(3)')
 await page.evaluate("const e=document.createElement('div');e.id='nav-edit-test';e.contentEditable='true';e.textContent='ABC';document.getElementById('chapter-main').appendChild(e);e.focus()")
 await page.keyboard.press('End');await page.keyboard.press('Backspace');await page.keyboard.press('Enter')
 await check('Contenteditable is not hijacked',await idx(page)==3 and 'AB' in await page.locator('#nav-edit-test').inner_text())
 await page.evaluate("document.getElementById('nav-edit-test').remove()");await blur(page)
 b=await page.locator('.takeaway').bounding_box();await page.mouse.move(b['x']+3,b['y']+10);await page.mouse.down();await page.mouse.move(b['x']+170,b['y']+10,steps=12);await page.mouse.up()
 await check('Drag selection leaves current slide',await idx(page)==3)
 await blur(page)
 await page.evaluate("const e=document.querySelector('.takeaway');const r=document.createRange();r.selectNodeContents(e);window.getSelection().addRange(r)")
 await canvas_click(page);await check('Clearing selected text does not advance',await idx(page)==3)
 await blur(page)
 await page.locator('#viewBtn').click();await canvas_click(page);await check('Reading view mouse selection is safe',await idx(page)==3)
 await blur(page);await page.keyboard.press('Enter');await check('Keyboard works in Reading view',await idx(page)==4)
 await page.locator('#viewBtn').click();await blur(page)
 await page.evaluate('iscarb.startStation(1)');start=await idx(page);await canvas_click(page)
 await check('Mouse does not skip a station',await idx(page)==start and await page.locator('.station').count()==1)
 f=page.locator('.station textarea').first;await f.fill('ABC');await f.press('End');await f.press('Backspace');await f.press('Enter')
 await check('Station field editing preserved',await idx(page)==start and await f.input_value()=='AB\n')
 await page.locator('#station-back').click();await blur(page)
 fig=await page.evaluate('iscarb.data.slides.findIndex(s=>!!s.figure)')
 if fig>=0:
  await page.evaluate('i=>iscarb.go(i)',fig);await page.locator('.figure-button').click()
  await check('Figure opens zoom without advancing',await idx(page)==fig and not await page.locator('#modal').is_hidden())
  await page.keyboard.press('Escape');await blur(page)
 for i in range(20):
  await page.evaluate('i=>iscarb.go(i)',i)
  bad=await page.evaluate("(()=>{const m=document.getElementById('chapter-main'),r=m.getBoundingClientRect(),f=document.querySelector('.footerbar').getBoundingClientRect();return m.scrollHeight>m.clientHeight+3||r.bottom>f.top+3||document.documentElement.scrollWidth>innerWidth+3})()")
  assert not bad,f'{ch} {kind} overflow at {i}'
 await page.evaluate('iscarb.go(3)');await page.wait_for_timeout(100)
 if ch==11:await page.screenshot(path=str(out/f'ch11-{kind}-desktop.png'))
 await page.set_viewport_size({'width':390,'height':844});await canvas_click(page)
 await check('Narrow layout ignores mouse slide shortcuts',await idx(page)==3)
 await blur(page);await page.keyboard.press('Enter');await page.keyboard.press('Backspace');await check('Narrow layout keyboard preserved',await idx(page)==3)
 for i in range(20):
  await page.evaluate('i=>iscarb.go(i)',i)
  assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+3'),f'{ch} {kind} mobile width at {i}'
 if ch==11:
  await page.evaluate('iscarb.go(3)');await page.screenshot(path=str(out/f'ch11-{kind}-mobile.png'),full_page=True)
 await check('No JavaScript errors',not errors)
 await context.close();return {'chapter':ch,'mode':kind,'passed':passed,'layout_checks':40}
async def main(a):
 root=a.root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 server=None
 if a.base:base=a.base
 else:
  server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 report={'version':VERSION,'base':base,'cases':[],'downloads':[]}
 try:
  async with async_playwright() as p:
   options={'headless':True}
   if os.environ.get('CHROMIUM_EXECUTABLE'):options['executable_path']=os.environ['CHROMIUM_EXECUTABLE']
   browser=await p.chromium.launch(**options)
   downloader=await browser.new_page();await downloader.goto(urljoin(base,'iscarb.html'),wait_until='load')
   for ch in CHAPTERS:
    link=downloader.locator(f'#chapter-{ch} a[download]')
    assert await link.count()==1
    href=await link.get_attribute('href');assert href.split('?')[0]==f'lectures/iscarb/packages/Ch{ch}-iSCARB.zip',href
    async with downloader.expect_download() as pending:await link.click()
    d=await pending.value;package=out/f'Ch{ch}-iSCARB.zip';await d.save_as(package)
    assert d.suggested_filename.endswith('.zip')
    if (root/'curriculum/publication.json').is_file():
     pub=json.loads((root/'curriculum/publication.json').read_text());assert hashlib.sha256(package.read_bytes()).hexdigest()==pub['delivery_asset_sha256'][href.split('?')[0]],'Live package differs from reviewed bytes'
    extracted=out/f'extracted-{ch}'
    with zipfile.ZipFile(package) as z:
     assert z.testzip() is None
     for name in z.namelist():assert (extracted/name).resolve().is_relative_to(extracted.resolve())
     z.extractall(extracted)
    lecture=[x for x in (extracted/'lectures/iscarb').glob(f'Ch{ch}-*.html') if 'data-navigation' in x.read_text()];assert len(lecture)==1
    path=lecture[0].relative_to(extracted).as_posix()
    report['cases'].append(await run_case(browser,urljoin(base,path),ch,False,out,'online'))
    report['cases'].append(await run_case(browser,lecture[0].as_uri(),ch,True,out,'offline'))
    report['downloads'].append({'chapter':ch,'file':d.suggested_filename,'bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest()})
    print(f'PASS Ch{ch}: real download, online + offline keyboard/mouse/editing; 80 slide layouts',flush=True)
   await browser.close()
  report['status']='passed';report['total_layout_checks']=sum(c['layout_checks'] for c in report['cases']);report['total_behavior_checks']=sum(len(c['passed']) for c in report['cases'])
 finally:
  (out/'navigation-proof.json').write_text(json.dumps(report,indent=2))
  if server:server.shutdown()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--base',default=os.environ.get('COURSE_BASE_URL'));p.add_argument('--output',type=Path,default=Path('test-results/navigation'));asyncio.run(main(p.parse_args()))
