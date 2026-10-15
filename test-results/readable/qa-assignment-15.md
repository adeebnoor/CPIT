# Assignment 6 · Chapter 15 · Software Reuse

**Edition:** 2026-09-ch15-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-15  
**Commit ID:** 769331eb-ae90-489f-bd8b-f8448f7e1534  
**Part A committed:** 2026-10-15T05:42:14.615Z  
**STRESS revealed:** 2026-10-15T05:42:14.627Z

## Scenario
A fictional faculty needs a room-booking service for a three-year trial (pilot), starting next term.

Option A is a ready-made commercial product that the team can configure. It has the required booking features and an export API (a way for another program to retrieve data). The supplier promises support for two years.
Option B is an existing university application. The university owns its source code, and the team knows that code. It cannot yet create repeating bookings. There are no measurements of how it performs at the busiest times.
Neither option has a reliable estimate of the full cost over its use, including support and later changes.

The goal is a trial next term, not replacing the faculty's whole system. Recommend an option, a limited evaluation, or a hold.
A colleague's draft recommendation — review it; do not copy it: “Choose Option A for the whole faculty next term. It already has all the booking features, so changing its settings will be enough. Two years of support is fine for a three-year trial: we can simply renew it. Finishing Option B would take too long; the team's knowledge of its code makes no difference. Option A clearly costs less overall because it is ready-made.”

## Chapter boundary sentence (written in the lecture)
Not written in the lecture on this device.

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
    assert 1 == 1


## BUILD RECORD
BUILD RECORD · Assignment 6 (Chapter 15) · 2026-10-15T05:42:14.463Z
Code fingerprint: eac82db7ba76d8c4 (the code above, exactly as run)
Run 2 on this device · previous code fingerprint: d64dd4bae169e8af
Micro-viva change request (from Student ID QA-DESIGN-ONLY): The vendor sends a measured peak-load report for Option A that passes. Change one fact and show the new shortlist.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check
Coverage of your code by your own tests: not measured by this runner.


## COVERAGE SENTENCE (COURSE OUTCOME 11)
QA: after run 2 the refusal branch is still not tested; a malformed input would test it.

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
FIT: 1; COMPARE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. TESTS RUN: required (recorded runs and the coverage sentence; longer writing does not replace them). Instructor assessment required.


## Preparation and workload
Required reading: Reuse approaches and planning: slides 12–15; Frameworks and inversion of control: slides 16–21
Reported total active minutes (reading, check and assignment): Not reported
