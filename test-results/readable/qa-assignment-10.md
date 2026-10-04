# Assignment 1 · Chapter 10 · Dependable Systems

**Edition:** 2026-09-ch10-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-04  
**Commit ID:** a1a980ff-fb35-4158-8598-be9570562ead  
**Part A committed:** 2026-10-04T21:28:02.530Z  
**STRESS revealed:** 2026-10-04T21:28:02.542Z

## Scenario
At 11:30, a fictional university's course-registration portal is experiencing intermittent errors during peak registration. Registration closes at 12:00. Two application servers support the portal, and automatic failover is enabled. The available failover test passed during a quiet period; no peak-load failover result is available. Current checks show that students can sign in and that confirmed registrations can be retrieved. No lost or duplicate registrations have been confirmed, but this has not yet been comprehensively checked. You are the duty software engineer. The registrar owns the registration deadline and may authorize an alternative submission route; you cannot change either policy yourself.Your decision: Recommend one immediate operating plan: continue with stated controls, limit operation, or pause the affected function. Start with one governing dependability property, one observable boundary, one action with a responsible role, and one inspectable evidence item. Explain any mechanism you rely on. State what is known and what you would still need to verify. Your plan must address students' ability to complete registration and the integrity of confirmed registrations. There is no single required choice.

## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 26: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## STRESS
QA evidence for chapter 10: this opens automatically after commitment.

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

## Rubric — 4 points
FIT: 1; TECHNICAL REASONING: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Redundancy, diversity and shared causes: slides 26–31; Formal methods and their scope: slides 40–43
Reported total active minutes (reading, check and assignment): Not reported
