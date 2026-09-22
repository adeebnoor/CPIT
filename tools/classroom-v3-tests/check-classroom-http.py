"""Real-origin Chromium verification of the reviewed iSCARB release.

Run against an HTTP-served staged site or the explicitly selected live site.
Student data is never used: each test gets a fresh browser context and QA-only
local state. The static assignment does not submit work to an LMS.
"""
import asyncio, json, os, re, sys
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2]
PUB=json.loads((ROOT/'curriculum/publication.json').read_text())
BASE=os.environ.get('COURSE_BASE_URL','http://127.0.0.1:8765/').rstrip('/')+'/'
OUT=Path(os.environ.get('COURSE_TEST_OUTPUT','test-results/classroom-v3'));OUT.mkdir(parents=True,exist_ok=True)
CHS=[x['chapter'] for x in PUB['lectures']]
async def main():
 errors=[]; checked=0; records=[]; interactions=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True)
  for viewport in [{'width':1440,'height':900},{'width':390,'height':844}]:
   for c in PUB['lectures']:
    ch=c['chapter'];ctx=await browser.new_context(viewport=viewport,accept_downloads=True);page=await ctx.new_page()
    page_http=[]
    page.on('pageerror',lambda e:errors.append({'javascript':str(e)}))
    page.on('response',lambda r:page_http.append({'http':r.status,'url':r.url}) if r.status>=400 and 'favicon.ico' not in r.url else None)
    page.on('dialog',lambda d:d.accept())
    try:
     response=await page.goto(urljoin(BASE,c['path'])+'#START',wait_until='networkidle');assert response.status==200
     await page.wait_for_function('!!window.iscarb');D=await page.evaluate('iscarb.data')
     assert D['release']==PUB['release'] and len(D['slides'])==20
     assert 'This earlier unit' not in await page.locator('#modal-body').inner_text(),'Existing hub entry must resolve'
     await page.evaluate('iscarb.closeModal()')
     assert not await page.evaluate("performance.getEntriesByType('resource').some(x=>/\\.(pdf|pptx)([?#]|$)/i.test(x.name))"),'Sources must be on demand'
     for i,s in enumerate(D['slides']):
      await page.evaluate('(i)=>iscarb.go(i)',i)
      await page.locator('#chapter-main img').evaluate_all('(imgs)=>Promise.all(imgs.map(im=>im.decode().catch(()=>{})))')
      bad=await page.evaluate('''()=>{const f=document.querySelector('.footerbar').getBoundingClientRect();return [...document.querySelectorAll('#chapter-main h1,#chapter-main p,#chapter-main li,#chapter-main td,#chapter-main th,#chapter-main img')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.left< -2||r.right>innerWidth+2||(innerWidth>1000&&r.bottom>f.top+2));}).map(e=>e.textContent.slice(0,90));}''')
      assert not bad,f'Layout CH{ch} {s["id"]} {viewport}: {bad}'
      assert await page.locator('#chapter-main img').evaluate_all('(a)=>a.every(i=>i.complete&&i.naturalWidth>0)')
      checked+=1
      if viewport['width']==1440 and i in (0,6,14):await page.screenshot(path=str(OUT/f'ch{ch}-{i}-desktop.png'))
      if viewport['width']==390 and i==6:await page.screenshot(path=str(OUT/f'ch{ch}-{i}-phone.png'))
     if viewport['width']==1440:
      # Visible station buttons, authored hints, real timer and persistent shared card.
      for st in D['stations']:
       await page.evaluate('(n)=>iscarb.go(n)',next(i for i,s in enumerate(D['slides']) if s['id']==st['at']))
       await page.locator('#stationBtn').click();await page.locator('#hintBtn').click()
       assert st['hint'] in await page.locator('#coach').inner_text()
       for k in st['fields']:await page.locator(f'[data-field="{k}"]').fill(f'QA CH{ch} station {st["no"]} {k}: bounded evidence, not student work.')
       await page.locator('#timer-start').click();await page.wait_for_timeout(1150)
       assert await page.locator('#timer-output').inner_text()!='03:00'
       await page.locator('#timer-start').click();t=await page.locator('#timer-output').inner_text();await page.wait_for_timeout(280);assert await page.locator('#timer-output').inner_text()==t
       await page.locator('#timer-reset').click();assert await page.locator('#timer-output').inner_text()=='03:00'
       await page.locator('#station-back').click()
      await page.evaluate('iscarb.open("CARD")');claim=await page.locator('[data-field="claim"]').input_value()
      await page.reload(wait_until='networkidle');await page.evaluate('iscarb.open("CARD")');assert await page.locator('[data-field="claim"]').input_value()==claim
      async with page.expect_download() as download:
       await page.locator('[data-export="json"]').click()
      downloaded=await download.value;backup=OUT/f'ch{ch}-qa-backup.json';await downloaded.save_as(backup)
      package=json.loads(backup.read_text());assert package['chapter']==ch and package['state']['fields']['claim']==claim
      await page.locator('[data-field="claim"]').fill('temporary changed draft')
      async with page.expect_file_chooser() as chooser:await page.locator('#import').click()
      await (await chooser.value).set_files(str(backup));await page.wait_for_timeout(100)
      assert await page.locator('[data-field="claim"]').input_value()==claim
      await page.evaluate('iscarb.closeModal();iscarb.open("RULES")');assert await page.locator('[data-rule]').count()==20
      for r in D['rules']:
       for target in r['targets']:
        await page.evaluate('(t)=>iscarb.open(t)',target)
        assert 'This earlier unit' not in await page.locator('#modal-body').inner_text()
        await page.evaluate('iscarb.closeModal()')
      await page.evaluate('iscarb.open("QUIZ")');await page.locator('#quiz-check').click();assert 'Choose' in await page.locator('#quiz-feedback').inner_text()
      for i,q in enumerate(D['quiz']):
       await page.locator(f'[data-quiz="{i}"]').first.click();await page.locator(f'input[name="quiz"][value="{q["answer"]}"]').check();await page.locator('#quiz-check').click();assert 'Correct for' in await page.locator('#quiz-feedback').inner_text()
      if ch==11:
       await page.evaluate('iscarb.open("CALCULATOR")');assert '99.9%' in await page.locator('#calc-result').inner_text()
       await page.locator('#calc-events').fill('0');await page.locator('#calculate').click();assert 'not estimable' in await page.locator('#calc-result').inner_text()
       await page.locator('#calc-demands').fill('');await page.locator('#calculate').click();assert 'blank is not zero' in await page.locator('#calc-result').inner_text()
      # All source pages and real original binary resources resolve over HTTP.
      sr=await ctx.request.get(urljoin(BASE,c['study_path']));assert sr.status==200
      ids=set(map(int,re.findall(r'id="source-slide-(\d+)"',await sr.text())));assert ids==set(range(1,c['source_slide_count']+1))
      for target in [c['source_download'],c['offline_package']]:
       rr=await ctx.request.head(urljoin(BASE,target));assert rr.status==200,target
      interactions.append({'chapter':ch,'stations':3,'timer':True,'reload':True,'export_import':True,'quiz':5,'source_slides':len(ids)})
     # Retry transient CDN/server failures before treating a resource as broken.
     for item in page_http:
      if item['http']>=500:
       recovered=False
       for _ in range(3):
        await page.wait_for_timeout(250)
        rr=await ctx.request.get(item['url'])
        if rr.status<400:
         recovered=True;break
       if not recovered:errors.append(item)
      else:errors.append(item)
     records.append({'chapter':ch,'viewport':viewport,'slides':20,'pass':True})
     print('PASS HTTP CH',ch,viewport,flush=True)
    except Exception as e:
     errors.append({'chapter':ch,'viewport':viewport,'error':str(e)});await page.screenshot(path=str(OUT/f'FAIL-{ch}-{viewport["width"]}.png'),full_page=True)
    finally:await ctx.close()
  # On a real origin, confirm all assessed cases still defer STRESS until commitment.
  for c in PUB['assignments']:
   ctx=await browser.new_context();page=await ctx.new_page();requests=[]
   page.on('request',lambda r:requests.append(r.url) if '/reveal/' in r.url else None)
   page.on('dialog',lambda d:d.accept())
   try:
    await page.add_init_script("sessionStorage.setItem("+json.dumps(c['access_key'])+",JSON.stringify("+json.dumps({'sid':'QA-RELEASE-ONLY','acknowledged':True,'edition':c['edition']})+"));")
    await page.goto(urljoin(BASE,c['path']),wait_until='networkidle');assert not requests
    assert await page.locator('#classroom-assignment-alignment').count()==1
    for k in ['fit','measure','bound','act','evidence','technical']:
     if await page.locator('#'+k).count():await page.locator('#'+k).fill('QA technical reasoning with a defined mechanism, an inspectable artifact and an explicit limit. Not student work.')
    await page.locator('#sourceUse').fill('Slide '+str(c['reading_pages'][0])+' explains the relevant mechanism and its assumptions. This source concept supports a bounded claim in the artifact.')
    if c['chapter'] in [16,17]:
     cases=([{'name':'normal','durationMinutes':30,'expectedStatus':'accepted','expectedSeconds':1800},{'name':'upper','durationMinutes':120,'expectedStatus':'accepted','expectedSeconds':7200},{'name':'invalid','durationMinutes':0,'expectedStatus':'rejected','expectedSeconds':None}] if c['chapter']==16 else [{'name':'restart same identity','events':['send:a','lose-response','restart','retry:a'],'expectedReservations':1},{'name':'different identity','events':['send:b','lose-response','retry:c'],'expectedReservations':2}])
     await page.locator('#labPrediction').fill('QA: baseline may violate the stated expectation; corrected model should meet it within its limited scope.')
     await page.locator('#labCases').fill(json.dumps(cases));await page.locator('[data-lab-mode="baseline"]').click();await page.locator('[data-lab-mode="corrected"]').click()
    await page.evaluate('commit()');await page.wait_for_timeout(300)
    assert len(requests)==1,requests
    assert await page.locator('#fit').evaluate('(e)=>e.readOnly')
    assert await page.locator('#partB').is_visible()
    first=await page.locator('#fit').input_value();await page.reload(wait_until='networkidle');assert await page.locator('#fit').input_value()==first and await page.locator('#fit').evaluate('(e)=>e.readOnly')
    assert len(requests)==1,'Reveal should restore from the correct saved edition'
    print('PASS HTTP assignment',c['chapter'],'commit / delayed reveal / locked reload',flush=True)
   except Exception as e:errors.append({'assignment':c['chapter'],'error':str(e)});await page.screenshot(path=str(OUT/f'FAIL-assignment-{c["chapter"]}.png'),full_page=True)
   finally:await ctx.close()
  await browser.close()
 report={'base':BASE,'release':PUB['release'],'real_http_slide_checks':checked,'viewports':records,'interactions':interactions,'errors':errors}
 (OUT/'http-results.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'checks':checked,'errors':errors},indent=2))
 if errors:raise SystemExit(1)
asyncio.run(main())
