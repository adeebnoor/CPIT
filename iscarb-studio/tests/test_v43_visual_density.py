"""Slides must carry a diagram, not a row of boxes in a third of the page.

A deck exported from live production drew 9 vector marks per page with no
connectors, no axes and no scale, and left the bottom quarter of every slide
empty: 19 of its 20 pages were near-blank. These tests pin the geometry and
the connective marks that fixed it.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import pymupdf

from app.cimt_native_v43 import (
    BAND_BOTTOM,
    BAND_TOP,
    export_cimt_presenter_pdf_v43,
)
from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.session_gate import apply_90_minute_timebox
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile

LECTURES = Path(__file__).resolve().parents[2] / "lectures" / "cimt"

# The TRY rule is drawn at y=64 and the question line ends near y=445.
FOOTER_RULE_Y = 64.0
QUESTION_BASELINE_Y = 445.0


class BandGeometryTests(unittest.TestCase):
    def test_the_band_clears_the_footer_rule(self):
        self.assertGreater(BAND_BOTTOM, FOOTER_RULE_Y)

    def test_the_band_stays_under_the_question_line(self):
        self.assertLess(BAND_TOP, QUESTION_BASELINE_Y)

    def test_the_band_uses_most_of_the_slide(self):
        # It previously ran 423->150, leaving 72pt blank above the footer.
        self.assertGreater(BAND_TOP - BAND_BOTTOM, 320)


class RenderedDensityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pdf = LECTURES / "CPIT455-class2-NooR.pdf"
        if not pdf.exists():  # pragma: no cover - source bundle not checked out
            raise unittest.SkipTest(f"missing reference lecture {pdf}")
        bundle = SourceBundle(
            items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
            lecture_focus="",
            session_minutes=90,
        )
        profile = build_deterministic_source_profile(bundle, "visual density tests")
        bp = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
        cls.tmp = Path(__file__).resolve().parent / "_density_probe.pdf"
        export_cimt_presenter_pdf_v43(bp, cls.tmp)
        cls.doc = pymupdf.open(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        cls.doc.close()
        cls.tmp.unlink(missing_ok=True)

    def _page_marks(self):
        return [(len(p.get_drawings()), len(p.get_images())) for p in self.doc]

    def test_the_deck_still_has_twenty_pages(self):
        self.assertEqual(len(self.doc), 20)

    def test_almost_no_page_is_near_blank(self):
        marks = self._page_marks()
        thin = [i + 1 for i, (d, im) in enumerate(marks) if d < 12 and im == 0]
        # The cover and the two closing summary slides are legitimately sparse.
        self.assertLessEqual(len(thin), 4, f"near-blank pages: {thin}")

    def test_teaching_pages_carry_more_than_the_frame(self):
        # The frame alone accounts for about five marks; a teaching page that
        # adds nothing on top of it is the defect this guards.
        for i in range(5, 15):
            drawings, images = self._page_marks()[i]
            self.assertTrue(drawings > 5 or images > 0,
                            f"unit {i + 1} draws nothing beyond the frame")


class ConnectiveMarkTests(unittest.TestCase):
    """Arrows, ticks and stems are what separate a diagram from a box row."""

    @classmethod
    def setUpClass(cls):
        whole = (Path(__file__).resolve().parents[1]
                 / "app" / "cimt_native_v43.py").read_text(encoding="utf-8")
        # Scope to the PDF renderer: the PPTX exporter has its own _ppt_* forms
        # and matching kind names, so an unscoped split silently reads those.
        cls.whole = whole
        cls.src = whole.split("def _r_redraw(")[1].split("\ndef ")[0]

    def test_an_arrow_helper_exists(self):
        self.assertIn("def _arrow(", self.whole)

    def test_the_chain_links_its_stages(self):
        chain = self.src.split('if kind in {"chain","mutation"}:')[1].split("return")[0]
        self.assertIn("_arrow(", chain, "a chain with no arrows is a row of boxes")

    def test_the_stack_shows_where_change_travels(self):
        stack = self.src.split('if kind == "stack":')[1].split("return")[0]
        self.assertIn("_arrow(", stack)
        self.assertIn("BAND_BOTTOM", stack, "the stack must fill the slide band")

    def test_the_curve_is_drawn_against_a_scale(self):
        curve = self.src.split('if kind == "curve":')[1].split("return")[0]
        self.assertIn("_tick_label(", curve, "an unlabelled axis carries no scale")

    def test_the_timeline_ties_markers_to_labels(self):
        timeline = self.src.split('if kind == "timeline":')[1].split("return")[0]
        self.assertIn("_arrow(", timeline)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()


class VerdictLabelTests(unittest.TestCase):
    """A slide must not contradict its own headings."""

    @classmethod
    def setUpClass(cls):
        from app.cimt_native_v43 import _spec

        pdf = LECTURES / "CPIT455-class2-NooR.pdf"
        if not pdf.exists():  # pragma: no cover - source bundle not checked out
            raise unittest.SkipTest(f"missing reference lecture {pdf}")
        bundle = SourceBundle(
            items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
            lecture_focus="",
            session_minutes=90,
        )
        profile = build_deterministic_source_profile(bundle, "verdict tests")
        bp = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
        cls.kind, cls.items = _spec(bp, bp.units[19])

    def test_unit_20_uses_the_verdict_form(self):
        self.assertEqual(self.kind, "verdict")

    def test_the_options_box_carries_the_verdict_options(self):
        label, body = self.items[1]
        self.assertEqual(label, "THE OPTIONS")
        self.assertIn("APPROVE", body.upper())

    def test_residual_uncertainty_is_not_a_verdict_option(self):
        # ped[0] is the APPROVE line; taking it put a verdict under this heading.
        from app.cimt_native_v43 import _names_a_verdict

        label, body = self.items[2]
        self.assertEqual(label, "RESIDUAL UNCERTAINTY")
        self.assertFalse(_names_a_verdict(body), f"a verdict option is labelled residual: {body!r}")

    def test_verdict_detection_separates_the_two_kinds_of_line(self):
        from app.cimt_native_v43 import _names_a_verdict

        self.assertTrue(_names_a_verdict("APPROVE — the evidence supports it."))
        self.assertTrue(_names_a_verdict("REJECT — the evidence contradicts it."))
        self.assertFalse(_names_a_verdict("Keep residual uncertainty visible."))
