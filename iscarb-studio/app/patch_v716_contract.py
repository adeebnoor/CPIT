from __future__ import annotations

"""v7.1.6 final contract hardening.

This patch does not rebuild the engine. It makes the already-active production
policy authoritative in the generation prompt and in /api/health so no legacy
Software-Engineering/public-image/white-canvas metadata can contradict the
current ISCARB release contract.
"""

from . import master_guidelines_v470 as master
from . import start_v440 as base
from . import unit_contract

_PATCHED = False

FINAL_MASTER_GUIDELINES = """
ISCARB MASTER GUIDELINES (release conditions across all IT/computing lecture topics):
1) P1 AUTHORITY: P1 defines mandatory technical scope, terminology and conflict precedence. S1-S7 may clarify, evidence or contextualize P1; they never replace P1 or silently create a new mandatory topic list.
2) TWENTY CORE UNITS: Preserve exactly 20 learner-visible ISCARB Core Units. Physical slides may expand only for genuine source-content overflow and must remain within the Balanced30 ceiling.
3) COGNITIVE LOAD: Never paste PRIMARY-source paragraphs into presenter slides. Use concise teaching propositions and large readable type; keep narrative detail in P1 / speaker notes or a Source Expansion when genuinely necessary.
4) SOURCE FIGURES FIRST: Prefer an information-bearing P1 figure anchored to the Unit. If no useful P1 figure exists, use an ISCARB native/generated local-context explanatory visual or text-first composition. Public keyword-image fallback, Wikipedia/Wikimedia fallback and unrelated stock imagery are forbidden.
5) DOMAIN SPINE: Unit 2 is a curated 5-8-node source-derived map, never a dump of source headings. The coverage ledger, not the spine, owns complete P1 coverage.
6) OPENING CRISIS: Unit 1 must expose a concrete P1-supported incident, failure, risk or engineering stake. A generic crisis is release-blocking; do not invent one merely to satisfy the template.
7) BOUNDED LOCAL CONTEXT: Local scenarios are explicitly hypothetical, state a precise constraint, and may use only mechanisms already taught in this P1 lecture.
8) SCALABILITY/TREND: Name an explicit numeric or structural stress variable and ask which assumption fails first; reject generic 'what changes when it grows?' questions.
9) AI GOVERNANCE: AI may generate candidate tests/options/draft structure; accountable human engineering sign-off cannot be delegated to the model.
10) PERFORMANCE GRADING: Capability credit and final verdicts require defended learner performance, one learner artifact, and traceable P1 evidence.
"""


def apply_v716_contract_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    # contract_text() reads this module-global value at call time, so this fixes
    # generation, repair and audit prompts without duplicating their machinery.
    unit_contract.MASTER_GUIDELINES = FINAL_MASTER_GUIDELINES

    # Defense in depth: v6.9 already disables these paths, but keep the final
    # release layer explicit in case an older module is called directly.
    master.PUBLIC_VISUAL_UNITS = frozenset()
    master._public_candidates = lambda *args, **kwargs: []

    previous_health = base._health_v440

    def health():
        data = dict(previous_health())
        data.pop("approved_hero_blob", None)
        data.update({
            "release_ui": "7.1.6",
            "generic_it_scope": True,
            "course_hardcoding": False,
            "software_engineering_dependency": False,
            "primary_source_modes": ["public website / direct public document URL", "uploaded file"],
            "accepted_file_types": ["PDF", "PPTX", "DOCX", "TXT", "MD"],
            "primary_source_exactly_one": True,
            "supporting_sources_enabled": True,
            "max_supporting_sources": 7,
            "source_hierarchy": "P1 mandatory scope and conflict precedence; S1..S7 optional clarification/evidence/context only",
            "strict_20_unit_contract": True,
            "presenter_renderer": "cover + U01-U20 learner-visible core units + genuine SOURCE EXPANSION pages + close; max 30 physical slides",
            "balanced30": "20 core units remain visible; source expansion only for genuine non-lossy P1 overflow; max 8 expansion pages / 30 physical slides total",
            "visual_contract": "P1 source figure first; otherwise ISCARB native/generated local-context explanatory visual or text-first; public/random keyword image fallback disabled",
            "visual_policy": "P1 source figure -> native diagram -> generated local-context visual -> text-first",
            "visual_priority": "P1 source figure > ISCARB native/generated local-context visual > text-first",
            "public_web_image_fallback": False,
            "random_keyword_image_search": False,
            "source_visual_public_url": "DISABLED",
            "presenter_contract": "BlackNative/TextGold; magenta/cyan accents; large readable type; 20 core units; genuine source expansion only; max 30 physical slides",
            "presenter_visual_contract": "BlackNative #05070D + TextGold with magenta/cyan accents; large type; source figures first; no unrelated public imagery",
            "presenter_theme": "BlackNative/TextGold source-first visual narrative",
            "domain_spine": "curated 5-8 P1-derived chapter-level nodes; never a heading dump; full coverage remains in the ledger",
            "opening_crisis": "concrete P1-supported incident/failure/risk/stake required; generic crisis blocks release",
            "approved_hero_asset": "hero_user_original.png",
            "approved_hero_web_derivative": "hero_user_web.jpg",
            "approved_hero_original_sha256": "8967fa14fe910e5831531a6b74c64bcd650c965ad691697dd2d705d450b6e50d",
            "approved_hero_web_sha256": "fcad23fe86a60e6ca881eb46829d5f7dbe894d9bf57a17c0453952edf5ec7c12",
            "hero_delivery": "exact user-supplied hero_user_original.png; hero_user_web.jpg is only its optimized web derivative",
            "hero_original_raster": True,
            "hero_user_supplied": True,
            "hero_redraw": False,
            "hero_generated_substitute": False,
            "hero_static_dependency": True,
            "hero_live_release": "7.1.6",
        })
        return data

    base._health_v440 = health
    base.engine.health = health
