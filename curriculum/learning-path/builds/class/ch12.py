# --- buggy ---
# Hazard: trim pushes the nose down.
# Current design:
tree = OR(
    Event("AoA sensor reads wrong", "fact"),
    AND(Event("Trim command repeats", "fact"),
        Event("Crew misses runaway trim",
              "assumption")),
)
# --- fixed ---
# Revised: a second sensor must also miss it.
tree = OR(
    AND(Event("AoA sensor reads wrong", "fact"),
        Event("Cross-check misses it",
              "proposed")),
    AND(Event("Trim command repeats", "fact"),
        Event("Crew misses runaway trim",
              "assumption")),
)
# --- tests ---
def test_no_single_event_causes_hazard():
    assert single_points(tree) == []

def test_sensor_fault_stays_in_tree():
    names = [e.name for e in events(tree)]
    assert "AoA sensor reads wrong" in names

def test_new_control_marked_proposed():
    tags = [e.source for e in events(tree)]
    assert "proposed" in tags
# --- show ---
cut_sets(tree)
