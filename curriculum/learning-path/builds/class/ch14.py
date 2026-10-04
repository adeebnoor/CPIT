# --- buggy ---
def merge(central, offline):
    # after the outage, add everything recorded on paper
    return central + offline
# --- fixed ---
def merge(central, offline):
    seen, out = {r["id"] for r in central}, list(central)
    for r in offline:
        # identity decides, not content
        if r["id"] not in seen:
            seen.add(r["id"]); out.append(r)
    return out
# --- tests ---
C = [{"id": "r1", "who": "Huda"}]
def test_new_offline_record_is_added():
    assert len(merge(C, [{"id": "r2", "who": "Omar"}])) == 2
def test_record_already_synced_is_not_doubled():
    assert len(merge(C, [{"id": "r1", "who": "Huda"}])) == 1
def test_central_list_is_not_changed():
    merge(C, [{"id": "r2", "who": "Omar"}])
    assert len(C) == 1
