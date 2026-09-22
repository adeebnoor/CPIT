"""Browser-level student journey for Assignments 1 and 2.
Uses fake local-only student IDs; does not submit to an LMS and does not inspect hidden reveal files directly.
"""
import argparse, asyncio, json
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright
CASES={
10:{
 'title':'Dependable Systems: a decision you can defend','points':'4 points',
 'fields':{
  'fit':'Availability and integrity govern this decision because students must reach the service and confirmed registrations must remain correct.',
  'bound':'This plan remains acceptable only while confirmed registrations remain retrievable and no duplicate or lost records are observed.',
  'act':'Continue only bounded service under the duty engineer and ask the registrar to approve an alternative route if access worsens.',
  'evidence':'Use the current retrieval checks and request a peak-load failover test; the peak-load result is proposed and not yet measured.',
  'sourceUse':'Slide 26 — redundancy and diversity — supports the failover reasoning but does not remove shared causes.',
  'technical':'Shared power and a shared specification remain common causes; diversity can reduce shared failure but costs extra engineering.'
 }},
11:{
 'title':'Reliability Engineering','points':'5 points',
 'fields':{
  'fit':'Use a failure-rate metric for the authorization service because the decision concerns repeated transaction failures under a stated workload.',
  'measure':'Observed ROCOF = 4 failures / 2000 hours = 0.002 failures per hour; compare this with the stated target using the same event definition.',
  'bound':'This conclusion remains valid only for the stated service window and operational profile; reopen it when workload or failure definition changes.',
  'act':'Keep the release bounded while the service owner obtains representative profile evidence and recovery records for the deployed version.',
  'evidence':'Use dated failure logs and representative statistical-test results; any requested test remains proposed until it is actually executed.',
  'sourceUse':'Slide 19 — reliability metrics — supports choosing an exposure-based rate and requires the event and denominator to stay explicit.',
  'technical':'Two identical servers can reduce a single-machine outage but shared software requirements remain a common failure cause.'
 }}
}
async def check_assignment(browser,base,ch,out):
 cfg=CASES[ch]
 ctx=await browser.new_context(viewport={'width':1440,'height':900},accept_downloads=True)
 page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 await page.goto(urljoin(base,f'fbr-submission.html?chapter={ch}'),wait_until='networkidle')
 assert await page.locator('#sid').is_visible()
 await page.locator('#sid').fill(f'9900{ch}01')
 await page.locator('#ack').check()
 assert await page.locator('#openBtn').is_enabled()
 await page.locator('#openBtn').click()
 await page.wait_for_load_state('networkidle')
 assert f'Ch{ch}-FBR-Student-Assignment.html' in page.url
 body=await page.locator('body').inner_text()
 assert 'THIS WEEK · SUBMISSION CHECKLIST' in body
 assert 'No extra 20-rule forms are required' in body
 assert 'READ BEFORE ANSWERING' in body
 assert 'Units menu' not in body
 assert 'Commit is not LMS submission' in body
 assert cfg['points'] in body
 await page.locator('#requiredPreparation').screenshot(path=str(out/f'a{ch-9}-ch{ch}-preparation.png'))
 rubric=page.locator('#rubric-heading').locator('xpath=..')
 await rubric.screenshot(path=str(out/f'a{ch-9}-ch{ch}-rubric.png'))

 # Fill Part A and verify ordinary draft persistence before commitment.
 if await page.locator('#student').count(): await page.locator('#student').fill('QA Student')
 if await page.locator('#section').count(): await page.locator('#section').fill('QA')
 for field,value in cfg['fields'].items():
     await page.locator('#'+field).fill(value)
 await page.locator('#save').click()
 await page.wait_for_timeout(150)
 fit_before=await page.locator('#fit').input_value()
 await page.reload(wait_until='networkidle')
 assert await page.locator('#fit').input_value()==fit_before
 for field,value in cfg['fields'].items():
     assert await page.locator('#'+field).input_value()==value

 # Commit is local staging, not LMS submission. Accept only the explicit page confirmation.
 page.once('dialog',lambda d: asyncio.create_task(d.accept()))
 await page.locator('#lock').click()
 await page.locator('#partB .stress').wait_for(timeout=15000)
 assert await page.locator('#fit').is_editable()==False
 assert await page.locator('#lock').is_disabled()
 stress_text=await page.locator('#partB .stress').inner_text()
 assert len(stress_text)>50 and 'STRESS' in stress_text.upper()
 await page.locator('#partB .stress').screenshot(path=str(out/f'a{ch-9}-ch{ch}-stress.png'))

 # Complete the post-STRESS human-owned record.
 await page.locator('input[name="boundaryState"][value="CROSSED"]').check()
 await page.locator('input[name="refit"][value="REVISE"]').check()
 await page.locator('#refitwhy').fill('The new evidence crosses the original boundary, so the initial scope cannot be widened without a revised check and explicit owner review.')
 await page.locator('#revised').fill('Revise the operating decision, keep service bounded to the verified conditions, obtain the named evidence, and have the responsible owner and reviewer accept the remaining uncertainty.')
 await page.locator('#aiUse').fill('No AI used for this QA student-flow check.')
 await page.locator('#signer').fill('QA Student')
 await page.locator('#attested').check()
 await page.wait_for_timeout(150)
 assert await page.locator('#pdf').is_enabled()
 assert await page.locator('#download').is_enabled()
 async with page.expect_download() as pending:
     await page.locator('#download').click()
 download=await pending.value
 path=out/f'a{ch-9}-ch{ch}-final.md';await download.save_as(path)
 assert path.stat().st_size>500
 final_text=path.read_text()
 assert 'AI-use declaration' in final_text and 'Human review' in final_text and 'STRESS' in final_text

 # Mobile student view: no horizontal clipping in the key sections.
 await page.set_viewport_size({'width':390,'height':844})
 assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth+2')
 await page.locator('#rubric-heading').scroll_into_view_if_needed()
 await page.screenshot(path=str(out/f'a{ch-9}-ch{ch}-mobile.png'))
 assert not errors,errors
 await ctx.close()
 return {'chapter':ch,'entry':True,'draft_reload':True,'commit_lock':True,'stress_after_commit':True,'final_export_enabled':True,'mobile_no_horizontal_overflow':True,'errors':errors}

async def main(a):
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 base=a.base.rstrip('/')+'/'
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True)
  results=[]
  for ch in [10,11]:
   results.append(await check_assignment(browser,base,ch,out))
   print('PASS student flow Assignment',ch-9,'Chapter',ch,flush=True)
  await browser.close()
 report={'base':base,'assignments':results,'note':'Fake IDs and local browser storage only. No LMS submission was attempted; reveal files were not directly inspected.'}
 (out/'student-submission-proof.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--output',type=Path,default=Path('test-results/student-submit-v1'));asyncio.run(main(p.parse_args()))
