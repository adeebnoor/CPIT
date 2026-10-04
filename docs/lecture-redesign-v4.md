# Lecture redesign v4: story, engagement and slide design

Revision `20261002-story-stage-v4`. **Rolled out from Chapter 12 (Assignment 3) onward**: Chapters 12–17 and 20 use it. Chapters 10 and 11 were already taught and stay exactly as students saw them (verified pixel-identical). Their pilot episodes are kept inactive in `story-v3.js`. To include them in a later offering, change `firstChapter` there. Episodes are numbered from Chapter 12 (Episode 1) to Chapter 20 (Episode 7).

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
| Story | One fictional case, stated once, no characters | A seven-episode series, *Layan's first year* (Chapters 12–20). A junior engineer (the student's seat) and a mentor recur in every chapter. Each episode adds a client under pressure, a deadline and stakes, and has five acts that follow the chapter's five roadmap branches. |
| Twist | The changed constraint appeared inside a station | The class must **commit** a one-sentence decision before the twist is revealed. This is the iSCARB COMMIT → STRESS → REFIT sequence, done in class. |
| Opening | Title, tags, hook | A **cold open**: a short scene, a deadline chip, and a **gut-check vote** before any theory. |
| Closing | Readiness checklist | An **episode close**: an epilogue that hands the open question to the assignment, a **revote** on the opening question (with the start counts shown), an **exit ticket**, then the required work. |
| Concept slides | Title + takeaway + "case thread" + four equal cards | The takeaway is **the headline** (assertion–evidence) and the title becomes a small kicker. A slim **act ribbon** shows progress (act 1–5, one colour per act). The **first slide of each act** shows a one-line story scene. |
| Layout | Mostly four equal cards | Layout follows the content: two-way split, three-step flow with arrows, 2×2 grid, or numbered steps. Checkpoints read as a **think → pair → record** routine. |
| Question bar | "Back to the story" + *Model answer* (modal) | "**Your call**": a **30-second think timer**, then *Reveal answer* in place (no dialog), and *Full explanation*. |
| Checks for understanding | After class only (five-objective practice) | A **class vote at the end of every act** (peer instruction): vote alone → convince a neighbour (60 s) → vote again → reveal with the explanation. Tap to count hands, and see both rounds as bars. |
| Pacing | Whole slide at once | Whole slide at once, by the instructor's choice after trying builds: no click-to-reveal and no animation. |
| Projection | Body text ≈ 14–17 px on many cards; text covered about 27% of the content area on average and 12% on figure slides | Evidence text **grows to fill the space** each slide gives it, up to 1.65× and without overflow: average coverage 45%, minimum 29%. |
| Type sizes | Same small sizes on every slide | Headlines 26–39 px; body text from 16–22 px upward, fitted per slide. The layout is checked to fit 1366×768 and 1440×900 with no overlap, and reflows on phones. |

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
| Projection legibility (common presentation guidance) | Large type for the back row; one idea at a time | Small text in large cards | Larger type that grows to fill each slide's space; one headline per slide |

## Fitting a 50-minute lecture

Doing every activity takes about 85–90 minutes, so presenter mode uses a **50-minute plan by default**. Add `&pace=60` for a one-hour class or `&pace=full` for everything.

| Plan | Class votes | Stations | Per-slide budget |
|---|---|---|---|
| `pace=50` (default) | After acts 2 and 4 | All three marked "if time allows"; the twist slide's commit replaces station 3 | Cover 3 min, map 1, case file 2, close 3, twist +3, each vote +4; the remaining ~30 min is shared across the concept slides (about 2 min each) |
| `pace=60` | After acts 2 and 4 | Station 2 planned (+5 min), others optional | As above, with about 2.3 min per concept slide |
| `pace=full` | After every act | All three | No clock |

A chip beside the slide number shows the minute by which the current slide should be finished, the elapsed time, and whether the class is on time, ahead or behind (±3 min). The clock starts when the presenter leaves the cover, which counts as its planned 3 minutes. Clicking the chip re-aligns the clock to the plan at the current slide. Detail not discussed in class remains in *Full explanation* and the required source review. Students' copies have no clock and keep every vote for self-study.

## Using it in class (presenter)

1. Open the lecture with `?presenter=1` (or from *Faculty-Presenter.html*). Students' copies show no builds.
2. **Cold open**: read the scene, then ask the gut-check question. Students show 1, 2 or 3 fingers; tap each option to count.
3. **Concept slides**: press Enter to reveal one idea at a time. Start the 30-second think timer, take answers, then *Reveal answer*.
4. **Class votes** (after acts 2 and 4 in the 50-minute plan): *Class vote · Act N*. Enter steps through vote → discuss → revote → reveal.
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

## Revision after the first classroom review (3 Oct 2026)

