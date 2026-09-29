# STRESS opens automatically after Part A

As requested by the instructor on 29 September 2026, all nine assessed assignments and
their nine previous editions require **no unlock code**.

1. Complete and review Part A.
2. Confirm commitment. The page saves and verifies the original responses before fetching STRESS.
3. Read the new evidence and complete REFIT, the final record, AI declaration and human review.
4. Export, inspect the PDF and submit it in Blackboard.

Part A remains read-only. Draft keys, edition IDs, commit IDs, timestamps, assessment text,
rubrics, points and deadlines are unchanged. A previously committed draft waiting for a code
resumes on reload in the same browser with the same Student ID. Already revealed work is restored.
Network failures preserve Part A and offer Retry STRESS; failed storage prevents reveal.

## Publication model

The existing evidence text is served as chapter- and edition-specific JSON and fetched only after
a verified commitment in the normal interface. This is pedagogical sequencing, not access control:
public JSON is technically readable outside that interface. Students should commit their own
initial reasoning before reading STRESS. The instructor intentionally removed the separate code
distribution step after it blocked students from completing homework.

Edit the appropriate `lectures/iscarb/reveal/*.json` directly when changing evidence. Do not run the
historical `tools/seal_stress.py` utility: sealed payloads fail the current publication audit.
Update the reviewed hashes with `tools/refresh_release_hashes.py` after an intentional change.
Historical private code files are unnecessary for students and must not be published.
