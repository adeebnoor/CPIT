# How STRESS reaches students

## Assignments 1–2 (Chapters 10–11): automatic

Since 29 September 2026 these two assignments, and their previous editions, need **no unlock code**.
After the student confirms Part A, the page verifies the saved commitment and fetches the chapter's
public `lectures/iscarb/reveal/*.json`.

## Assignments 3–9 (Chapters 12–20): through Blackboard

From 3 October 2026 the STRESS text for these assignments is **not in the repository or on the site**
(`tools/apply_lms_stress.py`). The current and previous editions both use this flow:

1. The student commits Part A. It becomes read-only, as before.
2. The page shows the Blackboard steps. The student prints/saves the committed Part A record and uploads
   it to *Assignment N · Part A (committed record)*.
3. Blackboard releases *Assignment N · New evidence* through Adaptive Release.
4. The student pastes the text into the page. The page compares a SHA-256 of the normalised text
   (whitespace, quotes and dashes normalised) with `stress_text_sha256` in `curriculum/publication.json`.
   A match is labelled *matches the Blackboard release*. A mismatch can still continue after a warning,
   but is labelled *UNVERIFIED* in the record.
5. REFIT, the final record, the AI declaration and the human review continue as before, and the PDF is
   submitted in Blackboard.

Blackboard set-up steps are in the instructor guide (`instructor-guide.html#stress-codes`).

## Integrity notes

- The paper-fidelity contract keeps the original pinned STRESS hash (`stress_sha256_lf`) and adds
  `stress_delivery: "lms"` and `stress_text_sha256`. The audit checks that each page carries the same
  fingerprint. The assessed text did not change; only its delivery did.
- The texts for Chapters 12–20 were public in this repository's history between 29 September and
  3 October 2026. A determined student could still find them there. Pair this flow with the micro-viva
  ownership check, or rotate the STRESS texts in a later offering.
- To change a STRESS text, update the Blackboard item and its fingerprint in `publication.json` and in
  the contract (revision record), then re-pin with `tools/refresh_release_hashes.py`.
