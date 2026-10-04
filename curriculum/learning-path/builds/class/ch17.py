# --- buggy ---
class Payments:
    def __init__(self, store):
        self.store = store; store.setdefault("charges", [])
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
        if request_id in self.store["done"]:     # a retry
            return self.store["done"][request_id]
        self.store["charges"].append(amount)
        rid = len(self.store["charges"])
        self.store["done"][request_id] = rid
        return rid
# --- tests ---
def test_two_payments_make_two_charges():
    st = {}; p = Payments(st); p.pay("a", 50); p.pay("b", 50)
    assert len(st["charges"]) == 2
def test_retry_after_lost_reply_charges_once():
    st = {}; p = Payments(st); p.pay("a", 50); p.pay("a", 50)
    assert len(st["charges"]) == 1
def test_retry_after_restart_charges_once():
    st = {}; Payments(st).pay("a", 50); Payments(st).pay("a", 50)
    assert len(st["charges"]) == 1
