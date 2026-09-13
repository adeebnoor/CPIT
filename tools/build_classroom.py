"""Validate the instructor's lecture; automatic generation is disabled.

This compatibility command never writes classroom artifacts. New releases need
explicit authoring and an instructor-approved update to publication.json.
"""
from audit_classroom import main

if __name__ == "__main__":
    print("Automatic lesson generation is disabled; validating without modifying approved files.")
    raise SystemExit(main())
