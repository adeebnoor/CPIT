# Saudi alignment and source-figure review — 28 September 2026

Scope: all nine published CPIT-455 lectures, their shared runtime, the learning hub, national-alignment page and offline packages.

## Findings and corrections

- The prior NELC addition was a generic badge and modal. Added two full supplementary reference slides inside every lecture: `#NATIONAL-JAHEZIAH` and `#NATIONAL-NELC`. They have their own 1/2 counter and restore the same classroom position. They are explicitly outside the pinned 20-slide scientific sequence.
- Jaheziah readiness now names a chapter-specific knowledge task, applied skill, responsibility and inspectable evidence. The detailed view retains all five existing objectives and their assessment opportunities. National outcome codes and exam weights are not fabricated; formal program approval remains outstanding.
- NELC uses the five principles and six stages in the supplied official September 2026 v1.0 framework, with the student/AI/instructor boundary and chapter-specific evidence. The page distinguishes designed opportunities, planned evaluation and demonstrated learning outcomes.
- Logos identify the reference organizations; they are not certification or partnership marks. NeLC logo is extracted from the supplied official PDF without redesign; ETEC logo comes from `https://media.etec.gov.sa/media/yx3dtn4o/etec-logo-dark.svg`.
- The previous runtime replaced raster scientific diagrams with generic text cards. Those cards can lose the original relationships. Replaced all 58 raster figure placements using original-source vector alternatives. EMF media were extracted from the supplied PPTX files and converted to SVG; Chapter 10's curve was extracted from the original PDF. Source 13/6 was manually matched to the system-layer diagram. Chapter 14's previously tiny combined figure now has separately selectable original diagrams (source 8 and 15). See `source-vector-provenance-20260928.json`.
- Original sources, all scientific lecture-data, five objectives, three stations, twenty rules, assessed Mastery v2 assignments and delayed STRESS payloads remain unchanged. AI is still the transfer/practice layer described in the preprint.
- Offline packages include the same runtime, vector diagrams, logos, reference page and framework PDF as the live version.

## Coverage and limits

All nine chapter spines were compared with their declared source sections and the existing `iscarb-content-coverage-audit-20260927.md`. The changes restore the original diagrams, without removing concepts or rearranging the scientific route. Detailed source reading remains required; a twenty-slide lecture is not the full textbook.

The syllabus item **Code Coverage** remains openly recorded as missing teaching material in the course-outcome map. This release does not claim that the nine chapters complete every syllabus item.

The Jaheziah mapping is educational and proposed; formal specialization codes and program approval are not established. NELC design alignment does not establish certification, institutional compliance, causal effectiveness or student attainment.

## Verification

- `check_paper_fidelity.py`: pinned scientific and assessment contracts.
- `audit_classroom.py`: publication hashes, dependencies, source files and grammar.
- `build_public_site.py` and `check-fbr-release.mjs`: staged release integrity and script syntax.
- `check-readable-course.cjs`: 180 classroom slides at five viewports, the two reference slides per chapter, image loading, return navigation, local practice interactions and separate assessed assignments. Execution evidence is recorded by GitHub Actions; this document does not pre-assert that a run passed.

Framework source: National eLearning Center, *إطار تصميم التعليم والتعلم المدعوم بالذكاء الاصطناعي*, v1.0, September 2026, printed pp. 3–10. Included unmodified under its CC BY-NC-SA 4.0 license.
