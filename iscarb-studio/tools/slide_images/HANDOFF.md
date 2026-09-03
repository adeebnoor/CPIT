# ISCARB Studio v4.8.0 — handoff to the team

/ تسليم للفريق

## What is in this package

| Folder | Contents |
|---|---|
| `repo.bundle` | The whole `adeebnoor/CPIT` history, with six commits on `main` ahead of origin. `git clone repo.bundle iscarb` gives you the working tree; from an existing clone, `git pull /path/to/repo.bundle main`. |
| `slides_4k/` | The 20 rendered lecture slides, 3840×2160 PNG. |
| `figures/` | The three figure regions cropped out of the source PDF. |
| `presenter/` | Presenter PDF and PPTX regenerated from the same blueprint. |
| `blueprint.json` | The 20-unit blueprint everything above was generated from. |
| `verify_report.txt` | The grammar check, run against the rendered slides. |

## The two things that are still blocked

Neither is a code problem, and neither can be resolved from the session that
produced this package.

**1. Nothing has been pushed.** The six commits are local only. The session
was refused write access to `adeebnoor/CPIT`:

```
remote: access denied by the git proxy: adeebnoor/CPIT is not in this
session's authorized repository set
```

Someone with push rights clones or pulls `repo.bundle` and pushes `main`:

```bash
git clone repo.bundle iscarb && cd iscarb
git remote set-url origin https://github.com/adeebnoor/CPIT.git
git push origin main
```

**2. The live site was never reached.** `iscarb-lecture-studio.onrender.com`
is blocked by the session's egress policy, and no Render API key was
available. So every acceptance test that needs the deployed site — the visual
check on the homepage, generating a lecture from the live app, confirming
`/api/health` returns 4.8.0 — **has not been done**. Do not treat this package
as evidence that it has.

What *is* verified is that `/api/health` returns `4.8.0` and
`faculty-studio-v4.8.0-cimt-visual-output` when the app is booted locally,
and that the `X-ISCARB-Version` header agrees with it.

## What changed

**Release.** `app/start_v480.py` layers the 4.8.0 identity on v4.7.0 and
`run.py` boots it, so the version `/api/health` reports cannot drift from the
module Render loads. `render.yaml` still starts from `iscarb-studio` and its
stale `ISCARB_RELEASE_VERSION` (4.4.0) now matches the release.

**Source de-hyphenation.** A justified book page hyphenates across the line
break, and the trailing hyphen was being stripped as bullet furniture, so
slides carried `security engi neering` and `an opera tional environment`.
Fixed at extraction, before cleaning.

**Unit 19's rubric.** Six criteria × four levels were printing the same two
sentences in all 24 cells — a table that could not separate a learner who
traced a mechanism from one who recited it, while the gate reported PASS. Each
cell now names the observable act that earns that level.

**`tools/slide_images/`** turns blueprint JSON into shareable slide images.
Every character is laid out by a headless browser from the JSON, verbatim. No
image model writes slide text: asked to draw a slide it returns plausible
letterforms rather than the source's sentences, and a slide that misquotes its
own P1 anchor is worse than no slide.

## How to regenerate everything

```bash
cd iscarb-studio
pip install -r requirements.txt playwright && playwright install chromium

# 1. crop real figures out of the source PDF (refuses text pages and covers)
python -m tools.slide_images.figures SOURCE.pdf blueprint.json \
       --out figures --map figures.json

# 2. render the deck — refuses to ship if any unit breaks the contract
python -m tools.slide_images.render blueprint.json --out slides \
       --figures figures.json --scale 2 --theme dark

# 3. the grammar check on its own
python -m tools.slide_images.verify blueprint.json --figures figures.json
```

`--theme light` gives the navy-on-off-white treatment; `--format jpg` and
`--scale 3` are available. If the environment's Chromium does not match
Playwright's version pin, set `ISCARB_CHROMIUM=/path/to/chrome`.

## Why there is a second checker

Gate v16 checks the **Blueprint**. `verify.py` checks the **rendered slide**.
They are not the same question, and the gap between them is where this
project's real defects were living: a unit can hold a perfect Decision/Unknown
pair in its JSON and project a title over a black rectangle, and the gate will
still say PASS.

Run against the rendered slides for the first time, the checker found **10 of
20 units breaking the contract while the gate reported zero failures** — the
opening slide blank, unit 3 showing one of five CLOs, unit 8 with no
alternatives, unit 13 with no stress variable. Every one traced back to the
renderer discarding labelled content, not to the pipeline. All 20 pass now,
and `render` refuses to write images while any unit fails.

The checker is not a replacement for reading the slides. It cannot tell you
whether a student understands unit 7 in five seconds. It can only tell you
that what the contract requires is actually on the canvas.

## Known-failing, deliberately

Four tests in `tests/test_v46_free_draft_gates.py` fail, and were left failing.

v4.8.0 raised the presenter density floor (12 → 24 payload words, and at least
three visible teaching items). Three archived lectures and the synthetic
chapter fixture fall below the new floor and are now blocked by the critical
release gate. The floor is right; the deterministic builder not filling it is
the real defect. Lowering it to make the suite green would weaken exactly the
guideline the release exists to enforce, and marking real lectures "by design"
failures would hide it. **This is a decision for the team, not a bug to
silence.**

The likely fix is to merge thin sections rather than emit thin units — keeping
20 units while redistributing content — which is a substantial change to the
allocation logic and should not be made blind.

## Still worth doing

- The figure crop occasionally catches a line or two of body text below the
  figure (visible on unit 15). The crop box comes from drawn regions; caption
  and following prose sit close enough to be included.
- Slide titles are the source's section numbers — `14.2.2 Design guidelines`
  appears on two units, `14.3 System survivability` on two more. A student sees
  the textbook's table of contents rather than an engineering idea. This lives
  in the blueprint, not the renderer.
- Unit tasks are still sometimes mechanical ("Redraw 14.2.1 from memory"),
  which measures recall rather than the judgement the unit is supposed to build.
