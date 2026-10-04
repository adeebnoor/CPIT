# Practice build: the loan rule for the lab-equipment desk (not assessed).
# student = {"id": "s1", "loans": 1, "overdue": False}   loans = items the student holds now
# item    = {"id": "cam-3", "available": True}
# Rule: lend only if the item is available, the student holds fewer than LIMIT items and has
# nothing overdue. Anything else, including malformed input, is refused (False).

def can_borrow(student, item):
    return item["available"]   # CHANGE ME: today the desk only checks the shelf

# Your tests: at least three functions whose names start with test_
# The course also runs your tests against known buggy versions: each bug must make one of them fail.
def test_normal_loan_is_allowed():
    assert can_borrow({"id": "s1", "loans": 0, "overdue": False}, {"id": "cam-3", "available": True})
