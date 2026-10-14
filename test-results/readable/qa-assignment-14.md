# Assignment 5 · Chapter 14 · Resilience Engineering

**Edition:** 2026-09-ch14-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-14  
**Commit ID:** c40d5b02-f3a7-43e9-89cf-8d955ac3d5ae  
**Part A committed:** 2026-10-14T21:59:48.478Z  
**STRESS revealed:** 2026-10-14T21:59:48.486Z

## Scenario
A fictional campus transport desk needs to read today's pickup list even when the central scheduling server stops working.

A copy of the list is updated on the desk device at 06:00. Staff with permission can read this local copy.
Changes made after 06:00 normally stay on the central server until the next update of the local copy.
A record shows that a backup server restarted successfully. Nobody has tested the full service from the staff member's point of view.
During an outage, staff can write changes on an approved paper form.

Your decision: is this backup way of working (fallback) ready for a limited trial? Explain what the desk can safely do and what still needs checking.

## Chapter boundary sentence (written in the lecture)
Not written in the lecture on this device.

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## RECOVER
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 18: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BUILD PLAN
QA: the build enforces the rule; tests cover a normal, an edge and a refused case.

## PYTHON BUILD (CODE AND TESTS)
def test_a():
    assert True


## BUILD RECORD
BUILD RECORD · Assignment 5 (Chapter 14) · 2026-10-14T21:59:48.291Z
Code fingerprint: d64dd4bae169e8af (the code above, exactly as run)
Micro-viva change request (from Student ID QA-DESIGN-ONLY): Return conflicts with the pickup id as well as the change id. Change the code and one test.
Your tests: 3 of 3 pass · Course checks: 1 of 1 pass
Your tests:
  ✓ test_a
  ✓ test_b
  ✓ test_c
Course checks:
  ✓ course check


## STRESS
QA evidence for chapter 14: this opens automatically after commitment.

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
FIT: 1; RECOVER: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Sociotechnical and organizational resilience: slides 18–23; Survivability analysis: slides 42–45
Reported total active minutes (reading, check and assignment): Not reported
