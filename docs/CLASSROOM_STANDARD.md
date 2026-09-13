# ISCARB classroom standard — September 2026

Chapter 10 supplies the common CRISIS → MAP → TRADE-OFF → EVIDENCE → VERDICT route. Chapters 10–17 and 20 each have 20 visible instructional units, a planned 50-minute sequence, five learning outcomes, eight chapter-specific concept explanations, fourteen explanatory figures, two polls, a worked example, transfer practice, a collaborative challenge and four retrieval questions. All 19 question groups per chapter have a substantive answer and explanation in a closed native details element.

The canonical lecture HTML is self-contained. Reading, diagrams and details work without network access. JavaScript adds slide navigation, reading mode, text sizing, theme, fullscreen, outline and optional local resume. The original InClass-Presenter query URLs redirect to the same canonical edition instead of scaling an iframe. Chapter 10's earlier full reference remains at Ch10-Dependable-Systems-Final100.html.

## Authoring

- Edit `curriculum/chapters.py` for chapter-specific content.
- Edit `curriculum/classroom.css` and `curriculum/classroom.js` for the common reader.
- Run `python tools/build_classroom.py` and commit the generated HTML with its source.
- `python tools/update_learning_pages.py` updates the hub and assignment scaffolds. It preserves assessment storage identities and the commit/reveal protocol.
- Run `python tools/audit_classroom.py`, `node tools/check-fbr-release.mjs`, then `python tools/build_public_site.py`.

The old split-patch generator no longer rewrites Chapter 11 from Chapter 10 or commits generated pages automatically. The compatibility command now calls the shared classroom builder. Publication does not inject runtime content or typography patches into the classroom editions. Each chapter is checked against its own content anchors, not a concatenation of all chapters.

## Assessment progression

| Assignments | Scaffolding | Main demand |
| --- | --- | --- |
| 1–3 (10–12) | Worked example and visible sentence frames | Identify, measure, trace hazards |
| 4–6 (13–15) | Criteria and optional planning prompts | Compare controls, disruptions and alternatives |
| 7–9 (16–17, 20) | Optional reminders with independent design | Compose, distribute, integrate and defend |

Every assignment starts with an ungraded transfer warm-up. Part A retains FIT, BOUND, ACT and EVIDENCE; STRESS is requested after commitment, and REFIT remains part of the four-point rubric. Warm-up answers do not expose the assessed STRESS. Existing saved attempts retain their chapter and student storage keys. LMS submission remains unchanged.

## Pedagogical and accessibility basis

- Sommerville, *Software Engineering*, 10th ed., chapters 10–17 and 20; the author's presentation index: https://software-engineering-book.com/slides/
- IES/What Works Clearinghouse, *Organizing Instruction and Study to Improve Student Learning*: https://ies.ed.gov/ncee/wwc/PracticeGuide/1 — alternate examples and problems, integrate diagrams with explanations, retrieval and spaced review.
- W3C, WCAG 2.2 Understanding Reflow: https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
- W3C, WCAG 2.2 Understanding Text Spacing: https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html

Explanatory diagrams and scenarios are course-authored; cases are not reports of real incidents. Readiness questions are course practice, not official ETEC items. This implementation does not claim a formal accessibility certification or a measured improvement in learning outcomes. Content coverage is the core chapter sequence; extended textbook detail and exercises remain assigned reading.
