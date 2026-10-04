# --- buggy ---
class Payments:
    def __init__(self, store):
        self.store = store
        store.setdefault("charges", [])
    def pay(self, request_id, amount):
        # every call charges
        self.store["charges"].append(amount)
        return len(self.store["charges"])
# --- fixed ---
class Payments:
    def __init__(self, store):
        self.store = store
        store.setdefault("charges", [])
        store.setdefault("done", {})
    def pay(self, request_id, amount):
        done = self.store["done"]
        if request_id in done:   # a retry
            return done[request_id]
        self.store["charges"].append(amount)
        done[request_id] = len(done) + 1
        return done[request_id]
# --- tests ---
def test_two_payments_two_charges():
    st = {}
    p = Payments(st)
    p.pay("a", 50)
    p.pay("b", 50)
    assert len(st["charges"]) == 2

def test_retry_after_lost_reply():
    st = {}
    p = Payments(st)
    p.pay("a", 50)
    p.pay("a", 50)   # same request id
    assert len(st["charges"]) == 1

def test_retry_after_restart():
    st = {}
    Payments(st).pay("a", 50)
    Payments(st).pay("a", 50)   # new process
    assert len(st["charges"]) == 1
