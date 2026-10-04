# Assignment 9 build: honest feed display for the shared dashboard.
# feed = {"available": True or False, "updated": minute of the last update, or None}
# display_state: "unavailable" if the feed is unavailable, has no update time, or its update
# time is in the future; "stale" if it is older than limit minutes; otherwise "live".
# headline(states): "All feeds live" only when every feed is live; otherwise name every
# feed that is not live with its state, for example "Degraded: B stale, C unavailable".

def display_state(feed, now, limit=LIMIT):
    return "live"   # CHANGE ME: the proposed design shows every feed as live

def headline(states):
    return "All feeds live"   # CHANGE ME

# Your tests: at least three functions whose names start with test_
# The course also runs your tests against known buggy versions: each bug must make one of them fail.
def test_fresh_feed_is_live():
    assert display_state({"available": True, "updated": 100}, now=102) == "live"
