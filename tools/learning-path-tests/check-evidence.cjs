// Verify the statistics on evidence.html against reference values computed independently with SciPy.
// Uses synthetic fixtures only (evidence-fixtures/, not student data).
// Usage: COURSE_BASE_URL=http://localhost:8770/ node tools/learning-path-tests/check-evidence.cjs
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs = require('fs'), path = require('path');
const F = path.join(__dirname, 'evidence-fixtures'), BASE = process.env.COURSE_BASE_URL || 'http://localhost:8770/';
let failed = 0; const ok = (n, c, x) => { console.log((c ? 'PASS ' : 'FAIL ') + n + (c || !x ? '' : ' · ' + x)); if (!c) failed++; };
(async () => {
  const br = await chromium.launch(); const ctx = await br.newContext({ acceptDownloads: true, viewport: { width: 1366, height: 900 } });
  const pg = await ctx.newPage(); const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto(BASE + 'evidence.html', { waitUntil: 'networkidle' });
  await pg.setInputFiles('#preFile', F + '/pre.csv'); await pg.setInputFiles('#postFile', F + '/post.csv'); await pg.waitForTimeout(800);
  const g = await pg.locator('#gainOut').innerText();
  ok('concept gain: 28 matched, 1 pre-only, 2 post-only', /28 \(pre only 1, post only 2\)/.test(g), g);
  ok('concept gain: <g> = 0.29 (SciPy 0.294)', /⟨g⟩\s*0\.29/.test(g));
  ok('concept gain: paired t(27) = 4.84, p < .001 (SciPy 4.842, 4.7e-5)', /t\(27\) = 4\.84, p < \.001/.test(g));
  ok('concept gain: mean change 16% [9%, 23%] (SciPy 0.161 [0.093, 0.229])', /16% \[9%, 23%\]/.test(g));
  ok('concept gain: d_z 0.92, Hedges g_av 0.79 (SciPy 0.915, 0.794)', /dz\s*0\.92/.test(g) && /gav\s*0\.79/.test(g));
  const md = fs.readdirSync(F).filter(f => f.endsWith('.md') && f !== 'README.md').map(f => F + '/' + f);
  await pg.setInputFiles('#buildFiles', md); await pg.waitForFunction(() => !/Reading/.test(document.getElementById('buildOut').innerText));
  const b = await pg.locator('#buildOut').innerText();
  ok('build: bugs caught A4 55%, A5 70%, A9 65%', /A4\t10\t70%\t3\.00\t55%/.test(b) && /A5\t10\t90%\t3\.00\t70%/.test(b) && /A9\t10\t100%\t3\.00\t65%/.test(b), b);
  await pg.setInputFiles('#gradeFile', F + '/grades.csv'); await pg.waitForTimeout(500);
  const gr = await pg.locator('#gradeOut').innerText();
  ok('grades: a "Needs Grading" cell is skipped (A5 N = 29)', /A5\t29\t/.test(gr), gr);
  ok('grades: within-course t(29) = 3.57, d_z = 0.65 (SciPy 3.571, 0.652)', /t\(29\) = 3\.57, p = \.001, dz = 0\.65/.test(gr), gr);
  ok('grades: r with final = 0.80 [0.62, 0.90] (SciPy 0.803 [0.623, 0.902])', /Final: r = 0\.80 \[0\.62, 0\.90\]/.test(gr), gr);
  await pg.setInputFiles('#surveyFile', F + '/survey.csv'); await pg.waitForTimeout(500);
  const sv = await pg.locator('#surveyOut').innerText();
  ok('survey: Engagement M 3.28, SD 1.15, α 0.90 (SciPy 3.280, 1.145, 0.903)', /Engagement\t3\t25\t3\.28\t1\.15\t0\.90/.test(sv), sv);
  ok('survey: “Neither agree nor disagree” is read as 3, not 2', /Clarity\t3\t25\t3\.44/.test(sv), sv);
  await pg.fill('#salt', 'fixture phrase'); await pg.setInputFiles('#consentFile', F + '/consent.csv');
  const [dl] = await Promise.all([pg.waitForEvent('download'), pg.click('#datasetBtn')]); const csv = fs.readFileSync(await dl.path(), 'utf8');
  ok('dataset: only the 20 consenting students are written', csv.trim().split('\n').length === 21);
  ok('dataset: no raw Student ID appears', !/\b2410\d\d\b/.test(csv));
  const [dl2] = await Promise.all([pg.waitForEvent('download'), pg.click('#datasetBtn')]);
  ok('dataset: the same phrase gives the same codes', fs.readFileSync(await dl2.path(), 'utf8') === csv);
  ok('summary has a results paragraph', /Results paragraph/.test(await pg.locator('#summary').inputValue()));
  ok('no page errors', !errs.length, errs.join(' | '));
  await br.close(); console.log(failed ? failed + ' FAILED' : 'ALL PASS'); process.exit(failed ? 1 : 0);
})();
