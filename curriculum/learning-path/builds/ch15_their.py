# Run 3 · their change (Assignment 6). The supplier ships version 2 of the component's facts:
# the same names, but one promise is gone. Your code and tests are not changed.
CHANGE = "The supplier ships version 2 of its product facts. The names are the same, but the promise of an export API for option A is no longer stated."
BEFORE = '("A", "export-api"): "met",'
AFTER = '(removed in version 2: the supplier no longer states this promise)'

def install(ns):
    facts = dict(ns["FACTS"])
    facts.pop(("A", "export-api"), None)
    ns["FACTS"] = facts

def scenario(ns):
    fit, need, short = ns["fit"], ns["evidence_needed"], ns["shortlist"]
    f, e, s = fit("A", "export-api"), need("A"), short(["A", "B"])
    lines = [f"fit('A', 'export-api') = {f!r}", f"evidence_needed('A') = {e!r}", f"shortlist(['A', 'B']) = {s!r}"]
    correct = f == "unknown" and "export-api" in list(e) and "A" not in list(s)
    return lines, correct
