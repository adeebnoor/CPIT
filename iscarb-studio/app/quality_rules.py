from __future__ import annotations

QUALITY_ADDENDUM = r"""

ISCARB v1.7 QUALITY ADDENDUM — HARD GENERATION RULES

A0) ONE 90-MINUTE LECTURE, NOT A CHAPTER DUMP
The output is one live 90-minute lecture.
- Teach only SourceProfile.topic_families / in_scope_families selected for this session.
- Never reintroduce deferred_topics into Units 1-20.
- If the bundle is broader than 90 minutes, scope_fit may be COMPRESS and important excess content must be listed in deferred_topics.
- If the bundle represents multiple unrelated lectures/topics, scope_fit=MIXED and release must be blocked rather than fusing them.
- Twenty Units are twenty pages/stops in one decision journey, not twenty equal mini-lectures.
- Units 16-20 brief/launch assessment work; they do not imply the full portfolio is completed live in class.

A1) SOURCE-BUNDLE HIERARCHY
There is exactly one PRIMARY [P1] source and optional SUPPORTING [S#] sources.
- [P1] determines scope, terminology, and conflict precedence.
- [S#] sources may clarify/deepen/evidence an in-scope idea but may not create a second lecture merely because they were supplied.
- Every technical source_anchor must name the source ID, e.g. [P1] SLIDES 7-12 or [S2] p.4.
- If a supporting source conflicts materially with [P1], preserve [P1] and report the conflict.

A) TRIPLE PROVENANCE — DO NOT MIX THESE LAYERS
Every Unit has three distinct content channels:
1. core_content = ONLY user-supplied lecture-bundle technical content. No ISCARB pedagogy, no unsupplied current trend claims, no unsupplied Saudi facts, no AI guidance, no rubric/evidence/assurance method.
2. pedagogy_content = ISCARB instructional scaffolding and learner reasoning: CLO wording, H-Stack, PREDICT/DERIVE prompts, Senior Design Review, known/unknown framework, falsification protocol, peer critique, portfolio instructions, evidence policy, rubric method, assurance-case method, ethical/accountability framing.
3. enrichment_content = contextual/current/cultural/external extensions beyond the user-supplied lecture bundle. Every enrichment claim needs an enrichment_basis. If no verified source is supplied, state it as an explicit hypothetical scenario rather than a fact.
Pure pedagogy Units (especially 3, 4, 16, 18, 19, 20) may have empty core_content. Do NOT invent a source claim simply to fill core_content or source_anchor.

B) ONE COHERENT CENTRAL SYSTEM
Do not fuse unrelated source examples into one fictional platform. Choose ONE coherent central system for the Unit-1-to-Unit-20 decision thread. Other supplied examples may be used as comparisons but not merged into the crisis.

C) SOURCE ANCHOR ACCURACY
source_anchor must support only core_content and must name [P1]/[S#]. If core_content is empty, source_anchor may be empty or "N/A — ISCARB PEDAGOGY". If several supplied sources support a technical synthesis, cite each relevant source ID/range. Never cite a source to legitimize pedagogy or enrichment.

D) NAMED ETHICAL PURPOSE
Set named_ethical_purpose to one explicit professional/ethical purpose appropriate to the week. Unit 1 pedagogy_content must state this purpose as the professional reason the decision matters. Do not force religious vocabulary if artificial.

E) HYPOTHETICAL CONTEXT LANGUAGE
When a context is hypothetical, use explicit phrases such as "Assume that..." or "In this hypothetical Saudi scenario...". Never state invented national rules, mandates, data residency, infrastructure capabilities, SLAs, or regulations as facts.

F) SYNTHETIC EXERCISE DATA
Invented numbers are permitted only as clearly labeled synthetic/normalized exercise data and only if used by the learner in a calculation, sensitivity analysis, or decision threshold. Never present synthetic values as observed facts. Do not invent a technical formula and call it a standard formula. If supplied sources contain no formula, use a qualitative/ordinal matrix or explicitly define a local exercise score.

G) ETEC READINESS — MINIMUM SUFFICIENT ALIGNMENT
ETEC SLOs are all-or-nothing claims. Select the smallest set of SLOs that the 90-minute in-scope content PLUS learner task can fully demonstrate. Partial overlap does not count.
- Do not claim SLO9.1.2 for input validation alone; it materially also includes client/server-side development, cookies, and JavaScript.
- Do not claim SLO7.1.3 for misuse-case discussion alone; it requires detailed use cases, event flows, and functional-requirement relationships.
- Do not claim SLO8.1.5 for deployment discussion alone; it materially includes version control and project hosting.
- Prefer one fully evidenced SLO over four partial SLOs.
- Copy the official SLO→KLO map exactly; never infer it.
For every readiness_alignment item, atomicity_evidence must explain how EVERY material component of each selected SLO is taught/assessed. If this cannot be stated truthfully, remove that SLO.

H) ELITE ENGINEERING SEQUENCE
Unit 5 pedagogy_content must explicitly include PREDICT, CONSTRAINT, DERIVATION, and NAMED PRINCIPLE. Do not invent a formula absent from the supplied sources.
Unit 8 must present at least two defensible designs using source-derived mechanisms; do not solve the trade-off with new external controls unless taught in [P1]/[S#].
Unit 10 MUST be MARIS and must include in pedagogy_content: KNOWN / UNKNOWN / DECISION-SENSITIVE UNKNOWN / WHAT WE MONITOR.
Unit 15 pedagogy_content must contain explicit headings/phrases "AI MAY ASSIST" and "AI MUST NOT BE TRUSTED AUTONOMOUSLY". Avoid empirical AI claims unless a verified supplied source supports them.
Unit 17 must mutate a constraint but must not pre-solve the redesign with new technologies absent from Units 1-15. Require the learner to adapt source-derived mechanisms.

I) UNIT FUNCTION FIDELITY
Unit 2 = Domain Spine of all selected 90-minute topic families, not all material in a larger chapter bundle.
Unit 3 = exactly five visible CLOs in pedagogy_content (CLO1...CLO5).
Unit 4 = six visible H-Stack competencies in pedagogy_content.
Units 6–10 are MARIS; Units 11–15 ATQAN; Units 16–20 MAYYIZ.
Units 16–20 synthesize/assess; they do not introduce selected weekly content for the first time.

J) TREND, WELLBEING, AI, ACCOUNTABILITY
- Unit 13: source-derived enduring principles belong in core_content; contemporary practices beyond the supplied bundle belong in enrichment_content.
- Unit 14: source deployment/configuration mechanisms may be core_content; wellbeing/cognitive-load interpretation belongs in pedagogy_content unless externally verified.
- Unit 12: source logging/permission mechanisms may be core_content; ethical/accountability chain and amanah belong in pedagogy_content.
- Unit 15: source mechanisms being audited may be core_content; AI audit protocol belongs in pedagogy_content.

K) EVIDENCE / RUBRIC / ASSURANCE
Unit 18 pedagogy_content = CLAIM → EVIDENCE → WARRANT → COUNTER-EVIDENCE → RESIDUAL UNCERTAINTY. Do not introduce new technical methods as source facts unless present in [P1]/[S#].
Unit 19 pedagogy_content explains the 4-level rubric; rubric_criteria contains >=6 complete criterion×level descriptors.
Unit 20 pedagogy_content constructs a bounded assurance case. Never use absolute proof language. Prefer "supports a bounded claim" and keep technical subclaims proportional to supplied evidence.
"""

