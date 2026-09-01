# 4.5.2 — lossless draft layout and actionable source diagnostics

- Consecutive short PDF-extraction fragments are packed without deleting words,
  changing labels, or summarizing source statements. Paragraph spacing scales
  with typography instead of imposing a nine-point gap on every tiny fragment.
- PDF, PPTX, and preview share a preflight. Vertical/horizontal overflow and
  question/task collisions reject the export with HTTP 422 and an actionable
  unit list before a partial file is written. Original-source downloads remain
  available. This does not relax the 16-point readable-release gate.
- Evidence diagnostics distinguish absent IDs, wrong source coordinates, short
  headings, and excerpts absent from actual unit core content.
- Mandatory source teaching is allocated to units 6–15. Introductory domain maps
  and outcome lists cannot stand in for substantive source coverage.

## Verification

Replayed the saved class-3 production draft from 4.5.0: 20 PDF pages, zero
off-canvas text blocks (previously two). The dense units 12/15 use 12/11-point
body text after packing, so the draft still does NOT meet classroom release
readability. Visual review confirmed all content stayed on the pages; it did
not certify source fidelity or teaching readiness.

A fresh class-2 `gemini-3.5-flash-lite` trial on 4.5.1 reached generation but
rejected source coverage assigned to domain-spine unit 2. No semantic release
was issued. This motivated the teaching-span allocation rule above.

Regression tests cover no-file-on-overflow for PDF/PPTX, preview consistency,
source-word preservation, HTTP 422 handling, evidence-repair diagnostics, and
rejection of introductory-unit source allocation. Full live acceptance of this
release remains separate from these deterministic tests.

## Live follow-up

On 4.5.2, the class-3 source-only review job completed and its PDF/PPTX downloads
both returned HTTP 200 (3,792,505 and 2,976,526 bytes). This is an export test,
not semantic acceptance. The class-2 AI trial saved four units, then rejected
a cross-phase batch because model-provided phase labels were wrong.

Follow-up fixes derive phase labels from unit numbers before checking the batch;
content and learner-visible role checks are unchanged. Text wrapping now uses a
bounded 4,096-entry immutable cache. The saved class-3 sample produced identical
layout blocks in 0.164 seconds versus 0.406 seconds uncached; this is not a claim
about end-to-end generation latency. Live semantic acceptance remains unproven.
