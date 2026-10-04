// Regenerate the annotated screenshots in assets/guide/ (served site on :8770; arg: folder holding pyodide/ for an offline Python).
// Usage: node tools/guide-screenshots.cjs <folder-with-pyodide>; then convert to WebP and run python3 tools/apply_visual_guide.py
// Annotated screenshots for the visual assignment guide. Numbers only; captions live in the page.
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs = require('fs'), path = require('path');
const OUT = '/home/user/CPIT/assets/guide/', PY = process.argv[2] + '/pyodide';
const W = 1100;
async function mark(pg, items) {
  await pg.addStyleTag({ content: '.site-header{display:none!important}' });
  await pg.evaluate(items => {
    document.querySelectorAll('.zz-mark').forEach(e => e.remove());
    for (const it of items) {
      let el = document.querySelector(it.sel); if (!el) throw Error('missing ' + it.sel); if (it.up) for (let k = 0; k < it.up; k++) el = el.parentElement;
      let r = el.getBoundingClientRect();
      if (it.text) { const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n, rg = null; while ((n = w.nextNode())) { const i = n.textContent.indexOf(it.text); if (i >= 0) { rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + it.text.length); break; } } if (!rg) throw Error('text ' + it.text); r = rg.getBoundingClientRect(); }
      const x = r.left + scrollX, y = r.top + scrollY;
      const box = document.createElement('div'); box.className = 'zz-mark';
      Object.assign(box.style, { position: 'absolute', left: (x - 4) + 'px', top: (y - 4) + 'px', width: (r.width + 8) + 'px', height: (r.height + 8) + 'px', border: '3px solid #e11d48', borderRadius: '10px', zIndex: 99998, pointerEvents: 'none' });
      const b = document.createElement('div'); b.className = 'zz-mark'; b.textContent = it.n;
      Object.assign(b.style, { position: 'absolute', left: (x - 18) + 'px', top: (y - 18) + 'px', width: '34px', height: '34px', borderRadius: '50%', background: '#e11d48', color: '#fff', font: '800 18px/34px Arial,sans-serif', textAlign: 'center', zIndex: 99999, boxShadow: '0 2px 6px rgba(0,0,0,.35)' });
      document.body.append(box, b);
    }
  }, items);
}
async function shot(pg, name, sels, pad = 30, maxH = 900) {
  await pg.addStyleTag({ content: '.site-header{display:none!important}' });
  const boxes = await pg.evaluate(sels => sels.map(s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left + scrollX, r.top + scrollY, r.right + scrollX, r.bottom + scrollY]; }), sels);
  const x0 = Math.max(0, Math.min(...boxes.map(b => b[0])) - pad), y0 = Math.max(0, Math.min(...boxes.map(b => b[1])) - pad);
  const x1 = Math.min(W, Math.max(...boxes.map(b => b[2])) + pad), y1 = Math.min(y0 + maxH, Math.max(...boxes.map(b => b[3])) + pad);
  await pg.evaluate(y => window.scrollTo(0, Math.max(0, y - 120)), y0);
  await pg.screenshot({ path: OUT + name + '.png', clip: { x: x0, y: y0, width: x1 - x0, height: y1 - y0 }, fullPage: true });
  console.log('wrote', name, Math.round(x1 - x0) + 'x' + Math.round(y1 - y0));
}
(async () => {
  const br = await chromium.launch(); const ctx = await br.newContext({ viewport: { width: W, height: 900 } });
  await ctx.addInitScript(() => { try { localStorage.setItem('iscarb-theme', 'light'); } catch (e) {} });
  await ctx.route('https://cdn.jsdelivr.net/pyodide/v0.26.4/full/**', r => { const f = path.join(PY, path.basename(new URL(r.request().url()).pathname)); r.fulfill({ status: 200, body: fs.readFileSync(f), headers: { 'content-type': f.endsWith('.wasm') ? 'application/wasm' : f.endsWith('.js') || f.endsWith('.mjs') ? 'text/javascript' : 'application/octet-stream', 'access-control-allow-origin': '*' } }); });
  const pg = await ctx.newPage(); pg.on('dialog', d => d.accept());
  // 1 · gateway
  await pg.goto('http://localhost:8770/fbr-submission.html?chapter=20', { waitUntil: 'networkidle' });
  await pg.locator('#sid').fill('2412345'); await pg.locator('#ack').check();
  await mark(pg, [{ sel: '#sid', n: 1 }, { sel: '#ack', n: 2, up: 1 }, { sel: '#openBtn', n: 3 }]);
  await pg.evaluate(() => { const b = document.getElementById('openBtn'); b.style.marginTop = '22px'; }); await mark(pg, [{ sel: '#sid', n: 1 }, { sel: '#ack', n: 2, up: 1 }, { sel: '#openBtn', n: 3 }]); await shot(pg, 'step-open', ['#sid', 'label:has(#ack)', '#openBtn'], 40);
  // 2 · assignment page, Part A
  await pg.addInitScript(() => sessionStorage.setItem('fbr:access:ch20:path:v1', JSON.stringify({ sid: '2412345', acknowledged: true })));
  await pg.goto('http://localhost:8770/lectures/iscarb/Ch20-FBR-Student-Assignment.html', { waitUntil: 'networkidle' });
  await mark(pg, [{ sel: '#scenarioText', n: 1 }, { sel: '#fit', n: 2 }]);
  await shot(pg, 'step-parta-1', ['#scenarioText', '#fit'], 30, 760);
  await mark(pg, [{ sel: '#measure', n: 3 }, { sel: '#bound', n: 4 }, { sel: '#act', n: 5 }, { sel: '#evidence', n: 6 }]);
  await shot(pg, 'step-parta-2', ['#measure', '#evidence'], 30, 1100);
  // 3 · build
  await pg.locator('#labPrediction').fill('My plan: what my code will do, then my tests: a normal case, an edge case, and a case that must be refused or fail safely.');
  await mark(pg, [{ sel: '#labPrediction', n: 1 }, { sel: '#labCases', n: 2 }, { sel: '#buildRun', n: 3 }]);
  await shot(pg, 'step-build', ['#labPrediction', '#buildRun'], 30, 1000);
  // fill Part A with neutral text, run the starter so a record exists, commit
  for (const id of ['fit', 'measure', 'bound', 'act', 'evidence', 'technical']) await pg.locator('#' + id).fill('Your own answer for this part goes here: specific to the case, checkable, and within the word budget.');
  await pg.locator('#sourceUse').fill('Slide 15 · the concept from the assigned reading · how it supports my artifact.');
  await pg.locator('#buildRun').click(); await pg.waitForFunction(() => /^BUILD RECORD/.test(document.getElementById('labEvidence').value), null, { timeout: 150000 });
  await mark(pg, [{ sel: '#lock', n: 1 }]);
  await shot(pg, 'step-commit', ['#lock', '#clear'], 40);
  await pg.evaluate(() => document.querySelectorAll('.zz-mark').forEach(e => e.remove()));
  await pg.locator('#lock').click(); await pg.waitForTimeout(800); console.log('MSG', await pg.locator('#msg').innerText().catch(()=>''), '|', await pg.evaluate(()=>document.querySelector('[role=alert],.error')?.innerText||'')); await pg.waitForSelector('#lmsStress');
  await pg.locator('#lmsText').fill('Paste the WHOLE “New evidence” item from Blackboard here.');
  await mark(pg, [{ sel: '#lmsPartA', n: 1 }, { sel: '#lmsText', n: 2 }, { sel: '#lmsCheck', n: 3 }]);
  await shot(pg, 'step-stress', ['#lmsStress'], 20, 900);
  // Part B via the unverified path, then hide anything specific
  await pg.evaluate(() => document.querySelectorAll('.zz-mark').forEach(e => e.remove()));
  await pg.locator('#lmsCheck').click(); await pg.locator('#lmsCheck').click(); await pg.waitForSelector('input[name="boundaryState"]');
  await pg.evaluate(() => { const b = document.getElementById('partB'); b.querySelectorAll('*').forEach(e => { if (e.children.length === 0 && /UNVERIFIED|Paste the WHOLE/.test(e.textContent)) e.textContent = 'The new evidence from Blackboard appears here.'; }); });
  await pg.locator('input[name="boundaryState"][value="PRESSURED"]').check(); await pg.locator('input[name="refit"][value="REVISE"]').check();
  await mark(pg, [{ sel: 'input[name="boundaryState"][value="INTACT"]', n: 1, up: 2 }, { sel: 'input[name="refit"][value="RETAIN"]', n: 2, up: 2 }, { sel: '#refitwhy', n: 3 }, { sel: '#revised', n: 4 }]);
  await shot(pg, 'step-refit', ['input[name="boundaryState"][value="INTACT"]', '#revised'], 40, 1000);
  await mark(pg, [{ sel: '#aiUse', n: 1 }, { sel: '#signer', n: 2 }, { sel: '#attested', n: 3, up: 1 }]);
  await shot(pg, 'step-submit', ['#aiUse', '#attested'], 40, 600);
  await mark(pg, [{ sel: '#pdf', n: 4 }]);
  await shot(pg, 'step-pdf', ['#pdf', '#copy'], 40, 300);
  // build record, from the not-assessed practice build
  const px = await ctx.newPage();
  await px.goto('http://localhost:8770/assignment-example.html', { waitUntil: 'networkidle' });
  await px.locator('#sid').fill('2412345');
  await px.locator('#labPrediction').fill('My plan: refuse unless the item is available, the limit is not reached and nothing is overdue.');
  const sol = await px.evaluate(() => document.getElementById('exampleSolution').textContent);
  await px.locator('#labCases').fill(sol.replace('def test_overdue_student_is_refused', 'def _left_out'));
  await px.locator('#buildRun').click(); await px.waitForFunction(() => /^BUILD RECORD/.test(document.getElementById('labEvidence').value), null, { timeout: 150000 });
  await mark(px, [{ sel: '#buildOutput', text: 'Micro-viva change request', n: 1 }, { sel: '#buildOutput', text: 'Your tests:\n', n: 2 }, { sel: '#buildOutput', text: 'Course checks:\n', n: 3 }, { sel: '#buildOutput', text: 'an overdue item is ignored · not caught', n: 4 }]);
  await shot(px, 'step-record', ['#buildOutput'], 34, 900);
  await br.close();
})();
