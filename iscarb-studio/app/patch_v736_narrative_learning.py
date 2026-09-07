from __future__ import annotations

"""v7.3.6 — Narrative Learning Experience Engine.

Adds stateful student/instructor surfaces without changing the Golden v6.6
technical grammar. It also exposes narrative bridges in presenter headers and
makes the production home explain the learning journey instead of presenting
ISCARB as a file generator only.
"""

from fastapi.responses import HTMLResponse

from . import main as engine
from . import start_v440 as base
from . import presenter_v67_prod as presenter
from .learning_experience import TRANSITIONS, health_fragment, install_learning_experience

_PATCHED = False

_NARRATIVE_HOME_STYLE = r"""
<style id="iscarb-v736-narrative-home">
.narrativeIntro{margin-top:10px;margin-bottom:32px;padding:24px;border:1px solid rgba(44,220,255,.22);border-radius:24px;background:linear-gradient(135deg,rgba(44,220,255,.045),rgba(255,37,140,.035));box-shadow:0 24px 60px rgba(0,0,0,.18)}
.narrativeIntroHead{display:flex;gap:18px;align-items:flex-end;justify-content:space-between;margin-bottom:18px}.narrativeIntroHead h2{margin:0;max-width:760px}.narrativeIntroHead p{margin:0;max-width:430px;color:var(--muted,#B7BDC8);line-height:1.55}
.narrativeJourney{display:grid;grid-template-columns:repeat(5,1fr);gap:9px}.narrativeStep{position:relative;min-height:94px;padding:14px;border:1px solid rgba(255,255,255,.11);border-radius:16px;background:rgba(5,7,13,.58)}.narrativeStep::after{content:"→";position:absolute;right:-9px;top:34px;z-index:2;color:#DCB56B;font-weight:900}.narrativeStep:last-child::after{display:none}.narrativeStep b{display:block;margin-bottom:7px;color:#F5F5F8;font-size:12px}.narrativeStep span{display:block;color:#B7BDC8;font-size:11px;line-height:1.45}.narrativeStep i{display:inline-block;margin-bottom:9px;color:#2CDCFF;font-size:10px;font-style:normal;font-weight:900;letter-spacing:.08em}
.narrativeSurfaces{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}.narrativeSurface{padding:14px 16px;border:1px solid rgba(220,181,107,.20);border-radius:14px;background:rgba(220,181,107,.025)}.narrativeSurface b{display:block;color:#DCB56B;margin-bottom:4px}.narrativeSurface span{color:#B7BDC8;font-size:12px;line-height:1.45}
.heroArt::after{content:"P1 SOURCE  ·  20 CORE UNITS  ·  PREDICT → TEST → EVIDENCE → VERDICT"!important}
html[data-lang="ar"] .heroArt::after{content:"المصدر P1  ·  ٢٠ وحدة  ·  توقّع ← اختبر ← ابنِ الدليل ← قرّر"!important}
@media(max-width:980px){.narrativeJourney{grid-template-columns:1fr 1fr}.narrativeStep::after{display:none}.narrativeIntroHead{display:block}.narrativeIntroHead p{margin-top:8px;max-width:none}}
@media(max-width:620px){.narrativeJourney,.narrativeSurfaces{grid-template-columns:1fr}.narrativeIntro{padding:17px}}
</style>
"""

_NARRATIVE_SECTION = r"""
<section class="section shell narrativeIntro" id="learning-journey">
  <div class="narrativeIntroHead">
    <div>
      <span class="itAutoBadge">NARRATIVE LEARNING ENGINE · v7.3.6</span>
      <h2><span data-lang="en">The lecture is now a decision journey—not a slide package.</span><span lang="ar" dir="rtl" data-lang="ar">المحاضرة أصبحت رحلة قرار هندسي — وليست حزمة شرائح.</span></h2>
    </div>
    <p><span data-lang="en">The faculty builds from P1. The learner must predict, test, justify and issue a bounded professional verdict. Progress is autosaved.</span><span lang="ar" dir="rtl" data-lang="ar">يبني عضو هيئة التدريس من المصدر P1، بينما يلتزم الطالب بالتوقع والاختبار والتبرير وإصدار قرار مهني محدود. ويحفظ التقدم تلقائيًا.</span></p>
  </div>
  <div class="narrativeJourney" aria-label="ISCARB five-station learning journey">
    <div class="narrativeStep"><i>01</i><b>CRISIS · PREDICT</b><span>Commit to a failure variable before the mechanism is revealed.</span></div>
    <div class="narrativeStep"><i>02</i><b>ANALYSE · FALSIFY</b><span>Name the observable condition that would break the current claim.</span></div>
    <div class="narrativeStep"><i>03</i><b>DESIGN · OWN</b><span>Compare trade-offs, map risk and name the accountable verifier.</span></div>
    <div class="narrativeStep"><i>04</i><b>EVIDENCE · CHALLENGE</b><span>Build claim → evidence → warrant and expose it to peer critique.</span></div>
    <div class="narrativeStep"><i>05</i><b>BOUND THE VERDICT</b><span>Accept, condition, redesign or reject—only as far as the evidence allows.</span></div>
  </div>
  <div class="narrativeSurfaces">
    <div class="narrativeSurface"><b>Faculty Studio</b><span>Compile, audit and export the source-locked 20-unit lecture, then launch its student journey and protected instructor dashboard.</span></div>
    <div class="narrativeSurface"><b>Student Experience</b><span>Five narrative stations, mandatory gates, 5-second autosave, peer critique and a conservative four-level capability signal.</span></div>
  </div>
</section>
"""


