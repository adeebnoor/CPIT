def _g(ns, n):
    f = ns.get(n); assert callable(f), f"define {n}"
    return f
def live(ns, out):
    d = _g(ns, "display_state")
    assert d({"available": True, "updated": 100}, 102) == "live", "a 2-minute-old available feed is live"
    assert d({"available": True, "updated": 100}, 105) == "live", "exactly at the limit is still live"
def stale(ns, out):
    assert _g(ns, "display_state")({"available": True, "updated": 100}, 106) == "stale", "older than the limit must be stale"
def unavailable(ns, out):
    d = _g(ns, "display_state")
    for f, why in [({"available": False, "updated": 100}, "an unavailable feed"), ({"available": True, "updated": None}, "a feed with no update time"), ({"available": True, "updated": 120}, "an update time in the future")]:
        assert d(f, 110) == "unavailable", f"{why} must be shown as unavailable"
def limit_param(ns, out):
    assert _g(ns, "display_state")({"available": True, "updated": 100}, 108, limit=10) == "live", "use the limit argument"
def honest(ns, out):
    h = _g(ns, "headline")
    assert h({"A": "live", "B": "live"}) == "All feeds live", "all live: say 'All feeds live'"
    t = h({"A": "live", "B": "stale", "C": "unavailable"})
    assert "All feeds live" not in t, "never claim all feeds live when one is not"
    for part in ["B", "stale", "C", "unavailable"]:
        assert part in t, f"the headline must name every feed that is not live with its state (missing {part!r})"

CHECKS = [
    ("a fresh available feed is live", live),
    ("an old feed is stale", stale),
    ("unavailable, missing or future times show as unavailable", unavailable),
    ("the freshness limit is a parameter", limit_param),
    ("the headline never hides a degraded feed", honest),
]
