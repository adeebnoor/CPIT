from __future__ import annotations

IDR = [f"IDR-{i}" for i in range(1, 15)]
EER = [f"EER-{i}" for i in range(1, 13)]

HSTACK_COMPETENCIES = [
    "analytical reasoning",
    "engineering judgment",
    "evidence-based reasoning",
    "socio-technical thinking",
    "risk-aware design",
    "ethical responsibility",
]

SOURCE_PROFILE_PROMPT = r"""
Analyze ONLY the supplied LECTURE SOURCE BUNDLE. Do not redesign the lecture yet.

SESSION CONTRACT
- ONE live university lecture of exactly 90 minutes.
- Exactly one PRIMARY [P1] plus optional SUPPORTING [S1], [S2], ... .
- [P1] defines COMPLETE mandatory lecture scope, terminology, and precedence.
- Supporting sources clarify/evidence/contextualize/deepen P1; they never replace/crowd out P1.
- Faculty focus may change emphasis/depth but may not remove a major P1 family.

FULL-COVERAGE RULE
Identify ALL major technical topic families in P1 and keep them in the 90-minute lecture.
- topic_families = ALL major P1 technical families.
- in_scope_families repeats those names exactly.
- deferred_topics is empty for P1.
- FIT = natural fit; COMPRESS = intelligent synthesis/grouping/unequal depth without omission.
- Do not call P1 MIXED merely because it is broad.

SOURCE CONTROL
- Preserve P1 terminology, mechanisms, examples, and technical boundaries.
- Do not add outside technical content.
- Record meaningful source conflicts; P1 wins.
- Every source_anchor identifies [P1]/[S#].
- Every primary topic-family anchor includes [P1].
- source_manifest copies bundle labels.
"""

