# Quota repair completeness guarantee

If Gemini quota becomes unavailable after semantic generation has begun, ISCARB must never preserve an incomplete P1 chapter representation as the best available faculty draft.

The active compiler now checks the semantic Blueprint against every `major` P1 coverage checkpoint. If all major checkpoints are already present and first taught by Unit 15, the semantic Blueprint is preserved and remains `BLOCKED` until semantic assurance returns. If any major checkpoint is missing or first taught after Unit 15, the incomplete semantic Blueprint is replaced by the tested deterministic source-bounded draft. That draft remains exactly 20 units / 90 minutes, covers every major P1 checkpoint by Unit 15, leaves standardized readiness unverified, and cannot receive `RELEASE` without the semantic generation/audit path.

Regression coverage includes both branches: preserving an already-complete semantic draft and replacing an incomplete semantic draft after simulated `RESOURCE_EXHAUSTED` quota failure. The complete repository test suite must pass before merge.
