# ISCARB 20-Unit Grammar — Reference Specification

This document is a **human reference**, not an input the engine reads. It maps
the ISCARB 20-unit teaching grammar to what the code actually enforces, so a
reviewer can check any generated lecture against a single source of truth.

Every unit's instructional job is authored in
[`app/unit_contract.py`](../app/unit_contract.py) (`UNIT_JOBS`), enforced as a
deterministic role check in [`app/gate_v15.py`](../app/gate_v15.py)
(`unit_role_checks`), and given a phase + CIMT lens for display in
[`app/presenter_v44.py`](../app/presenter_v44.py) (`PHASES`, `LENSES`,
`eyebrow`). The whole draft is produced **with zero API calls** by
[`app/deterministic_blueprint_fallback.py`](../app/deterministic_blueprint_fallback.py);
Gemini is an optional enrichment, never a dependency.

## The four phases

The gate requires exactly this phase sequence — five units each
(`gate_v15.EXPECTED_PHASES = ["IFHAM"]*5 + ["MARIS"]*5 + ["ATQAN"]*5 + ["MAYYIZ"]*5`):

| Phase (stored) | Displayed as | Units |
|---|---|---|
| `IFHAM`  | UNDERSTAND   | 1–5   |
| `MARIS`  | PRACTISE     | 6–10  |
| `ATQAN`  | MASTER       | 11–15 |
| `MAYYIZ` | DISTINGUISH  | 16–20 |

A second, per-unit **CIMT lens** (`C` Concept · `I` Implementation ·
`M` Measurement · `T` Trend) is layered on top for the slide header
(`_CIMT_BY_UNIT`); it is an additional teaching cue, independent of the phase.

## The twenty units

Each row: the unit's job, the CIMT lens it prints, and the deterministic gate
check(s) that must pass for it. Checks named `v15_unitNN_job_is_visible` come
from `unit_role_checks`; the cross-unit obligation tags come from
`unit_contract.TAG_OWNERS`.

### Phase 1 — UNDERSTAND (units 1–5)

| # | Job | Lens | Gate check | Tags |
|---|-----|------|-----------|------|
| 1 | Open ONE ill-structured crisis + professional purpose; show `central_engineering_crisis`, a `Decision:` question and an `Unknown:` gap; do not reveal the diagnosis | C | `v15_unit01_job_is_visible` | IDR-5, EER-1 |
| 2 | Domain spine: map ALL locked source topic families in ≥2 source-grounded entries with a P1 anchor | C | `v15_unit02_job_is_visible` | IDR-7, IDR-12 |
| 3 | Exactly five CLOs in `pedagogy_content` (`CLO1:`…`CLO5:`); empty core/source | C | `v15_unit03_five_clos_only` | — |
| 4 | Exactly six H-Stack capabilities, one per pedagogy entry; empty core/source | C | `v15_unit04_hstack_is_exact` | — |
| 5 | `PREDICT:` → `CONSTRAINT:` → `DERIVE:` → `NAME:`, in order, ≥4 meaningful words each | C | `v15_unit05_predict_constraint_derive_name` | EER-2, EER-3 |

### Phase 2 — PRACTISE (units 6–10)

| # | Job | Lens | Gate check | Tags |
|---|-----|------|-----------|------|
| 6  | Teach the assigned P1 mechanism from first principles (≥3 substantive entries) | C·I | `v15_unit06_job_is_visible` | IDR-1 |
| 7  | Teach P1 architecture / implementation structure; ask the learner to trace or apply it | I | `v15_unit07_job_is_visible` | IDR-2 |
| 8  | Compare TWO defensible alternatives: `Alternative A:`, `Alternative B:`, `Trade-off:` | I | `v15_unit08_job_is_visible` | EER-4, EER-5 |
| 9  | `Measure:` and `Falsifier:`; observable result, test conditions, a disconfirming result | M | `v15_unit09_job_is_visible` | EER-7, EER-8 |
| 10 | Design review: `Known:`, `Unknown:`, `Decision-sensitive unknown:`, `Monitor:` | M | `v15_unit10_job_is_visible` | EER-6, EER-11 |

