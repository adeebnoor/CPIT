# Assignment 9 · Chapter 20 · Systems of Systems

**Edition:** 2026-09-ch20-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-04  
**Commit ID:** 0243c7fa-b7be-4e5e-bff7-1e3edc9b5205  
**Part A committed:** 2026-10-04T20:44:02.722Z  
**STRESS revealed:** 2026-10-04T20:44:02.802Z

## Scenario
A fictional university plans a shared incident dashboard using campus security, transport and facilities systems. Each system remains operational on its own and has a different owner and release schedule. Security supplies incident identifiers; transport supplies vehicle locations with timestamps; facilities supplies building-access status. The owners agree to a limited daytime pilot, but no agreement defines a common freshness limit or how to display an unavailable feed. Local API tests passed. No cross-system failure rehearsal has been performed.Proposed integration design from the transport team · review it before the pilot: “The dashboard polls the three feeds every minute and shows the latest value from each as live. If a feed fails, the dashboard keeps showing its last value so the screen never looks empty. Each owner signs a one-page agreement promising 99.9% availability. Acceptance test: each API returns HTTP 200 with the agreed JSON schema.”

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
BUILD RECORD · Assignment 9 (Chapter 20) · 2026-10-04T20:44:02.555Z
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
