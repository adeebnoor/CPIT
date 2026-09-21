"""Test the student download path, then the extracted files without networking.
Run against an HTTP staging origin or the public course. No analytics endpoint,
student account, LMS submission or real student draft is used.
"""
from __future__ import annotations
import asyncio, hashlib, json, os, re, tempfile, zipfile
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('COURSE_BASE_URL', 'https://adeebnoor.github.io/CPIT/').rstrip('/') + '/'
OUT = ROOT / 'test-results' / 'offline-downloads'
PUB = json.loads((ROOT / 'curriculum/publication.json').read_text(encoding='utf-8'))
CHAPTERS = [10, 11, 12, 13, 14, 15, 16, 17, 20]

async def loaded_images(page):
    await page.locator('img').evaluate_all('''async imgs => {
      imgs.forEach(i => { i.loading = 'eager'; });
      await Promise.all(imgs.map(i => i.decode().catch(() => {})));
    }''')
    broken = await page.locator('img').evaluate_all('(imgs)=>imgs.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)')
    assert not broken, 'Missing offline images: ' + repr(broken)

async def offline_check(browser, archive, chapter, folder):
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), 'Duplicate archive entries'
        assert z.testzip() is None, 'ZIP CRC failure'
        assert 'START-HERE.html' in names, 'Missing obvious entry file'
        assert sum(i.file_size for i in z.infolist()) < 200_000_000
        for info in z.infolist():
            assert not info.filename.startswith(('/', '\\'))
            assert (folder / info.filename).resolve().is_relative_to(folder.resolve())
            assert ((info.external_attr >> 16) & 0o170000) != 0o120000, 'Archive symlink'
        z.extractall(folder)
    context = await browser.new_context(offline=True, viewport={'width':1440,'height':900})
    page = await context.new_page()
    errors, failed, remote = [], [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('requestfailed', lambda r: failed.append({'url':r.url,'error':r.failure}))
    page.on('request', lambda r: remote.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    await page.goto((folder / 'START-HERE.html').as_uri(), wait_until='load')
    await page.wait_for_function('!!window.iscarb', timeout=15000)
    data = await page.evaluate('iscarb.data')
    assert data['chapter'] == chapter and len(data['slides']) == 20
    assert len(data['rules']) == 20 and len(data['objectives']) == 5
    assert urlsplit(page.url).scheme == 'file', 'Offline test must not use an HTTP server'
    assert await page.locator('#chapter-main').inner_text()
    assert await page.locator('#app').evaluate('e=>getComputedStyle(e).display') != 'inline', 'Missing CSS'
    for i, slide in enumerate(data['slides']):
        await page.evaluate('(i)=>iscarb.go(i)', i)
        await loaded_images(page)
        assert await page.locator('#chapter-main h1').inner_text()
        if await page.locator('[data-full]').count():
            await page.locator('[data-full]').click()
            assert await page.locator('#modal-body').inner_text()
            await page.locator('#modal-close').click()
            await page.locator('[data-answer]').click()
            assert await page.locator('#modal-body').inner_text()
            await page.locator('#modal-close').click()
    for station in data['stations']:
        await page.evaluate('(n)=>iscarb.startStation(n)', station['no'])
        await page.locator('#hintBtn').click()
        assert 'Authored hint' in await page.locator('#coach').inner_text()
        assert await page.locator('#timer-start').is_visible()
        if station['no'] == 1:
            await page.locator('#timer-start').click()
            await page.wait_for_timeout(1200)
            await page.locator('#timer-reset').click()
        await page.locator('#station-back').click()
    await page.evaluate("iscarb.open('CARD')")
    await page.locator('[data-field="claim"]').fill('OFFLINE_QA_CH' + str(chapter))
    async with page.expect_download() as item:
        await page.locator('[data-export="json"]').click()
    backup = folder / 'qa-card.json'
    await (await item.value).save_as(backup)
    record = json.loads(backup.read_text())
    assert record['state']['fields']['claim'] == 'OFFLINE_QA_CH' + str(chapter)
    await page.reload(wait_until='load')
    await page.wait_for_function('!!window.iscarb')
    assert await page.evaluate('iscarb.getState().fields.claim') == 'OFFLINE_QA_CH' + str(chapter)
    await page.evaluate("iscarb.open('QUIZ')")
    for i, question in enumerate(data['quiz']):
        await page.locator('[data-quiz="'+str(i)+'"]').first.click()
        await page.locator('input[name="quiz"][value="'+str(question['answer'])+'"]').check()
        await page.locator('#quiz-check').click()
        assert 'Correct for this case.' in await page.locator('#quiz-feedback').inner_text()
    await page.locator('#modal-close').click()
    await page.evaluate('iscarb.go(3)')
    await page.screenshot(path=str(OUT / f'ch{chapter}-offline-desktop.png'))
    await page.set_viewport_size({'width':390,'height':844})
    await loaded_images(page)
    assert await page.locator('#nextBtn').is_visible()
    await page.screenshot(path=str(OUT / f'ch{chapter}-offline-mobile.png'), full_page=True)
    source = folder / f'lectures/iscarb/sources/Ch{chapter}-Study.html'
    await page.goto(source.as_uri(), wait_until='load')
    assert await page.locator('#source-slide-1').count() == 1
    await loaded_images(page)
    for resource in [data.get('original'), data.get('textbook')]:
        if resource:
            assert (folder / 'lectures/iscarb' / resource).is_file(), resource
    assert not errors, errors
    assert not failed, failed
    assert not remote, 'Offline work attempted network access: ' + repr(remote)
    await context.close()
    return {'chapter':chapter,'slides':20,'quiz_items':5,'stations':3,'file_origin':True,
            'network_disabled':True,'remote_requests':remote,'errors':errors,'failed_requests':failed,
            'source_review':True,'figures':True,'card_export_and_reload':True}

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {'base':BASE,'scope':'Download links and offline classroom/source review; assessed assignments and Blackboard require internet.', 'chapters':[]}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            online = await browser.new_context(accept_downloads=True)
            page = await online.new_page()
            response = await page.goto(urljoin(BASE,'iscarb.html')+'?offline-test='+PUB['release'], wait_until='networkidle')
            assert response and response.status == 200
            for chapter in CHAPTERS:
                link = page.locator(f'#chapter-{chapter} a[download]').filter(has_text='Offline ZIP')
                assert await link.count() == 1, f'CH{chapter}: expected one download link'
                target = f'lectures/iscarb/packages/Ch{chapter}-iSCARB.zip'
                assert urlsplit(await link.get_attribute('href')).path == target, f'CH{chapter}: ZIP label points to wrong resource'
                with tempfile.TemporaryDirectory(prefix=f'iscarb-ch{chapter}-') as tmp:
                    folder = Path(tmp)
                    async with page.expect_download(timeout=60000) as pending:
                        await link.click()
                    download = await pending.value
                    assert download.suggested_filename == f'Ch{chapter}-iSCARB.zip', download.suggested_filename
                    archive = folder / 'download.zip'
                    await download.save_as(archive)
                    assert archive.read_bytes().startswith(b'PK\x03\x04'), 'Downloaded HTML instead of ZIP'
                    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
                    assert digest == PUB['delivery_asset_sha256'][target], 'Published archive hash mismatch'
                    result = await offline_check(browser, archive, chapter, folder / 'extracted')
                    result.update({'download_filename':download.suggested_filename,'archive_bytes':archive.stat().st_size,'sha256':digest})
                    report['chapters'].append(result)
                    print('PASS',json.dumps(result),flush=True)
            await online.close()
            await browser.close()
        report['result'] = 'PASS'
    except Exception as e:
        report['result'] = 'FAIL'; report['error'] = str(e)
        raise
    finally:
        (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__ == '__main__':
    asyncio.run(main())
