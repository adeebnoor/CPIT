# Assignment 9 · Chapter 20 · Systems of Systems

**Edition:** 2026-09-ch20-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-28  
**Commit ID:** be66e72e-cbd9-47c3-a450-6fa078200234  
**Part A committed:** 2026-10-28T15:15:15.133Z  
**STRESS revealed:** 2026-10-28T15:15:15.145Z

## Scenario
A fictional university wants one screen showing incidents using information from security, transport and facilities.

Each system can work on its own. Each has its own owner and schedule for releasing software updates.
Security sends incident IDs. Transport sends vehicle locations and the time each location was recorded. Facilities sends building-access status.
The owners agree to a limited daytime trial. They have not agreed how old information may be before it is unsuitable, or what the screen should show when a system stops sending data.

Each system passed its own API tests (tests of its program-to-program connection). Nobody has tested a failure involving the systems working together.
An AI assistant's draft design for the transport team — review it before the trial: “The screen asks all three systems for data every minute. It labels the latest value received from each as live. If a system stops sending data, it keeps displaying that system's last value so the screen is never empty. Each owner signs a one-page promise of 99.9% availability. To accept the design, check that every API returns HTTP 200 (a successful response code) and uses the agreed JSON data structure.”

## Chapter boundary sentence (written in the lecture)
Not written in the lecture on this device.

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
    assert 1 == 1


## BUILD RECORD
BUILD RECORD · Assignment 9 (Chapter 20) · 2026-10-28T15:15:14.881Z
Code fingerprint: eac82db7ba76d8c4 (the code above, exactly as run)
Run 2 on this device · previous code fingerprint: d64dd4bae169e8af
Micro-viva change request (from Student ID QA-DESIGN-ONLY): Add a fourth feed, parking, that is unavailable. What does the headline say? Show it with a test.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check
Coverage of your code by your own tests: not measured by this runner.


THEIR CHANGE · run 3 · your code and tests unchanged (fingerprint eac82db7ba76d8c4)
What changed (you did not write it): Owner B changes what "updated" means in feed B, without changing the version number (still v1). It now means minutes since the last update, not the minute of the last update.
  - "updated": minute of the last update        # feed B, version v1
  + "updated": minutes since the last update    # feed B, version still v1
Your tests after their change: 3 of 3 pass
  ✓ test_a
  ✓ test_b
  ✓ test_c
What the shared case shows:



## COVERAGE SENTENCE (COURSE OUTCOME 11)
QA: after run 2 the refusal branch is still not tested; a malformed input would test it.

## THEIR CHANGE · YOUR TESTS
Yes: my tests stayed green after their change

## THEIR CHANGE · THE RESULT
No: the result is no longer correct after their change

## THEIR CHANGE · YOUR SENTENCE
QA: my tests stayed green after their change, but the shared result is no longer correct.

## THEIR CHANGE · RUN 3 RECORD (verified after commitment)
their-v1:eyJoIjoiZWFjODJkYjdiYTc2ZDhjNCIsImdyZWVuIjp0cnVlLCJjb3JyZWN0IjpmYWxzZX0=

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
FIT: 1; INTEGRATE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. TESTS RUN: required (recorded runs and the coverage sentence; longer writing does not replace them). THEIR CHANGE: required (run 3; your answer must match the run; no points). Instructor assessment required.


## Preparation and workload
Required reading: SoS classification and independence: slides 15–20; Data feeds and architecture patterns: slides 48–53
Reported total active minutes (reading, check and assignment): Not reported


## THEIR CHANGE · run 3 verdict
The run showed: your tests stayed green; the result was no longer correct.
Your answer: tests green; result not correct.
THEIR CHANGE row: met. This row adds no points.
