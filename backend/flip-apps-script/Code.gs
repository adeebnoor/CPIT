/**
 * CPIT-455 flipped lectures: seat booking backend (Google Apps Script bound to a private Google Sheet).
 *
 * Rules enforced here, on the server:
 *  - Booking and cancelling run under one script lock, so two students pressing the same seat at the same moment
 *    cannot both succeed; the second is told the seat was just booked.
 *  - The student ID and university email must match the roster. One seat per student.
 *  - Booking and cancelling close 72 hours before the lecture, by Google's server clock.
 *  - The public endpoint returns only which seats are booked or closed: never a name, ID or email.
 *  - The cancellation code is stored only as a salted SHA-256 hash and is shown to the student once.
 *  - The admin page and admin functions require the signed-in instructor's Google account.
 * No student data is in this file. The roster is kept in the private Sheet only.
 */
var ADMIN_EMAILS = ['arnoor@kau.edu.sa', 'adeeb.noor@gmail.com'];
var CLOSE_HOURS = 72, DRAFT_HOURS = 48;
var COLS = {
  lectures: ['id', 'number', 'chapter', 'title_en', 'title_ar', 'assignment_en', 'assignment_ar', 'starts_at'],
  seats: ['id', 'lecture_id', 'part_no', 'title_en', 'title_ar', 'slides'],
  roster: ['student_id', 'full_name', 'email'],
  bookings: ['seat_id', 'student_id', 'entered_name', 'cancel_salt', 'cancel_code_hash', 'cancel_attempts', 'created_at',
             'accuracy', 'understanding', 'quiz', 'commitment']
};
var LECTURES = [
 {
  "id": 1,
  "number": 1,
  "chapter": "Ch15",
  "title_en": "Software Reuse",
  "title_ar": "إعادة استخدام البرمجيات",
  "assignment_en": "Assignment 6",
  "assignment_ar": "الواجب 6",
  "starts_at": "2026-10-29T15:00:00+03:00",
  "seats": [
   {
    "id": 11,
    "part_no": 1,
    "title_en": "Seat 1",
    "title_ar": "المقعد 1",
    "slides": ""
   },
   {
    "id": 12,
    "part_no": 2,
    "title_en": "Seat 2",
    "title_ar": "المقعد 2",
    "slides": ""
   },
   {
    "id": 13,
    "part_no": 3,
    "title_en": "Seat 3",
    "title_ar": "المقعد 3",
    "slides": ""
   }
  ]
 },
 {
  "id": 2,
  "number": 2,
  "chapter": "Ch16",
  "title_en": "Component-based Software Engineering",
  "title_ar": "هندسة البرمجيات القائمة على المكونات",
  "assignment_en": "Assignment 7",
  "assignment_ar": "الواجب 7",
  "starts_at": "2026-11-05T15:00:00+03:00",
  "seats": [
   {
    "id": 21,
    "part_no": 1,
    "title_en": "Seat 1",
    "title_ar": "المقعد 1",
    "slides": ""
   },
   {
    "id": 22,
    "part_no": 2,
    "title_en": "Seat 2",
    "title_ar": "المقعد 2",
    "slides": ""
   },
   {
    "id": 23,
    "part_no": 3,
    "title_en": "Seat 3",
    "title_ar": "المقعد 3",
    "slides": ""
   }
  ]
 },
 {
  "id": 3,
  "number": 3,
  "chapter": "Ch17",
  "title_en": "Distributed Software Engineering",
  "title_ar": "هندسة البرمجيات الموزعة",
  "assignment_en": "Assignment 8",
  "assignment_ar": "الواجب 8",
  "starts_at": "2026-11-12T15:00:00+03:00",
  "seats": [
   {
    "id": 31,
    "part_no": 1,
    "title_en": "Seat 1",
    "title_ar": "المقعد 1",
    "slides": ""
   },
   {
    "id": 32,
    "part_no": 2,
    "title_en": "Seat 2",
    "title_ar": "المقعد 2",
    "slides": ""
   },
   {
    "id": 33,
    "part_no": 3,
    "title_en": "Seat 3",
    "title_ar": "المقعد 3",
    "slides": ""
   }
  ]
 },
 {
  "id": 4,
  "number": 4,
  "chapter": "Ch20",
  "title_en": "Systems of Systems",
  "title_ar": "أنظمة الأنظمة",
  "assignment_en": "Assignment 9",
  "assignment_ar": "الواجب 9",
  "starts_at": "2026-11-19T15:00:00+03:00",
  "seats": [
   {
    "id": 41,
    "part_no": 1,
    "title_en": "Seat 1",
    "title_ar": "المقعد 1",
    "slides": ""
   },
   {
    "id": 42,
    "part_no": 2,
    "title_en": "Seat 2",
    "title_ar": "المقعد 2",
    "slides": ""
   },
   {
    "id": 43,
    "part_no": 3,
    "title_en": "Seat 3",
    "title_ar": "المقعد 3",
    "slides": ""
   }
  ]
 },
 {
  "id": 5,
  "number": 5,
  "chapter": "Testing",
  "title_en": "Test cases and code coverage",
  "title_ar": "حالات الاختبار وتغطية الشيفرة",
  "assignment_en": "Coverage step, Assignments 3–9",
  "assignment_ar": "خطوة التغطية في الواجبات 3–9",
  "starts_at": "2026-11-26T15:00:00+03:00",
  "seats": [
   {
    "id": 51,
    "part_no": 1,
    "title_en": "Seat 1",
    "title_ar": "المقعد 1",
    "slides": ""
   },
   {
    "id": 52,
    "part_no": 2,
    "title_en": "Seat 2",
    "title_ar": "المقعد 2",
    "slides": ""
   },
   {
    "id": 53,
    "part_no": 3,
    "title_en": "Seat 3",
    "title_ar": "المقعد 3",
    "slides": ""
   }
  ]
 }
];

