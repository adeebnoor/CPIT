# Assignment 7 · Chapter 16 · Component-based Software Engineering

**Edition:** 2026-09-ch16-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-14  
**Commit ID:** 0402ad98-8957-4f53-9835-4ab8ef8adec8  
**Part A committed:** 2026-10-14T20:26:17.308Z  
**STRESS revealed:** 2026-10-14T20:26:17.319Z

## Scenario
A fictional lab-booking app uses an existing software component with the function reserve(roomId, duration).

The app sends duration in minutes. The component's instructions say duration is in seconds and must be between 1 and 7200, inclusive. An accepted request returns a reservation ID.
A small connecting function (adapter) currently passes both values to the component without changing them.
A sample request with duration = 30 returns an ID. Nobody has tested the saved end time or what happens with invalid input.

Your decision: use the component, adapt the connection, replace the component, or hold the limited trial. Explain what must be checked before relying on it.

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
BUILD RECORD · Assignment 7 (Chapter 16) · 2026-10-14T20:26:17.123Z
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