- **Text size.** A fitting step enlarges the evidence text (cards, explanation points, tables, approaches) until it fills its panel without overflow. It is recomputed on every slide, resize and answer reveal. At 1366×768, text coverage rose from 27% to 45% of the content area; figure slides rose from 12–13% to at least 29%.
- **No click-to-reveal.** Builds were removed. The twist no longer sits behind a button: the slide before it says *"Before the next slide: write your decision in one sentence"*, and the twist slide states the new information openly. This keeps commit-before-STRESS through slide order alone.
- **AI is the practice layer; engineering judgment is assessed.** This is now part of the story:
  - every episode has a `practice` line in which Layan uses AI to rehearse, while the decision she signs is her own; it is shown on the chapter's first AI-segment slide;
  - the principle appears on the cold open and in the case file;
  - the episode close spells out what is assessed (FIT, BOUND, ACT, EVIDENCE and REFIT, in the student's own words);
  - class votes are labelled practice, not assessment.

## Assessment revision (3 Oct 2026, Assignments 3–9)

Applied after a review against the standards of research-university software-engineering courses:

1. **Ownership check (micro-viva).** Each assignment page announces that the student may be asked to explain their Part A and REFIT in two minutes. `micro-viva.html` gives the instructor a random picker (runs locally) and a question bank per assignment. Each question asks about the student's own submitted reasoning.
2. **STRESS through Blackboard.** The texts were removed from the site, the repository and the offline packages (`tools/apply_lms_stress.py`; see `docs/stress-unlock.md`). Blackboard releases them after the Part A upload, and the page verifies the pasted text by fingerprint.
3. **Executable labs.** Assignments 3–5 gained a small executable lab, like Assignments 7–8 (`curriculum/learning-path/labs.js`): a fail-safe barrier decision, server-side access control, and an outage fallback. Five of the seven assignments from Assignment 3 onward now include executed tests.
4. **Varied formats.** Assignment 6 asks students to critique a colleague's flawed recommendation, and Assignment 9 to review another team's design. Criteria, points and fields are unchanged.
5. **Shorter pages.** The lecture-connection section, the scope notes and the partial-credit rubric levels are folded. Visible text before the task fell by about 38%.
6. **Pre/post concept inventory.** Fourteen items for Chapters 12–20, kept privately with the instructor (not in this repository) so that items stay unseen.
7. **Story.** The episode close now says "your turn: same reasoning, new case in the assignment", because assignment cases differ from the lecture story.

## Practice and evidence revision (3 Oct 2026)

Applied after a second review that scored evidence of effectiveness, engineering practice, assessment calibration and page length lowest.

**Lecture extra track (23 slides at most; the 20 pinned slides are unchanged).** In presenter mode, Enter on slide 19 opens three extra slides before the close. Students reach them from the close (*Lab & practice*).

1. *Live lab: predict, then run.* The class predicts the baseline on three demo cases, then runs the baseline and the corrected model of the assignment's teaching lab (`runtime/labs.js`, the same code the assignment uses). At least one case fails on the baseline.
2. *Explain it in two minutes.* Pairs rehearse the ownership check: decision, boundary, evidence that would change it.
3. *Your assignment, step by step.* Six steps, the format, the time, and links to the assignment and the student guide.

The 50-minute plan absorbs the track (+7 minutes on slide 19, taken from the concept-slide budget). Chapters 10 and 11 are unchanged (pixel-identical).

**Executed tests in every assignment from Assignment 3.** Assignments 3–9 each include a lab in which the student writes their own cases, runs a baseline and a corrected model, and explains the difference.

**Evidence of learning (`evidence.html`).** Three measures, computed locally from files the instructor already has:

| Measure | Source | Reported |
|---|---|---|
| Concept gain | Private 14-item inventory as Blackboard pre-test (start of Chapter 12) and post-test (after Chapter 20) | Normalized gain ⟨g⟩, mean individual gain, paired d<sub>z</sub>, improved/same/lower |
| Peer-instruction gain | Presenter close: *Export class evidence (CSV)* (counts from the presenting device) | % correct before and after discussion per vote, weighted overall gain; gut-check shift |
| Ownership | Micro-viva sheet downloaded as CSV and completed | Agrees / partly / does not agree, per assignment |

Plan for this offering: run the pre-test before Chapter 12, export class evidence after every lecture, run micro-vivas on 3–5 students per section per assignment, run the post-test after Chapter 20, then paste the page's summary into the course report. Reference points are Hake (1998) for ⟨g⟩ and Crouch & Mazur (2001) for peer instruction. Small sections give wide uncertainty, so the N is always reported.

**Grader calibration.** Anchored examples at full, partial and no credit for each criterion of Assignments 3–9 are kept privately with the instructor (not in this repository, because they reveal the assessed cases).

## Real cases and the two roles of AI (4 Oct 2026)

After teaching Chapter 12, the instructor found the aircraft example from the earlier lecture clearer than the abstract controller, and said the role of AI was hard to show in class.

**One documented real case per chapter.** The cover shows a *REAL CASE* chip. The first extra slide after slide 19, *This really happened*, lists four verified facts, maps the lecture's ideas to the real event, and links its sources. The lecture thus has at most 24 slides.

| Chapter | Real case | Same pattern as the episode |
|---|---|---|
| 12 Safety | Boeing 737 MAX · MCAS (2018–2019) | Each activation was bounded; repeated activations were not |
| 13 Security | First American Financial (2019) | Changing one number in the address opened other customers' documents |
| 14 Resilience | Maersk · NotPetya (2017) | Identity service lost; recovery relied on one surviving copy |
| 15 Reuse | Ariane 5 · Flight 501 (1996) | Reused code kept assumptions that no longer held |
| 16 Components | Mars Climate Orbiter (1999) | Interfaces matched; units did not |
| 17 Distributed | AWS us-east-1 (2021) | Retries without back-off amplified a fault |
| 20 Systems of systems | Northeast blackout (2003) | Stale data looked live, and neighbours were not told |

**Chapter 12 is told on an aircraft.** An automatic trim function, a per-command limiter, and an AI assistant that proposes trim sequences. The pinned case text (a controller that limits each actuation command) is unchanged; only the story layer moved from a plant to an airliner.

**Two roles of AI, named separately.**
- *AI in the system, which we analyse.* It appears on the case file and on the AI-segment slide, as an engineering question: does the protection hold whatever the AI proposes?
- *AI at your desk, which you practise with.* It appears on the explain-it extra slide, with three concrete uses: play the reviewer, generate test cases you then judge, and ask the two-minute check questions. "You sign the decision. AI does not."
