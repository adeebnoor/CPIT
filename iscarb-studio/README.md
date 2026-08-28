# ISCARB Lecture Studio v1

A source-grounded weekly engineering lecture compiler that transforms one uploaded lecture into an exact **20-unit ISCARB blueprint**, audits it, repairs failed gates, and exports PPTX/PDF/DOCX/JSON.

## Design lineage

- **CIMT:** Concept → Implementation → Measurement → Trend
- **IMAM:** Ifham → Maris → Atqan → Mayyiz
- **HIMMA:** CLOs → H-Stack → decisions → portfolio → evidence → rubric → assurance
- **ISCARB:** problem framing, first principles, trade-offs, uncertainty, falsification, critique, constraint mutation, AI audit, accountability, proof of capability

## One-click deployment

The repository includes a root `render.yaml` Blueprint. Deploy it through Render, then enter only your `GEMINI_API_KEY` when prompted. No source-code editing is required.

The default production model is `gemini-3.7-flash`.

## Pipeline

`Weekly source → Source Profile → 20-Unit Generator → Deterministic Gate → Semantic Auditor → Repair Loop → RELEASE/BLOCKED → Export`

## Supported inputs

PDF, PPTX, DOCX, TXT, Markdown.

## Release gate

The service checks exact 20-unit structure, exactly five CLOs, IFHAM/MARIS/ATQAN/MAYYIZ sequencing, CIMT coverage, inherited IDR requirements, elite EER requirements, source anchors, Saudi contextual consequence, practitioner wellbeing, AI literacy, constraint mutation, falsification, authentic portfolio evidence, rubric quality, and the closing assurance case.

## Security

Never commit a Gemini API key to GitHub. The hosting platform stores it as an environment variable.
