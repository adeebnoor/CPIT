# --- helpers ---
class Pump:
    """Documented contract: infuse(ml), ml a whole number from 1 to 5000."""
    def __init__(self):
        self.calls = []
    def infuse(self, ml):
        self.calls.append(ml)
        return ml
# --- buggy ---
def give(pump, litres):
    # the types match: a number is a number
    return pump.infuse(litres)
# --- fixed ---
def give(pump, litres):
    # precondition: checked before the call
    ok = type(litres) in (int, float) and 0.001 <= litres <= 5
    if not ok:
        raise ValueError("litres must be 0.001 to 5")
    ml = round(litres * 1000)
    # postcondition: checked on the result
    if pump.infuse(ml) != ml:
        raise RuntimeError("pump broke its promise")
    return ml
# --- tests ---
def test_half_litre_reaches_pump_as_500_ml():
    p = Pump(); give(p, 0.5)
    assert p.calls == [500]
def test_too_much_is_refused_before_the_call():
    p = Pump()
    try:
        give(p, 9); assert False, "accepted"
    except ValueError:
        assert p.calls == []
def test_zero_is_refused():
    p = Pump()
    try:
        give(p, 0); assert False, "accepted"
    except ValueError:
        assert p.calls == []
