from __future__ import annotations

"""Clean v7.2 faculty-facing home surface.

The historic CPIT source library remains in repository history for reproducible
research, but it is not part of the production product. This route serves an
IT-wide surface with no fake sign-in, no external lecture-library links and no
legacy Software-Engineering-only cards.
"""

import re
from pathlib import Path

from fastapi.responses import HTMLResponse, Response


_CLEAN_STYLE = r"""
<style id="iscarb-v720-home">
:root{--iscarb-bg:#05070D;--iscarb-magenta:#FF258C;--iscarb-cyan:#2CDCFF;--iscarb-gold:#DCB56B;--iscarb-text:#F5F5F8;--iscarb-muted:#B7BDC8}
.hero.shell{align-items:center;gap:clamp(28px,4vw,72px)}
.heroArt{position:relative!important;aspect-ratio:16/9!important;min-height:0!important;border-radius:28px;overflow:hidden;isolation:isolate;display:block!important;background-color:#05070D!important;background-image:url('/static/hero_user_web.jpg?v=7.2.0')!important;background-size:cover!important;background-position:center center!important;background-repeat:no-repeat!important}
.heroArt>svg,.heroArt>.heroPhoto,.heroArt>.floatCard{display:none!important}
.heroArt::before{content:"";position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient(90deg,rgba(5,7,13,.015),rgba(5,7,13,0) 50%,rgba(5,7,13,.015))}
.heroArt::after{content:"20 CORE UNITS  ·  SOURCE-LOCKED  ·  SOURCE FIGURES FIRST";position:absolute;right:16px;bottom:16px;z-index:3;padding:8px 12px;border:1px solid rgba(255,37,140,.55);border-radius:999px;background:rgba(5,7,13,.82);color:var(--iscarb-text);font-size:10px;font-weight:800;letter-spacing:.07em;backdrop-filter:blur(8px)}
html[data-lang="ar"] .heroArt::after{content:"٢٠ وحدة أساسية  ·  مقيدة بالمصدر  ·  صور المصدر أولاً";right:auto;left:16px;letter-spacing:0;font-family:"Segoe UI","Noto Naskh Arabic",Tahoma,sans-serif}
.version{color:var(--iscarb-cyan)!important;font-weight:800!important}.brand small{color:var(--iscarb-cyan)!important}.hero h1 em{color:var(--iscarb-magenta)!important}.heroSub{max-width:650px}#state{letter-spacing:.06em}
.languageToggle{min-width:76px!important;border:1px solid rgba(220,181,107,.32)!important;border-radius:999px!important;padding:7px 11px!important;color:var(--iscarb-gold)!important;background:rgba(220,181,107,.04)!important;font-weight:750!important}.languageToggle:hover{border-color:var(--iscarb-gold)!important;background:rgba(220,181,107,.09)!important}
html[data-lang="ar"] body{text-align:right}html[data-lang="ar"] .header nav,html[data-lang="ar"] .headerTools{direction:rtl}html[data-lang="ar"] input,html[data-lang="ar"] textarea,html[data-lang="ar"] select{text-align:right}
@media(max-width:900px){.heroArt{aspect-ratio:16/9!important;min-height:0!important}.heroArt::after{right:10px;bottom:10px;font-size:8.5px}html[data-lang="ar"] .heroArt::after{right:auto;left:10px}}
</style>
"""

_SCOPE_SECTION = r"""
<section class="section shell" id="sources">
  <div class="sectionHead">
    <div>
      <h2><span class="ornament">❦</span><span data-lang="en">One engine for IT &amp; computing</span><span lang="ar" dir="rtl" data-lang="ar">محرك واحد لكل تخصصات تقنية المعلومات والحوسبة</span></h2>
      <p class="itScopeIntro"><span data-lang="en">Upload the lecture you actually teach. The primary source defines the concepts, mechanisms, examples, formulas and technical vocabulary.</span><span lang="ar" dir="rtl" data-lang="ar">ارفع المحاضرة التي تدرّسها فعليًا؛ المصدر الأساسي هو الذي يحدد المفاهيم والآليات والأمثلة والمعادلات والمصطلحات التقنية.</span></p>
    </div>
    <span class="itAutoBadge">SOURCE-ADAPTIVE</span>
  </div>
  <div class="itScopeGrid" aria-label="Supported IT domains">
    <div class="itScopeChip">Programming &amp; software development</div>
    <div class="itScopeChip">Databases &amp; data management</div>
    <div class="itScopeChip">Networks &amp; infrastructure</div>
    <div class="itScopeChip">Cybersecurity</div>
    <div class="itScopeChip">AI &amp; data science</div>
    <div class="itScopeChip">Cloud &amp; distributed systems</div>
    <div class="itScopeChip">Human-computer interaction</div>
    <div class="itScopeChip">Systems &amp; architecture</div>
    <div class="itScopeChip">IT governance &amp; service management</div>
    <div class="itScopeChip">Any other IT / computing lecture</div>
  </div>
  <div class="genericFlow">
    <div><b>1 · Upload</b><span>One primary lecture plus optional supporting sources.</span></div>
    <div><b>2 · Transform</b><span>Twenty fixed learning jobs; technical content remains source-locked.</span></div>
    <div><b>3 · Inspect &amp; download</b><span>Presenter, faculty/student packs, blueprint and complete ZIP package.</span></div>
  </div>
</section>
"""


