# Known bugs. Your own tests must catch each one (at least one of your tests fails).
MUTANTS = [
    ("every call books again", '''
class BookingService:
    def __init__(self, store):
        self.store = store
        store.setdefault("reservations", {})
    def reserve(self, request_id, user, event):
        if not request_id:
            raise ValueError("request_id is required")
        rid = f"R{len(self.store['reservations']) + 1}"
        self.store["reservations"][rid] = {"user": user, "event": event}
        return rid
'''),
    ("request ids are remembered in memory only, so a restart books again", '''
class BookingService:
    def __init__(self, store):
        self.store, self.seen = store, {}
        store.setdefault("reservations", {})
    def reserve(self, request_id, user, event):
        if not request_id:
            raise ValueError("request_id is required")
        if request_id in self.seen:
            return self.seen[request_id]
        rid = f"R{len(self.store['reservations']) + 1}"
        self.store["reservations"][rid] = {"user": user, "event": event}
        self.seen[request_id] = rid
        return rid
'''),
    ("a missing request id is accepted", '''
class BookingService:
    def __init__(self, store):
        self.store = store
        store.setdefault("reservations", {})
        store.setdefault("requests", {})
    def reserve(self, request_id, user, event):
        if request_id in self.store["requests"]:
            return self.store["requests"][request_id]
        rid = f"R{len(self.store['reservations']) + 1}"
        self.store["reservations"][rid] = {"user": user, "event": event}
        self.store["requests"][request_id] = rid
        return rid
'''),
]