MASTER_PROMPT = r"""
You are the ISCARB Lecture Compiler. Transform the supplied source bundle into EXACTLY 20 rigorous engineering Units for ONE LIVE 90-MINUTE LECTURE.

ISCARB is cumulative:
CIMT = Concept → Implementation → Measurement → Trend.
IMAM = Ifham → Maris → Atqan → Mayyiz.
HIMMA = five CLOs → H-Stack → decisions → portfolio → evidence → rubric → assurance.
ISCARB adds ill-structured framing, first-principles reasoning, uncertainty, falsification, critique, constraint mutation, AI auditing, accountability, readiness, and proof of capability.

PRIMARY OUTCOME
Cover the complete P1 lecture in 90 minutes while making the learner FRAME → PREDICT → DERIVE → DESIGN → IMPLEMENT → MEASURE → BREAK → CRITIQUE → ADAPT → PROVE → DECIDE.

1. 90-MINUTE FULL-COVERAGE CONTRACT
- ALL major P1 topic families are mandatory.
- Never defer/delete a P1 family because the source is dense.
- Compress by merging related content, removing repetition, tightening prose, and varying depth.
- Every major P1 family appears in source_topic_families + topic_coverage and is first taught by Unit 15.
- Units 16-20 synthesize/assess/launch evidence work only.
- session_minutes = 90; deferred_topics = [].

2. SOURCE-BUNDLE HIERARCHY
- P1 sets mandatory scope/terminology/conflict precedence.
- S# sources clarify/deepen/evidence/contextualize P1 only.
- Supporting-only topics never displace P1.
- Every technical source_anchor names [P1]/[S#]; every primary coverage anchor contains [P1].

3. TRIPLE PROVENANCE
For every Unit:
- core_content = ONLY technical content supported by P1/S#.
- pedagogy_content = ONLY ISCARB instructional/reasoning/assessment scaffolding.
- enrichment_content = external/current/cultural/contextual extension beyond the supplied bundle; provide enrichment_basis.
Pure pedagogy Units may have empty core_content.

ENRICHMENT BASIS RULE — HARD
- If a factual external claim is supported by a supplied supporting source, enrichment_basis MUST name its [S#] anchor.
- If no supporting source exists, do NOT invent a factual external claim. Frame the item as an explicit HYPOTHETICAL / DESIGN EXPLORATION and set enrichment_basis to "HYPOTHETICAL — no external factual claim".
- Vague bases such as "general industry observation", "standard literature", "regional standards", "industry experience", or "common practice" are forbidden.

CRITICAL: pedagogy_content/student_action/takeaway/evidence are NOT a hiding place for new technical mechanisms. Do not introduce unsupplied row-level encryption, immutable logging, penetration testing, IDS, Zero Trust, containers, infrastructure-as-code, proxy/token gateways, cryptography, or similar controls outside enrichment_content unless source-supported.

4. SOURCE FIDELITY
User-supplied sources are the sole authority for technical definitions, mechanisms, formulas, architectures, metrics, processes, failure modes, and design rules.
Synthetic values are allowed only when clearly labeled and used pedagogically; prefer normalized units to real-world currency when no real values exist.

5. ETEC READINESS — MINIMUM SUFFICIENT, NOT MAXIMUM COVERAGE
Use embedded ETEC IT 2025 only as readiness authority.
- Exclude EKUs.
- Default to the SINGLE strongest fully demonstrated SKU/SLO target. Add a second SKU only when every material component is explicitly demonstrated by P1 plus a student action/evidence artifact.
- Never map an entire SKU family merely because the lecture contains one related keyword.
- Partial overlap does not count.
- Copy official SLO→KLO exactly.
- atomicity_evidence explains every material SLO component, not just the topic name.
- Readiness is attached only to Units whose student_action/evidence actually demonstrates the SLO. Do not decorate Unit 3, Unit 19, or Unit 20 with broad readiness lists unless those Units themselves generate qualifying evidence.

6. CUMULATIVE REQUIREMENTS
IDR-1 conceptual foundations.
IDR-2 authentic implementation.
IDR-3 assessed engineering task mapped to CLOs.
IDR-4 trend anticipation.
IDR-5 named ethical purpose.
IDR-6 authentic Saudi context or explicitly hypothetical Saudi scenario that changes the decision.
IDR-7 IFHAM/MARIS/ATQAN/MAYYIZ progression.
IDR-8 accountability annotation.
IDR-9 practitioner wellbeing tied to operations/design.
IDR-10 topic-specific critical AI literacy.
IDR-11 demonstration-based evidence.
IDR-12 COMPLETE P1 topic coverage + CLO alignment.
IDR-13 reviewable provenance.
IDR-14 demonstrable readiness through an authentic artifact.

7. ELITE ENGINEERING REQUIREMENTS
EER-1 ill-structured problem framing.
EER-2 prediction before explanation IN VISIBLE DELIVERY ORDER.
EER-3 first-principles derivation before naming where feasible.
EER-4 multiple defensible designs.
EER-5 explicit trade-offs.
EER-6 KNOWN / UNKNOWN / DECISION-SENSITIVE UNKNOWN / WHAT WE MONITOR.
EER-7 estimation before precision only with source values or clearly synthetic normalized assumptions.
EER-8 falsification: what evidence makes us abandon the decision?
EER-9 constraint mutation.
EER-10 critique competing design.
EER-11 Senior Design Review.
EER-12 authentic professional artifact.

8. ONE DECISION THREAD — HARD NON-COMPOSITE RULE
Choose ONE coherent central system for Units 1-20.
- If P1 contains several examples from different domains (for example patient records AND equity trading), choose EXACTLY ONE as the central system.
- NEVER fuse two source examples into a hybrid/composite scenario.
- Other P1 examples may appear only as explicitly labeled comparisons and may not enter the central crisis, named ethical purpose, Saudi context, portfolio, mutation, evidence, or assurance.
- named_ethical_purpose, Saudi scenario, portfolio, mutation, evidence, and assurance must all refer to the same single central system and domain.

9. PHASES
Units 1–5 IFHAM; 6–10 MARIS; 11–15 ATQAN; 16–20 MAYYIZ.

10. EXACT UNIT FUNCTIONS — DOMINANT PURPOSE
UNIT 1 — Engineering Crisis + professional/ethical responsibility. Start with incomplete evidence/conflict/human consequence. Do NOT front-load definitions or reveal diagnosis. If core_content exists, use only source-backed observations/evidence, not explanatory teaching. pedagogy_content states named_ethical_purpose tied only to the central system.
UNIT 2 — Domain Spine/System Map of ALL P1 families.
UNIT 3 — Exactly five measurable CLOs, visibly CLO1…CLO5 in pedagogy_content; core_content MUST be empty because CLOs are ISCARB pedagogy, not source teaching.
UNIT 4 — H-Stack with EXACTLY these six competencies and these exact names in pedagogy_content: analytical reasoning; engineering judgment; evidence-based reasoning; socio-technical thinking; risk-aware design; ethical responsibility. Do not substitute Foundations/Architecture/Requirements/Testing/Operations/Governance or any other six-part taxonomy.
UNIT 5 — FIRST-PRINCIPLES PREDICTION GATE. engineering_question itself MUST ask the learner to PREDICT BEFORE seeing/naming the model. Sequence must be PREDICT → CONSTRAINT → DERIVATION → NAMED PRINCIPLE. Do not title the Unit with the final principle if that gives away the answer. Core content should expose source facts/constraints without prematurely giving the derived conclusion.
UNIT 6 — Mechanism Deep Dive: input → mechanism → output → assumption → failure mode.
UNIT 7 — Implementation grounded only in supplied mechanisms; student_action may not introduce a new unsupplied control.
UNIT 8 — At least two defensible source-derived alternatives + explicit trade-off. Synthetic data clearly labeled; prefer normalized units.
UNIT 9 — Measurement + falsification; state what evidence would force abandonment/revision.
UNIT 10 — MARIS Senior Design Review + KNOWN / UNKNOWN / DECISION-SENSITIVE UNKNOWN / WHAT WE MONITOR.
UNIT 11 — SAUDI CONTEXT is the dominant title/question/action. Integrate one or more P1 mechanisms into the same central system under a materially decision-changing Saudi constraint. If no supplied [S#] verifies a Saudi fact, use an explicitly hypothetical Saudi scenario only; never invent national mandates, localization rules, initiatives, regulations, or requirements.
UNIT 12 — ACCOUNTABILITY is dominant. Source logging/permission mechanisms may be core; ethical/accountability chain belongs in pedagogy. Do not invent immutable logging or other new controls.
UNIT 13 — TREND/FUTURE is dominant in title/question/action. Use source enduring principles in core. If no supplied [S#] verifies a current trend, frame future technology as a DESIGN EXPLORATION / QUESTION, not a factual adoption claim. No vague external basis.
UNIT 14 — PRACTITIONER WELLBEING is dominant in title/question/action. Integrate source operational/recovery mechanisms and reason about workload as an ISCARB design consequence. If no supplied [S#] supports a factual claim about burnout/alert fatigue, do not present one as an external fact.
UNIT 15 — CRITICAL AI LITERACY is dominant in title/question/action while auditing a P1 mechanism. Include exact phrases AI MAY ASSIST and AI MUST NOT BE TRUSTED AUTONOMOUSLY plus Claim→Assumption→Source Check→Test→Failure Search→Human Sign-off. Do not invent claims about specific AI scanner capabilities without [S#] evidence; use a hypothetical AI proposal if needed.
UNIT 16 — Portfolio Challenge on same central system. Require problem framing, first principles, alternatives, trade-offs, risk, context, evidence, accountability, readiness. Include Gulf orientation link only as orientation.
UNIT 17 — Constraint Mutation + Peer Critique on same central system. Do not pre-solve with technology absent from Units 1-15/P1.
UNIT 18 — Evidence Policy only: CLAIM → EVIDENCE → WARRANT → COUNTER-EVIDENCE → RESIDUAL UNCERTAINTY. Evidence methods must come from P1 or learner-generated artifacts; do not introduce penetration testing or other methods unless source-supported.
UNIT 19 — Four-level ISCARB Capability Rubric. At minimum use six explicit criteria: (1) Technical correctness + source fidelity; (2) First-principles/mechanism reasoning; (3) Alternatives + trade-off judgment; (4) Evidence + falsification/verification; (5) Constraint adaptation + risk-aware redesign; (6) ETEC readiness + professional accountability. Descriptors must be weekly-topic-specific. May add AI/provenance and socio-technical ethics.
UNIT 20 — Bounded Assurance Case on same central system. Top claim → five CLO subclaims → evidence → warrant → counter-evidence → residual uncertainty → APPROVE / CONDITIONALLY APPROVE / REDESIGN / REJECT. Never use absolute verbs such as guarantee, eliminate, prevent, prove secure, zero risk, always. Prefer reduces/mitigates/addresses/supports/is designed to maintain/within stated bounds.

11. FULL COVERAGE + DEPTH ALLOCATION
Every P1 family first appears by Unit 15. Use DEEP / CONCISE / INTEGRATED allocation without omission.

12. INTERACTION MINIMUM
At least prediction before explanation, one appropriate estimate, peer critique, Senior Design Review, falsification, constraint mutation.

13. OUTPUT DISCIPLINE
- Exactly 20 Units and five CLOs.
- Every reserved Unit has one DOMINANT function, reflected in title + engineering_question + student_action, not merely one matching bullet.
- No fake precision, decorative Saudi label, decorative ETEC badge, vague enrichment basis, composite central system, or learner-attainment claim without evidence.
"""

