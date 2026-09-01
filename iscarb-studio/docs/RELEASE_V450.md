# 4.5.0 — transactional generation

The model now emits a metadata/source-allocation plan, followed by five batches
of four units. A batch with missing/duplicate unit numbers, wrong phases, or
missing assigned source evidence is retried once and never partially committed.
Completed batches are saved as review-only snapshots; unfinished slots retain
the source-only draft. All calls share the existing ten-minute model budget.

Repairs target unit numbers reported by the audit or deterministic checks.
Unlocalized defects trigger a separate metadata repair, not regeneration of all
twenty units. Unresolved global/content defects still block release.

Each major source item requires an exact excerpt in the assigned unit's core
content, in addition to its ledger row. This is structural evidence only: it
does not establish semantic fidelity, figure legibility or teaching quality.
Independent semantic audit and all existing release gates remain mandatory.

Transport-free tests cover the six-call plan/batch sequence, rejected duplicate
and wrong-phase batches, missing source allocations, evidence hidden only in
pedagogy, timeout preservation, and immutability of unaffected units on repair.
These tests are not a substitute for live-model acceptance on three lectures.

## Production acceptance — 2026-09-01

Commit 6f26c343ff14 passed 193 local tests plus 131 subtests, GitHub CI, and
deployed successfully. Real `auto` generation with one repair round was tested:

| Source | Result |
| --- | --- |
| CPIT455 class 2 | Blocked: configured Gemini quota exhausted; no AI batch saved. |
| CPIT455 class 3 | Eight AI units saved; next batch rejected for missing matching source evidence. No semantic release. |
| CPIT455 class 4 | First batch rejected for missing source evidence. No semantic release. |

The active class-3 PDF download returned HTTP 200 and 20 review-marked pages.
Inspection found two off-canvas text blocks in remaining source-draft units
12 and 15. Generated unit 8 also added a three-version hardware interpretation
not stated in its cited RR3 source. Therefore classroom acceptance FAILED;
download availability and source-ledger coverage must not be advertised as
semantic correctness or readable final slides. Dense-draft pagination remains
unresolved. No further model calls were made after quota exhaustion was found.

### 4.5.1 follow-up

- New batch schemas require explicit coverage evidence; legacy jobs remain readable.
- The four-word/20-character evidence constraint is now explicit in the prompt
  and schema description.
- PAGE/SLIDE aliases compare using source IDs and page coordinates; wrong pages
  and wrong sources are still rejected.
- Content-contract rejection yields a blocked review draft with a useful reason,
  not an application-error state. Preserved content is never promoted to ready.
- Hypothetical applications are explicitly prohibited in source-core statements.

The follow-up has local regression coverage. A fresh three-lecture semantic
acceptance run is blocked by the configured provider quota and is NOT claimed.
