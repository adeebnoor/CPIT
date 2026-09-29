# STRESS unlock codes

Each assessed assignment asks students to commit Part A before they see new evidence (STRESS).
Until September 2026 the STRESS text was published as plain JSON, so anyone could read it before
committing. The payloads are now **sealed**: the site stores only ciphertext, and the assignment page
decrypts it in the browser after the student commits Part A and enters an unlock code.

- One code per chapter. The same code opens the current edition and the previous edition of that chapter.
- Codes are never stored in this repository. The instructor keeps them privately and releases each one in Blackboard.
- Sealing uses PBKDF2-SHA256 (250,000 iterations) to derive an AES-256-GCM key from the code; the chapter
  and edition are bound to the ciphertext, so a payload cannot be moved to another chapter.
- This protects the sequence against casual reading of the public files. It is still not a secure examination
  system: a student who has the code can share it. Release the code when sharing no longer matters.

## Releasing a code in Blackboard

Choose one of these, per chapter:

1. **After the Part A deadline.** Post the code in an announcement or item that becomes visible at the Part A
   due time. Everyone commits first, then everyone unlocks.
2. **Adaptive release.** Create a Blackboard item containing the code and set adaptive release so it appears
   only after the student has submitted their Part A PDF (or a short Part A attempt).

Suggested announcement (Arabic):

> رمز فتح الأدلة الجديدة (STRESS) للفصل NN: XXXX-XXXX-XXXX
> أدخلوا الرمز في صفحة الواجب بعد اعتماد الجزء A. لا يغيّر الرمز إجاباتكم المعتمدة، ولا يُعد إدخاله تسليمًا؛
> التسليم يتم برفع ملف PDF في البلاكبورد.

Students who committed Part A before the code is released see an unlock box instead of STRESS. Their Part A stays
committed in the browser; they return when the code is available. Students who opened STRESS before this change
keep it in their saved draft and do not need a code.

## Changing STRESS text or codes

Keep the plain text and the codes outside the repository, then run:

```bash
pip install cryptography
python3 tools/seal_stress.py --new-codes ~/private/stress-codes.json      # only when you want new codes
python3 tools/seal_stress.py --plain ~/private/stress-plain.json --codes ~/private/stress-codes.json
python3 tools/seal_stress.py --verify --plain ~/private/stress-plain.json --codes ~/private/stress-codes.json
```

`stress-plain.json` maps each payload path to its `label`, `text` and optional `principle`, for example
`{"lectures/iscarb/reveal/r16-mastery-v2.json": {"label": "STRESS · new evidence", "text": "…"}}`.
Changing a payload changes its hash; update `curriculum/iscarb-paper-fidelity.json` in the same reviewed commit.
`tools/audit_classroom.py` fails the build if any published payload is in plain text.
