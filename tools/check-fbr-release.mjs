// Compatibility release gate: only explicitly approved Chapter 10 is published.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const release = JSON.parse(read('curriculum/publication.json'));
assert.equal(release.automatic_generation, false, 'Automatic generation remains disabled');
assert.deepEqual(release.assignments, [], 'No assignment is released');
assert.deepEqual(release.lectures.map(item => item.chapter), [10], 'Only Chapter 10 is released');
const pages = [...release.iscarb_public_files.filter(file => file.endsWith('.html')),
  'iscarb.html', 'download.html', 'fbr-submission.html', 'student-guide.html', 'course-resources.html'];
let scripts = 0;
for (const file of pages) {
  const html = read(file);
  for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
    if (/\btype\s*=\s*["'](?:application\/ld\+json|application\/json)["']/i.test(match[1])) continue;
    if (!match[2].trim()) continue;
    new Function(match[2]);
    scripts++;
  }
}
for (const file of ['iscarb-hub.js']) {
  new Function(read(file));
  scripts++;
}
const gateway = read('fbr-submission.html');
assert(!/Ch\d+-FBR-Student-Assignment\.html/i.test(gateway), 'Withdrawn gateway cannot open an assignment');
const lecture = read(release.lectures[0].path);
for (const id of ['prevBtn', 'nextBtn']) assert(lecture.includes(`id="${id}"`), `Lecture navigation: ${id}`);
assert(read('.github/workflows/static.yml').includes('tools/build_public_site.py'));
console.log(`PASS: release catalog, ${scripts} valid scripts, standalone navigation, no active assignment gateway.`);
