def _f(ns):
    f = ns.get("can_read"); assert callable(f), "define can_read(user, project)"
    return f
S1 = {"id": "s1", "role": "student", "groups": ["G1"]}
S2 = {"id": "s2", "role": "student", "groups": ["G1"]}
T1 = {"id": "t1", "role": "staff", "groups": ["G1"]}
T2 = {"id": "t2", "role": "staff", "groups": ["G2"]}
P = {"id": "p1", "owner": "s1", "group": "G1"}

def owner(ns, out):
    assert _f(ns)(S1, P) is True, "the owner must be allowed (return True)"
def other_student(ns, out):
    assert _f(ns)(S2, P) is False, "another student in the same group must be refused"
def assigned_staff(ns, out):
    assert _f(ns)(T1, P) is True, "staff assigned to the project's group must be allowed"
def other_staff(ns, out):
    assert _f(ns)(T2, P) is False, "staff from another group must be refused"
def unknown_role(ns, out):
    assert _f(ns)({"id": "s1", "role": "admin", "groups": ["G1"]}, P) is False, "an unknown role must be refused"
def malformed(ns, out):
    f = _f(ns)
    for u, p in [({}, P), (S1, {}), (None, P), (S1, None), ({"id": "t1", "role": "staff"}, P)]:
        try:
            r = f(u, p)
        except Exception as e:
            raise AssertionError(f"malformed input must be refused, not crash ({type(e).__name__})")
        assert r is False, f"malformed input must be refused: {u!r}, {p!r}"
def tests_refuse(ns, out):
    src = ns.get("__source__", "")
    n = src.count("not can_read(") + src.count("is False") + src.count("== False")
    assert n >= 2, "your tests must check at least two requests that are refused"

CHECKS = [
    ("the owner can read", owner),
    ("another student is refused, even in the same group", other_student),
    ("assigned staff can read", assigned_staff),
    ("staff from another group is refused", other_staff),
    ("an unknown role is refused", unknown_role),
    ("malformed input is refused without crashing", malformed),
    ("your tests include at least two refusals", tests_refuse),
]
