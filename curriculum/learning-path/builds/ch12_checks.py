def _tree(ns, name):
    t = ns.get(name)
    assert t is not None, f"define {name}"
    assert isinstance(t, Gate), f"{name} must start with AND(...) or OR(...)"
    return t

def complete(ns, out):
    for n in ("current", "revised"):
        ev = events(_tree(ns, n))
        assert len(ev) >= 3, f"{n} needs at least three events (has {len(ev)})"
        left = [e.name for e in ev if "CHANGE ME" in e.name]
        assert not left, f"{n} still has placeholders: " + "; ".join(left)

def rests_on_facts(ns, out):
    assert any(e.source == "fact" for e in events(_tree(ns, "current"))), "current must use at least one case fact"

def no_single_point(ns, out):
    sp = single_points(_tree(ns, "revised"))
    assert not sp, "in revised, these events still cause the hazard alone: " + "; ".join(sp)

def proposed_marked(ns, out):
    assert any(e.source == "proposed" for e in events(_tree(ns, "revised"))), "label your new control or test as proposed"

def keeps_facts(ns, out):
    facts = {e.name for e in events(_tree(ns, "current")) if e.source == "fact"}
    kept = {e.name for e in events(_tree(ns, "revised"))}
    missing = sorted(facts - kept)
    assert not missing, "revised drops case facts (add protection; do not delete causes): " + "; ".join(missing)

CHECKS = [
    ("both trees are complete: three or more events, no placeholders", complete),
    ("current rests on case facts", rests_on_facts),
    ("revised: no single event causes the hazard", no_single_point),
    ("revised labels new controls or tests as proposed", proposed_marked),
    ("revised keeps every case fact from current", keeps_facts),
]
