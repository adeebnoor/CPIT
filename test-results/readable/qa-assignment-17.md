# Assignment 8 · Chapter 17 · Distributed Software Engineering

**Edition:** 2026-09-ch17-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-24  
**Commit ID:** 99a4a71e-aeed-4656-b816-bac9a6e6052b  
**Part A committed:** 2026-10-24T19:10:39.947Z  
**STRESS revealed:** 2026-10-24T19:10:39.961Z

## Scenario
A fictional event-booking system has three parts: a browser, an application service that handles requests, and a database that stores bookings.

The browser sends a booking request through the service. If no reply arrives before the waiting time ends (timeout), the browser sends the request again with a new request ID.
The database creates one reservation for each new request ID.
Normal requests have succeeded. Nobody has tested what happens if the database saves a booking but the reply is then lost.

Recommend how these parts should work together in a trial, and the rule for sending a request again (retry).
An AI assistant's draft answer — review it; do not copy it: “Keep the current design. Normal requests succeed, so the booking flow is reliable. Sending the request again with a new request ID is safe, because the database creates exactly one reservation for each request ID. If a reply is lost, the browser's retry fixes the problem. A longer timeout would remove the risk completely.”

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
BUILD RECORD · Assignment 8 (Chapter 17) · 2026-10-24T19:10:39.597Z
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


THEIR CHANGE · run 3 · your code and tests unchanged (fingerprint eac82db7ba76d8c4)
What changed (you did not write it): The remote app ships a new release. After a lost reply it sends the same booking again, but with a new request_id.
  - retry after a lost reply: send the same request_id
  + retry after a lost reply: send a new request_id
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
FIT: 1; FAILURE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. TESTS RUN: required (recorded runs and the coverage sentence; longer writing does not replace them). THEIR CHANGE: required (run 3; your answer must match the run; no points). Instructor assessment required.


## Preparation and workload
Required reading: Distributed architectural patterns: slides 29–34; SaaS and service delivery: slides 53–58
Reported total active minutes (reading, check and assignment): Not reported


## THEIR CHANGE · run 3 verdict
The run showed: your tests stayed green; the result was no longer correct.
Your answer: tests green; result not correct.
THEIR CHANGE row: met. This row adds no points.
