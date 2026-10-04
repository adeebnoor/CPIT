class ContractError(Exception):
    """Raise this when the component breaks its documented promise."""

class FakeComponent:
    """Behaves as documented: reserve(room_id, duration) with duration in seconds, 1..7200."""
    def __init__(self, end_offset=0):
        self.calls, self.end_offset = [], end_offset
    def reserve(self, room_id, duration):
        self.calls.append((room_id, duration))
        if type(duration) is not int or not 1 <= duration <= 7200:
            raise ValueError("duration outside the documented contract")
        return {"id": f"R{len(self.calls)}", "start": 0, "end": duration + self.end_offset}
