def _g(ns, n):
    f = ns.get(n); assert callable(f), f"define {n}"
    return f
def known(ns, out):
    f = _g(ns, "fit")
    for k, v in FACTS.items():
        assert f(*k) == v, f"fit{k} should be {v!r} from the facts"
def unknown(ns, out):
    f = _g(ns, "fit")
    for o, r in [("A", "peak-load"), ("B", "export-api"), ("B", "support-3-years"), ("B", "peak-load"), ("C", "booking")]:
        assert f(o, r) == "unknown", f"fit({o!r}, {r!r}) is not settled by the facts: expected 'unknown', got {f(o, r)!r}"
def short(ns, out):
    assert list(_g(ns, "shortlist")(["A", "B"])) == [], "neither option is shown to meet every requirement, so the shortlist is empty"
    assert list(_g(ns, "shortlist")(["C"])) == [], "an option nobody has checked (no facts at all) must not be shortlisted"
def needed(ns, out):
    f = _g(ns, "evidence_needed")
    for o, want in [("A", ["peak-load"]), ("B", ["export-api", "support-3-years", "peak-load"])]:
        assert list(f(o)) == want, f"evidence_needed({o!r}) should be {want}, got {list(f(o))}"

CHECKS = [
    ("supplied facts are reported as given", known),
    ("unsettled requirements are unknown, never met", unknown),
    ("the shortlist needs evidence for every requirement", short),
    ("evidence_needed lists exactly the unknowns", needed),
]
