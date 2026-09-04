from __future__ import annotations

"""ISCARB v6.9.3 production home surface."""
from pathlib import Path
from fastapi.responses import HTMLResponse
from .start_v670_prod import app
from .patch_v671 import apply_v671_patch
from .patch_v680 import apply_v680_patch
from .patch_v690 import apply_v690_patch
from .patch_v691 import apply_v691_patch
from .patch_v692 import apply_v692_patch
from .patch_v693 import apply_v693_patch

apply_v671_patch(app)
apply_v680_patch(app)
apply_v690_patch(app)
apply_v691_patch(app)
apply_v692_patch(app)
apply_v693_patch(app)
PUBLIC_VERSION = "6.9.3"

app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/"]

_V670_STYLE = r"""
<style id="iscarb-v693-home-patch">
:root{--iscarb-bg:#05070D;--iscarb-magenta:#FF258C;--iscarb-cyan:#2CDCFF;--iscarb-gold:#DCB56B;--iscarb-text:#F5F5F8;--iscarb-muted:#B7BDC8}
.hero.shell{align-items:center;gap:clamp(28px,4vw,72px)}
.heroArt{position:relative!important;min-height:350px!important;border-radius:28px;overflow:hidden;background-color:#05070D!important;background-image:url('/static/hero_v672.webp?v=6.9.3')!important;background-position:center center!important;background-size:cover!important;background-repeat:no-repeat!important;isolation:isolate}
.heroArt::before{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(90deg,rgba(5,7,13,.02),rgba(5,7,13,0) 55%,rgba(5,7,13,.01))}
.heroArt::after{content:"20 CORE UNITS  ·  SOURCE-LOCKED  ·  NO PUBLIC FALLBACK";position:absolute;right:16px;bottom:16px;z-index:3;padding:8px 12px;border:1px solid rgba(255,37,140,.55);border-radius:999px;background:rgba(5,7,13,.82);color:var(--iscarb-text);font-size:10px;font-weight:800;letter-spacing:.07em;backdrop-filter:blur(8px)}
.heroArt>svg,.heroArt>.floatCard{display:none!important}.version{color:var(--iscarb-cyan)!important;font-weight:800!important}.brand small{color:var(--iscarb-cyan)!important}.hero h1 em{color:var(--iscarb-magenta)!important}.heroSub{max-width:620px}#state{letter-spacing:.06em}#outputAssets a[aria-busy="true"]{opacity:.72;cursor:wait;text-decoration:none}
@media(max-width:900px){.heroArt{min-height:245px!important;background-position:center center!important;background-size:cover!important}.heroArt::after{right:10px;bottom:10px;font-size:8.5px}}
</style>
"""


@app.get("/")
def faculty_studio_v670_home():
    body = (Path(__file__).with_name("static") / "index_v440.html").read_text(encoding="utf-8")
    body = body.replace("4.6 · Gate v15", "6.9.3 · Source-Locked")
    body = body.replace("Saudi Academic Engineering", "Saudi Engineering Learning System")
    body = body.replace("studio_v460.css?v=4.6.6", "studio_v460.css?v=6.9.3")
    body = body.replace("site_v460.js?v=4.6.6", "site_v460.js?v=6.9.3")
    body = body.replace("studio_v440.js?v=4.6.6", "studio_v440.js?v=6.9.3")
    body = body.replace(
        "</head>",
        _V670_STYLE + '\n<script src="/static/site_v671_fix.js?v=6.9.3" defer></script>\n</head>',
        1,
    )
    return HTMLResponse(
        body,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-ISCARB-Version": PUBLIC_VERSION,
            "X-ISCARB-Home": "v6.9.3-source-native-textgold-approved-hero",
        },
    )
