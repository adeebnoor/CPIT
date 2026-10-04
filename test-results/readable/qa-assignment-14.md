# Assignment 5 · Chapter 14 · Resilience Engineering

**Edition:** 2026-09-ch14-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-04  
**Commit ID:** 3612e217-14e8-45e4-8c63-3d09fa73e6f7  
**Part A committed:** 2026-10-04T17:23:05.203Z  
**STRESS revealed:** 2026-10-04T17:23:05.285Z

## Scenario
A fictional campus transport desk must retain access to the day’s pickup list when its central scheduling server is unavailable. A local copy is refreshed at 06:00. Authorized staff can read it on a desk device. Changes after 06:00 normally remain on the central server until the next refresh. The brief includes a successful restart log for a backup server, but no full service rehearsal. Staff can record changes on a controlled paper form during an outage. You recommend whether this fallback is ready for a limited trial.

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## RECOVER
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 18: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BUILD PLAN
QA: the build enforces the rule; tests cover a normal, an edge and a refused case.

## PYTHON BUILD (CODE AND TESTS)
def test_a():
    assert True


## BUILD RECORD
BUILD RECORD · Assignment 5 (Chapter 14) · 2026-10-04T17:23:05.037Z
Code fingerprint: d64dd4bae169e8af (the code above, exactly as run)
Micro-viva change request (from Student ID QA-DESIGN-ONLY): Return conflicts with the pickup id as well as the change id. Change the code and one test.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check


## STRESS
QA evidence for chapter 14: this opens automatically after commitment.

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
FIT: 1; RECOVER: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Sociotechnical and organizational resilience: slides 18–23; Survivability analysis: slides 42–45
Reported total active minutes (reading, check and assignment): Not reported
