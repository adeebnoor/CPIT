// Compatibility release gate: validate the explicitly approved classroom release.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const release = JSON.parse(read('curriculum/publication.json'));
assert.equal(release.automatic_generation, false, 'Automatic generation remains disabled');
assert.deepEqual(release.assignments.map(item => item.chapter), [10, 11, 12, 13, 14, 15, 16, 17, 20], 'All nine authorized chapters assignments are released');
assert.deepEqual(release.lectures.map(item => item.chapter), [10, 11, 12, 13, 14, 15, 16, 17, 20], 'All nine authorized chapters lectures are released');
assert.deepEqual(release.assignments.map(item => item.points), [4, 5, 5, 5, 5, 5, 5, 5, 5], 'Assignments preserve the intended progressive 4-point then 5-point structure');
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
for (const file of ['iscarb-hub.js', 'lectures/iscarb/runtime/classroom-v3.js']) {
  new Function(read(file));
  scripts++;
}
const gateway = read('fbr-submission.html');
for (const token of [
  'Ch10-FBR-Student-Assignment.html', 'fbr:access:ch10:v4',
  'Ch11-FBR-Student-Assignment.html', 'fbr:access:ch11:a2:v1'
]) assert(gateway.includes(token), `Gateway missing approved token: ${token}`);
for (const lectureSpec of release.lectures) {
  const lecture = read(lectureSpec.path);
  for (const id of ['prevBtn', 'nextBtn']) assert(lecture.includes(`id="${id}"`), `Chapter ${lectureSpec.chapter} navigation: ${id}`);
}
assert.equal(release.assignment_release, '20260925-ai-only-v3', 'AI-only assignment release must be active');
const rubrics = JSON.parse(read('curriculum/ai-assignment-rubrics.json'));
for (const item of release.assignments) {
  const html = read(item.path);
  assert(html.includes('data-assessment-edition="ai-v3"'), `Chapter ${item.chapter} must use AI-only v3`);
  assert(html.includes('How your AI assignment is assessed'), `Chapter ${item.chapter} must show the rubric before submission`);
  assert(html.includes('See a complete example before you start'), `Chapter ${item.chapter} must show a worked example`);
  assert(html.includes('22964248'), `Chapter ${item.chapter} must link the Zenodo research basis`);
  assert(html.includes('Download Blackboard JSON'), `Chapter ${item.chapter} must export the Blackboard JSON`);
  assert(rubrics.chapters[String(item.chapter)], `Chapter ${item.chapter} must have a machine-readable rubric`);
}
assert(read('.github/workflows/static.yml').includes('tools/build_public_site.py'));
console.log(`PASS: Nine AI-only assignments, ${scripts} valid scripts, visible examples/rubrics, Zenodo linkage, and Blackboard JSON export.`);