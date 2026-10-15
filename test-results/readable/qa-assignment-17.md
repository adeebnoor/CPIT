# Assignment 8 · Chapter 17 · Distributed Software Engineering

**Edition:** 2026-09-ch17-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-15  
**Commit ID:** ae4e6d2c-7860-43d2-a2bc-90260f49ebb6  
**Part A committed:** 2026-10-15T05:42:21.848Z  
**STRESS revealed:** 2026-10-15T05:42:21.860Z

## Scenario
A fictional event-booking system has three parts: a browser, an application service that handles requests, and a database that stores bookings.

The browser sends a booking request through the service. If no reply arrives before the waiting time ends (timeout), the browser sends the request again with a new request ID.
The database creates one reservation for each new request ID.
Normal requests have succeeded. Nobody has tested what happens if the database saves a booking but the reply is then lost.

Recommend how these parts should work together in a trial, and the rule for sending a request again (retry).

## Chapter boundary sentence (written in the lecture)
Not written in the lecture on this device.

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## FAILURE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 29: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BUILD PLAN
QA: the build enforces the rule; tests cover a normal, an edge and a refused case.

## PYTHON BUILD (CODE AND TESTS)
def test_a():
    assert 1 == 1


## BUILD RECORD
BUILD RECORD · Assignment 8 (Chapter 17) · 2026-10-15T05:42:21.664Z
Code fingerprint: eac82db7ba76d8c4 (the code above, exactly as run)
Run 2 on this device · previous code fingerprint: d64dd4bae169e8af
Micro-viva change request (from Student ID QA-DESIGN-ONLY): Remove the persistence of request ids and run again. Which test fails first, and which real failure is it?
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
QA evidence for chapter 17: this opens automatically after commitment.

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
FIT: 1; FAILURE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. TESTS RUN: required (recorded runs and the coverage sentence; longer writing does not replace them). Instructor assessment required.


## Preparation and workload
Required reading: Distributed architectural patterns: slides 29–34; SaaS and service delivery: slides 53–58
Reported total active minutes (reading, check and assignment): Not reported
