# CPIT-455 mastery release v2

The student-perspective review found that source availability did not establish required preparation, that the assignments sampled too few objectives, and that prose-based decisions did not establish executable testing competence.

This release adds two named source selections per chapter (8–12 original slides), one formative question for each of the five chapter objectives (45 total), explicit assessment scope and relative preparation deadlines. Blackboard remains authoritative for calendar dates and course-grade policy. Original source coverage and figures remain intact. The core route still has 16–19 units and three planned interactions.

Each assessment requires application of a named source concept and a short transfer response within its existing 4- or 5-point total. Four-level rubrics and contrasting practice examples explain answer quality. New evidence includes supporting, adverse and mixed observations plus the cost of delay, so a justified RETAIN can earn full credit. The complete response is guided toward 180–260 words; timing estimates are targets, not measured results.

Chapters 16 and 17 include student-authored executable test cases: a duration adapter and a sequential reservation/retry model. Students predict, run baseline and corrected models, inspect actual results and explain discrepancies and scope. Models are deterministic, local, use no eval and contact no service. Their outputs are not evidence about deployed systems. These logs replace prose; they are not additional assignments. Broad testing strategies and the supplied syllabus's missing Code Coverage pack remain open.

Feedback/revision fields allow a revised submission while preserving the first prepared local export. Local storage, page views and field-completeness checks do not certify mastery, identity, examination integrity or LMS submission. The instructor guide describes changed-example checks, rotating individual explanations, feedback and workload calibration.

Prior assignment editions and reveal payloads remain accessible. Each current assessment uses a new draft namespace. Previous work can be resumed with the same student ID and browser; completed submissions do not require retrospective repetition unless explicitly assigned.

Verification: nine lecture routes and source ledgers, preparation/feedback interactions, source-reference requirements, transfer-field commitment, model calculations, invalid inputs, both laboratory runs, first-export preservation, revision exports, saved reload, previous A1 recovery, blocked storage, incorrect reveal versions and network failure. These are DOM and static checks. The cloud browser again timed out, so no successful desktop/mobile visual inspection is claimed.

Rebuild with the extracted supplied source archive:

1. `python tools/build_learning_path.py --input ../extracted/Fall2026`
2. `python tools/build_mastery_release.py`
3. `python tools/audit_classroom.py`
4. `node tools/check-fbr-release.mjs`
5. With jsdom installed, run the checks in `tools/learning-path-tests` plus the preserved `tools/check-assignment-v5.cjs` and `tools/check-course-interactions.cjs`.
6. `python tools/build_public_site.py`

The frozen templates reproduce previous editions; they are not generated from current student drafts. Automatic legacy lecture generation remains disabled. The announcement in `docs/blackboard-announcement-ar.md` is a prepared copy; no Blackboard posting is claimed.
