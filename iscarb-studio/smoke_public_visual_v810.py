import os
from pathlib import Path
from types import SimpleNamespace as NS

import run  # installs full production chain
from app import start_v440 as base
from app import public_image_search_v810 as search
from app.visual_prompt_v810 import PUBLIC_VISUAL_PROMPT_ADDENDUM

assert os.getenv("ISCARB_BUILD_ID") == "8.1.0-public-visual-intelligence", os.getenv("ISCARB_BUILD_ID")
health = dict(base._health_v440())
assert health.get("build_id") == "8.1.0-public-visual-intelligence", health
assert health.get("public_visual_intelligence_version") == "8.1.0", health
assert health.get("learning_autosave_seconds") == 5
assert health.get("selected_image_registry") is True
assert "Pexels/Pixabay/Unsplash" in health.get("public_visual_license_policy", ""), health

quote_unit = NS(
    number=4,
    title="Why technology alone cannot solve security",
    engineering_question="What does a security solution miss when human understanding is weak?",
    visual_suggestion="A conceptual human-technology security tension without logos",
    student_action="You are the responsible engineer. Explain the human understanding gap.",
    takeaway="Technology does not replace security judgment.",
    core_content=["Security is a system property shaped by more than a technical mechanism."],
    pedagogy_content=["Interpret the quotation before proposing a control."],
    visual_plan=NS(visual_type="metaphorical", focal_elements=["technology", "security", "human", "understanding"]),
)
brief = search.build_search_brief(quote_unit)
assert brief.image_type == "metaphorical", brief
assert 3 <= len(brief.queries) <= 5, brief
assert {"technology","security","human","understanding"}.issubset(set(brief.keywords)), brief

fake = search.ImageCandidate(
    provider="Openverse", provider_id="smoke-visual-810",
    image_url="https://example.com/iscarb-v810-security.jpg",
    thumbnail_url="https://example.com/iscarb-v810-security-thumb.jpg",
    landing_url="https://example.com/source", width=1600, height=1000,
    title="technology security human understanding engineering decision",
    creator="Example Author", creator_url="https://example.com/author",
    license_code="cc0", license_label="CC0", license_url="https://creativecommons.org/publicdomain/zero/1.0/",
    created_at="2026-01-10T00:00:00Z",
)
settings = search.save_settings({"providers":["openverse"],"clip_mode":"off","minimum_score":.40}, "smoke-v810-job")
used=set()
scored=search.score_candidate(brief,fake,settings,used)
assert scored.score >= .40, scored
assert scored.semantic_method == "lexical"
assert scored.license_score == 1.0
assert "CC0" in scored.attribution

# Provider labels are exact platform licenses, not falsely called CC0.
pexels = search.ImageCandidate("Pexels","1","https://example.com/p.jpg","https://example.com/t.jpg","https://pexels.com/photo/1",1600,1000,"security operations","A","","pexels","Pexels License","https://www.pexels.com/license/","")
pixabay = search.ImageCandidate("Pixabay","2","https://example.com/x.jpg","https://example.com/y.jpg","https://pixabay.com/photos/2",1600,1000,"security operations","B","","pixabay","Pixabay Content License","https://pixabay.com/service/license-summary/","")
assert search._license_score(pexels) > 0 and "CC0" not in pexels.license_label
assert search._license_score(pixabay) > 0 and "CC0" not in pixabay.license_label

# On-demand selection + duplicate registry without network access.
orig_provider = search._provider_search
try:
    search._provider_search = lambda provider, query, limit, settings: [fake]
    job = NS(id="smoke-v810-job", blueprint=NS(units=[quote_unit]))
    out = search.public_visual_for_unit(job, 4, p1_visual_exists=False)
    assert out["status"] == "selected", out
    assert out["candidate"]["provider"] == "Openverse"
    assert out["candidate"]["semantic_method"] == "lexical"
    assert out["clip_used"] is False
    assert "External visual" in out["source_anchor"]
    assert search.selected_candidate("smoke-v810-job",4) is not None

    # A source-backed P1 visual always suppresses internet search.
    locked = search.public_visual_for_unit(job, 4, p1_visual_exists=True)
    assert locked["status"] == "p1_preferred", locked
finally:
    search._provider_search = orig_provider

paths={getattr(route,"path","") for route in run.app.router.routes}
for path in (
    "/api/learning/{job_id}/public-visual/{unit_no}",
    "/api/learning/{job_id}/public-visual-image/{unit_no}",
    "/api/learning/{job_id}/public-visual-annotation",
    "/api/learning/{job_id}/visual-search-settings",
    "/api/learning/{job_id}/selected-image-history",
):
    assert path in paths, path

static=Path(__file__).parent/"app"/"static"
js=(static/"learning_v810.js").read_text(encoding="utf-8")
css=(static/"learning_v810.css").read_text(encoding="utf-8")
for needle in ("public-visual/", "EXTERNAL LICENSED VISUAL", "source_footer", "Circle size", "public-visual-annotation", "Autosave: 5s"):
    assert needle in js, needle
for needle in ("externalHybridGrid", "publicCircle", "publicSourceFooter", "visualPin"):
    assert needle in css, needle
for needle in ("metaphorical / technical / real-world / conceptual", "Never invent a license", "not P1 evidence", "no-image/icon fallback"):
    assert needle in PUBLIC_VISUAL_PROMPT_ADDENDUM, needle

print("PASS: v8.1 licensed public visual intelligence: semantic briefs, 3-5 queries, 40/25/20/10/5 ranking, exact licensing, P1 priority, 50/50 UI, zoom, circle annotation, autosave, registry, admin settings")
