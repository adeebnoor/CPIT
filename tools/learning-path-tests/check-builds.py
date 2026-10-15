"""Check the Python build tasks (Assignments 3–9) with CPython, using the same harness the browser runs.

- builds.js carries exactly the helpers, starters and checks in curriculum/learning-path/builds/.
- Every starter runs without crashing and fails at least one course check (it is not a solution).
- Classic mistakes are caught by the check that names them (the checks discriminate).
- Every known bug (chNN_mutants.py) breaks at least one course check, and the mutation test reports
  bugs that weak tests miss.
- Syntax errors and missing tests are reported clearly.
Reference solutions are kept privately with the instructor and are not needed here.

Usage: python3 tools/learning-path-tests/check-builds.py
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'curriculum/learning-path/builds'
CH = [0, 12, 13, 14, 15, 16, 17, 20]   # 0 = the practice task on assignment-example.html
ns: dict = {}
exec((SRC / 'harness.py').read_text(encoding='utf-8'), ns)
MUT = {ch: (SRC / f'ch{ch}_mutants.py').read_text() if (SRC / f'ch{ch}_mutants.py').exists() else '' for ch in CH}
run = lambda ch, code: json.loads(ns['__run']((SRC / f'ch{ch}_helpers.py').read_text(), code, (SRC / f'ch{ch}_checks.py').read_text(), MUT[ch]))
failed = 0


def check(name: str, ok: bool, detail: str = '') -> None:
    global failed
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok or not detail else ' · ' + detail))
    failed += 0 if ok else 1


def failing(r: dict) -> list[str]:
    return [c[0] for c in r['checks'] if not c[1]]


# 1. the engine matches the sources
spec = json.loads(subprocess.run(['node', '-e', 'process.stdout.write(JSON.stringify(require(process.argv[1]).SPEC))', str(ROOT / 'curriculum/learning-path/builds.js')], capture_output=True, text=True, check=True).stdout)
for ch in CH:
    same = all(spec[str(ch)][k] == (SRC / f'ch{ch}_{k}.py').read_text(encoding='utf-8') for k in ('helpers', 'starter', 'checks'))
    same = same and spec[str(ch)].get('mutants', '') == MUT[ch] and len(spec[str(ch)].get('viva', [])) >= 4
    check(f'Ch{ch} builds.js matches the source files', same)

# 2. starters are not solutions
for ch in CH:
    r = run(ch, (SRC / f'ch{ch}_starter.py').read_text())
    check(f'Ch{ch} starter runs and fails at least one course check', r['error'] is None and bool(failing(r)), str(r['error']))

# 3. classic mistakes are caught by the named check
OWN = '\ndef test_a():\n    pass\ndef test_b():\n    pass\ndef test_c():\n    pass\n'
MISTAKES = {
    12: ('a revised tree that still has a single point of failure',
         'current = OR(Event("Camera misses a person", "fact"), Event("Night use", "fact"), Event("Stop not used", "assumption"))\n'
         'revised = OR(Event("Camera misses a person", "fact"), Event("Night use", "fact"), AND(Event("Stop not used", "assumption"), Event("Drill (proposed)", "proposed")))' + OWN,
         'no single event'),
    13: ('hiding the link but checking only the group for students',
         'def can_read(user, project):\n    try:\n        return project["group"] in user["groups"]\n    except Exception:\n        return False\n' + OWN, 'another student'),
    14: ('last write wins: a stale paper change overwrites the central record',
         'def reconcile(central, paper_log):\n    new = {k: dict(v) for k, v in central.items()}\n    seen = set()\n    for c in paper_log:\n        if c["change_id"] in seen:\n            continue\n        seen.add(c["change_id"])\n        old = new.get(c["pickup_id"], {"version": 0})\n        new[c["pickup_id"]] = {"time": c["time"], "version": old["version"] + 1}\n    return new, []\n' + OWN, 'stale change'),
    15: ('treating unknown as met (brochure reading)',
         'def fit(o, r):\n    return FACTS.get((o, r), "met")\ndef shortlist(options):\n    return [o for o in options if all(fit(o, r) == "met" for r in REQUIREMENTS)]\ndef evidence_needed(o):\n    return [r for r in REQUIREMENTS if fit(o, r) == "unknown"]\n' + OWN, 'unknown'),
    16: ('converting units but not checking the range',
         'def reserve_minutes(component, room_id, minutes):\n    return component.reserve(room_id, minutes * 60)\n' + OWN, 'rejected before the call'),
    17: ('deduplicating in memory only, so a restart books again',
         'class BookingService:\n    def __init__(self, store):\n        self.store = store\n        store.setdefault("reservations", {})\n        self.seen = {}\n    def reserve(self, request_id, user, event):\n        if not request_id:\n            raise ValueError("id")\n        if request_id in self.seen:\n            return self.seen[request_id]\n        rid = f"R{len(self.store[\'reservations\']) + 1}"\n        self.store["reservations"][rid] = {"user": user}\n        self.seen[request_id] = rid\n        return rid\n' + OWN, 'restart'),
    20: ('showing the last value as live when a feed is unavailable',
         'def display_state(feed, now, limit=LIMIT):\n    if feed.get("updated") is None:\n        return "unavailable"\n    return "stale" if now - feed["updated"] > limit else "live"\ndef headline(states):\n    bad = [f"{k} {v}" for k, v in states.items() if v != "live"]\n    return "All feeds live" if not bad else "Degraded: " + ", ".join(bad)\n' + OWN, 'unavailable'),
}
for ch, (what, code, key) in MISTAKES.items():
    r = run(ch, code)
    hit = [c for c in failing(r) if key in c]
    check(f'Ch{ch} catches {what}', r['error'] is None and bool(hit), f"failing: {failing(r)} error: {r['error']}")

# 4. every known bug is a real bug, and weak tests are told which bugs they miss
for ch in CH:
    if not MUT[ch]:
        continue
    m: dict = {}
    exec(MUT[ch], m)
    for label, code in m['MUTANTS']:
        r = run(ch, code + OWN)
        bad = [c for c in failing(r) if 'mutation' not in c and 'own tests' not in c]
        check(f'Ch{ch} known bug breaks a course check: {label}', r['error'] is None and bool(bad), str(r['error']))
    r = run(ch, (SRC / f'ch{ch}_starter.py').read_text().split('# Your tests')[0] + OWN)
    weak = r.get('mutants') or []
    check(f'Ch{ch} mutation test reports {len(weak)} bugs missed by empty tests', bool(weak) and not any(k for _, k in weak))

# 5. errors are reported clearly
r = run(13, 'def can_read(user, project:\n    return False\n')
check('a syntax error is reported with its line', bool(r['error']) and 'line 1' in r['error'], str(r['error']))
r = run(13, 'def can_read(user, project):\n    return False\n')
check('missing own tests are reported', any('at least three' in (c[2] or '') for c in r['checks'] if not c[1]))
r = run(13, 'raise SystemExit(1)\n')
check('SystemExit from student module code is contained and reported', bool(r['error']) and 'SystemExit: 1' in r['error'], str(r['error']))
r = run(13, 'def can_read(user, project):\n    raise SystemExit(2)\n' + OWN)
check('SystemExit raised through a course check is contained', any('SystemExit: 2' in (c[2] or '') for c in r['checks']), str(r['checks']))

# 6. coverage (course outcome 11): your own tests are measured, the course checks are not
for ch in CH:
    r = run(ch, (SRC / f'ch{ch}_starter.py').read_text())
    c = r.get('coverage')
    check(f'Ch{ch} the build record measures line and branch coverage of the starter', bool(c) and c['lines'][1] > 0 and c['lines'][0] <= c['lines'][1], str(c))
ADAPTER = ('def reserve_minutes(component, room_id, minutes):\n'
           '    if not isinstance(minutes, int) or isinstance(minutes, bool):\n'
           '        raise ValueError("whole minutes")\n'
           '    if minutes < 1 or minutes > 120:\n'
           '        raise ValueError("1..120")\n'
           '    r = component.reserve(room_id, minutes * 60)\n'
           '    if r["end"] - r["start"] != minutes * 60:\n'
           '        raise ContractError("postcondition")\n'
           '    return r\n')
T3 = ('def test_thirty():\n    c = FakeComponent(); reserve_minutes(c, "Lab-1", 30); assert c.calls == [("Lab-1", 1800)]\n'
      'def test_zero():\n    c = FakeComponent()\n    try:\n        reserve_minutes(c, "Lab-1", 0); assert False\n    except ValueError:\n        pass\n'
      'def test_top():\n    c = FakeComponent(); reserve_minutes(c, "Lab-1", INPUT)\n')
c1 = run(16, ADAPTER + T3.replace('INPUT', '120'))['coverage']
untested = [(row[0], row[3], row[5]) for row in c1['rows'] if not (row[3] and row[5])]
check('coverage names the branches three tests never take (type check true, postcondition true)', c1['branches'] == [4, 6] and untested == [(2, False, True), (7, False, True)] and c1['missed'] == [3, 8], str(c1))
c2 = run(16, ADAPTER + T3.replace('INPUT', '"30"'))['coverage']
check('changing one input and running again changes the coverage: the type-check branch is now taken', c2['branches'] == [5, 6] and [r[0] for r in c2['rows'] if not (r[3] and r[5])] == [7], str(c2))
r = run(16, ADAPTER + T3.replace('INPUT', '120'))
check('coverage counts only your own tests: the course checks do not add lines', r['coverage']['lines'] == c1['lines'] and all(ok for _, ok, _ in r['checks'][:4]), str(r['checks'][:4]))

TREE = ('current = OR(Event("Camera misses a person", "fact"), Event("Night use", "fact"), Event("Stop not used", "assumption"))\n'
        'revised = AND(OR(Event("Camera misses a person", "fact"), Event("Night use", "fact")), Event("Second sensor fails", "proposed"), Event("Stop not used", "assumption"))\n'
        'def test_cuts():\n    assert cut_sets(revised)\n'
        'def test_none():\n    assert not occurs(revised, set())\n'
        'def test_all():\n    assert occurs(revised, {"Camera misses a person", "Second sensor fails", "Stop not used"})\n')
g = run(12, TREE)['coverage']
check('Ch12 coverage measures gate outcomes in the fault tree (the current tree is never evaluated)', g and g.get('unit') == 'gates' and g['lines'] == [2, 3] and g['branches'] == [4, 6] and any(r[0].startswith('current') and not r[3] and not r[5] for r in g['rows']), str(g))

# 7. the in-class demos embedded in the lectures are current and behave as taught
import importlib.util
spec_cb = importlib.util.spec_from_file_location('apply_class_builds', ROOT / 'tools/apply_class_builds.py')
cb = importlib.util.module_from_spec(spec_cb); spec_cb.loader.exec_module(cb)
story = (ROOT / 'lectures/iscarb/runtime/story-v3.js').read_text(encoding='utf-8')
data = cb.build()
check('the lecture live labs embed the current demo results (run tools/apply_class_builds.py)', json.dumps({str(k): v for k, v in data.items()}, ensure_ascii=False, indent=1) in story)
for ch, d in data.items():
    check(f'Ch{ch} live lab: the design as taught fails a test, and the fix passes all three', any(not ok for _, ok, _ in d['result']['buggy']['tests']) and all(ok for _, ok, _ in d['result']['fixed']['tests']) and len(d['result']['fixed']['tests']) == 3)

print('ALL PASS' if not failed else f'{failed} FAILED')
sys.exit(1 if failed else 0)
