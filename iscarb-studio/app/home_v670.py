from __future__ import annotations

"""ISCARB production home surface + generic IT intake + single-language UI."""
from pathlib import Path
from fastapi.responses import HTMLResponse
from .start_v670_prod import app
from .patch_v671 import apply_v671_patch
from .patch_v680 import apply_v680_patch
from .patch_v690 import apply_v690_patch
from .patch_v691 import apply_v691_patch
from .patch_v692 import apply_v692_patch
from .patch_v693 import apply_v693_patch
from .patch_v694 import apply_v694_patch
from .patch_v700_generic import apply_generic_it_patch
from .patch_v702_strict20 import apply_v702_patch
from .patch_v703_web_source import apply_v703_patch
from .patch_v704_source_detail import apply_v704_patch
from .patch_v705_web_visuals import apply_v705_patch
from .patch_v711_hero import apply_v711_hero_patch

apply_v671_patch(app)
apply_v680_patch(app)
apply_v690_patch(app)
apply_v691_patch(app)
apply_v692_patch(app)
apply_v693_patch(app)
apply_v694_patch(app)
apply_generic_it_patch(app)
apply_v702_patch(app)
apply_v703_patch(app)
apply_v704_patch(app)
apply_v705_patch(app)
apply_v711_hero_patch(app)
PUBLIC_VERSION = "6.9.4"
UI_RELEASE = "7.1.1"
APPROVED_HERO = "hero_v671.svg"
APPROVED_HERO_BLOB = "8882ed948a0fae492d7bdb906c4237d5133d9bc3"

app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/"]

_V670_STYLE = r"""
<style id="iscarb-v711-home-patch">
:root{--iscarb-bg:#05070D;--iscarb-magenta:#FF258C;--iscarb-cyan:#2CDCFF;--iscarb-gold:#DCB56B;--iscarb-text:#F5F5F8;--iscarb-muted:#B7BDC8}
.hero.shell{align-items:center;gap:clamp(28px,4vw,72px)}
.heroArt{position:relative!important;min-height:350px!important;border-radius:28px;overflow:hidden;background-color:#05070D!important;background-image:url('/static/hero_v671.svg?v=7.1.1')!important;background-position:center center!important;background-size:cover!important;background-repeat:no-repeat!important;isolation:isolate}
.heroArt>svg{display:block!important;position:absolute!important;inset:0!important;width:100%!important;height:100%!important;z-index:0!important}
.heroArt>.heroPhoto{display:block!important;position:absolute!important;inset:0!important;width:100%!important;height:100%!important;object-fit:cover!important;object-position:center center!important;z-index:1!important}
.heroArt::before{content:"";position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient(90deg,rgba(5,7,13,.02),rgba(5,7,13,0) 55%,rgba(5,7,13,.01))}
.heroArt::after{content:"20 CORE UNITS  ·  SOURCE-LOCKED  ·  SOURCE FIGURES FIRST";position:absolute;right:16px;bottom:16px;z-index:3;padding:8px 12px;border:1px solid rgba(255,37,140,.55);border-radius:999px;background:rgba(5,7,13,.82);color:var(--iscarb-text);font-size:10px;font-weight:800;letter-spacing:.07em;backdrop-filter:blur(8px)}
html[data-lang="ar"] .heroArt::after{content:"٢٠ وحدة أساسية  ·  مقيدة بالمصدر  ·  صور المصدر أولاً";right:auto;left:16px;letter-spacing:0;font-family:"Segoe UI","Noto Naskh Arabic",Tahoma,sans-serif}
.heroArt>.floatCard{display:none!important}.version{color:var(--iscarb-cyan)!important;font-weight:800!important}.brand small{color:var(--iscarb-cyan)!important}.hero h1 em{color:var(--iscarb-magenta)!important}.heroSub{max-width:620px}#state{letter-spacing:.06em}#outputAssets a[aria-busy="true"]{opacity:.72;cursor:wait;text-decoration:none}
.languageToggle{min-width:76px!important;border:1px solid rgba(220,181,107,.32)!important;border-radius:999px!important;padding:7px 11px!important;color:var(--iscarb-gold)!important;background:rgba(220,181,107,.04)!important;font-weight:750!important}.languageToggle:hover{border-color:var(--iscarb-gold)!important;background:rgba(220,181,107,.09)!important}
html[data-lang="ar"] body{text-align:right}html[data-lang="ar"] .header nav,html[data-lang="ar"] .headerTools{direction:rtl}html[data-lang="ar"] input,html[data-lang="ar"] textarea,html[data-lang="ar"] select{text-align:right}
@media(max-width:900px){.heroArt{min-height:245px!important;background-position:center center!important;background-size:cover!important}.heroArt::after{right:10px;bottom:10px;font-size:8.5px}html[data-lang="ar"] .heroArt::after{right:auto;left:10px}}
</style>
"""


@app.get("/")
def faculty_studio_v670_home():
    body = (Path(__file__).with_name("static") / "index_v440.html").read_text(encoding="utf-8")
    body = body.replace('<html lang="en" dir="ltr" data-theme="dark">', '<html lang="en" dir="ltr" data-theme="dark" data-lang="en">', 1)
    body = body.replace("4.6 · Gate v15", "7.1.1 · IT-wide · Multi-source · Gate v15")
    body = body.replace("Saudi Academic Engineering", "Saudi Engineering Learning System")
    body = body.replace("studio_v460.css?v=4.6.6", "studio_v460.css?v=7.1.1")
    body = body.replace("site_v460.js?v=4.6.6", "site_v460.js?v=7.1.1")
    body = body.replace("studio_v440.js?v=4.6.6", "studio_v440.js?v=7.1.1")
    body = body.replace(
        '<div class="heroArt" aria-hidden="true">',
        '<div class="heroArt" aria-hidden="true"><img class="heroPhoto" src="/static/hero_v671.svg?v=7.1.1" alt="" loading="eager" decoding="sync" fetchpriority="high" onerror="this.remove()">',
        1,
    )
    body = body.replace(
        "</head>",
        _V670_STYLE
        + '\n<script src="/static/site_v671_fix.js?v=7.1.1" defer></script>'
        + '\n<script src="/static/site_v700_generic.js?v=it-scope-v3" defer></script>'
        + '\n<script src="/static/site_v701_i18n.js?v=single-language-v1" defer></script>'
        + '\n<script src="/static/site_v710_sources.js?v=clean-multisource-v1" defer></script>\n</head>',
        1,
    )
    return HTMLResponse(
        body,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-ISCARB-Version": PUBLIC_VERSION,
            "X-ISCARB-UI": UI_RELEASE,
            "X-ISCARB-Hero-Asset": APPROVED_HERO,
            "X-ISCARB-Hero-Blob": APPROVED_HERO_BLOB,
            "X-ISCARB-Home": "v7.1.1-generic-it-clean-multisource-single-language-decoder-safe-camel-hero-source-figures-first-gate-v15",
        },
    )