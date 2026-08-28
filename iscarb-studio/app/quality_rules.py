from __future__ import annotations

QUALITY_ADDENDUM = r"""

ISCARB v1.5 QUALITY ADDENDUM — APPLY AS HARD GENERATION RULES

1) ONE COHERENT CENTRAL SYSTEM
Do not fuse unrelated source examples into one fictional platform. Choose ONE coherent central system for the Unit-1-to-Unit-20 decision thread. Other examples present in the weekly source may appear as source examples or comparisons, but must not be merged into the central crisis unless the source itself integrates them.

2) PROVENANCE BY CONTENT TYPE
core_content is strictly weekly-source-derived technical content.
The following are normally ISCARB enrichment unless explicitly present in the weekly source and must therefore be placed in enrichment_content, not core_content: AI guidance, practitioner wellbeing/cognitive-load claims, ethical/accountability interpretation, Senior Design Review method, falsification method, constraint-mutation method, evidence-policy method, rubric methodology, readiness interpretation, and contemporary trend claims.
For these units, anchor the enrichment to a source-derived technical mechanism, but do not pretend the pedagogy itself came from the slide.

3) SOURCE ANCHOR ACCURACY
source_anchor must support the technical bullets actually present in core_content. If a unit synthesizes several source slides, cite a range/list such as "SLIDES 28-32" or "SLIDES 20,23-24" rather than a single unrelated slide. Assessment-only synthesis may use "SYNTHESIS OF SLIDES ...". Never cite one slide merely because the unit needs a non-empty anchor.

4) HYPOTHETICAL CONTEXT LANGUAGE
If enrichment_basis says hypothetical, every claim that sounds like a rule, mandate, national requirement, regulation, infrastructure fact, or system capability must be phrased explicitly as a scenario assumption (for example: "Assume that..." or "In this hypothetical scenario..."). Do not write "national initiatives require" or "market rules mandate" without a verified external authority supplied to the system.

5) SYNTHETIC EXERCISE DATA
Invented numbers are allowed only when clearly labeled as synthetic/normalized exercise data and only when the numbers are used in a learner calculation, sensitivity analysis, or decision threshold. Do not create decorative precision. Prefer normalized scores or ranges when real values are absent.

6) READINESS ATOMICITY
ETEC SLOs are all-or-nothing readiness claims. Claim an SLO only when the weekly source plus the learner task can demonstrate every material component of that SLO. Partial topic overlap is NOT a readiness target.
Examples: do not claim SLO9.1.2 merely because the lecture teaches input validation if it does not also teach/assess the other material elements stated in that SLO; do not claim SLO8.1.5 merely because the weekly source discusses deployment if version control/project hosting/deployment-services performance is not actually taught and assessed.
Prefer the minimum sufficient alignment: one fully evidenced SLO is better than four partial alignments.
Use the exact official SLO→KLO map supplied separately. Never infer KLO mappings.

7) ELITE ENGINEERING SEQUENCE
Unit 5 must visibly include a prediction before explanation and a first-principles derivation. Use explicit labels in the content or student action: PREDICT, CONSTRAINT, DERIVATION, NAMED PRINCIPLE.
Unit 8 must present two defensible alternatives and a decision criterion. A clear "A versus B" comparison is acceptable; do not force artificial Option A/Option B wording.
By Unit 10, uncertainty must be operationalized explicitly as KNOWN / UNKNOWN / DECISION-SENSITIVE UNKNOWN / WHAT WE MONITOR.

8) ASSESSMENT UNITS MUST NOT TEACH NEW WEEKLY CONTENT
Units 16-20 synthesize, mutate, assess, prove, and assure. They may reuse source mechanisms, but must not introduce a major weekly technical concept for the first time.

9) ASSURANCE LANGUAGE
An assurance case supports a bounded claim; it does not prove absolute security. Avoid "undeniable", "proves security", "proven secure", "guarantees security", "proving critical service survivability", or equivalent certainty language. Prefer "supports a bounded claim" and make residual uncertainty explicit.
"""

AUDIT_ADDENDUM = r"""

ISCARB v1.5 AUDITOR ADDENDUM — FAIL WHEN ANY OF THESE OCCUR
- the central crisis splices unrelated source examples/domains into one artificial platform;
- a Unit's source_anchor does not actually support its core_content or a multi-slide synthesis is falsely attributed to one slide;
- AI, wellbeing, accountability, design-review, falsification, evidence-policy, rubric, readiness, or trend methodology is presented as weekly-source technical content when absent from the source;
- hypothetical Saudi/contextual claims are phrased as factual mandates, regulations, national requirements, or verified system capabilities;
- synthetic numbers create false precision or are not used by a learner decision/calculation;
- any ETEC SLO is only partially supported by the weekly source/task;
- any selected SLO→KLO mapping differs from the exact official mapping supplied in the ETEC map;
- Unit 5 lacks a genuine prediction-before-explanation and a first-principles derivation;
- Unit 10 lacks explicit known/unknown/decision-sensitive-unknown/monitoring reasoning;
- Unit 20 uses absolute-proof language instead of bounded assurance.
Do not award source_fidelity_pass or provenance_separation_pass merely because fields are labeled correctly; audit the semantic contents of those fields against the weekly source.
"""

REPAIR_ADDENDUM = r"""

ISCARB v1.5 REPAIR ADDENDUM
When repairing:
- choose one coherent central system and preserve other source examples only as comparisons;
- move unsourced pedagogy/context from core_content to enrichment_content rather than deleting useful pedagogy;
- correct source anchors to the exact supporting slide(s);
- rewrite hypothetical claims as explicit assumptions;
- remove readiness targets that only partially satisfy an ETEC SLO;
- correct all SLO→KLO mappings to the supplied official map;
- make Unit 5 prediction/derivation explicit;
- make Unit 10 known/unknown/monitoring explicit;
- preserve bounded assurance language in Unit 20.
"""
