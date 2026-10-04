# Assignment 3 · Chapter 12 · Safety Engineering

**Edition:** 2026-09-ch12-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-04  
**Commit ID:** 3a872864-2731-48ab-9106-479fc0b8b242  
**Part A committed:** 2026-10-04T22:06:02.209Z  
**STRESS revealed:** 2026-10-04T22:06:02.222Z

## Scenario
A fictional campus is evaluating an automatic loading-bay barrier. The proposed safety requirement is: the barrier must not close while the monitored zone is occupied. A prototype has passed the recorded daylight tests with an unobstructed camera. The test report does not include low light, rain or a covered lens. A separate stop button exists, but no drill report shows how quickly an operator can recognize a hazard and use it. Deployment is proposed for both day and night. You advise the service owner: release, restrict the pilot, or hold.

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## TRACE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 25: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BUILD PLAN
QA: the build enforces the rule; tests cover a normal, an edge and a refused case.

## PYTHON BUILD (CODE AND TESTS)
def test_a():
    assert True


## BUILD RECORD
BUILD RECORD · Assignment 3 (Chapter 12) · 2026-10-04T22:06:02.042Z
Code fingerprint: d64dd4bae169e8af (the code above, exactly as run)
Micro-viva change request (from Student ID QA-DESIGN-ONLY): Remove your proposed control from revised and run again. Which check fails, and what does it say about the barrier?
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check


## STRESS
QA evidence for chapter 12: this opens automatically after commitment.

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
FIT: 1; TRACE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Fault-tree reasoning and reduction: slides 25–30; Static analysis: slides 50–53
Reported total active minutes (reading, check and assignment): Not reported
