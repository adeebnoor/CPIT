# --- buggy ---
def can_view(user, grade):
    # the page shows each student only a link to their own grade
    return user.get("logged_in", False)
# --- fixed ---
def can_view(user, grade):
    try:
        if user["role"] == "student":
            return grade["student"] == user["id"]
        if user["role"] == "instructor":
            return grade["course"] in user["courses"]
    except (KeyError, TypeError):
        pass
    return False   # fail-safe default
# --- tests ---
ALI  = {"id": "s1", "role": "student", "logged_in": True}
SARA = {"id": "s2", "role": "student", "logged_in": True}
G = {"student": "s1", "course": "CPIT-455"}
def test_own_grade_is_allowed():
    assert can_view(ALI, G)
def test_another_student_is_refused():
    assert can_view(SARA, G) is False
def test_broken_request_is_refused():
    assert can_view({}, G) is False
