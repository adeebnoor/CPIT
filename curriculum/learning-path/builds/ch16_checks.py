def _a(ns):
    f = ns.get("reserve_minutes"); assert callable(f), "define reserve_minutes(component, room_id, minutes)"
    return f
def converts(ns, out):
    c = FakeComponent(); r = _a(ns)(c, "L1", 30)
    assert c.calls == [("L1", 1800)], f"30 minutes must reach the component as 1800 seconds, got {c.calls}"
    assert isinstance(r, dict) and r.get("id"), "return the component's reservation"
def edges(ns, out):
    for m, s in [(1, 60), (120, 7200)]:
        c = FakeComponent(); _a(ns)(c, "L1", m)
        assert c.calls == [("L1", s)], f"{m} minutes must be accepted as {s} seconds"
def rejects(ns, out):
    for bad in [0, 121, -5, "30", 2.5, True, None]:
        c = FakeComponent()
        try:
            _a(ns)(c, "L1", bad)
        except ValueError:
            assert not c.calls, f"{bad!r} must be rejected before calling the component"
            continue
        except Exception as e:
            raise AssertionError(f"{bad!r} must raise ValueError, not {type(e).__name__}")
        raise AssertionError(f"{bad!r} must raise ValueError")
def post(ns, out):
    c = FakeComponent(end_offset=5)
    try:
        _a(ns)(c, "L1", 30)
    except ContractError:
        return
    raise AssertionError("a reservation whose end time is wrong must raise ContractError")

CHECKS = [
    ("minutes are converted to seconds", converts),
    ("1 and 120 minutes are accepted", edges),
    ("invalid minutes are rejected before the call", rejects),
    ("a wrong end time breaks the postcondition", post),
]
