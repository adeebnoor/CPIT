# Known bugs. Your own tests must catch each one (at least one of your tests fails).
MUTANTS = [
    ("off by one: a third item is lent", '''
def can_borrow(student, item):
    try:
        return bool(item["available"]) and type(student["loans"]) is int and student["loans"] <= LIMIT and student["overdue"] is False
    except Exception:
        return False
'''),
    ("an overdue item is ignored", '''
def can_borrow(student, item):
    try:
        return bool(item["available"]) and type(student["loans"]) is int and student["loans"] < LIMIT
    except Exception:
        return False
'''),
    ("malformed input crashes instead of being refused", '''
def can_borrow(student, item):
    return bool(item["available"]) and student["loans"] < LIMIT and student["overdue"] is False
'''),
]
