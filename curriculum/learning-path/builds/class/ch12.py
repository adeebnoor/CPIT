# --- buggy ---
# Hazard: automatic trim pushes the nose down. Current design.
tree = OR(
    Event("Angle-of-attack sensor reads wrong", "fact"),
    AND(Event("Trim command repeats", "fact"),
        Event("Crew misses runaway trim", "assumption")),
)
# --- fixed ---
# Revised: a second sensor must also fail to catch the error.
tree = OR(
    AND(Event("Angle-of-attack sensor reads wrong", "fact"),
        Event("Two-sensor cross-check misses it", "proposed")),
    AND(Event("Trim command repeats", "fact"),
        Event("Crew misses runaway trim", "assumption")),
)
# --- tests ---
def test_no_single_event_causes_the_hazard():
    assert single_points(tree) == []
def test_the_sensor_fault_stays_in_the_tree():
    assert any("sensor" in e.name for e in events(tree))
def test_new_control_is_marked_proposed():
    assert any(e.source == "proposed" for e in events(tree))
# --- show ---
cut_sets(tree)
