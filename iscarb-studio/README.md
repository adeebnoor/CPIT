# ISCARB Faculty Studio v3

**Engineering better university teaching.**

ISCARB Faculty Studio turns one complete weekly lecture into a **90-minute, 20-unit, source-locked engineering learning journey**. Faculty can start from a preserved ready lecture, upgrade their own material, preview a presenter-first visual deck, inspect readiness/evidence, and reuse the result.

## Start in three minutes

1. Open the live Faculty Studio.
2. Choose **Use a Ready Lecture** or **Upgrade My Lecture**.
3. Provide exactly one PRIMARY lecture (file or public URL).
4. Optionally add supporting files/URLs.
5. Compile, inspect the Presenter Preview, and read the release result.
6. Use the **Faculty Starter Kit** before piloting the method across multiple weeks.

## Three entry points

### 1) Use a Ready Lecture
The public studio exposes preserved CPIT-455 CIMT lectures as real teaching artifacts. A faculty member can open the original or load it directly into the ISCARB upgrade workflow.

### 2) Upgrade My Lecture
Keep the technical source. ISCARB upgrades how it is taught through first-principles reasoning, hard trade-offs, evidence, uncertainty, accountability, Saudi contextualization, critical AI literacy, portfolio proof and a bounded assurance case.

### 3) Adopt ISCARB
The `/starter-kit` page explains the 90-minute contract, primary/supporting source hierarchy, 20-unit grammar, evidence policy, readiness discipline and a small faculty-pilot workflow.

## The 90-minute contract

- **Exactly 20 Units**
- **One complete live lecture**
- **Full PRIMARY (P1) major-topic coverage**
- **One engineering decision thread**
- **No major technical topic first taught after Unit 15**
- **Presenter-first visual output + detailed faculty assets**

## Design lineage

- **CIMT:** Concept → Implementation → Measurement → Trend
- **IMAM:** Ifham → Maris → Atqan → Mayyiz
- **HIMMA:** CLOs → H-Stack → decisions → portfolio → evidence → rubric → assurance
- **ISCARB:** first principles, trade-offs, uncertainty, falsification, constraint mutation, AI audit, accountability and proof of capability

The current presenter philosophy intentionally restores the strongest **CIMT visual DNA**: white academic canvas, strong editorial titles, one dominant visual idea per slide and low visual noise. ISCARB retains the later reasoning, evidence, cultural, readiness and assurance layers.

## Provenance model

ISCARB separates every lecture into three channels:

1. **Weekly-source technical content** — only technical claims supported by the supplied lecture bundle.
2. **ISCARB pedagogy / decision work** — CLOs, H-Stack, prediction, Socratic challenge, evidence policy, rubric and assurance structure.
3. **Contextual enrichment** — Saudi context, contemporary practice, wellbeing, AI literacy, readiness or other external extensions not present in P1.

Supporting sources may clarify, verify, contextualize or deepen P1; they may not silently replace P1 or expand mandatory scope.

## ISCARB Verified

`ISCARB VERIFIED` is not a decorative badge. It is shown only when the complete release path passes:

- Source Fidelity
- Engineering Rigor
- Cumulative Fidelity
- Readiness Evidence
- Provenance Separation

A `BLOCKED` artifact remains downloadable for faculty review, but it must not be represented as verified.

## Current readiness scope

The public implementation currently carries the **ETEC Academic Standards for Information Technology Programs 2025 v2.0** readiness pack. Additional discipline packs should be added only after the relevant standard is validated and encoded; the system should not imply readiness coverage for unsupported disciplines.

## Outputs

- **Presenter Preview** — in-browser 20-unit visual teaching experience
- **Presenter Deck (PPTX)** — presenter-first lecture slides
- **Detailed Deck (PDF)** — source-grounded reading version
- **Instructor Guide (DOCX)** — teaching notes, evidence expectations and rubric
- **Blueprint + Readiness (JSON)** — auditable machine-readable artifact

## Pipeline

`P1 + supporting sources → Source Lock → 90-min Full Coverage → 20-Unit Compiler → Deterministic Gate → Semantic Audit → Repair / BLOCK → Visual Grammar → Faculty Assets`

## Supported inputs

PDF, PPTX, DOCX, TXT, Markdown, and supported public lecture URLs.

## Deployment

The repository includes a root `render.yaml`. Render runs the service from `iscarb-studio/` and stores the Gemini API key as an environment variable.

Never commit a Gemini API key to GitHub.

## Faculty-pilot principle

**Discover → Try → Trust → Teach → Reuse**

Do not ask faculty to adopt a framework before it earns reuse. Start with one lecture, teach it once, inspect what changed, and continue only if the workflow creates real instructional value.
