# --- buggy ---
def label(feed, now, limit=5):
    # the last value always looks live
    return f"{feed['name']}: {feed['value']} (live)"
# --- fixed ---
def label(feed, now, limit=5):
    if not feed.get("connected") or feed.get("at") is None:
        return f"{feed['name']}: unavailable"
    age = now - feed["at"]
    state = "live" if age <= limit else f"stale, {age} min old"
    return f"{feed['name']}: {feed['value']} ({state})"
# --- tests ---
F = {"name": "Lifts", "value": "2 down", "connected": True, "at": 100}
def test_fresh_feed_is_live():
    assert label(F, 103).endswith("(live)")
def test_old_feed_shows_its_age():
    assert "stale, 9 min old" in label(F, 109)
def test_lost_feed_is_not_shown_as_live():
    assert label(dict(F, connected=False), 101).endswith("unavailable")
