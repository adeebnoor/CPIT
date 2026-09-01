# ISCARB 4.4.0

Production entry: `app.start_v440:app`. The preceding bootstrap layers remain
intact; v4.4 installs Gate v15 and the new Presenter/public interface.

## Source integrity

- Parse explicit PAGE/SLIDE/p./pp. coordinates, including multiple ranges.
  `[P1]` is a source ID, never page 1.
- Never substitute an unrelated page when an explicit page is absent.
- Scope every live export to its own job upload directory. An expired upload
  cannot borrow an identically named file from another job.
- Preserve complete source-page excerpts in the deterministic profile and
  fallback; rejoin wrapped continuations and retain late list members.
- Do not silently discard source facts after the eighth core-content item.
- Detect image-bearing pages even when their extractable text is sparse.
- Preserve complete source images without fixed-percentage cropping.

## Learner-visible contract

- Gate v15 checks each of the twenty cognitive jobs, including the five CLOs,
  six H-Stack capabilities, prediction sequence, evidence policy and verdict.
- Source detail and sentence-fragment checks augment the existing semantic and
  deterministic gates. A measured text-fit gate blocks unreadably dense releases.
- The Presenter uses complete statements or exact source pages. It does not
  invent curves, fault trees or architectures from a generic visual-type label.
- PDF and PPTX share content/geometry; browser preview rasterizes the actual PDF
  surface. Four rubric levels are visible. Source/core text is retained in notes.
- PDF fonts are embedded for reliable spacing and Unicode symbols.

## Faculty workflow

- Responsive source → build → audit/results interface, direct original CIMT PDFs.
- Per-unit checks, source-coverage ledger, unresolved deterministic/semantic
  issues, actual planned minutes and clearly separated release/review states.
- Duplicate-submit guard, file/URL exclusivity, finite reconnect attempts,
  explicit missing-job handling and optional same-browser job resumption.

## Boundaries

A deterministic recovery draft is not a semantic release. Source extraction can
preserve words and pages but cannot certify their interpretation. Dense or
incomplete drafts remain BLOCKED. Storage is still ephemeral on the existing
Render service; download outputs before a restart. No paid infrastructure or
authentication policy was changed in this release.

## Regression checks

`pytest -q` includes the archived chapter suite and `tests/test_v44_release.py`:
page-ID parsing, unavailable anchors, job isolation, image-only pages, late list
members, ninth-item retention, hollow twenty-record drafts, uncut sentences,
title/rubric fit, embedded fonts, exact source images, editable PPTX notes and
production bootstrap/asset routes.
