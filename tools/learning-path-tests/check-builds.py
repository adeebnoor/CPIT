"""Check the Python build tasks (Assignments 3–9) with CPython, using the same harness the browser runs.

- builds.js carries exactly the helpers, starters and checks in curriculum/learning-path/builds/.
- Every starter runs without crashing and fails at least one course check (it is not a solution).
- Classic mistakes are caught by the check that names them (the checks discriminate).
- Syntax errors and missing tests are reported clearly.
Reference solutions are kept privately with the instructor and are not needed here.

Usage: python3 tools/learning-path-tests/check-builds.py
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'curriculum/learning-path/builds'
CH = [12, 13, 14, 15, 16, 17, 20]
ns: dict = {}
exec((SRC / 'harness.py').read_text(encoding='utf-8'), ns)
run = lambda ch, code: json.loads(ns['__run']((SRC / f'ch{ch}_helpers.py').read_text(), code, (SRC / f'ch{ch}_checks.py').read_text()))
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

# 4. errors are reported clearly
r = run(13, 'def can_read(user, project:\n    return False\n')
check('a syntax error is reported with its line', bool(r['error']) and 'line 1' in r['error'], str(r['error']))
r = run(13, 'def can_read(user, project):\n    return False\n')
check('missing own tests are reported', any('at least three' in (c[2] or '') for c in r['checks'] if not c[1]))

print('ALL PASS' if not failed else f'{failed} FAILED')
sys.exit(1 if failed else 0)
