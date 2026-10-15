# Run 3 · their change (Assignment 7). The component team ships version 2: the same call,
# reserve(room_id, duration), but duration is now in milliseconds. Your code and tests are not changed.
CHANGE = "The component team ships version 2. The call is the same, reserve(room_id, duration), but duration is now in milliseconds (1 to 7,200,000)."
BEFORE = 'reserve(room_id, duration)   # duration in seconds, 1..7200'
AFTER = 'reserve(room_id, duration)   # duration in milliseconds, 1..7,200,000'

def install(ns):
    class FakeComponent:
        """Version 2: reserve(room_id, duration) with duration in MILLISECONDS, 1..7,200,000."""
        def __init__(self, end_offset=0):
            self.calls, self.end_offset = [], end_offset
        def reserve(self, room_id, duration):
            self.calls.append((room_id, duration))
            if type(duration) is not int or not 1 <= duration <= 7200000:
                raise ValueError("duration outside the documented contract")
            return {"id": f"R{len(self.calls)}", "start": 0, "end": duration + self.end_offset}
    ns["FakeComponent"] = FakeComponent

def scenario(ns):
    c = ns["FakeComponent"]()
    try:
        ns["reserve_minutes"](c, "Lab-1", 30)
        sent = c.calls[-1][1] if c.calls else None
        lines = [f"reserve_minutes(component version 2, 'Lab-1', 30) sent duration = {sent!r}",
                 f"component version 2 books {sent / 1000:g} seconds" if isinstance(sent, int) else "component version 2 was not called"]
    except BaseException as e:
        sent = None
        lines = [f"reserve_minutes(component version 2, 'Lab-1', 30) raised {type(e).__name__}: {e}"]
    return lines, sent == 1800000
