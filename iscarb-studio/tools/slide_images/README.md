# ISCARB slide images — JSON → PNG/JPG

Turns a Blueprint JSON into shareable 16:9 slide images that carry the ISCARB
identity, at any resolution, with every character placed by code.

```bash
pip install playwright && playwright install chromium

python -m tools.slide_images.render blueprint.json --out images
python -m tools.slide_images.render blueprint.json --out images --format jpg --scale 3
python -m tools.slide_images.render blueprint.json --out images --units 1,11,19
```

`--scale` is a device pixel ratio, not an upscale: `--scale 2` renders the
1920×1080 stage at 3840×2160 with real subpixel type. Files land as
`unit_NN.png` / `unit_NN.jpg`.

If the environment ships a Chromium that Playwright's version pin does not
match (common in CI images), point at it explicitly:

```bash
ISCARB_CHROMIUM=/path/to/chrome python -m tools.slide_images.render ...
```

## Why no image model writes the slide

The words on these slides are the lecture's primary source. Asked to draw a
slide, a diffusion model returns plausible letter shapes — not the source's
sentences — and a slide that misquotes its own P1 anchor is worse than no
slide at all. So the split is strict:

- **Code owns every glyph.** Title, question, source excerpts, task, anchor and
  page number are laid out by a browser from the JSON, verbatim.
- **Generated art, if ever used, owns only the ground.** A background or a
  thematic icon may come from an image model, and the prompt for one must
  forbid text outright ("do NOT include any letters, words, or readable text")
  and leave the text area empty. Nothing generated is allowed to carry meaning
  a reader must read.

Because the browser lays out the exact string the JSON holds, the same input
always produces the same image — which is what makes these safe to publish.

## The three quality controls

**Fixed stage.** The viewport is pinned to 1920×1080 (`identity.Geometry`), so
components never reflow between slides and a deck of images stays uniform.
Resolution comes from the device pixel ratio, never from resizing a raster.

**Local fonts.** Noto Sans and Noto Naskh Arabic are resolved from the system,
with no network fetch at render time, and `document.fonts.ready` is awaited
before anything is measured — otherwise shrink-to-fit measures a fallback face
and picks the wrong size for the real one.

**Dynamic font resizing.** Padding is fixed and the type gives way: the page
measures its own overflow and steps the body size down (labels tracking at
70%) until the card fits, with a floor of 17px. A slide that still overflows at
the floor is reported on stderr rather than shipped clipped, because a silently
truncated last line loses a source fact.

## Direction and localisation

Direction is decided by the unit's own words, not by configuration: any Arabic
in the content flips the slide to RTL, switches to the Naskh face, and
translates the section furniture (`المصدر الأساسي`, `تطبيق`, `المطلوب منك`).
Numbers and the `ISCARB` / `P1` identifiers stay LTR inside bidi isolates so a
page number never reorders into `1 / 05`.

## Changing the identity

`identity.py` holds the whole visual system — palette, type scale, geometry.
Nothing downstream hard-codes a colour, so re-skinning every rendered image is
a single edit there.

Note: the values shipped here match the approved v4.8 presenter surface (dark
ground, bronze display type, magenta labels). A light navy/gold treatment is a
different brand, not a variant of this one — switch `PALETTE` deliberately.

## Deployment note

Chromium is ~300 MB. This tool deliberately lives under `tools/` rather than in
`app/`, so the Render web image does not carry a browser it never uses. Run it
in CI, locally, or from a worker — not from the request path of the free-tier
web service.