def _bridge(number: int) -> str:
    text = TRANSITIONS.get(number, "")
    if not text:
        return ""
    # Presenter must stay projection-readable; keep only the connective lead.
    return text.split(" — ", 1)[0].strip()


def _install_narrative_home(app) -> None:
    home_route = next((r for r in app.router.routes if getattr(r, "path", None) == "/"), None)
    if home_route is None:
        return
    original_home = home_route.endpoint
    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/"]

    @app.get("/")
    def narrative_home():
        response = original_home()
        body = response.body.decode("utf-8")
        body = body.replace(
            "<title>ISCARB IT Lecture Studio · Source-grounded lecture transformation</title>",
            "<title>ISCARB Learning Experience Engine · Source-grounded engineering judgment</title>",
            1,
        )
        body = body.replace("IT Lecture Transformation Studio", "Narrative Learning Experience Engine", 1)
        body = body.replace("7.2.0 · CLEAN · IT-WIDE", "7.3.6 · NARRATIVE LEARNING · SOURCE-LOCKED", 1)
        body = body.replace(
            "Turn any lecture into a defendable <em>learning experience.</em>",
            "Turn every lecture into an <em>engineering decision journey.</em>",
            1,
        )
        body = body.replace(
            "حوّل أي محاضرة إلى تجربة تعليمية <em>هندسية</em>",
            "حوّل كل محاضرة إلى <em>رحلة قرار هندسي</em>",
            1,
        )
        body = body.replace(
            "From trusted source to classroom experience—ready to defend.",
            "From P1 source to prediction, falsification, evidence and a bounded professional verdict.",
            1,
        )
        body = body.replace(
            "من مصدر موثوق إلى تجربة صفية جاهزة للدفاع.",
            "من المصدر P1 إلى التوقع والتزييف وبناء الدليل ثم قرار مهني محدود.",
            1,
        )
        body = body.replace(
            "Presenter, faculty/student packs, blueprint and complete ZIP package.",
            "Presenter, student journey, instructor dashboard and source-traceable teaching package.",
            1,
        )
        marker = '<section class="section shell" id="sources">'
        if marker in body and "id=\"learning-journey\"" not in body:
            body = body.replace(marker, _NARRATIVE_SECTION + "\n" + marker, 1)
        body = body.replace("</head>", _NARRATIVE_HOME_STYLE + "\n</head>", 1)
        headers = dict(response.headers)
        for key in ("content-length", "content-type"):
            headers.pop(key, None)
        headers.update({
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "X-ISCARB-Version": "7.3.6",
            "X-ISCARB-UI": "7.3.6-narrative-learning",
            "X-ISCARB-Home": "v7.3.6-narrative-learning-experience",
        })
        return HTMLResponse(body, headers=headers)


def apply_v736_narrative_learning_patch(app):
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True
    install_learning_experience(app)
    _install_narrative_home(app)

    # Add connective words to presenter headers without adding slides, changing
    # source content, or weakening the 20-unit contract.
    original_ppt_header = presenter._ppt_header
    def ppt_header(slide, u, page_idx, total):
        original_ppt_header(slide, u, page_idx, total)
        cue = _bridge(getattr(u, "number", 0))
        if cue:
            presenter._ppt_text(slide, 10.35, .50, 2.55, .22, cue, 6.8, presenter.GOLD, True, presenter.PP_ALIGN.RIGHT)
    presenter._ppt_header = ppt_header

    original_pdf_header = presenter._pdf_header
    def pdf_header(c, u, page_idx, total):
        original_pdf_header(c, u, page_idx, total)
        cue = _bridge(getattr(u, "number", 0))
        if cue:
            presenter._pdf_text(c, 730, 530, 190, 15, cue, 5.8, presenter.GOLD, True, "right", 1)
    presenter._pdf_header = pdf_header

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update(health_fragment())
        data["build_id"] = "7.3.6-narrative-learning-experience"
        return data
    base._health_v440 = health
    base.engine.health = health