AUDIT_ADDENDUM = r"""

ISCARB v1.7 AUDITOR ADDENDUM — FAIL WHEN ANY OF THESE OCCUR
- the output behaves like exhaustive chapter coverage rather than one 90-minute lecture;
- deferred_topics are taught in Units 1-20;
- supporting [S#] sources silently expand or override the primary [P1] scope;
- a technical source_anchor lacks [P1]/[S#] identification;
- source-derived technical claims, ISCARB pedagogy, and contextual enrichment are mixed into the wrong provenance channel;
- a pedagogical Unit fabricates source bullets merely to satisfy core_content;
- source_anchor is used to legitimize pedagogy/enrichment rather than core_content;
- Unit 1 lacks a named ethical/professional purpose or reveals the diagnosis;
- unrelated source examples are fused into one crisis;
- a formula is introduced without source support and not explicitly defined as a local synthetic exercise score;
- a hypothetical contextual claim is written as a real Saudi mandate/regulation/capability;
- Unit 10 is not MARIS or lacks KNOWN/UNKNOWN/DECISION-SENSITIVE UNKNOWN/WHAT WE MONITOR;
- Unit 13 places unsupplied contemporary trend claims in core_content;
- Unit 15 lacks explicit AI MAY ASSIST / AI MUST NOT BE TRUSTED AUTONOMOUSLY language, or makes unsupported empirical AI claims;
- Unit 17 solves the mutation using technical controls not taught earlier/source-supported;
- Unit 18/19/20 pedagogy masquerades as source technical content;
- any ETEC SLO is only partially supported by the IN-SCOPE 90-minute content/task;
- the selected SLO→KLO mapping differs from the exact official map;
- assurance language overstates what evidence can establish.
Do not award PASS because fields are labeled correctly; audit the semantic content.
"""

REPAIR_ADDENDUM = r"""

ISCARB v1.7 REPAIR ADDENDUM
When repairing:
- preserve the one-lecture 90-minute scope and do not reintroduce deferred topics;
- keep [P1] primary precedence; use [S#] only to support the same lecture focus;
- preserve correct supplied technical content;
- MOVE ISCARB teaching/assessment scaffolding from core_content into pedagogy_content;
- MOVE unsupplied current/contextual claims into enrichment_content or rewrite as explicit scenario assumptions;
- allow core_content to be empty in pure pedagogy units; never fabricate source content;
- correct phases and fixed Unit functions;
- remove unsupported formulas/technologies rather than rationalizing them;
- reduce ETEC alignment to the minimum fully evidenced SLO set and provide truthful atomicity_evidence;
- reuse source mechanisms for Unit 17 adaptation;
- keep Unit 20 assurance bounded and evidence-proportionate;
- ensure every technical source_anchor names [P1]/[S#].
"""
