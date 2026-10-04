# --- helpers ---
SOURCES = {"arabic-ui": "demonstrated", "single-sign-on": "brochure"}
# --- buggy ---
def status(feature):
    # anything the vendor mentions counts
    return "met" if feature in SOURCES else "unknown"
# --- fixed ---
def status(feature):
    # only a demonstrated instance counts as met
    shown = SOURCES.get(feature) == "demonstrated"
    return "met" if shown else "unknown"
# --- tests ---
def test_demonstrated_feature_is_met():
    assert status("arabic-ui") == "met"
def test_brochure_claim_is_not_evidence():
    assert status("single-sign-on") == "unknown"
def test_unchecked_feature_is_unknown():
    assert status("export") == "unknown"
