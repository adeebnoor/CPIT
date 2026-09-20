# CPIT-455 visual lecture release v3

The lecture reading layout put diagrams, explanations, questions and references
on long scrolling pages. This release uses a fixed presentation viewport and
explicit page navigation. CSS columns reflow full explanations; JavaScript uses
their measured width to expose every page. Text is not truncated or scaled to fit.

All nine chapters have authored visual summaries: 102 concept takeaways, source
figures or labelled concept diagrams, and a short opening case. The recurring
sequence is SEE, EXPLAIN, TEST, DECIDE, then required preparation and transfer.
Full explanations and answers remain in Details. All 579 original source slides,
original embedded figures, 45 preparation questions, assignments and draft keys
are retained. Long readings, tables and tool dialogs use the same page controls.

Content review corrected shorthand that could change the taught concept:
dependability includes resilience; reliability requirements include checking,
recovery, redundancy and process; the distributed chapter retains its six design
issues, four layers and five patterns. The inherited pump example now separates
POFOD targets from estimates and uncertainty rather than asserting an invalid
minimum test length. Deployment failure claims now state their assumptions.

The instructor guide and editable `iSCARB-Teaching-Template.md` make Professor
Adeeb Noor's method easier to adapt to another course. Design references:

- [MIT 6.102 course organization](https://web.mit.edu/6.102/www/sp25/general/):
  preparation, exercises and feedback.
- [W3C reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html):
  retain access to information and functionality when content is enlarged.
- [NIST confidence intervals for proportions](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm):
  distinguish an observed proportion from uncertainty in the underlying value.

These references inform specific decisions. They do not establish equivalent
learning outcomes or WCAG conformance.

Verification: all nine source ledgers and original fields/images are retained;
visual overview and complete explanation modes work; forward/backward navigation
traverses all simulated pages; keyboard page controls, dialog reopening, local
draft storage, preparation feedback, and exported-file re-opening pass DOM tests.
Offline exports no longer duplicate generated navigation. Static publication
audits and the public staging build pass. These checks are automated DOM/static
checks, not browser layout tests. The approved cloud browser timed out, so actual
CSS fragmentation, text enlargement and phone/desktop visual fit remain unverified.

Rebuild using the supplied extracted archive:

```sh
python tools/build_visual_release.py --input ../extracted/Fall2026
python tools/audit_classroom.py
node tools/check-fbr-release.mjs
npm --prefix tools/learning-path-tests test
python tools/build_public_site.py
```

Install the test directory's jsdom dependency before running its checks. Do not
run the older mastery builder after this step; it generates the previous guide
sections. GitHub Actions also runs preserved assignment and interaction checks.
The Blackboard announcement file is prepared copy, not a posted announcement.
