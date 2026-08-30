from __future__ import annotations

import re
import unittest
from pathlib import Path

from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.session_gate import apply_90_minute_timebox
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile, _clean, _is_furniture_line

LECTURES = Path(__file__).resolve().parents[2] / "lectures" / "cimt"
BULLET_GLYPH = re.compile(r"[■▪◆●▶◼◾•‣⁃]")
CONTACT = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


class LabelCleaningTests(unittest.TestCase):
    def test_bullet_glyphs_are_stripped_from_labels(self):
        for raw in ("■ TEMPLATE: The system shall achieve", "• Reliability metrics", "◆ Fault tolerance ◆"):
            with self.subTest(raw=raw):
                self.assertFalse(BULLET_GLYPH.search(_clean(raw)), _clean(raw))

    def test_contact_blocks_are_treated_as_furniture(self):
        self.assertTrue(_is_furniture_line("Instructor: Prof. A. Person (someone@example.edu ("))
        self.assertFalse(_is_furniture_line("11.3 Fault-tolerant architectures"))


class ArchivedLectureOutputTests(unittest.TestCase):
    """The deterministic draft is what faculty see when quota runs out, so its
    headings must be presentable, not raw extractor output."""

    @classmethod
    def setUpClass(cls):
        cls.blueprints = []
        for pdf in sorted(LECTURES.glob("*.pdf")):
            bundle = SourceBundle(
                items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
                lecture_focus="",
                session_minutes=90,
            )
            profile = build_deterministic_source_profile(bundle, "label hygiene regression")
            bp = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
            cls.blueprints.append((pdf.name, bp))

    def test_every_archived_lecture_converts(self):
        self.assertGreaterEqual(len(self.blueprints), 10)
        for name, bp in self.blueprints:
            with self.subTest(lecture=name):
                self.assertEqual([u.number for u in bp.units], list(range(1, 21)))
                self.assertEqual(sum(u.planned_minutes for u in bp.units), 90)
                self.assertEqual(len(bp.clOs), 5)

    def test_no_heading_carries_extractor_glyph_noise(self):
        for name, bp in self.blueprints:
            with self.subTest(lecture=name):
                self.assertFalse(BULLET_GLYPH.search(bp.lecture_title), bp.lecture_title)
                for unit in bp.units:
                    self.assertFalse(BULLET_GLYPH.search(unit.title), f"unit {unit.number}: {unit.title}")

    def test_no_heading_exposes_an_instructor_contact_address(self):
        for name, bp in self.blueprints:
            with self.subTest(lecture=name):
                self.assertIsNone(CONTACT.search(bp.lecture_title), bp.lecture_title)
                for unit in bp.units:
                    self.assertIsNone(CONTACT.search(unit.title), f"unit {unit.number}: {unit.title}")


if __name__ == "__main__":
    unittest.main()
