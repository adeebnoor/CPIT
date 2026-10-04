# Assignment 5 build: reconcile the controlled paper log after the central server recovers.
# central   = {"P12": {"time": "08:15", "version": 3}, ...}
# paper_log = [{"change_id": "c1", "pickup_id": "P12", "time": "08:40", "base_version": 3}, ...]
# Rules: apply each change once (same change_id twice = once). If the central version moved
# since the change was written (version != base_version), do not overwrite: record a conflict.
# A pickup missing centrally is added (base_version 0). Each applied change adds 1 to version.
# Return (new_central, conflicts): conflicts is a list of change_ids. Do not modify the inputs.

def reconcile(central, paper_log):
    new = dict(central)
    for c in paper_log:
        new[c["pickup_id"]] = {"time": c["time"], "version": c["base_version"] + 1}
    return new, []   # CHANGE ME

# Your tests: at least three functions whose names start with test_
def test_one_change_is_applied():
    new, conflicts = reconcile({"P1": {"time": "08:00", "version": 1}},
                               [{"change_id": "c1", "pickup_id": "P1", "time": "08:30", "base_version": 1}])
    assert new["P1"] == {"time": "08:30", "version": 2} and conflicts == []
