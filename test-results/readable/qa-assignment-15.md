# Assignment 6 · Chapter 15 · Software Reuse

**Edition:** 2026-09-ch15-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-04  
**Commit ID:** bca63d38-09bc-4d90-b91e-f01d999b708c  
**Part A committed:** 2026-10-04T20:43:54.922Z  
**STRESS revealed:** 2026-10-04T20:43:55.003Z

## Scenario
A fictional faculty needs a room-booking service for a three-year pilot. Option A is a configurable commercial product with the required booking functions and an export API; its support commitment ends after two years. Option B is an existing university application with an owned codebase, but it lacks recurring bookings and has no measured peak-load results. The team knows the university codebase. No reliable total-cost estimates have been supplied. The target is a pilot next term, not a complete enterprise replacement. Recommend an option, a restricted evaluation or a hold.Colleague’s draft recommendation · review it, do not copy it: “Choose Option A for the whole faculty from next term. It already has every booking function we need, so configuration is enough. Support ending after two years is not a problem for a three-year pilot: we will simply renew. Option B would take too long to finish, and the team’s knowledge of it does not change that. Total cost is clearly lower for A because it is ready.”

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## COMPARE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 12: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BUILD PLAN
QA: the build enforces the rule; tests cover a normal, an edge and a refused case.

## PYTHON BUILD (CODE AND TESTS)
def test_a():
    assert True


## BUILD RECORD
BUILD RECORD · Assignment 6 (Chapter 15) · 2026-10-04T20:43:54.754Z
Code fingerprint: d64dd4bae169e8af (the code above, exactly as run)
Micro-viva change request (from Student ID QA-DESIGN-ONLY): The vendor sends a measured peak-load report for Option A that passes. Change one fact and show the new shortlist.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check


## STRESS
QA evidence for chapter 15: this opens automatically after commitment.

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
FIT: 1; COMPARE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Reuse approaches and planning: slides 12–15; Frameworks and inversion of control: slides 16–21
Reported total active minutes (reading, check and assignment): Not reported
