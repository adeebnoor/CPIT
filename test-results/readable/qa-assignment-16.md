# Assignment 7 · Chapter 16 · Component-based Software Engineering

**Edition:** 2026-09-ch16-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-04  
**Commit ID:** d4a901a4-3b5b-4225-92c0-912fe2a0715c  
**Part A committed:** 2026-10-04T21:14:46.444Z  
**STRESS revealed:** 2026-10-04T21:14:46.527Z

## Scenario
A fictional lab-booking application reuses a component with reserve(roomId, duration). The caller supplies duration in minutes. The component documentation defines duration in seconds, requires 1 ≤ duration ≤ 7200, and says an accepted call returns a reservation identifier. A thin adapter currently forwards both arguments unchanged. A sample call using duration = 30 returns an identifier. No test has checked the stored end time or invalid-input behavior. Recommend whether to use, adapt or replace the component for a limited pilot.

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## CONTRACT
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
BUILD RECORD · Assignment 7 (Chapter 16) · 2026-10-04T21:14:46.277Z
Code fingerprint: d64dd4bae169e8af (the code above, exactly as run)
Micro-viva change request (from Student ID QA-DESIGN-ONLY): The maximum becomes 90 minutes. Change one thing and show the test that proves it.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check


## STRESS
QA evidence for chapter 16: this opens automatically after commitment.

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
FIT: 1; CONTRACT: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Composition types: slides 40–43; Interface semantics and OCL: slides 51–55
Reported total active minutes (reading, check and assignment): Not reported
