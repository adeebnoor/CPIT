# Lecture redesign v4: story, engagement and slide design

Revision `20261002-story-stage-v4`. Applies to all nine iSCARB lectures (Chapters 10–17, 20).

## Why

After teaching with the September 2026 lectures, the instructor's observations were:

- the story was weak;
- the design was repetitive;
- there was no real student engagement.

The screenshots confirmed all three.

- **Story.** The case appeared once (slide 3). After that, the same "CASE THREAD" banner and question repeated on up to 17 slides, and the case only came back near the end. It had no people, no deadline and no consequence.
- **Design.** About half of the concept slides used the same four equal pastel cards. Most of the rest used the same diagram-plus-bullets split. Each slide had two headlines (title, then takeaway), and the same chrome repeated on every slide.
- **Engagement.** Every slide ended with "Back to the story" plus a *Model answer* button, which gave the answer away before anyone had tried. Stations were static text. The lectures had no voting, prediction, timing or checkpoint where the class had to commit.

## What changed

| Area | Before | Now |
|---|---|---|
| Story | One fictional case, stated once, no characters | A nine-episode series, *Layan's first year*. A junior engineer (the student's seat) and a mentor recur in every chapter. Each episode adds a client under pressure, a deadline and stakes, and has five acts that follow the chapter's five roadmap branches. |
| Twist | The changed constraint appeared inside a station | The class must **commit** a one-sentence decision before the twist is revealed. This is the iSCARB COMMIT → STRESS → REFIT sequence, done in class. |
| Opening | Title, tags, hook | A **cold open**: a short scene, a deadline chip, and a **gut-check vote** before any theory. |
| Closing | Readiness checklist | An **episode close**: an epilogue that hands the open question to the assignment, a **revote** on the opening question (with the start counts shown), an **exit ticket**, then the required work. |
| Concept slides | Title + takeaway + "case thread" + four equal cards | The takeaway is **the headline** (assertion–evidence) and the title becomes a small kicker. A slim **act ribbon** shows progress (act 1–5, one colour per act). The **first slide of each act** shows a one-line story scene. |
| Layout | Mostly four equal cards | Layout follows the content: two-way split, three-step flow with arrows, 2×2 grid, or numbered steps. Checkpoints read as a **think → pair → record** routine. |
| Question bar | "Back to the story" + *Model answer* (modal) | "**Your call**": a **30-second think timer**, then *Reveal answer* in place (no dialog), and *Full explanation*. |
| Checks for understanding | After class only (five-objective practice) | A **class vote at the end of every act** (peer instruction): vote alone → convince a neighbour (60 s) → vote again → reveal with the explanation. Tap to count hands, and see both rounds as bars. |
| Pacing | Whole slide at once | In presenter mode, Enter reveals **one idea at a time** before moving on. Students reviewing on their own see everything. |
| Projection | Body text ≈ 14–17 px on many cards | Headlines 26–39 px, body text 16–22 px. The layout is checked to fit 1366×768 and 1440×900 with no overlap, and reflows on phones. |

Unchanged: the scientific lecture data (pinned hash, re-pinned **0** items), the 20-slide order, the 5 objectives, 3 stations, 20 rules, readings, assignments and STRESS. The new material is a presentation layer: `runtime/story-v3.js` (narrative) and `runtime/stage-v4.css` (design), plus rendering in `runtime/classroom-v3.js`.

## Comparison with established practice

| Practice (source) | What it recommends | v3 (before) | v4 (now) |
|---|---|---|---|
| Active learning (Freeman et al., 2014, *PNAS*; meta-analysis of 225 STEM studies) | Replace passive listening with frequent student activity | Activity confined to three stations | A vote every act, a think timer on every concept, commit-before-twist, gut check and exit ticket |
| Peer Instruction (Mazur, 1997; Crouch & Mazur, 2001) | ConcepTest: individual vote → peer discussion → revote → explanation | Absent | Built in, using each chapter's five objective questions, one per act |
| ICAP framework (Chi & Wylie, 2014) | Move students from passive to active, constructive and interactive | Mostly passive or active | Interactive (pair debate, vote discussion) and constructive (commit a decision, exit ticket) |
| Retrieval practice and pre-questions (Roediger & Karpicke, 2006; Richland, Kornell & Kao, 2009) | Attempt before being told; test before teaching | The model answer was one click away and came first | Think timer first, answer revealed in place afterwards; gut check before any theory; revote at the end |
| Narrative and case teaching (Willingham, 2009; Herreid's case-study method) | Stories with characters, conflict and a decision are remembered better than lists | A case statement without people or stakes | Recurring characters, a deadline and stakes in every episode, conflict in every act, a twist and an open resolution |
| Assertion–evidence slides (Alley, 2013; Garner & Alley, 2013) | A sentence headline supported by visual evidence, not bullet lists | Title plus a separate takeaway, card lists | The takeaway is the headline, with evidence (diagram, table, structured layout) underneath |
| Multimedia principles (Mayer, 2009): signalling, segmenting, coherence, personalisation | Cue structure, present in segments, cut redundancy, use conversational characters | Repeated banner, everything shown at once, double headings | Act colours and progress (signalling), builds and votes (segmenting), single headline (coherence), named characters (personalisation) |
| Attention resets (Bunce et al., 2010; Bradbury, 2016) | Change activity every 10–15 minutes | Long stretches between stations | An activity change roughly every four slides: act scene, vote, station or twist |
| Minute paper (Angelo & Cross, 1993) | Close with a one-minute reflection and the muddiest point | Absent | Exit ticket on every episode close |
| Projection legibility (common presentation guidance) | Large type for the back row; one idea at a time | Small text in large cards | Larger type, fewer words visible at once in presenter mode |

## Using it in class (presenter)

1. Open the lecture with `?presenter=1` (or from *Faculty-Presenter.html*). Students' copies show no builds.
2. **Cold open**: read the scene, then ask the gut-check question. Students show 1, 2 or 3 fingers; tap each option to count.
3. **Concept slides**: press Enter to reveal one idea at a time. Start the 30-second think timer, take answers, then *Reveal answer*.
4. **End of each act**: *Class vote · Act N*. Enter steps through vote → discuss → revote → reveal.
5. **Twist slide**: students write one sentence first, then *Reveal the new information*.
6. **Episode close**: revote (the start counts are shown), then the exit ticket.

Counts stay on the presenting device only. Nothing is sent to a server, and none of it is graded.

## Verification

- Release gate: `audit_classroom`, `check_paper_fidelity`, `check-fbr-release`, `build_public_site`: PASS.
- jsdom suites (interactions, assignment v5, path, visual, assignments, labs, hub): PASS.
- `check_story_v2` (9 chapters) and `check_navigation_v1` (9 chapters, online and offline): PASS.
- Layout sweep: 9 chapters × 20 slides × {1440×900, 1366×768, 390×844} × {light, dark} × {student, presenter}. No element crosses the footer, no content block overflows into the next one, there is no horizontal scroll on phones, and there are no script errors.
- Presenter interaction test (19 checks): builds, think timer, inline answer, full vote cycle, twist lock and reveal, gut-check counts carried to the end, persistence through reload, and no builds for students.

Known limit: on 1366×768 screens, the largest metric table in Chapter 11 scrolls inside its panel instead of shrinking below projection size. It already overflowed in v3.
