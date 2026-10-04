# --- buggy ---
def merge(central, offline):
    # add everything written on paper
    return central + offline
# --- fixed ---
def merge(central, offline):
    seen = {r["id"] for r in central}
    out = list(central)
    for r in offline:
        # identity decides, not content
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out
# --- tests ---
C = [{"id": "r1", "who": "Huda"}]
NEW = {"id": "r2", "who": "Omar"}
SAME = {"id": "r1", "who": "Huda"}

def test_new_offline_record_is_added():
    assert len(merge(C, [NEW])) == 2

def test_synced_record_is_not_doubled():
    assert len(merge(C, [SAME])) == 1

def test_central_list_is_not_changed():
    merge(C, [NEW])
    assert len(C) == 1
