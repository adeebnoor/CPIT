# 4.6.0 — free-first authoring workspace

- The default API and web flow use `source-only`: no model client is created.
- A completed source-backed draft can export an authoring prompt containing the
  20-unit contract, source profile, extracted source text, readiness context and
  Blueprint schema. Attach the original documents in the chosen authoring tool
  so figures are not reduced to extracted text.
- Importing an edited Blueprint creates a new job, preserves the locked source
  profile and copies original source files. It runs the active local gates;
  it never imports an audit or claims semantic approval. No API calls occur.
- Optional `free` AI mode uses only Gemini 3.5 Flash-Lite, skips the redundant
  AI source-profiling call and permits at most one repair round. Provider quota
  rejection stops the job without model fan-out. Source-upload quota failures
  are not retried by subsequent stages of the same job.
- The optional API route requires explicit confirmation that the configured
  project is on the unpaid Free Tier. This is a user attestation, not a billing
  check: the Gemini API does not give this application authority to inspect or
  change billing. A billed project can incur charges. No-API mode is the route
  that guarantees zero model API usage.
- No billing, paid plan, account, credential, or hosting change is made. Provider
  rate limits remain in force. A 429 alone does not identify which quota was hit.

Local deterministic checks and exports are not semantic release acceptance.
Manual/source-only drafts remain REVIEW DRAFTS, including when local gates pass.
Download files promptly: the existing free Render container is ephemeral.

Provider references (checked 2026-09-01):
- https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash-lite
- https://ai.google.dev/gemini-api/docs/rate-limits
