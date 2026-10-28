# Assignment 7 · Chapter 16 · Component-based Software Engineering

**Edition:** 2026-09-ch16-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-28  
**Commit ID:** 56892670-ddc8-4834-8009-42254e07f4db  
**Part A committed:** 2026-10-28T13:36:24.756Z  
**STRESS revealed:** 2026-10-28T13:36:24.766Z

## Scenario
A fictional lab-booking app uses an existing software component with the function reserve(roomId, duration).

The app sends duration in minutes. The component's instructions say duration is in seconds and must be between 1 and 7200, inclusive. An accepted request returns a reservation ID.
A small connecting function (adapter) currently passes both values to the component without changing them.
A sample request with duration = 30 returns an ID. Nobody has tested the saved end time or what happens with invalid input.

Your decision: use the component, adapt the connection, replace the component, or hold the limited trial. Explain what must be checked before relying on it.
An AI assistant's draft answer — review it; do not copy it: “Use the component as it is. The sample request with duration = 30 returned a reservation ID, so the connection works correctly. Both sides call the value duration, so the adapter only needs to pass it through. Any duration up to 7200 is accepted, so a three-hour booking (180 minutes) is safe. No more tests are needed before the trial.”

## Chapter boundary sentence (written in the lecture)
Not written in the lecture on this device.

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
    assert 1 == 1


## BUILD RECORD
BUILD RECORD · Assignment 7 (Chapter 16) · 2026-10-28T13:36:24.503Z
Code fingerprint: eac82db7ba76d8c4 (the code above, exactly as run)
Run 2 on this device · previous code fingerprint: d64dd4bae169e8af
Micro-viva change request (from Student ID QA-DESIGN-ONLY): The maximum becomes 90 minutes. Change one thing and show the test that proves it.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check
Coverage of your code by your own tests: not measured by this runner.


THEIR CHANGE · run 3 · your code and tests unchanged (fingerprint eac82db7ba76d8c4)
What changed (you did not write it): The component team ships version 2. The call is the same, reserve(room_id, duration), but duration is now in milliseconds (1 to 7,200,000).
  - reserve(room_id, duration)   # duration in seconds, 1..7200
  + reserve(room_id, duration)   # duration in milliseconds, 1..7,200,000
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
FIT: 1; CONTRACT: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. TESTS RUN: required (recorded runs and the coverage sentence; longer writing does not replace them). THEIR CHANGE: required (run 3; your answer must match the run; no points). Instructor assessment required.


## Preparation and workload
Required reading: Composition types: slides 40–43; Interface semantics and OCL: slides 51–55
Reported total active minutes (reading, check and assignment): Not reported


## THEIR CHANGE · run 3 verdict
The run showed: your tests stayed green; the result was no longer correct.
Your answer: tests green; result not correct.
THEIR CHANGE row: met. This row adds no points.
