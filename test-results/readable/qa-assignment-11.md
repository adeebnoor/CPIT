# Assignment 2 · Chapter 11 · Reliability Engineering

**Edition:** 2026-09-ch11-mastery-v2  
**Student:**   
**Student ID:** QA-DESIGN-ONLY  
**Section:** QA  
**Date:** 2026-10-04  
**Commit ID:** c2257f63-10d1-4e19-9bf8-5215175b0a2f  
**Part A committed:** 2026-10-04T13:43:06.397Z  
**STRESS revealed:** 2026-10-04T13:43:06.411Z

## Scenario

A candidate release of a fictional university payment-authorization service will be used during registration week. The service handles many short, similar requests. The stated non-functional requirement is: ROCOF shall be no greater than 0.0005 authorization failures per payment transaction during registration service hours.
In the latest reliability test, the candidate processed 20,000 payment-authorization transactions and logged 6 authorization failures. The service was reachable for 99.98% of the test period. Two application instances run behind automatic failover. The test report says the dataset is “registration-like,” but the detailed operational-profile distribution is not included in the brief you received. No duplicate confirmed payments were found in the inspected sample, but the duplicate-payment audit is not yet complete.
You are the duty software engineer preparing a recommendation to the service owner. Choose one immediate action: release, release with explicit restrictions/conditions, or hold. Your recommendation must distinguish what the measured data supports from what remains unverified.


## FIT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## MEASURE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## BOUND
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ACT
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## EVIDENCE
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## ASSIGNED SOURCE APPLICATION
Slide 19: the source concept constrains the model assumptions and defines a bounded control that must be independently checked.

## TRANSFER CHECK
QA: Use a chapter mechanism, independent evidence, explicit conditions and a human owner; proposed checks are unmeasured.

## STRESS
QA evidence for chapter 11: this opens automatically after commitment.

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
FIT: 1; MEASURE: 1; BOUND: 1; ACT + EVIDENCE: 1; REFIT: 1. Instructor assessment required.


## Preparation and workload
Required reading: Reliability metrics and requirements: slides 19–24; Measurement and operational profiles: slides 70–75
Reported total active minutes (reading, check and assignment): Not reported
