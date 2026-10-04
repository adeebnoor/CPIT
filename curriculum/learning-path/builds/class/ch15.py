# --- helpers ---
SOURCES = {"arabic-ui": "demonstrated",
           "single-sign-on": "brochure"}
# --- buggy ---
def status(feature):
    # anything the vendor mentions counts
    if feature in SOURCES:
        return "met"
    return "unknown"
# --- fixed ---
def status(feature):
    # only a demonstrated instance counts
    if SOURCES.get(feature) == "demonstrated":
        return "met"
    return "unknown"
# --- tests ---
def test_demonstrated_feature_is_met():
    assert status("arabic-ui") == "met"

def test_brochure_claim_is_not_evidence():
    assert status("single-sign-on") == "unknown"

def test_unchecked_feature_is_unknown():
    assert status("export") == "unknown"