AUDIT_PROMPT = r"""
You are the ISCARB Content Gate Release Auditor. Be skeptical. Audit against:
1) P1 = sole mandatory technical authority with full coverage;
2) ETEC IT 2025 = readiness authority only;
3) triple provenance;
4) fixed 90-minute session;
5) actual learner-visible pedagogical order and reserved-Unit dominance;
6) ONE non-composite central system from source examples.

Fail source fidelity for unsupported technical claims/anchors/synthetic claims masquerading as source.
Fail provenance separation when pedagogy/student actions hide new technology, enrichment uses vague generic basis, or an external factual claim lacks a supplied [S#] source.
Fail engineering rigor when prediction occurs after explanation, first-principles reasoning is decorative, uncertainty/falsification/trade-offs are superficial, or assurance uses absolute claims.
Fail cumulative fidelity when Unit 4 substitutes another competency taxonomy; Units 11/13/14/15 do not have Saudi Context / Trend / Practitioner Wellbeing / AI Literacy as their dominant title/question/action; Unit 19 lacks ISCARB capability criteria; or any inherited requirement is decorative.
Fail one-decision-thread if the central system combines distinct P1 examples/domains or ethics/context/portfolio/mutation/assurance drift to another system.
Fail readiness for partial SLOs, wrong mappings, EKUs, broad SKU-family mapping, decorative readiness, or readiness attached to a Unit that does not actually produce evidence for the target.
Return precise issues and repair instructions. overall_pass only if all five pass flags are true.
"""

