# 4.5.4 — consistent unit roles and source-preserving repairs

The live 4.5.3 class-2 trial generated all 20 units but failed acceptance.
The audit even suggested reversing the core/pedagogy separation for units 15
and 18. A legacy channel check prohibited technical AI content even when it
was explicitly part of the original lecture. Repair could regenerate source
allocations without rechecking their evidence.

Changes:

- One explicit role/channel contract is supplied to planning, each scoped
  generation batch, independent audit and targeted repair.
- Batch acceptance uses the same executable unit-role functions as the final
  gate. Empty labels, misplaced CLO content and missing reasoning jobs are
  rejected before committing the batch. The five-CLO and six-H-Stack checks
  also require their exact counts and pure instructional channels.
- P1 technical AI remains permissible only with a source AI topic and P1
  anchor; instructional AI-use directives remain prohibited in technical core.
  This channel check does not establish semantic truth.
- Generic gate summaries no longer trigger speculative metadata regeneration.
  Repairs retain the locked coverage ledger and verify every selected source
  assignment's visible evidence after replacement.
- Readability failures identify the exact units for targeted repair. The 16pt
  body / 12pt rubric thresholds and independent semantic approval are unchanged.

Regression tests reproduce these defects with transport-free fixtures. They
prove compiler behavior, not that a model-generated lecture is correct. Live
acceptance must still pass every deterministic check and independent audit.

## 4.5.5 follow-up: visible opening crisis

The first live 4.5.4 attempt stopped at the opening-unit role check. Inspection
found that this check ignored `central_engineering_crisis` and
`named_ethical_purpose`, even though the presenter displays those fields on
slide 1. The check now includes that actual visible content; the evidence gap
and decision requirements remain mandatory. A regression verifies both the
valid displayed crisis and rejection of a generic introduction. The generator
also receives explicit Decision/Unknown prompts. Public rejection messages no
longer dump the full instructional contract; correction still receives it.
