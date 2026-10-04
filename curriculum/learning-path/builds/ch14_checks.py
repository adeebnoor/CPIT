def _r(ns):
    f = ns.get("reconcile"); assert callable(f), "define reconcile(central, paper_log)"
    return f
def _c(cid, pid, t, base):
    return {"change_id": cid, "pickup_id": pid, "time": t, "base_version": base}

def applies(ns, out):
    new, conf = _r(ns)({"P1": {"time": "08:00", "version": 1}}, [_c("c1", "P1", "08:30", 1)])
    assert new["P1"] == {"time": "08:30", "version": 2}, f"one change should give version 2 at 08:30, got {new.get('P1')}"
    assert list(conf) == [], "no conflict expected"
def once(ns, out):
    new, conf = _r(ns)({"P1": {"time": "08:00", "version": 1}}, [_c("c1", "P1", "08:30", 1), _c("c1", "P1", "08:30", 1)])
    assert new["P1"]["version"] == 2, "the same change_id must be applied once"
    assert list(conf) == [], "a repeated change is not a conflict"
def conflict(ns, out):
    new, conf = _r(ns)({"P1": {"time": "09:00", "version": 5}}, [_c("c1", "P1", "08:30", 4)])
    assert new["P1"] == {"time": "09:00", "version": 5}, "a stale paper change must not overwrite the central record"
    assert list(conf) == ["c1"], f"expected conflict ['c1'], got {list(conf)}"
def adds(ns, out):
    new, conf = _r(ns)({}, [_c("c1", "P9", "10:00", 0)])
    assert new.get("P9") == {"time": "10:00", "version": 1}, "a pickup missing centrally should be added with version 1"
def chain(ns, out):
    new, conf = _r(ns)({"P1": {"time": "08:00", "version": 3}}, [_c("c1", "P1", "08:30", 3), _c("c2", "P1", "08:45", 4)])
    assert new["P1"] == {"time": "08:45", "version": 5}, f"two successive changes should give version 5 at 08:45, got {new['P1']}"
def pure(ns, out):
    central = {"P1": {"time": "08:00", "version": 1}}; log = [_c("c1", "P1", "08:30", 1)]
    a, b = copy.deepcopy(central), copy.deepcopy(log)
    _r(ns)(central, log)
    assert central == a and log == b, "reconcile must not modify its inputs"

CHECKS = [
    ("a paper change is applied", applies),
    ("the same change is applied only once", once),
    ("a stale change becomes a conflict, not an overwrite", conflict),
    ("a missing pickup is added", adds),
    ("successive changes to one pickup are both applied", chain),
    ("the inputs are not modified", pure),
]
