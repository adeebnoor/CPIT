"""Browser-level student journey for all nine AI-only assignments.
Uses fake local-only student IDs. It does not submit to Blackboard or inspect hidden
STRESS payloads directly; STRESS must arrive through the normal commit/reveal flow.
"""
import argparse, asyncio, json
from pathlib import Path
from urllib.parse import urljoin
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
PUB=json.loads((ROOT/"curriculum/publication.json").read_text(encoding="utf-8"))
ASSIGN={x["chapter"]:x for x in PUB["assignments"]}
CHAPTERS=[10,11,12,13,14,15,16,17,20]

def qa_fields(ch):
    page=ASSIGN[ch]["reading_pages"][0]
    return {
      "fit":"The AI-specific engineering claim is bounded by the chapter mechanism, the supplied scenario facts, and an accountable human decision.",
      "measure":"This AI engineering artifact makes the mechanism inspectable, states assumptions explicitly, and separates supplied facts from proposed checks.",
      "bound":"The claim applies only to the stated model/version and operating conditions; a material profile, dependency, interface, or evidence change reopens it.",
      "act":"Use a bounded action under a named service owner and reviewer; do not widen deployment until the stated evidence is inspected.",
      "evidence":"Supplied and derived evidence is identified here. Any additional test remains proposed until it is executed on the named version and conditions.",
      "sourceUse":f"Slide {page}: the assigned source concept constrains this AI-system claim by making its mechanism, assumptions, and evidence boundary explicit.",
      "technical":"The AI-specific failure or assumption can remain even when ordinary software/API checks pass; an independent engineering control and inspectable evidence are required."
    }

async def check_assignment(browser,base,ch,out):
    a=ASSIGN[ch]; sid=f"9900{ch}01"; number=CHAPTERS.index(ch)+1
    ctx=await browser.new_context(viewport={"width":1440,"height":900},accept_downloads=True)
    page=await ctx.new_page(); errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    await page.goto(urljoin(base,f"fbr-submission.html?chapter={ch}"),wait_until="networkidle")
    await page.locator("#sid").fill(sid); await page.locator("#ack").check()
    assert await page.locator("#openBtn").is_enabled()
    await page.locator("#openBtn").click(); await page.wait_for_load_state("networkidle")
    assert f"Ch{ch}-FBR-Student-Assignment.html" in page.url
    body=await page.locator("body").inner_text()
    for phrase in ["AI-ONLY","How your AI assignment is assessed","See a complete example before you start","Blackboard JSON"]:
        assert phrase.lower() in body.lower(),(ch,phrase)
    assert "22964248" in await page.content()
    assert f"{a['points']} points" in body
    await page.locator("#requiredPreparation").screenshot(path=str(out/f"a{number}-ch{ch}-preparation.png"))
    await page.locator("#rubric-heading").locator("xpath=..").screenshot(path=str(out/f"a{number}-ch{ch}-rubric.png"))

    if await page.locator("#student").count(): await page.locator("#student").fill("QA Student")
    if await page.locator("#section").count(): await page.locator("#section").fill("QA")
    values=qa_fields(ch)
    for field,value in values.items():
        loc=page.locator("#"+field)
        if await loc.count() and await loc.is_editable(): await loc.fill(value)
    await page.locator("#save").click(); await page.wait_for_timeout(120)
    fit_before=await page.locator("#fit").input_value()
    await page.reload(wait_until="networkidle")
    assert await page.locator("#fit").input_value()==fit_before

    for field,value in values.items():
        loc=page.locator("#"+field)
        if await loc.count() and await loc.is_editable():
            assert await loc.input_value()==value,(ch,field)

    page.once("dialog",lambda d: asyncio.create_task(d.accept()))
    await page.locator("#lock").click()
    await page.locator("#partB .stress").wait_for(timeout=15000)
    assert not await page.locator("#fit").is_editable()
    assert await page.locator("#lock").is_disabled()
    stress_text=await page.locator("#partB .stress").inner_text()
    assert len(stress_text)>50 and "STRESS" in stress_text.upper()

    await page.locator('input[name="boundaryState"][value="CROSSED"]').check()
    await page.locator('input[name="refit"][value="REVISE"]').check()
    await page.locator("#refitwhy").fill("The new AI evidence crosses or materially weakens the original boundary, so the initial claim must be revised before the system is widened.")
    await page.locator("#revised").fill("Keep the AI-enabled action bounded to the verified conditions, obtain the named inspectable evidence on the stated version, and require the responsible owner and reviewer to approve any wider use.")
    await page.locator("#aiUse").fill("AI used only to proofread this QA response; the engineering claim and any calculation were checked against the supplied scenario and chapter source.")
    await page.locator("#signer").fill("QA Student")
    await page.locator("#attested").check()
    await page.wait_for_timeout(180)
    assert await page.locator("#json").is_enabled(),ch

    async with page.expect_download() as pending:
        await page.locator("#json").click()
    download=await pending.value
    jp=out/f"a{number}-ch{ch}-blackboard.json"
    await download.save_as(jp)
    sub=json.loads(jp.read_text(encoding="utf-8"))
    assert sub["schema"]=="cpit455-ai-v3"
    assert int(sub["chapter"])==ch
    assert sub["student"]["id"]==sid
    assert sub["humanReview"]["attested"] is True
    assert sub["paper"]["url"].endswith("/22964248")
    assert sub["commit"]["id"] and sub["stress"]
    assert sub["partA"]["fit"]==fit_before

    await page.set_viewport_size({"width":390,"height":844})
    assert await page.evaluate("document.documentElement.scrollWidth<=innerWidth+2")
    await page.locator("#rubric-heading").scroll_into_view_if_needed()
    await page.screenshot(path=str(out/f"a{number}-ch{ch}-mobile.png"))
    assert not errors,errors
    await ctx.close()
    return {"chapter":ch,"assignment":number,"entry":True,"draft_reload":True,
            "commit_lock":True,"stress_after_commit":True,"json_export":True,
            "mobile_no_horizontal_overflow":True,"errors":errors}

async def main(a):
    out=a.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    base=a.base.rstrip("/")+"/"
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        results=[]
        for ch in CHAPTERS:
            results.append(await check_assignment(browser,base,ch,out))
            print("PASS AI-only student flow Assignment",CHAPTERS.index(ch)+1,"Chapter",ch,flush=True)
        await browser.close()
    report={"base":base,"release":PUB.get("assignment_release"),"assignments":results,
            "note":"Fake IDs and local browser storage only. No Blackboard submission was attempted; STRESS was reached only through commit/reveal."}
    (out/"student-submission-proof.json").write_text(json.dumps(report,indent=2),encoding="utf-8")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base",required=True)
    p.add_argument("--output",type=Path,default=Path("test-results/student-submit-v1"))
    asyncio.run(main(p.parse_args()))
