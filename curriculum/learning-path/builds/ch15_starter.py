# Assignment 6 build: an evidence-only fit check for the colleague's draft.
# FACTS[(option, requirement)] is "met" or "gap", read only from the scenario. REQUIREMENTS lists what the pilot needs.
# A requirement the facts do not settle is "unknown". Unknown never counts as met.

def fit(option, requirement):
    return FACTS.get((option, requirement), "met")   # CHANGE ME: brochure reading

def shortlist(options):
    """Options with no known gap and no unknown requirement."""
    return [o for o in options if all(fit(o, r) != "gap" for r in REQUIREMENTS)]   # CHANGE ME

def evidence_needed(option):
    """The requirements still unknown for this option, in REQUIREMENTS order."""
    return []   # CHANGE ME

# Your tests: at least three functions whose names start with test_
# The course also runs your tests against known buggy versions: each bug must make one of them fail.
def test_known_gap():
    assert fit("A", "support-3-years") == "gap"
