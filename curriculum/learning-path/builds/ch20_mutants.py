# Known bugs. Your own tests must catch each one (at least one of your tests fails).
_HEAD = '''
def headline(states):
    bad = [f"{k} {v}" for k, v in states.items() if v != "live"]
    return "All feeds live" if not bad else "Degraded: " + ", ".join(bad)
'''
MUTANTS = [
    ("an unavailable feed keeps showing its last value", '''
def display_state(feed, now, limit=LIMIT):
    u = feed.get("updated")
    if u is None or u > now:
        return "unavailable"
    return "stale" if now - u > limit else "live"
''' + _HEAD),
    ("a feed exactly at the limit is shown as stale", '''
def display_state(feed, now, limit=LIMIT):
    u = feed.get("updated")
    if not feed.get("available") or u is None or u > now:
        return "unavailable"
    return "stale" if now - u >= limit else "live"
''' + _HEAD),
    ("an update time in the future is shown as live", '''
def display_state(feed, now, limit=LIMIT):
    u = feed.get("updated")
    if not feed.get("available") or u is None:
        return "unavailable"
    return "stale" if now - u > limit else "live"
''' + _HEAD),
    ("the headline hides a stale feed", '''
def display_state(feed, now, limit=LIMIT):
    u = feed.get("updated")
    if not feed.get("available") or u is None or u > now:
        return "unavailable"
    return "stale" if now - u > limit else "live"
def headline(states):
    bad = [f"{k} {v}" for k, v in states.items() if v == "unavailable"]
    return "All feeds live" if not bad else "Degraded: " + ", ".join(bad)
'''),
]