def _clean_studio_source(static_root: Path) -> str:
    source = (static_root / "studio_v440.js").read_text(encoding="utf-8")
    # Remove the old hard-coded CPIT-455 library dataset itself.
    source = re.sub(r"^const SOURCE_NAMES\s*=.*?;\s*\n", "", source, count=1, flags=re.M)
    start = source.find("SOURCE_NAMES.forEach((title, i) => {")
    if start >= 0:
        end_marker = "\n});\n$('primaryFile').addEventListener"
        end = source.find(end_marker, start)
        if end < 0:
            raise RuntimeError("Legacy source-library block changed unexpectedly")
        source = source[:start] + "$('primaryFile').addEventListener" + source[end + len(end_marker):]
    if "adeebnoor.github.io/CPIT/lectures/cimt" in source:
        raise RuntimeError("Legacy lecture-library links survived the v7.2 client cleanup")
    return source


def apply_v720_home_clean_patch(app, static_root: Path, hero_sha: str, original_hero_sha: str) -> None:
    # Validate transformed JS at startup, not after a faculty member opens page.
    _clean_studio_source(static_root)

    app.router.routes[:] = [
        r for r in app.router.routes
        if getattr(r, "path", None) not in {"/", "/ui/studio_v720_clean.js"}
    ]

    @app.get("/ui/studio_v720_clean.js", include_in_schema=False)
    def studio_v720_clean_js():
        return Response(
            _clean_studio_source(static_root),
            media_type="application/javascript",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
        )

    @app.get("/")
    def clean_home():
        body = (static_root / "index_v440.html").read_text(encoding="utf-8")
        body = body.replace('<html lang="en" dir="ltr" data-theme="dark">', '<html lang="en" dir="ltr" data-theme="dark" data-lang="en">', 1)
        body = body.replace("<title>ISCARB Faculty Studio · Saudi Academic Engineering</title>", "<title>ISCARB IT Lecture Studio · Source-grounded lecture transformation</title>")
        body = body.replace("Saudi Academic Engineering", "IT Lecture Transformation Studio")
        body = body.replace("4.6 · Gate v15", "7.2.0 · CLEAN · IT-WIDE")
        body = body.replace("studio_v460.css?v=4.6.6", "studio_v460.css?v=7.2.0")
        body = body.replace("site_v460.js?v=4.6.6", "site_v460.js?v=7.2.0")
        body = body.replace('<script src="/static/studio_v440.js?v=4.6.6" defer></script>', '<script src="/ui/studio_v720_clean.js?v=7.2.0" defer></script>')

        # Remove the fake authentication affordance. /starter-kit remains the
        # explicit Guides route; it is not misrepresented as an account action.
        body = re.sub(r'\s*<a class="signIn" href="/starter-kit">.*?</a>', "", body, count=1, flags=re.S)
        body = body.replace('<a href="#sources">Source Library</a>', '<a href="#sources">IT Scope</a>')
        body = body.replace('<a href="#upgrade">Upgrade My Lecture</a>', '<a href="#upgrade">Build Lecture</a>')
        body = body.replace('Upgrade My Lecture', 'Build My Lecture')
        body = body.replace('Explore Library', 'Supported IT Areas')

        # Replace the historic hard-coded lecture library before any JavaScript
        # executes. This guarantees there are no stale external lecture links in
        # the served DOM, even during first paint.
        pattern = r'<section class="section shell" id="sources">.*?</section>\s*(?=<section class="section shell" id="upgrade">)'
        body, count = re.subn(pattern, _SCOPE_SECTION + "\n", body, count=1, flags=re.S)
        if count != 1:
            raise RuntimeError("Could not replace legacy source library in clean home")

        body = body.replace(
            "Your content is secure and used only for academic enhancement.",
            "Use only material you are authorized to process. Do not upload confidential or restricted content.",
        )
        body = body.replace(
            "Five defendable outputs—aligned, structured, and ready to teach.",
            "A complete source-traceable teaching package—structured for faculty review and classroom use.",
        )

        body = body.replace(
            "</head>",
            '<link rel="preload" as="image" href="/static/hero_user_web.jpg?v=7.2.0" type="image/jpeg" fetchpriority="high">\n'
            + _CLEAN_STYLE
            + '\n<script src="/static/site_v671_fix.js?v=7.2.0" defer></script>'
            + '\n<script src="/static/site_v700_generic.js?v=it-scope-v4" defer></script>'
            + '\n<script src="/ui/site_v701_i18n_fixed.js?v=single-language-v3" defer></script>'
            + '\n<script src="/static/site_v710_sources.js?v=clean-multisource-v2" defer></script>\n</head>',
            1,
        )

        # Production surface must not silently reacquire retired links/copy.
        forbidden = (
            "adeebnoor.github.io/CPIT/cimt.html",
            "CPIT455-class",
            'class="signIn"',
            "Original Source Library",
            "Your content is secure and used only for academic enhancement.",
        )
        leaked = [x for x in forbidden if x in body]
        if leaked:
            raise RuntimeError("Clean home contains retired production content: " + ", ".join(leaked))

        return HTMLResponse(
            body,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-ISCARB-Version": "7.2.0",
                "X-ISCARB-UI": "7.2.0",
                "X-ISCARB-Hero-SHA256": hero_sha,
                "X-ISCARB-Hero-Original-SHA256": original_hero_sha,
                "X-ISCARB-Home": "v7.2-clean-it-wide-no-legacy-library-links-source-figures-first",
            },
        )
