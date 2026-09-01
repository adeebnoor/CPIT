# 4.5.3 — one authoritative source passage

The post-phase-fix live class-2 trial revealed quotation drift: the model's
evidence excerpts were absent from its separate core-content field, even after
correction. The precise 4.5.2 diagnostics established this failure mode.

New batches now return `source_passages` with coverage IDs and student-visible
text. The compiler builds BOTH core content and coverage evidence from that one
text value, using source coordinates from the locked plan. It rejects unknown
IDs and still checks all assigned coverage items. Legacy saved blueprints retain
their old compatible structure. Repairs use the same materialization path.

This establishes structural traceability, not semantic truth. A passage can
still be factually wrong or superficial; the original-source semantic audit,
20-unit role checks, readiness checks and readable-fit gate remain mandatory.
No new verified lecture or classroom-readiness claim follows from this change.

Tests cover visible-text/evidence identity, unknown-ID rejection, complete batch
assembly, untouched-unit preservation on repair, and legacy compatibility.
