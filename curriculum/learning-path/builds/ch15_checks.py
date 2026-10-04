def _g(ns, n):
    f = ns.get(n); assert callable(f), f"define {n}"
    return f
def known(ns, out):
    f = _g(ns, "fit")
    for k, v in FACTS.items():
        assert f(*k) == v, f"fit{k} should be {v!r} from the facts"
def unknown(ns, out):
    f = _g(ns, "fit")
    for o, r in [("A", "export-api"), ("A", "peak-load"), ("B", "peak-load")]:
        assert f(o, r) == "unknown", f"fit({o!r}, {r!r}) is not settled by the facts: expected 'unknown', got {f(o, r)!r}"
def short(ns, out):
    assert list(_g(ns, "shortlist")(["A", "B"])) == [], "neither option is shown to meet every requirement, so the shortlist is empty"
def needed(ns, out):
    f = _g(ns, "evidence_needed")
    assert list(f("A")) == ["export-api", "peak-load"], f"evidence_needed('A') should be ['export-api', 'peak-load'], got {list(f('A'))}"
    assert list(f("B")) == ["export-api", "peak-load"], f"evidence_needed('B') should be ['export-api', 'peak-load'], got {list(f('B'))}"

CHECKS = [
    ("supplied facts are reported as given", known),
    ("unsettled requirements are unknown, never met", unknown),
    ("the shortlist needs evidence for every requirement", short),
    ("evidence_needed lists exactly the unknowns", needed),
]
