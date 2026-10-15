# Run 3 · their change (Assignment 8). The remote app ships a new release: after a lost reply it
# sends the same booking again, but with a NEW request_id. Your code and tests are not changed.
CHANGE = "The remote app ships a new release. After a lost reply it sends the same booking again, but with a new request_id."
BEFORE = 'retry after a lost reply: send the same request_id'
AFTER = 'retry after a lost reply: send a new request_id'

def install(ns):
    pass   # the remote app is not part of your code: only the scenario uses it

def scenario(ns):
    store = {}
    s = ns["BookingService"](store)
    first = s.reserve("pay-7f3a", "u1", "E1")      # the reply to this call is lost
    second = s.reserve("pay-91c2", "u1", "E1")     # the remote app retries the same action with a new id
    n = len(store.get("reservations", {})) if isinstance(store.get("reservations"), dict) else None
    lines = [f"first send (reply lost): reserve('pay-7f3a', 'u1', 'E1') = {first!r}",
             f"retry with a new request id: reserve('pay-91c2', 'u1', 'E1') = {second!r}",
             f"reservations in the store for this one user action: {n if n is not None else 'not readable'}"]
    return lines, first == second
