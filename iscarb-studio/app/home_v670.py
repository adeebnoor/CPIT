from __future__ import annotations

"""ISCARB production home surface + generic IT intake + single-language UI."""
import hashlib
from pathlib import Path
from fastapi.responses import HTMLResponse, Response
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
from .patch_v716_contract import apply_v716_contract_patch
from .patch_v717_source_intelligence import apply_v717_source_intelligence_patch
from .patch_v718_opening_stake import apply_v718_opening_stake_patch
from .patch_v720_clean_release import apply_v720_clean_release_patch

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
apply_v716_contract_patch(app)
apply_v717_source_intelligence_patch(app)
apply_v718_opening_stake_patch(app)
apply_v720_clean_release_patch(app)

PUBLIC_VERSION = "7.2.0"
UI_RELEASE = "7.2.0"
ORIGINAL_HERO = "hero_user_original.png"
ORIGINAL_HERO_SHA256 = "8967fa14fe910e5831531a6b74c64bcd650c965ad691697dd2d705d450b6e50d"
WEB_HERO = "hero_user_web.jpg"
WEB_HERO_SHA256 = "fcad23fe86a60e6ca881eb46829d5f7dbe894d9bf57a17c0453952edf5ec7c12"

_STATIC_ROOT = Path(__file__).with_name("static")
_original_path = _STATIC_ROOT / ORIGINAL_HERO
_web_path = _STATIC_ROOT / WEB_HERO
if not _original_path.exists():
    raise RuntimeError("Exact user-supplied ISCARB hero PNG is missing")
_original_bytes = _original_path.read_bytes()
if len(_original_bytes) != 2_315_610 or not _original_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
    raise RuntimeError("Exact user-supplied ISCARB hero PNG is invalid")
if hashlib.sha256(_original_bytes).hexdigest() != ORIGINAL_HERO_SHA256:
    raise RuntimeError("Exact user-supplied ISCARB hero PNG checksum mismatch")
if not _web_path.exists():
    raise RuntimeError("Optimized ISCARB web hero is missing")
_web_bytes = _web_path.read_bytes()
if len(_web_bytes) != 269_820 or not (_web_bytes.startswith(b"\xff\xd8") and _web_bytes.endswith(b"\xff\xd9")):
    raise RuntimeError("Optimized ISCARB web hero is invalid")
if hashlib.sha256(_web_bytes).hexdigest() != WEB_HERO_SHA256:
    raise RuntimeError("Optimized ISCARB web hero checksum mismatch")

# Chromium can starve its event loop if a MutationObserver watches placeholder
# attributes while the localization pass unconditionally writes the same value
# back to those attributes. Serve the existing localization source with one
# idempotence guard so we preserve the complete bilingual dictionary without a
# second divergent copy of it.
_I18N_SOURCE = _STATIC_ROOT / "site_v701_i18n.js"
_I18N_BAD = """      const en=el.dataset.i18nPlaceholderEn;
      el.setAttribute('placeholder',lang==='ar' && PLACEHOLDER_AR[en] ? PLACEHOLDER_AR[en] : en);"""
_I18N_FIXED = """      const en=el.dataset.i18nPlaceholderEn;
      const target=lang==='ar' && PLACEHOLDER_AR[en] ? PLACEHOLDER_AR[en] : en;
      if(el.getAttribute('placeholder')!==target) el.setAttribute('placeholder',target);"""


def _fixed_i18n_source() -> str:
    source = _I18N_SOURCE.read_text(encoding="utf-8")
    if _I18N_FIXED in source:
        return source
    if _I18N_BAD not in source:
        raise RuntimeError("ISCARB localization guard target changed unexpectedly")
    return source.replace(_I18N_BAD, _I18N_FIXED, 1)


# Validate the hot-path transformation at process startup rather than failing
# only when a browser requests the asset.
_fixed_i18n_source()