// ---- Setup (run once from the editor) --------------------------------------------------------------------------
function setup() {
  var ss = SpreadsheetApp.getActive();
  if (!ss.getSheetByName('roster')) {  // the roster was uploaded as the first tab
    var first = ss.getSheets()[0], h = first.getRange(1, 1, 1, 3).getDisplayValues()[0].join();
    if (h === COLS.roster.join()) first.setName('roster');
  }
  Object.keys(COLS).forEach(function (name) {
    var sh = ss.getSheetByName(name) || ss.insertSheet(name);
    var head = sh.getRange(1, 1, 1, COLS[name].length);
    if (sh.getLastRow() === 0 || head.getValues()[0].join() !== COLS[name].join()) {
      if (name === 'roster' && sh.getLastRow() > 0) { /* keep an uploaded roster; just check the header */ }
      else { sh.getRange(1, 1, 1, COLS[name].length).setValues([COLS[name]]); }
    }
    if (name !== 'roster') sh.getRange('A:Z').setNumberFormat('@');  // text: dates stay ISO
    sh.setFrozenRows(1);
  });
  writeTable_('lectures', LECTURES.map(function (l) { return COLS.lectures.map(function (k) { return String(l[k]); }); }));
  var seats = [];
  LECTURES.forEach(function (l) { l.seats.forEach(function (s) { seats.push([s.id, l.id, s.part_no, s.title_en, s.title_ar, s.slides].map(String)); }); });
  writeTable_('seats', seats);
  return 'Setup done: ' + LECTURES.length + ' lectures, ' + seats.length + ' seats, ' + (table_('roster').length) + ' students in the roster.';
}

// ---- Public endpoint (deployment: Execute as me, Who has access: Anyone) ----------------------------------------
function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.view === 'admin') return adminPage_();
  if (p.action === 'status') return json_(status_());
  return json_({ ok: false, error: 'bad_request' });
}

