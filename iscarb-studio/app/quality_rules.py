from __future__ import annotations

QUALITY_ADDENDUM = r"""

ISCARB v1.9 QUALITY ADDENDUM — 90-MINUTE FULL-COVERAGE + ROLE-FIDELITY CONTRACT

A0) EXACTLY ONE 90-MINUTE LECTURE — FULL PRIMARY COVERAGE
The output is one live 90-minute lecture and MUST cover the complete PRIMARY [P1] lecture source at the level of all major technical topic families.
- Never defer, omit, replace, or move a major P1 topic to another lecture because P1 is long or dense.
- FIT = natural fit. COMPRESS = intelligent grouping, tighter synthesis, unequal depth, and removal of repetition — never omission.
- deferred_topics must remain empty for the primary lecture.
- A faculty focus changes emphasis/depth only; it may not narrow mandatory P1 coverage.
- Units 16-20 synthesize/assess/launch take-home evidence work; they never teach a major P1 family for the first time.

A1) SOURCE-BUNDLE HIERARCHY
There is exactly one PRIMARY [P1] and optional SUPPORTING [S#] sources.
- [P1] defines mandatory lecture scope, terminology, and conflict precedence.
- [S#] may clarify, deepen, verify, contextualize, or exemplify a P1 topic.
- Supporting-only topics never crowd out P1.
- Every technical source_anchor names [P1]/[S#]. Every primary topic-family ledger entry retains [P1].

A2) SMART COMPRESSION WITHOUT COVERAGE LOSS
When P1 is dense:
1. Preserve every major topic family explicitly.
2. Go deepest on mechanism-heavy, decision-critical, high-risk, or assessment-critical ideas.
3. Treat descriptive/detail topics concisely but visibly.
4. Merge related subtopics only when their technical meaning remains intact.
5. Eliminate repetition, not content.
6. Domain Spine + Topic Coverage ledger must prove complete P1 coverage by Unit 15.

A3) REAL PEDAGOGICAL ORDER — NOT TAG COMPLIANCE
Prediction-before-explanation must occur in the actual visible delivery order.
- Unit 1 must start from the crisis/evidence gap, not from explanatory definitions. Do not front-load the diagnosis or lecture definitions before the crisis.
- Unit 5 engineering_question itself MUST be a prediction prompt (use PREDICT / "before seeing the model" / equivalent) so the learner predicts before core explanation appears.
- Unit 5 should present raw constraints/evidence first; the NAMED PRINCIPLE comes only after learner prediction + derivation. Do not title Unit 5 with the final principle if doing so gives away the answer.
- A keyword such as PREDICT is insufficient if the technical explanation was already supplied first.

A) TRIPLE PROVENANCE — STRICT
Each Unit has three distinct channels:
1. core_content = ONLY user-supplied technical content.
2. pedagogy_content = ONLY ISCARB instructional scaffolding/reasoning/assessment structures.
3. enrichment_content = external/current/cultural/contextual extensions beyond the supplied bundle, each with a defensible enrichment_basis.
Pure pedagogy Units may have empty core_content. Never fabricate source content merely to populate a source anchor.

A4) PEDAGOGY IS NOT A HIDING PLACE FOR NEW TECHNOLOGY
pedagogy_content, student_action, takeaway, evidence, and scenario_assumptions must NOT smuggle in unsupplied technical controls or empirical technical claims.
- Examples of prohibited leakage unless source-supported: row-level encryption, immutable logging, penetration testing, IDS, Zero Trust, proxy/token gateways, container images, infrastructure-as-code, configuration-drift tooling, cryptography, or any other new implementation mechanism.
- If an external technical idea is genuinely needed, put it in enrichment_content with a real/explicit basis, or rewrite it as a non-factual design question. Do not disguise it as pedagogy.
- Prefer source-native wording: e.g., "record-level access control" rather than invented "row-level encryption"; "separate logging infrastructure" rather than invented "immutable logging".

A5) ENRICHMENT BASIS QUALITY
A vague phrase such as "standard literature", "industry best practice", or "modern practice" is NOT a release-quality basis.
- If a supplied supporting source supports the enrichment, identify it.
- If no verified supporting source exists, phrase the item as an explicit hypothetical/future exploration rather than a factual contemporary claim.
- Unit 13 may ask a future-facing design question without asserting unsupported adoption facts.

B) ONE COHERENT CENTRAL SYSTEM
Choose ONE coherent system from Unit 1 through Unit 20.
- Do not fuse unrelated P1 examples into one fictional platform.
- Comparative source examples may appear only as clearly labeled comparisons.
- named_ethical_purpose, Saudi scenario, portfolio artifact, mutation, evidence policy, and Unit 20 assurance case must all refer to the same central system.

C) SOURCE ANCHOR ACCURACY
source_anchor supports core_content only. If core_content is empty, use blank or "N/A — ISCARB PEDAGOGY". Never cite P1 to legitimize pedagogy or enrichment.

D) NAMED ETHICAL PURPOSE
Use one explicit professional/ethical purpose appropriate to the chosen central system. Do not widen the purpose to unrelated source examples merely because they appear elsewhere in P1.

E) HYPOTHETICAL CONTEXT LANGUAGE
When Saudi context is hypothetical, say "Assume that..." or "In this hypothetical Saudi scenario...". Never invent national mandates, SLAs, infrastructure capabilities, data-residency rules, or regulations as facts.

F) SYNTHETIC EXERCISE DATA
Synthetic values must be clearly labeled and actually used by the learner. Prefer normalized exercise units to currency unless real values are source-supported. Never present synthetic values as observed facts and never invent a formula as a standard formula.

G) ETEC READINESS — MINIMUM SUFFICIENT ALIGNMENT
ETEC SLOs are all-or-nothing claims. Select the smallest set fully demonstrated by the 90-minute P1 coverage + learner artifact.
- Partial overlap does not count.
- SLO→KLO mappings must match the official map exactly.
- atomicity_evidence must explain how EVERY material SLO component is taught/assessed.
- Prefer one fully evidenced SLO over four partial SLOs.
- EKUs are excluded from standardized-readiness targeting.

H) ELITE ENGINEERING SEQUENCE
Unit 5: real PREDICT → CONSTRAINT → DERIVATION → NAMED PRINCIPLE in visible order.
Unit 8: at least two defensible source-derived designs + explicit trade-off.
Unit 9: measurement + falsification; state what evidence would make us abandon the decision.
Unit 10: MARIS Senior Design Review + KNOWN / UNKNOWN / DECISION-SENSITIVE UNKNOWN / WHAT WE MONITOR.
Unit 15: explicit AI MAY ASSIST + AI MUST NOT BE TRUSTED AUTONOMOUSLY + Claim→Assumption→Source Check→Test→Failure Search→Human Sign-off.
Unit 17: mutate the constraint without pre-solving with untaught technology.

I) UNIT FUNCTION FIDELITY — DOMINANT PURPOSE, NOT A DECORATIVE BULLET
Unit 2 = Domain Spine of ALL major P1 families.
Unit 3 = exactly five visible CLOs.
Unit 4 = all six H-Stack competencies.
Units 11–15 = SOURCE-FIRST TECHNICAL TEACHING. Their titles/questions must name the P1 topic or mechanism being taught. Saudi context, accountability, future implications, practitioner workload, and critical AI literacy are integrated teaching moves in pedagogy/enrichment when relevant; they must not replace the technical spine.
Unit 11 should include a Saudi/Gulf application only when it materially changes the decision, explicitly HYPOTHETICAL if unsourced.
Unit 12 should integrate accountability/roles where relevant.
Unit 13 may include a future/design exploration, but the P1 evolution/improvement mechanism remains dominant.
Unit 14 may include practitioner workload/wellbeing only as a bounded consequence of the P1 mechanism; do not invent cognitive-load, alert-fatigue, or burnout facts.
Unit 15 may include AI audit literacy in pedagogy; the learner-facing title remains the P1 maturity/audit mechanism.
Unit 16 = Source-grounded Design Challenge.
Unit 17 = Change the Constraint + Peer Critique.
Unit 18 = Defend the Decision with evidence.
Unit 19 = Take-home Capabilities; detailed four-level rubric stays in rubric metadata.
Unit 20 = Take-home Decision / bounded assurance.
No Unit may invent numeric precision (percentages, thresholds, multipliers, adoption rates) absent from an identified source.

J) RUBRIC MUST ASSESS ISCARB CAPABILITY — NOT ONLY WEEKLY TOPICS
Unit 19 must have at least these six explicit criterion dimensions (weekly descriptors may be topic-specific):
1. Technical correctness + source fidelity.
2. First-principles / mechanism reasoning.
3. Alternatives + trade-off engineering judgment.
4. Evidence + falsification / verification quality.
5. Constraint adaptation + risk-aware redesign.
6. ETEC readiness + professional accountability.
Prefer also AI-audit/provenance and socio-technical/ethical responsibility when useful.
Every criterion has Distinguished / Ready / Developing / Not Yet Ready descriptors.

K) EVIDENCE / ASSURANCE BOUNDS
Unit 18 pedagogy_content = CLAIM → EVIDENCE → WARRANT → COUNTER-EVIDENCE → RESIDUAL UNCERTAINTY, using source- or learner-generated evidence only.
Unit 20 must remain bounded and evidence-proportionate.
- Avoid absolute assurance verbs in Unit 20 subclaims: guarantee, eliminate, prevent, prove secure, ensure zero risk, always, impossible to breach.
- Prefer: reduces, addresses, mitigates, supports, is designed to maintain, within the stated scenario/bounds.
- The final decision must retain residual uncertainty and allow APPROVE / CONDITIONALLY APPROVE / REDESIGN / REJECT.
"""