### Phase 3 — MASTER (units 11–15)

| # | Job | Lens | Gate check | Tags |
|---|-----|------|-----------|------|
| 11 | Teach P1, then a concrete **hypothetical** Saudi application + the condition that changes the decision | I | `v15_unit11_job_is_visible` | IDR-6 |
| 12 | Integrate accountability: responsible role/owner, the evidence they check, the sign-off point | I·M | `v15_unit12_job_is_visible` | IDR-8 |
| 13 | Ask how a change / future improvement affects the mechanism (hypothetical unless P1 supplies a fact) | T | `v15_unit13_job_is_visible` | IDR-4 |
| 14 | Practitioner workload / wellbeing as a bounded design question or source-supported consequence | M·T | `v15_unit14_job_is_visible` | IDR-9 |
| 15 | Teach P1 AI content; AI-use rules ONLY in pedagogy: `AI MAY ASSIST:`, `AI MUST NOT BE TRUSTED AUTONOMOUSLY:`, `Human sign-off:` | T | `v15_unit15_job_is_visible` | IDR-10 |

### Phase 4 — DISTINGUISH (units 16–20)

| # | Job | Lens | Gate check | Tags |
|---|-----|------|-----------|------|
| 16 | Launch one source-grounded design/portfolio artifact with a trade-off and observable evidence; name only locked ETEC targets | I | `v15_unit16_job_is_visible` | IDR-3, IDR-14, EER-12 |
| 17 | Change a constraint; require peer critique and a revised artifact with rerun evidence | T | `v15_unit17_job_is_visible` | EER-9, EER-10 |
| 18 | Evidence protocol in pedagogy: `Claim:`, `Evidence:`, `Warrant:`, `Counter-evidence:`, `Residual uncertainty:` | M | `v15_unit18_job_is_visible` | IDR-11, IDR-13 |
| 19 | The six rubric criteria with all four levels: Distinguished, Ready, Developing, Not Yet Ready | M | `v15_unit19_job_is_visible` | — |
| 20 | Bounded assurance + a decision among APPROVE / CONDITIONALLY APPROVE / REDESIGN / REJECT; no absolute guarantees | T | `v15_unit20_job_is_visible` | — |

## Two invariants the grammar depends on

These are what make the grammar **checkable** rather than merely descriptive
(`unit_contract.CHANNEL_CONTRACT`):

1. **Channel separation.** `core_content` / `source_passages` carry
   source-supported technical knowledge only. `pedagogy_content` carries
   instructional questions, reasoning steps, AI-use rules, and assessment /
   assurance scaffolds. The two are never inverted to satisfy an audit
   suggestion. Units 3, 4 and 18 have empty core by contract; unit 15 keeps
   source-backed AI facts in core but the AI-*use* rules in pedagogy.

2. **Source fidelity.** Every mandatory source ID stays visibly taught in its
   locked unit (6–15); nothing is invented, no source list is truncated, and a
   bare label never counts as substantive work. The local role checks never
   substitute for independent review against the original lecture — the
   locally derived readiness trail always reads **UNVERIFIED**, which is why
   the three official-ETEC map checks stay unresolved by design on a free draft.

## Whole-draft checks

Beyond the per-unit checks, the gate also asserts, among others:

- `v15_unit_numbers_are_exact` — units are exactly 1…20.
- `v15_phase_sequence_is_exact` — the 5/5/5/5 phase blocks above.
- `v15_complete_20_unit_grammar` — every per-unit role check passed.
- `v15_technical_units_retain_source_detail` — units 6–15 keep their source facts.
- `v15_no_source_fragment_ends_mid_thought` — no source excerpt is cut mid-thought.
- `v15_presenter_fits_readable_canvas` / `presenter_unitNN_readable` — every
  slide fits the projected canvas without clipping.
