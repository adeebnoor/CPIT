from __future__ import annotations

"""Build-time assertions for the final ISCARB v7.1.6 release contract."""

from app.home_v670 import app  # noqa: F401
from app import start_v440 as base
from app import unit_contract


def main() -> None:
    h = dict(base._health_v440())
    assert h.get("release_ui") == "7.1.6", h
    assert h.get("generic_it_scope") is True, h
    assert h.get("course_hardcoding") is False, h
    assert h.get("software_engineering_dependency") is False, h
    assert h.get("accepted_file_types") == ["PDF", "PPTX", "DOCX", "TXT", "MD"], h
    assert h.get("primary_source_exactly_one") is True, h
    assert h.get("supporting_sources_enabled") is True, h
    assert h.get("max_supporting_sources") == 7, h
    assert "P1 mandatory scope" in h.get("source_hierarchy", ""), h
    assert h.get("strict_20_unit_contract") is True, h
    assert "max 30 physical slides" in h.get("presenter_renderer", ""), h
    assert h.get("public_web_image_fallback") is False, h
    assert h.get("random_keyword_image_search") is False, h
    assert h.get("source_visual_public_url") == "DISABLED", h
    assert "BlackNative" in h.get("presenter_contract", ""), h
    assert "TextGold" in h.get("presenter_contract", ""), h
    assert "magenta/cyan" in h.get("presenter_contract", ""), h
    assert "curated 5-8" in h.get("domain_spine", ""), h
    assert "generic crisis blocks release" in h.get("opening_crisis", ""), h
    assert h.get("approved_hero_asset") == "hero_user_original.png", h
    assert h.get("approved_hero_web_derivative") == "hero_user_web.jpg", h
    assert h.get("hero_redraw") is False and h.get("hero_generated_substitute") is False, h

    contract = unit_contract.MASTER_GUIDELINES
    assert "all IT/computing lecture topics" in contract
    assert "advanced software-engineering topics" not in contract
    assert "P1 AUTHORITY" in contract
    assert "S1-S7" in contract
    assert "TWENTY CORE UNITS" in contract
    assert "SOURCE FIGURES FIRST" in contract
    assert "Public keyword-image fallback" in contract
    assert "DOMAIN SPINE" in contract
    assert "OPENING CRISIS" in contract

    print("ISCARB v7.1.6 final contract smoke PASS")


if __name__ == "__main__":
    main()
