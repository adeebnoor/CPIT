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
