# --- helpers ---
class Pump:
    """Contract: infuse(ml), 1 to 5000 ml."""
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
    # precondition: before the call
    ok = type(litres) in (int, float)
    if not (ok and 0.001 <= litres <= 5):
        raise ValueError("0.001 to 5 litres")
    ml = round(litres * 1000)
    # postcondition: on the result
    if pump.infuse(ml) != ml:
        raise RuntimeError("pump broke contract")
    return ml
# --- tests ---
def test_half_litre_is_500_ml():
    p = Pump()
    give(p, 0.5)
    assert p.calls == [500]

def test_too_much_refused_before_call():
    p = Pump()
    try:
        give(p, 9)
        assert False, "accepted"
    except ValueError:
        assert p.calls == []

def test_zero_is_refused():
    p = Pump()
    try:
        give(p, 0)
        assert False, "accepted"
    except ValueError:
        assert p.calls == []
