# Run 3 · their change (Assignment 9). Three feeds, each passing its owner's own test. Owner B changes what
# "updated" means without changing the feed version. Your code and tests are not changed.
CHANGE = "Owner B changes what \"updated\" means in feed B, without changing the version number (still v1). It now means minutes since the last update, not the minute of the last update."
BEFORE = '"updated": minute of the last update        # feed B, version v1'
AFTER = '"updated": minutes since the last update    # feed B, version still v1'

def install(ns):
    pass   # the feeds are not part of your code: only the scenario uses them

def scenario(ns):
    now = 102
    feeds = {"A": {"available": True, "updated": 100}, "B": {"available": True, "updated": 100}, "C": {"available": True, "updated": 99}}
    states = {k: ns["display_state"](f, now) for k, f in feeds.items()}
    head = ns["headline"](states)
    lines = ["each owner's own feed test passes: A, B and C",
             "feed B sends updated = 100, which now means 100 minutes since its last update",
             f"your display at minute {now}: " + ", ".join(f"{k} {v}" for k, v in states.items()),
             f"your headline: {head!r}"]
    correct = states.get("B") == "stale" and "All feeds live" not in str(head) and "B" in str(head)
    return lines, correct
