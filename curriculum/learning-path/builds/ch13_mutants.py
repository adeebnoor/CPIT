# Known bugs. Your own tests must catch each one (at least one of your tests fails).
MUTANTS = [
    ("the group is enough for a student (the hidden-link bug)", '''
def can_read(user, project):
    try:
        if user["role"] in ("student", "staff"):
            return project["group"] in user["groups"]
    except Exception:
        return False
    return False
'''),
    ("any staff member can read any project", '''
def can_read(user, project):
    try:
        if user["role"] == "staff":
            return True
        if user["role"] == "student":
            return project["owner"] == user["id"]
    except Exception:
        return False
    return False
'''),
    ("an unknown role is treated like staff", '''
def can_read(user, project):
    try:
        if user["role"] == "student":
            return project["owner"] == user["id"]
        return project["group"] in user["groups"]
    except Exception:
        return False
'''),
    ("malformed input crashes instead of being refused", '''
def can_read(user, project):
    if user["role"] == "student":
        return project["owner"] == user["id"]
    if user["role"] == "staff":
        return project["group"] in user["groups"]
    return False
'''),
]