AUDIT_ADDENDUM = r"""

ISCARB v1.9 AUDITOR ADDENDUM — FAIL WHEN ANY OF THESE OCCUR
- any major P1 family is omitted/deferred/replaced;
- Domain Spine/topic_coverage does not account for all P1 families;
- Unit 5 says PREDICT but the learner has already been given the explanatory principle before prediction;
- Unit 1 front-loads definitions/diagnosis before the crisis;
- Units 11–15 use framework labels as the dominant title/question instead of the P1 technical mechanism;
- pedagogy/student_action/takeaway/evidence smuggles in unsupplied technical controls;
- enrichment has only vague basis such as "standard literature" or "industry best practice" and is written as fact;
- source-derived content, pedagogy, and enrichment are mixed;
- the ethical purpose/Saudi scenario/portfolio/mutation/assurance refer to different central systems;
- synthetic data appears factual or fake-precise;
- Unit 19 rubric lacks explicit first-principles, trade-off, evidence/falsification, constraint adaptation, and readiness dimensions;
- Unit 20 uses absolute assurance language such as guarantee/eliminate/prevent/prove secure without source-bounded meaning;
- any ETEC SLO is partially supported or mapped incorrectly.
Do not award PASS because labels/tags exist. Judge what the student actually sees and does.
"""

REPAIR_ADDENDUM = r"""

ISCARB v1.9 REPAIR ADDENDUM
When repairing:
- preserve fixed 90 minutes and full P1 topic-family coverage;
- repair PEDAGOGICAL ORDER, not just metadata: prediction must actually precede explanation;
- make Units 11–15 visibly source-first and integrate Saudi context / accountability / future implication / practitioner consequence / AI audit only when relevant;
- remove new technical controls from pedagogy/student actions unless source-supported; move legitimate external ideas to enrichment or rewrite as questions;
- replace vague enrichment bases with supplied-source IDs or explicit hypothetical/future-exploration language;
- keep one coherent central system across ethics, context, portfolio, mutation, and assurance;
- rebuild Unit 19 around explicit ISCARB capability dimensions, with weekly-topic-specific descriptors;
- rewrite Unit 20 absolute verbs into bounded evidence-proportionate claims;
- preserve correct source content and exact source anchors;
- reduce ETEC alignment to the minimum fully evidenced set;
- never introduce new technical content merely to make a gate pass.
"""
