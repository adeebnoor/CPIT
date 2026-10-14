# Assignment 9 · Chapter 20 · Systems of Systems

**Edition:** 2026-09-ch20-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-14  
**Commit ID:** abe7d78b-c162-4ed4-ac4e-f231c53b07e0  
**Part A committed:** 2026-10-14T20:26:24.557Z  
**STRESS revealed:** 2026-10-14T20:26:24.570Z

## Scenario
A fictional university wants one screen showing incidents using information from security, transport and facilities.

Each system can work on its own. Each has its own owner and schedule for releasing software updates.
Security sends incident IDs. Transport sends vehicle locations and the time each location was recorded. Facilities sends building-access status.
The owners agree to a limited daytime trial. They have not agreed how old information may be before it is unsuitable, or what the screen should show when a system stops sending data.

Each system passed its own API tests (tests of its program-to-program connection). Nobody has tested a failure involving the systems working together.
The transport team's proposed design — review it before the trial: “The screen asks all three systems for data every minute. It labels the latest value received from each as live. If a system stops sending data, it keeps displaying that system's last value so the screen is never empty. Each owner signs a one-page promise of 99.9% availability. To accept the design, check that every API returns HTTP 200 (a successful response code) and uses the agreed JSON data structure.”

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## INTEGRATE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 15: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BUILD PLAN
QA: the build enforces the rule; tests cover a normal, an edge and a refused case.

## PYTHON BUILD (CODE AND TESTS)
def test_a():
    assert True


## BUILD RECORD
BUILD RECORD · Assignment 9 (Chapter 20) · 2026-10-14T20:26:24.356Z
Code fingerprint: d64dd4bae169e8af (the code above, exactly as run)
Micro-viva change request (from Student ID QA-DESIGN-ONLY): Add a fourth feed, parking, that is unavailable. What does the headline say? Show it with a test.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check


## STRESS
QA evidence for chapter 20: this opens automatically after commitment.

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
FIT: 1; INTEGRATE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: SoS classification and independence: slides 15–20; Data feeds and architecture patterns: slides 48–53
Reported total active minutes (reading, check and assignment): Not reported
