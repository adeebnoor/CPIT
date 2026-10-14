# Assignment 4 · Chapter 13 · Security Engineering

**Edition:** 2026-09-ch13-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-14  
**Commit ID:** 43f42e5c-f224-4823-a36c-52ded782153d  
**Part A committed:** 2026-10-14T20:26:06.442Z  
**STRESS revealed:** 2026-10-14T20:26:06.454Z

## Scenario
A fictional university website stores student project files. It has two user roles: student and staff.

Students may read only their own project files. Staff may read files only for the groups assigned to them.
The screen hides other students' files. A developer says all normal upload and download tests passed.
Each request sent to the server includes a project ID (the value that identifies a project). The API is the way the website sends these requests. The brief includes no test of a user requesting someone else's project.
The system is set up to keep activity logs (records of what happened). Nobody has checked a sample for private information.

Your decision: release the service, allow only limited access, or hold the release. Explain your choice using the facts above.

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## TEST
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 40: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BUILD PLAN
QA: the build enforces the rule; tests cover a normal, an edge and a refused case.

## PYTHON BUILD (CODE AND TESTS)
def test_a():
    assert True


## BUILD RECORD
BUILD RECORD · Assignment 4 (Chapter 13) · 2026-10-14T20:26:06.258Z
Code fingerprint: d64dd4bae169e8af (the code above, exactly as run)
Micro-viva change request (from Student ID QA-DESIGN-ONLY): Remove your malformed-input handling and run again. Which known bug is no longer caught, and why?
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check


## STRESS
QA evidence for chapter 13: this opens automatically after commitment.

## Boundary status — INTACT

## REFIT — RETAIN
QA: the changed evidence breaks the shared-dependency assumption, so revise the boundary and require an independent check.

## Final engineering decision record
QA: keep the model advisory-only; a human owner checks independently. Verify version and workload, record missing tests and reopen the decision when assumptions change.

## AI-use declaration
No AI used.

## Human review
Name: QA test  
Attested: Yes — reviewed and responsibility accepted

## Rubric — 5 points
FIT: 1; TEST: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Misuse cases and requirements: slides 40–43; Secure design principles: slides 44–47
Reported total active minutes (reading, check and assignment): Not reported
