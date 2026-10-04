# Assignment 8 build: an idempotent booking service.
# The app sends one request_id per user action and reuses it on every retry.
# store survives restarts. reserve() must create at most one reservation per request_id
# and return the same reservation id when the request is repeated. Reject a missing request_id.

class BookingService:
    def __init__(self, store):
        self.store = store
        store.setdefault("reservations", {})

    def reserve(self, request_id, user, event):
        rid = f"R{len(self.store['reservations']) + 1}"   # CHANGE ME: every call books again
        self.store["reservations"][rid] = {"user": user, "event": event}
        return rid

# Your tests: at least three functions whose names start with test_
# The course also runs your tests against known buggy versions: each bug must make one of them fail.
def test_two_actions_two_bookings():
    s = BookingService({})
    assert s.reserve("a", "u1", "E1") != s.reserve("b", "u1", "E1")
