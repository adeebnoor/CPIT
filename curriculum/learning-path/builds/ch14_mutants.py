# Known bugs. Your own tests must catch each one (at least one of your tests fails).
MUTANTS = [
    ("last write wins: a stale paper change overwrites the central record", '''
def reconcile(central, paper_log):
    new, seen = {k: dict(v) for k, v in central.items()}, set()
    for c in paper_log:
        if c["change_id"] in seen:
            continue
        seen.add(c["change_id"])
        cur = new.get(c["pickup_id"], {"version": 0})
        new[c["pickup_id"]] = {"time": c["time"], "version": cur["version"] + 1}
    return new, []
'''),
    ("a repeated change_id is applied again (and then reported as a conflict)", '''
def reconcile(central, paper_log):
    new, conflicts = {k: dict(v) for k, v in central.items()}, []
    for c in paper_log:
        cur = new.get(c["pickup_id"], {"version": 0})
        if cur["version"] != c["base_version"]:
            conflicts.append(c["change_id"]); continue
        new[c["pickup_id"]] = {"time": c["time"], "version": cur["version"] + 1}
    return new, conflicts
'''),
    ("the central list passed in is changed in place", '''
def reconcile(central, paper_log):
    new, seen, conflicts = central, set(), []
    for c in paper_log:
        if c["change_id"] in seen:
            continue
        seen.add(c["change_id"])
        cur = new.get(c["pickup_id"], {"version": 0})
        if cur["version"] != c["base_version"]:
            conflicts.append(c["change_id"]); continue
        new[c["pickup_id"]] = {"time": c["time"], "version": cur["version"] + 1}
    return new, conflicts
'''),
    ("a pickup missing from the central list is dropped", '''
def reconcile(central, paper_log):
    new, seen, conflicts = {k: dict(v) for k, v in central.items()}, set(), []
    for c in paper_log:
        if c["change_id"] in seen or c["pickup_id"] not in new:
            continue
        seen.add(c["change_id"])
        cur = new[c["pickup_id"]]
        if cur["version"] != c["base_version"]:
            conflicts.append(c["change_id"]); continue
        new[c["pickup_id"]] = {"time": c["time"], "version": cur["version"] + 1}
    return new, conflicts
'''),
]
