# 4.4.1 — bounded generation and usable review drafts

This release fixes failures observed in a real production run of CPIT455 class 2.

- Save a 20-unit source-preserving review draft before calling the model.
- Offer `model=source-only` for a completed local draft with no model dependency.
- Limit a model request to 150 seconds, disable nested SDK retries, and limit the shared model-call budget to 600 seconds. Timeouts preserve a review draft; they never issue a verified release.
- Allow PDF/PPTX snapshots during audit. Use independent temporary export paths so simultaneous downloads cannot overwrite each other, then clean up after delivery.
- Provide the exact original PDF as a separate source companion, including diagrams and examples not visible in the twenty-unit presenter. This is not evidence that the presenter alone covers every source detail.
- Fix false failures for a substantive visible prediction and for a pedagogical design review without invented primary-source claims.
- Preserve source explanations in Units 1 and 5; widen the teaching sidebar without removing pedagogical content.
- Replace bare fallback labels with actionable review, alternatives, measurement and AI-permission prompts.

## Boundaries

Source-only output is a **review draft**, not a semantic-audit PASS or ETEC certification. Faculty must check contextual activities, source coverage, and readability. A verified release still requires all deterministic checks and the independent semantic audit. The free Render service retains uploads only until restart; download the files during the session.

## Regression coverage

Tests cover deadline exhaustion, timeout classification, source-only completion without a model, complete coverage ledger, source preservation in opening/prediction units, non-vacuous grammar checks, active-audit PDF/PPTX exports, 20 pages/slides, PDF canvas bounds, exact original PDF bytes and export cleanup.

## Production verification — 2026-09-01

- Render served 4.4.1 at commit `8deb1069c815`.
- Source-only runs completed for CIMT class 2 and class 3: 20 units, terminal review status, no application error.
- Class 2 presenter PDF, PPTX, original PDF, reading PDF, instructor DOCX, student DOCX and blueprint JSON all returned HTTP 200. Downloaded files opened successfully; PDF/PPTX had 20 pages/slides, reading pack had 24 pages. Original PDF bytes matched the repository source. Both tested presenters had no out-of-canvas words.
- The AI run did **not** achieve semantic release. It terminated with a preserved review draft instead of leaving downloads blocked. This verifies the failure-recovery path, not successful automatic certification.
- CI: 186 tests and 131 subtests passed, plus runtime smoke and capacity retry. An additional diagnostic-message regression test was added afterward.
