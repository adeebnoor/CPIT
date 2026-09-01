# Production deployment contract

The Render service deploys the `main` branch from the `iscarb-studio` root directory.

Pre-deploy GitHub checks must validate code and artifacts only. They must not wait for the live Render service to change version, because Render may be configured to deploy only after CI checks pass. Live production validation therefore runs as a separate post-deploy/manual workflow.

Release sequence:

1. Merge validated source changes to `main`.
2. Let repository CI complete successfully.
3. Render auto-deploys the changed `iscarb-studio` tree.
4. Run `ISCARB Production Validation` against multiple archived CIMT lectures.
5. A production release is accepted only when health reports v4.4.0 / Gate v15 and the live multi-lecture validation passes.

This separation prevents a circular dependency in which production checks wait for Render while Render waits for those same checks.

## Runtime safety limits

The service accepts uploads from anyone who can reach it, so the container
protects itself rather than trusting the caller:

| Limit | Default | Override |
|---|---|---|
| Maximum bytes per uploaded source | 25 MB | `ISCARB_MAX_UPLOAD_MB` |
| Retention for jobs, uploads, exports and the raster cache | 48 h | `ISCARB_RETENTION_HOURS` (`0` disables) |
| Concurrent compile workers | 2 | `ISCARB_WORKERS` |
| Supporting sources per lecture | 7 | — |

Uploads stream to disk against the ceiling and a rejected source is deleted, so
one oversized request cannot exhaust the disk shared by every faculty job.
Expired artifacts are pruned at startup and after each compile.

Every response carries `X-Content-Type-Options: nosniff`,
`Referrer-Policy: strict-origin-when-cross-origin`,
`Content-Security-Policy: frame-ancestors 'self'` and `X-Frame-Options: SAMEORIGIN`.

## Composition gotcha

`app/main.py` defines the pipeline routes but is **not** the served application.
`app/faculty_main.py` builds the served app and copies those route objects into
it. A copied route brings its handler only — middleware, exception handlers and
lifespan hooks do not travel with it. Register anything application-wide on the
served app in `faculty_main.py`, never on `engine.app`.

## Storage is ephemeral

The Render `free` plan provides no persistent disk and idles the container after
inactivity. Compiled outputs therefore survive the working session, not longer:
faculty must download their exports before leaving the Studio. Attach a Render
persistent disk if outputs need to outlive a restart.

## Source-visual resolution

Source pages rasterize at `PDF_RENDER_ZOOM = 2.6`, which puts roughly 163 DPI on
a 13.33in teaching canvas. The previous 1.45x delivered about 91 DPI, which is
why reused figures looked enlarged and soft. The render zoom is part of the
cache key, so raising it invalidates pages rasterized at the old setting instead
of serving them from cache.

A source figure earns the main canvas only if it is readable there. An asset
narrower than `MIN_PRESENTABLE_ASSET_WIDTH` (1100 px) is not eligible for USE and
the unit falls back to a redrawn diagram, which teaches more than an image
enlarged past its own resolution. This matters most for SlideShare sources,
where the image resolution is whatever the host CDN served. An asset whose size
cannot be measured keeps its source visual rather than being rejected on a guess.

Cost at this resolution, measured on an archived 22-page chapter: about 9 MB of
cached pages per deck, and a deck reusing ten source figures produces roughly a
3.9 MB HTML preview and a 2.8 MB PPTX.
