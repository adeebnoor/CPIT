# --- buggy ---
def label(feed, now, limit=5):
    # the last value always looks live
    return f"{feed['name']}: live"
# --- fixed ---
def label(feed, now, limit=5):
    name, at = feed["name"], feed.get("at")
    if not feed.get("connected") or at is None:
        return f"{name}: unavailable"
    age = now - at
    if age <= limit:
        return f"{name}: live"
    return f"{name}: stale, {age} min old"
# --- tests ---
F = {"name": "Lifts", "connected": True,
     "at": 100}
LOST = dict(F, connected=False)

def test_fresh_feed_is_live():
    assert label(F, 103) == "Lifts: live"

def test_old_feed_shows_its_age():
    assert "9 min old" in label(F, 109)

def test_lost_feed_is_not_live():
    assert label(LOST, 101) == "Lifts: unavailable"
