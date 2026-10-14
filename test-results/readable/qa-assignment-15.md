# Assignment 6 · Chapter 15 · Software Reuse

**Edition:** 2026-09-ch15-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-14  
**Commit ID:** 9bdc99c2-e78a-497c-b0be-f89bdc90256f  
**Part A committed:** 2026-10-14T20:26:13.670Z  
**STRESS revealed:** 2026-10-14T20:26:13.683Z

## Scenario
A fictional faculty needs a room-booking service for a three-year trial (pilot), starting next term.

Option A is a ready-made commercial product that the team can configure. It has the required booking features and an export API (a way for another program to retrieve data). The supplier promises support for two years.
Option B is an existing university application. The university owns its source code, and the team knows that code. It cannot yet create repeating bookings. There are no measurements of how it performs at the busiest times.
Neither option has a reliable estimate of the full cost over its use, including support and later changes.

The goal is a trial next term, not replacing the faculty's whole system. Recommend an option, a limited evaluation, or a hold.
A colleague's draft recommendation — review it; do not copy it: “Choose Option A for the whole faculty next term. It already has all the booking features, so changing its settings will be enough. Two years of support is fine for a three-year trial: we can simply renew it. Finishing Option B would take too long; the team's knowledge of its code makes no difference. Option A clearly costs less overall because it is ready-made.”

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
BUILD RECORD · Assignment 6 (Chapter 15) · 2026-10-14T20:26:13.457Z
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
