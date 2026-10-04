# iSCARB · CPIT-455 · Evaluation plan for evidence of effectiveness

Status: plan for the current term (written 5 Oct 2026). No outcome data exist yet. Every number reported from this plan must come from the instruments below, computed on the [evidence page](https://adeebnoor.github.io/CPIT/evidence.html).

## 1. Research questions

| | Question | Primary measure |
|---|---|---|
| RQ1 | Do students' conceptual understanding of dependable-systems engineering improve across Chapters 12–20? | Concept inventory, pre/post: normalized gain ⟨g⟩ and paired effect size |
| RQ2 | Does discussion in class change students' answers toward the correct one? | Peer-instruction votes, round 1 → round 2 |
| RQ3 | Do students learn to write tests that find faults, not only tests that pass? | Share of known bugs caught (mutation test), Assignments 4 → 9 |
| RQ4 | Does new evidence change students' engineering decisions appropriately? | Boundary status and REFIT choice after STRESS; REFIT rubric scores |
| RQ5 | Do assignment results agree with independent measures of learning? | Correlation of A3–A9 with the final exam (convergent validity); micro-viva agreement (ownership) |
| RQ6 | How do students perceive engagement, clarity, judgment and the build? | 12-item survey, four scales, Cronbach's α |

## 2. Design

**Single cohort with repeated measures.** All students of the term's sections take part. Two built-in contrasts:

- **Pre/post (RQ1).** The same 14-item concept inventory is given twice as a Blackboard test:
  - once before Chapter 12 is assessed;
  - once after Chapter 20, before the final exam.

  The items are not exam items and are not released.
- **Within-course comparison (RQ5, secondary).** Assignments 1–2 (Chapters 10–11) keep the earlier format. Assignments 3–9 use the story lecture, the in-class Python lab, the Python build with mutation testing, and the new-evidence (STRESS → REFIT) cycle. The same students therefore provide a paired comparison.

  This contrast is **quasi-experimental**: chapter content, difficulty and timing also differ. Report it as supporting evidence, never as a causal effect.

**Optional historical comparison.** The previous cohort of CPIT-455 used the earlier format for every chapter. Its results may be compared only under these conditions:
- the same items or rubric criteria exist in both years;
- archival use of the grades is approved by the ethics committee.

**Note on timing this term.** If the pre-test was not given before the Chapter 12 lecture, give it before the Chapter 13 lecture. Then report two things:
- that Chapter 12 had already been taught;
- the gain separately for items on Chapters 13–20, as well as overall.

## 3. Instruments

| Instrument | Where | Who keeps it |
|---|---|---|
| Concept inventory, 14 items (pre and post) | Blackboard test | Instructor (private, not in the repository) |
| Class votes, rounds 1 and 2 | Lecture presenter mode → *Export class evidence (CSV)* | Instructor |
| Build record (course checks, own tests, known bugs caught, viva request) | In each student's final export | Student submission |
| Boundary status and REFIT choice | In each student's final export | Student submission |
| Rubric scores, five criteria per assignment | Blackboard Grade Center | Instructor |
| Micro-viva record (agrees / partly / does not agree) | [Micro-viva page](https://adeebnoor.github.io/CPIT/micro-viva.html) | Instructor |
| Perception survey, 12 items, 4 scales | Anonymous Blackboard survey after Assignment 9 (items listed on the evidence page) | Instructor |
| University course evaluation | KAU system (Qeem / Odus Plus) | University |

## 4. Analysis

The evidence page computes all of the following in the browser:

- **RQ1.**
  - Class normalized gain ⟨g⟩ (Hake, 1998), with a bootstrap 95% CI (2000 resamples, fixed seed).
  - The paired t-test.
  - The mean change with a 95% CI.
  - Effect sizes d_z and Hedges' g_av (Lakens, 2013).
  - Students are matched by ID; unmatched students are reported, not imputed.
- **RQ2.** % correct before and after discussion, weighted by first-round votes, with the gain per vote (Crouch & Mazur, 2001).
- **RQ3.** Mean share of known bugs caught per assignment (A4–A9). The expected pattern is an upward trajectory. Report N per assignment.
- **RQ4.** The distribution of boundary status (INTACT / PRESSURED / CROSSED) and REFIT choice (RETAIN / REVISE / REPLACE) per assignment. A RETAIN after a CROSSED boundary is examined qualitatively.
- **RQ5.**
  - Pearson r between each student's mean A3–A9 score and the midterm and final exams, with Fisher-z 95% CIs.
  - The paired comparison A1–A2 → A3–A9 (d_z, CI).
  - The micro-viva agreement rate.
- **RQ6.** Scale means and SDs, with Cronbach's α per scale (Cronbach, 1951). Treat α ≥ .70 as acceptable, and report α with N. Open answers are coded thematically by two readers.

Report intervals and N with every estimate. With one or two sections, N is small, so emphasise effect sizes and intervals over p-values.

## 5. Ethics and data protection

1. **Approval first.** Before any data are used outside the course report, obtain approval or an exemption from the KAU research ethics committee.
2. **Inform and allow opt-out.** At the start of the term, publish a short notice in Blackboard. It must say three things:
   - which course data may be analysed for research;
   - that analysis is de-identified;
   - that students can opt out at any time by email, with no effect on grades.

   Keep the list of students who do not opt out (or who consent, if the committee requires opt-in).
3. **De-identify.** Use section 7 of the evidence page:
   - Student IDs become keyed HMAC-SHA-256 codes, using a secret phrase that only the instructor keeps.
   - Only consenting students are written.
   - No names, IDs or free text leave the instructor's computer.
4. **Separate roles.** Grades are final before any research analysis of the same term. The survey is anonymous.
5. **Retention.** Keep raw files on university storage only. Delete the key phrase when the study ends if no further linkage is needed.

## 6. Threats to validity and how they are handled

| Threat | Handling |
|---|---|
| No randomised control group | Report as a cohort study. Use the within-course contrast and the historical comparison only as supporting evidence. |
| Testing effect (same inventory twice) | Answers are not released between the tests. The post-test is several weeks later. |
| Instructor as researcher | Rubric anchors and grader calibration are written in advance. A second marker re-grades a random 10% of one assignment; report agreement. |
| Novelty or Hawthorne effect | Measure across seven assignments, not one. Report the trajectory. |
| Attrition | Report pre-only and post-only students separately. |
| Mutation-test ceiling | Report the share of students who catch all bugs per assignment. A ceiling limits RQ3 trends. |
| AI assistance | AI-use declarations are coded. Micro-viva agreement is reported as a check on ownership. |

## 7. Timeline (this term)

| When | Step |
|---|---|
| Now | Ethics application; Blackboard research notice; pre-test (see the timing note) |
| Every lecture | Run the votes in two rounds; export class evidence at the episode close |
| After each assignment | Micro-viva for 3–5 random students per section; keep the record sheet |
| After Assignment 9 | Post-test; perception survey |
| After grades are final | Grade Center export; collect the final .md exports (or PDFs); run sections 1–7; download the de-identified dataset |

## 8. Reporting checklist (for a paper)

- [ ] Context: course, level, number of sections and students, term, instructor role
- [ ] Intervention described so it can be reproduced: story lecture, votes, in-class Python lab, build with mutation testing, STRESS → REFIT, micro-viva (link the public site and repository)
- [ ] Every measure with N, mean, SD or CI, and effect size
- [ ] Reliability of the survey scales (α) and grader agreement
- [ ] Limitations from section 6
- [ ] Ethics approval number and the consent procedure

## References

- Cronbach, L. J. (1951). Coefficient alpha and the internal structure of tests. *Psychometrika*, 16(3), 297–334.
- Crouch, C. H., & Mazur, E. (2001). Peer Instruction: Ten years of experience and results. *American Journal of Physics*, 69(9), 970–977.
- Hake, R. R. (1998). Interactive-engagement versus traditional methods: A six-thousand-student survey of mechanics test data for introductory physics courses. *American Journal of Physics*, 66(1), 64–74.
- Lakens, D. (2013). Calculating and reporting effect sizes to facilitate cumulative science: A practical primer for t-tests and ANOVAs. *Frontiers in Psychology*, 4, 863.