@app.get("/ui/site_v701_i18n_fixed.js", include_in_schema=False)
def site_v701_i18n_fixed():
    return Response(
        _fixed_i18n_source(),
        media_type="application/javascript",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/"]

_V670_STYLE = r"""
<style id="iscarb-v716-home-patch">
:root{--iscarb-bg:#05070D;--iscarb-magenta:#FF258C;--iscarb-cyan:#2CDCFF;--iscarb-gold:#DCB56B;--iscarb-text:#F5F5F8;--iscarb-muted:#B7BDC8}
.hero.shell{align-items:center;gap:clamp(28px,4vw,72px)}
.heroArt{position:relative!important;aspect-ratio:16/9!important;min-height:0!important;border-radius:28px;overflow:hidden;isolation:isolate;display:block!important;background-color:#05070D!important;background-image:url('/static/hero_user_web.jpg?v=7.2.0')!important;background-size:cover!important;background-position:center center!important;background-repeat:no-repeat!important}
.heroArt>svg{display:none!important}
.heroArt>.heroPhoto{display:none!important}
.heroArt::before{content:"";position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient(90deg,rgba(5,7,13,.015),rgba(5,7,13,0) 50%,rgba(5,7,13,.015))}
.heroArt::after{content:"20 CORE UNITS  ·  SOURCE-LOCKED  ·  SOURCE FIGURES FIRST";position:absolute;right:16px;bottom:16px;z-index:3;padding:8px 12px;border:1px solid rgba(255,37,140,.55);border-radius:999px;background:rgba(5,7,13,.82);color:var(--iscarb-text);font-size:10px;font-weight:800;letter-spacing:.07em;backdrop-filter:blur(8px)}
html[data-lang="ar"] .heroArt::after{content:"٢٠ وحدة أساسية  ·  مقيدة بالمصدر  ·  صور المصدر أولاً";right:auto;left:16px;letter-spacing:0;font-family:"Segoe UI","Noto Naskh Arabic",Tahoma,sans-serif}
.heroArt>.floatCard{display:none!important}.version{color:var(--iscarb-cyan)!important;font-weight:800!important}.brand small{color:var(--iscarb-cyan)!important}.hero h1 em{color:var(--iscarb-magenta)!important}.heroSub{max-width:620px}#state{letter-spacing:.06em}#outputAssets a[aria-busy="true"]{opacity:.72;cursor:wait;text-decoration:none}
.languageToggle{min-width:76px!important;border:1px solid rgba(220,181,107,.32)!important;border-radius:999px!important;padding:7px 11px!important;color:var(--iscarb-gold)!important;background:rgba(220,181,107,.04)!important;font-weight:750!important}.languageToggle:hover{border-color:var(--iscarb-gold)!important;background:rgba(220,181,107,.09)!important}
html[data-lang="ar"] body{text-align:right}html[data-lang="ar"] .header nav,html[data-lang="ar"] .headerTools{direction:rtl}html[data-lang="ar"] input,html[data-lang="ar"] textarea,html[data-lang="ar"] select{text-align:right}
@media(max-width:900px){.heroArt{aspect-ratio:16/9!important;min-height:0!important}.heroArt::after{right:10px;bottom:10px;font-size:8.5px}html[data-lang="ar"] .heroArt::after{right:auto;left:10px}}
</style>
"""


@app.get("/")
def faculty_studio_v670_home():
    body = (Path(__file__).with_name("static") / "index_v440.html").read_text(encoding="utf-8")
    body = body.replace('<html lang="en" dir="ltr" data-theme="dark">', '<html lang="en" dir="ltr" data-theme="dark" data-lang="en">', 1)
    body = body.replace("4.6 · Gate v15", "7.2.0 · IT-wide · Multi-source · Gate v15")
    body = body.replace("Saudi Academic Engineering", "Saudi Engineering Learning System")
    body = body.replace("studio_v460.css?v=4.6.6", "studio_v460.css?v=7.2.0")
    body = body.replace("site_v460.js?v=4.6.6", "site_v460.js?v=7.2.0")
    body = body.replace("studio_v440.js?v=4.6.6", "studio_v440.js?v=7.2.0")
    body = body.replace(
        "</head>",
        '<link rel="preload" as="image" href="/static/hero_user_web.jpg?v=7.2.0" type="image/jpeg" fetchpriority="high">\n'
        + _V670_STYLE
        + '\n<script src="/static/site_v671_fix.js?v=7.2.0" defer></script>'
        + '\n<script src="/static/site_v700_generic.js?v=it-scope-v4" defer></script>'
        + '\n<script src="/ui/site_v701_i18n_fixed.js?v=single-language-v3" defer></script>'
        + '\n<script src="/static/site_v710_sources.js?v=clean-multisource-v2" defer></script>\n</head>',
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
            "X-ISCARB-Hero-Asset": WEB_HERO,
            "X-ISCARB-Hero-SHA256": WEB_HERO_SHA256,
            "X-ISCARB-Hero-Original-SHA256": ORIGINAL_HERO_SHA256,
            "X-ISCARB-Home": "v7.2-clean-it-wide-source-figures-first",
        },
    )


# Register the final production home after the legacy-compatible route above.
# It removes that route and serves the clean IT-wide surface plus a transformed
# client bundle with the retired hard-coded CPIT source links physically absent.
from .patch_v720_home_clean import apply_v720_home_clean_patch
apply_v720_home_clean_patch(app, _STATIC_ROOT, WEB_HERO_SHA256, ORIGINAL_HERO_SHA256)
