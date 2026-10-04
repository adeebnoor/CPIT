# Assignment 7 build: the adapter between the booking app (minutes) and the component (seconds).
# component.reserve(room_id, duration) expects SECONDS, 1..7200, and returns
# {"id": ..., "start": seconds, "end": seconds}. FakeComponent behaves exactly like that.
# Precondition: minutes is a whole number from 1 to 120, else raise ValueError before calling.
# Postcondition: end - start equals the requested seconds, else raise ContractError.

def reserve_minutes(component, room_id, minutes):
    return component.reserve(room_id, minutes)   # CHANGE ME: today the adapter forwards unchanged

# Your tests: at least three functions whose names start with test_
def test_thirty_minutes():
    c = FakeComponent()
    reserve_minutes(c, "Lab-1", 30)
    assert c.calls == [("Lab-1", 1800)]
