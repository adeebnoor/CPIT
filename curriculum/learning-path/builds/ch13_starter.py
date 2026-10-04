# Assignment 4 build: the server-side authorization rule for the project portal.
# user    = {"id": "s1", "role": "student" or "staff", "groups": ["G1", ...]}
# project = {"id": "p7", "owner": "s1", "group": "G1"}
# Rule: a student may read only a project they own. Staff may read only projects in a
# group assigned to them. Anything else, including malformed input, is refused (False).

def can_read(user, project):
    return True   # CHANGE ME: today the API serves any project identifier it receives

# Your tests: at least three functions whose names start with test_
# Include at least two requests that must be refused.
def test_owner_can_read():
    assert can_read({"id": "s1", "role": "student", "groups": []},
                    {"id": "p1", "owner": "s1", "group": "G1"})