function doPost(e) {
  var b = {};
  try { b = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { return json_({ ok: false, error: 'bad_request' }); }
  if (b.action === 'book') return json_(locked_(function () { return book_(b); }));
  if (b.action === 'cancel') return json_(locked_(function () { return cancel_(b); }));
  if (b.action === 'status') return json_(status_());
  return json_({ ok: false, error: 'bad_request' });
}

function status_() {
  var now = Date.now(), lec = byId_(table_('lectures')), booked = {};
  table_('bookings').forEach(function (b) { booked[b.seat_id] = true; });
  return table_('seats').map(function (s) {
    var l = lec[s.lecture_id];
    return { seat_id: +s.id, booked: !!booked[s.id], closed: !l || now >= Date.parse(l.starts_at) - CLOSE_HOURS * 3600000 };
  });
}

function book_(b) {
  var sid = String(b.student_id || '').trim(), mail = String(b.email || '').trim().toLowerCase(), seatId = String(b.seat_id || '');
  if (!/^[0-9]{7}$/.test(sid) || !table_('roster').some(function (r) { return r.student_id === sid && String(r.email).toLowerCase() === mail; }))
    return { ok: false, error: 'not_in_roster' };
  var seat = table_('seats').filter(function (s) { return s.id === seatId; })[0];
  if (!seat) return { ok: false, error: 'no_seat' };
  var lec = byId_(table_('lectures'))[seat.lecture_id];
  var starts = Date.parse(lec.starts_at);
  if (Date.now() >= starts - CLOSE_HOURS * 3600000) return { ok: false, error: 'closed' };
  var bookings = table_('bookings');
  // The page creates the code and sends it again if a reply is lost; the same request then confirms the same booking.
  var code = /^[A-HJ-NP-Z2-9]{6}$/.test(String(b.code || '').toUpperCase()) ? String(b.code).toUpperCase() : newCode_();
  var mine = bookings.filter(function (x) { return x.student_id === sid; })[0];
  if (mine && mine.seat_id === seatId && hash_(mine.cancel_salt, code) === mine.cancel_code_hash)
    return confirmation_(code, lec, seat, starts);
  if (mine) return { ok: false, error: 'already' };
  if (bookings.some(function (x) { return x.seat_id === seatId; })) return { ok: false, error: 'taken' };
  var salt = Utilities.getUuid();
  appendRow_('bookings', { seat_id: seatId, student_id: sid, entered_name: String(b.full_name || '').trim().slice(0, 120),
    cancel_salt: salt, cancel_code_hash: hash_(salt, code), cancel_attempts: '0', created_at: new Date().toISOString() });
  return confirmation_(code, lec, seat, starts);
}

function confirmation_(code, lec, seat, starts) {
  return { ok: true, code: code, lecture: +lec.number, chapter: lec.chapter, part: +seat.part_no, title_en: seat.title_en,
           title_ar: seat.title_ar, slides: seat.slides, starts_at: lec.starts_at,
           draft_due: new Date(starts - DRAFT_HOURS * 3600000).toISOString() };
}

function cancel_(b) {
  var sid = String(b.student_id || '').trim(), code = String(b.code || '').trim().toUpperCase();
  var sh = sheet_('bookings'), rows = table_('bookings'), i = -1;
  rows.forEach(function (x, k) { if (x.student_id === sid) i = k; });
  var done = 'cancelled:' + sid + ':' + hash_('', code);
  if (i < 0) return CacheService.getScriptCache().get(done) ? { ok: true } : { ok: false, error: 'bad_code' };
  var row = rows[i], seat = table_('seats').filter(function (s) { return s.id === row.seat_id; })[0];
  var lec = byId_(table_('lectures'))[seat.lecture_id];
  if (Date.now() >= Date.parse(lec.starts_at) - CLOSE_HOURS * 3600000) return { ok: false, error: 'closed' };
  if (+row.cancel_attempts >= 10) return { ok: false, error: 'locked' };
  if (hash_(row.cancel_salt, code) !== row.cancel_code_hash) {
    sh.getRange(i + 2, COLS.bookings.indexOf('cancel_attempts') + 1).setValue(String(+row.cancel_attempts + 1));
    return { ok: false, error: 'bad_code' };
  }
  sh.deleteRow(i + 2);
  CacheService.getScriptCache().put(done, '1', 600);  // a repeated request after a lost reply also gets "cancelled"
  return { ok: true };
}

// ---- Admin (deployment: Execute as me, Who has access: Only myself) ----------------------------------------------
function isAdmin_() {
  var email = String(Session.getActiveUser().getEmail() || '').toLowerCase();
  return ADMIN_EMAILS.indexOf(email) >= 0;
}
function requireAdmin_() { if (!isAdmin_()) throw new Error('forbidden'); }

function adminPage_() {
  if (!isAdmin_()) return HtmlService.createHtmlOutput('<p>Not authorised.</p>').setTitle('Not authorised');
  return HtmlService.createHtmlOutputFromFile('Admin').setTitle('Flipped lectures · instructor')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function adminData() {
  requireAdmin_();
  var roster = byKey_(table_('roster'), 'student_id'), seats = byId_(table_('seats')), lec = byId_(table_('lectures'));
  var bookings = table_('bookings').map(function (b) {
    var s = seats[b.seat_id], l = s ? lec[s.lecture_id] : null, r = roster[b.student_id] || {};
    var t = ['accuracy', 'understanding', 'quiz', 'commitment'].reduce(function (a, k) { return a + (+b[k] || 0); }, 0);
    return { seat_id: b.seat_id, student_id: b.student_id, full_name: r.full_name || b.entered_name, email: r.email || '',
             lecture: l ? +l.number : '', chapter: l ? l.chapter : '', part: s ? +s.part_no : '', created_at: b.created_at,
             accuracy: b.accuracy, understanding: b.understanding, quiz: b.quiz, commitment: b.commitment, total: t };
  }).sort(function (a, b) { return a.lecture - b.lecture || a.part - b.part; });
  var booked = {}; bookings.forEach(function (b) { booked[b.student_id] = true; });
  return { lectures: LECTURES, bookings: bookings,
           roster: table_('roster').map(function (r) { return { student_id: r.student_id, full_name: r.full_name, booked: !!booked[r.student_id] }; }) };
}

function adminScore(studentId, a, u, q, c) {
  requireAdmin_();
  var allowed = { accuracy: [1, 0.5, 0], understanding: [1, 0.5, 0], quiz: [0.5, 0.25, 0], commitment: [0.5, 0.25, 0] };
  var vals = { accuracy: a, understanding: u, quiz: q, commitment: c };
  Object.keys(vals).forEach(function (k) {
    if (vals[k] !== '' && vals[k] !== null && allowed[k].indexOf(+vals[k]) < 0) throw new Error('Invalid score for ' + k);
  });
  return locked_(function () {
    var i = rowIndex_('bookings', 'student_id', studentId);
    if (i < 0) return { ok: false, error: 'not_found' };
    var sh = sheet_('bookings');
    Object.keys(vals).forEach(function (k) { sh.getRange(i + 2, COLS.bookings.indexOf(k) + 1).setValue(vals[k] === null ? '' : String(vals[k])); });
    return { ok: true };
  });
}

function adminMove(studentId, seatId) {
  requireAdmin_();
  return locked_(function () {
    var rows = table_('bookings');
    if (rows.some(function (x) { return x.seat_id === String(seatId) && x.student_id !== studentId; })) return { ok: false, error: 'taken' };
    var i = rowIndex_('bookings', 'student_id', studentId);
    if (i < 0) return { ok: false, error: 'not_found' };
    sheet_('bookings').getRange(i + 2, 1).setValue(String(seatId));
    return { ok: true };
  });
}

function adminCancel(studentId) {
  requireAdmin_();
  return locked_(function () {
    var i = rowIndex_('bookings', 'student_id', studentId);
    if (i < 0) return { ok: false, error: 'not_found' };
    sheet_('bookings').deleteRow(i + 2);
    return { ok: true };
  });
}

// Adds a student to a seat, also after registration has closed. Returns a cancellation code for the student.
function adminAdd(studentId, seatId) {
  requireAdmin_();
  return locked_(function () {
    var rows = table_('bookings');
    if (!table_('roster').some(function (r) { return r.student_id === studentId; })) return { ok: false, error: 'not_in_roster' };
    if (rows.some(function (x) { return x.seat_id === String(seatId); })) return { ok: false, error: 'taken' };
    if (rows.some(function (x) { return x.student_id === studentId; })) return { ok: false, error: 'already' };
    var code = newCode_(), salt = Utilities.getUuid();
    appendRow_('bookings', { seat_id: String(seatId), student_id: studentId, entered_name: '', cancel_salt: salt,
      cancel_code_hash: hash_(salt, code), cancel_attempts: '0', created_at: new Date().toISOString() });
    return { ok: true, code: code };
  });
}

function adminRosterAdd(studentId, fullName, email) {
  requireAdmin_();
  studentId = String(studentId || '').trim(); email = String(email || '').trim().toLowerCase();
  if (!/^[0-9]{7}$/.test(studentId) || !/@/.test(email)) return { ok: false, error: 'invalid' };
  return locked_(function () {
    var i = rowIndex_('roster', 'student_id', studentId), sh = sheet_('roster');
    if (i >= 0) sh.getRange(i + 2, 1, 1, 3).setValues([[studentId, String(fullName).trim(), email]]);
    else appendRow_('roster', { student_id: studentId, full_name: String(fullName).trim(), email: email });
    return { ok: true };
  });
}

function adminCsv() {
  requireAdmin_();
  var head = ['student_id', 'full_name', 'lecture', 'part', 'accuracy', 'understanding', 'quiz', 'commitment', 'total'];
  var q = function (x) { x = x === undefined || x === null ? '' : String(x); return /[",\n]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x; };
  return '﻿' + head.join(',') + '\n' + adminData().bookings.map(function (b) { return head.map(function (k) { return q(b[k]); }).join(','); }).join('\n') + '\n';
}

// After the final grades are recorded: delete all bookings and the roster.
function adminPurge(confirm) {
  requireAdmin_();
  if (confirm !== 'DELETE') return { ok: false, error: 'confirm' };
  return locked_(function () {
    ['bookings', 'roster'].forEach(function (n) { var sh = sheet_(n); if (sh.getLastRow() > 1) sh.deleteRows(2, sh.getLastRow() - 1); });
    return { ok: true };
  });
}

// ---- Test data for the acceptance tests (run from the editor; removed afterwards) --------------------------------
function addTestData() {
  locked_(function () {
    var now = Date.now();
    appendRow_('lectures', { id: '98', number: '98', chapter: 'TEST', title_en: 'Test lecture (open)', title_ar: 'محاضرة اختبار', assignment_en: '-', assignment_ar: '-', starts_at: new Date(now + 30 * 86400000).toISOString() });
    appendRow_('lectures', { id: '99', number: '99', chapter: 'TEST', title_en: 'Test lecture (closed)', title_ar: 'محاضرة اختبار مغلقة', assignment_en: '-', assignment_ar: '-', starts_at: new Date(now + 48 * 3600000).toISOString() });
    [981, 982, 983].forEach(function (id, k) { appendRow_('seats', { id: String(id), lecture_id: '98', part_no: String(k + 1), title_en: 'Test part', title_ar: 'جزء اختبار', slides: '-' }); });
    [991, 992, 993].forEach(function (id, k) { appendRow_('seats', { id: String(id), lecture_id: '99', part_no: String(k + 1), title_en: 'Test part', title_ar: 'جزء اختبار', slides: '-' }); });
    ['9000001', '9000002', '9000003', '9000004'].forEach(function (id, k) { appendRow_('roster', { student_id: id, full_name: 'Test Student ' + (k + 1), email: 't' + (k + 1) + '@stu.kau.edu.sa' }); });
  });
  return 'Test data added.';
}

function removeTestData() {
  locked_(function () {
    var drop = function (name, test) { var sh = sheet_(name), rows = table_(name);
      for (var i = rows.length - 1; i >= 0; i--) if (test(rows[i])) sh.deleteRow(i + 2); };
    drop('bookings', function (r) { return /^9[89]\d$/.test(r.seat_id) || /^900000\d$/.test(r.student_id); });
    drop('seats', function (r) { return r.lecture_id === '98' || r.lecture_id === '99'; });
    drop('lectures', function (r) { return r.id === '98' || r.id === '99'; });
    drop('roster', function (r) { return /^900000\d$/.test(r.student_id); });
  });
  return 'Test data removed.';
}

// ---- Helpers ----------------------------------------------------------------------------------------------------
function locked_(fn) {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(25000)) return { ok: false, error: 'busy' };
  try { var r = fn(); SpreadsheetApp.flush(); return r; } finally { lock.releaseLock(); }
}
function sheet_(name) { return SpreadsheetApp.getActive().getSheetByName(name); }
function table_(name) {
  var sh = sheet_(name), n = sh.getLastRow() - 1, cols = COLS[name];
  if (n <= 0) return [];
  return sh.getRange(2, 1, n, cols.length).getDisplayValues().map(function (r) {
    var o = {}; cols.forEach(function (k, i) { o[k] = String(r[i]).trim(); }); return o; });
}
function writeTable_(name, rows) {
  var sh = sheet_(name), cols = COLS[name];
  if (sh.getLastRow() > 1) sh.getRange(2, 1, sh.getLastRow() - 1, cols.length).clearContent();
  if (rows.length) sh.getRange(2, 1, rows.length, cols.length).setValues(rows);
}
function appendRow_(name, obj) {
  var sh = sheet_(name), cols = COLS[name];
  sh.getRange(sh.getLastRow() + 1, 1, 1, cols.length).setNumberFormat('@')
    .setValues([cols.map(function (k) { return obj[k] === undefined ? '' : String(obj[k]); })]);
}
function rowIndex_(name, key, val) { var rows = table_(name); for (var i = 0; i < rows.length; i++) if (rows[i][key] === String(val)) return i; return -1; }
function byId_(rows) { return byKey_(rows, 'id'); }
function byKey_(rows, k) { var o = {}; rows.forEach(function (r) { o[r[k]] = r; }); return o; }
function newCode_() {
  var alphabet = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789', bytes = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, Utilities.getUuid() + Math.random());
  var s = ''; for (var i = 0; i < 6; i++) s += alphabet.charAt(((bytes[i] % 256) + 256) % 256 % alphabet.length); return s;
}
function hash_(salt, code) { return Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, salt + ':' + code)); }
function json_(obj) { return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON); }