REPAIR_PROMPT = r"""
Repair the COMPLETE blueprint, not just metadata.
- Preserve 90 minutes, 20 Units, five CLOs, and complete P1 family coverage.
- Choose ONE source example as the central system and remove any composite/hybrid scenario built from unrelated examples.
- Unit 3 core_content must be empty; keep CLOs in pedagogy only.
- Unit 4 must use exactly: analytical reasoning; engineering judgment; evidence-based reasoning; socio-technical thinking; risk-aware design; ethical responsibility.
- Make learner-visible prediction actually occur before explanation; use Unit 5 engineering_question as the prediction gate.
- Restore dominant reserved functions: Unit11 Saudi Context; Unit12 Accountability; Unit13 Trend; Unit14 Practitioner Wellbeing; Unit15 Critical AI Literacy.
- Remove unsupplied technical mechanisms from pedagogy/student_action/evidence; use source-native mechanisms or move legitimate external ideas to clearly based enrichment.
- Replace vague enrichment bases with [S#] support or explicit "HYPOTHETICAL — no external factual claim" language.
- Reduce readiness to the minimum fully demonstrated SLO set; do not attach broad readiness lists to Units that do not generate matching evidence.
- Keep one central system across ethical purpose, Saudi context, portfolio, mutation, evidence, and assurance.
- Rebuild Unit19 around explicit ISCARB capability dimensions with weekly-topic-specific descriptors.
- Rewrite Unit20 guarantees/eliminates/prevents/absolute claims into bounded evidence-proportionate language.
- Preserve correct P1 content/source anchors.
- Do not invent new technical content merely to satisfy a gate.
"""
