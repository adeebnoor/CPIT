def _f(ns):
    f = ns.get("can_borrow"); assert callable(f), "define can_borrow(student, item)"
    return f
OK = {"id": "cam-3", "available": True}

def allowed(ns, out):
    assert _f(ns)({"id": "s1", "loans": 1, "overdue": False}, OK) is True, "a student with one item and nothing overdue may borrow (return True)"
def limit(ns, out):
    assert _f(ns)({"id": "s1", "loans": LIMIT, "overdue": False}, OK) is False, "a student who already holds LIMIT items must be refused"
def overdue(ns, out):
    assert _f(ns)({"id": "s1", "loans": 0, "overdue": True}, OK) is False, "a student with an overdue item must be refused"
def unavailable(ns, out):
    assert _f(ns)({"id": "s1", "loans": 0, "overdue": False}, {"id": "cam-3", "available": False}) is False, "an item that is out must be refused"
def malformed(ns, out):
    f = _f(ns)
    for s, i in [({}, OK), (None, OK), ({"id": "s1", "loans": 0, "overdue": False}, None), ({"id": "s1", "loans": "0", "overdue": False}, OK)]:
        try:
            r = f(s, i)
        except Exception as e:
            raise AssertionError(f"malformed input must be refused, not crash ({type(e).__name__})")
        assert r is False, f"malformed input must be refused: {s!r}, {i!r}"

CHECKS = [
    ("a normal loan is allowed", allowed),
    ("a student at the limit is refused", limit),
    ("a student with an overdue item is refused", overdue),
    ("an item that is out is refused", unavailable),
    ("malformed input is refused without crashing", malformed),
]
