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
const assignment11 = read(release.assignments.find(item => item.chapter === 11).path);
assert(assignment11.includes('MEASURE · 1 POINT'), 'Assignment 2 must add exactly the MEASURE scored step');
assert(assignment11.includes('20,000'), 'Assignment 2 keeps the supplied measurement exercise');
assert(read('.github/workflows/static.yml').includes('tools/build_public_site.py'));
console.log(`PASS: Nine-chapter release catalog, ${scripts} valid scripts, standalone navigation, and progressive Assignment 2 gateway.`);