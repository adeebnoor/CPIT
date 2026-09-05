from __future__ import annotations

"""v7.3.4 — production homepage lock to the exact user-supplied hero.

This patch is intentionally presentation-only. It runs after the curriculum and
presenter patches, preserves the clean IT-wide homepage, and makes the original
PNG the final hero asset instead of the optimized derivative. No generated or
fallback hero artwork is allowed on the production root route.
"""

from fastapi.responses import HTMLResponse


_RELEASE = "7.3.4"
_ORIGINAL_HERO = f"/static/hero_user_original.png?v={_RELEASE}"

_HOME_STYLE = f"""
<style id="iscarb-v734-original-hero-lock">
.heroArt{{
  background-image:url('{_ORIGINAL_HERO}')!important;
  background-size:contain!important;
  background-position:center center!important;
  background-repeat:no-repeat!important;
  background-color:#05070D!important;
}}
.heroArt::after{{display:none!important;content:none!important}}
</style>
"""


def apply_v734_home_original_lock_patch(app) -> None:
    current = next(
        (r for r in reversed(app.router.routes)
         if getattr(r, "path", None) == "/" and "GET" in (getattr(r, "methods", set()) or set())),
        None,
    )
    if current is None:
        raise RuntimeError("ISCARB v7.3.4 could not find the production homepage route")

    previous_home = current.endpoint
    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/"]

    @app.get("/")
    def home_original_hero_lock():
        response = previous_home()
        body = bytes(response.body).decode("utf-8")

        # Replace both the CSS background and preload target from the optimized
        # derivative to the exact user-supplied original PNG.
        body = body.replace("/static/hero_user_web.jpg?v=7.2.0", _ORIGINAL_HERO)
        body = body.replace('type="image/jpeg" fetchpriority="high"', 'type="image/png" fetchpriority="high"')
        body = body.replace("7.2.0 · CLEAN · IT-WIDE", f"{_RELEASE} · CLEAN · IT-WIDE")
        body = body.replace("</head>", _HOME_STYLE + "\n</head>", 1)

        # Production invariant: the root page must not reference any retired or
        # generated hero. The original PNG is the only hero allowed here.
        forbidden = (
            "hero_user_web.jpg",
            "hero_v671.svg",
            "hero_desert.jpg",
        )
        leaked = [item for item in forbidden if item in body]
        if leaked:
            raise RuntimeError("ISCARB homepage hero lock failed: " + ", ".join(leaked))
        if _ORIGINAL_HERO not in body:
            raise RuntimeError("ISCARB exact original hero is not present in the homepage")

        headers = dict(response.headers)
        headers.update({
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-ISCARB-Version": _RELEASE,
            "X-ISCARB-UI": _RELEASE,
            "X-ISCARB-Hero-Mode": "exact-user-original-png",
            "X-ISCARB-Home": "v7.3.4-clean-it-wide-exact-original-hero",
        })
        return HTMLResponse(body, status_code=response.status_code, headers=headers)
