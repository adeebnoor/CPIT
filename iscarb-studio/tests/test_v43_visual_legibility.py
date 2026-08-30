from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app import source_visuals as sv
from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.session_gate import apply_90_minute_timebox
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile
from app.source_visuals_v42 import _is_presentable, plan_for_unit_v42

LECTURE = Path(__file__).resolve().parents[2] / "lectures" / "cimt" / "CPIT455-class3-NooR.pdf"

# What a 13.33in slide needs for projected diagram text to stay crisp.
TEACHING_CANVAS_INCHES = 11.5
MIN_ACCEPTABLE_DPI = 140


def _asset(tmp: Path, width: int, height: int) -> sv.VisualAsset:
    path = tmp / f"asset-{width}x{height}.png"
    Image.new("RGB", (width, height), "white").save(path)
    return sv.VisualAsset(1, "", "alt text", "", str(path), "local-pdf")


class RasterResolutionTests(unittest.TestCase):
    """A source page shown full-width used to arrive at roughly 91 DPI."""

    def test_rasterized_pages_are_crisp_at_presentation_size(self):
        registry = sv._build_pdf_registry(LECTURE, LECTURE.stem)
        self.assertIsNotNone(registry)
        for asset in registry.assets[:5]:
            path = sv.local_asset(asset)
            self.assertIsNotNone(path)
            with Image.open(path) as im:
                dpi = im.size[0] / TEACHING_CANVAS_INCHES
            self.assertGreaterEqual(
                dpi, MIN_ACCEPTABLE_DPI,
                f"slide {asset.slide_number} lands at {dpi:.0f} DPI on the teaching canvas",
            )

    def test_cache_key_moves_with_the_render_zoom(self):
        """Otherwise a deploy keeps serving pages rasterized at the old zoom."""
        import inspect
        source = inspect.getsource(sv._build_pdf_registry)
        self.assertIn("PDF_RENDER_ZOOM", source, "cache key ignores the render zoom")


class LegibilityGateTests(unittest.TestCase):
    """An image that cannot fill the canvas legibly is not a teaching visual."""

    def test_low_resolution_assets_are_not_presentable(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for width, height in ((640, 480), (1024, 768)):
                with self.subTest(width=width):
                    self.assertFalse(_is_presentable(_asset(tmp, width, height)))

    def test_full_resolution_assets_remain_presentable(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(_is_presentable(_asset(Path(td), 1872, 1404)))

    def test_unmeasurable_asset_does_not_lose_its_source_visual(self):
        missing = sv.VisualAsset(1, "", "alt", "", "/nonexistent/path.png", "local-pdf")
        self.assertTrue(_is_presentable(missing), "an unreadable asset must not be rejected on a guess")

    def test_a_soft_source_image_falls_back_to_a_redrawn_diagram(self):
        bundle = SourceBundle(
            items=[SourceItem("primary", "P1", LECTURE.name, LECTURE, LECTURE.name)],
            lecture_focus="", session_minutes=90,
        )
        profile = build_deterministic_source_profile(bundle, "legibility regression")
        blueprint = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
        registry = sv._build_pdf_registry(LECTURE, LECTURE.stem)

        sharp = {u.number for u in blueprint.units
                 if plan_for_unit_v42(blueprint, u, registry).reuse_mode == "USE"}
        self.assertTrue(sharp, "no unit uses a source visual, so the gate cannot be observed")

        with tempfile.TemporaryDirectory() as td:
            soft = Path(td) / "soft.png"
            Image.new("RGB", (640, 480), "white").save(soft)
            downgraded = sv.VisualRegistry(
                registry.source_url, registry.source_title,
                tuple(sv.VisualAsset(a.slide_number, a.image_url, a.alt_text, a.source_url, str(soft), a.source_kind)
                      for a in registry.assets),
                registry.source_kind,
            )
            for number in sorted(sharp):
                unit = blueprint.units[number - 1]
                plan = plan_for_unit_v42(blueprint, unit, downgraded)
                self.assertNotEqual(plan.reuse_mode, "USE", f"unit {number} still enlarges a soft image")
                self.assertFalse(plan.source_visual_available)


if __name__ == "__main__":
    unittest.main()
