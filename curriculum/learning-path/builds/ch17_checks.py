def _svc(ns, store):
    c = ns.get("BookingService"); assert c is not None, "define class BookingService"
    return c(store)
def _count(store):
    return len(store.get("reservations", {}))
def distinct(ns, out):
    st = {}; s = _svc(ns, st)
    a, b = s.reserve("a", "u1", "E1"), s.reserve("b", "u1", "E1")
    assert a != b and _count(st) == 2, "two different request ids must give two reservations"
def repeat(ns, out):
    st = {}; s = _svc(ns, st)
    a, b = s.reserve("a", "u1", "E1"), s.reserve("a", "u1", "E1")
    assert a == b, "the same request id must return the same reservation id"
    assert _count(st) == 1, f"the same request id must create one reservation, found {_count(st)}"
def lost(ns, out):
    st = {}; s = _svc(ns, st)
    s.reserve("x", "u1", "E1")          # the reply is lost
    rid = s.reserve("x", "u1", "E1")    # the app retries with the same id
    assert _count(st) == 1 and rid, "a retry after a lost reply must not book twice"
def restart(ns, out):
    st = {}
    first = _svc(ns, st).reserve("x", "u1", "E1")
    again = _svc(ns, st).reserve("x", "u1", "E1")   # the service restarted
    assert again == first and _count(st) == 1, "after a restart the same request id must return the first outcome"
def missing(ns, out):
    s = _svc(ns, {})
    for bad in [None, ""]:
        try:
            s.reserve(bad, "u1", "E1")
        except ValueError:
            continue
        raise AssertionError(f"request_id {bad!r} must raise ValueError")

CHECKS = [
    ("different actions create different reservations", distinct),
    ("the same request id books once and returns the same id", repeat),
    ("a retry after a lost reply does not book twice", lost),
    ("the outcome survives a restart", restart),
    ("a missing request id is rejected", missing),
]
