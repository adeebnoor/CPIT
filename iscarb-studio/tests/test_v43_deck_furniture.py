from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.session_gate import apply_90_minute_timebox
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import (
    _chunks,
    _meaningful_lines,
    _recurring_furniture,
    build_deterministic_source_profile,
)

ARCHIVE = Path(__file__).resolve().parents[2] / "lectures" / "cimt"


class ExcerptSeparatorTests(unittest.TestCase):
    """The excerpt joiner is U+00B7. Adding it to the inline-bullet cleaner
    collapsed every source slide into one run-on line, which silently broke both
    slide-importance scoring and furniture detection."""

    def test_excerpt_lines_survive_cleaning(self):
        pdf = next(iter(sorted(ARCHIVE.glob("*.pdf"))), None)
        if pdf is None:
            self.skipTest("no archived lecture available")
        _coordinate, chunks = _chunks(pdf)
        recovered = [len(_meaningful_lines(excerpt.replace(" · ", "\n"))) for _i, _l, excerpt in chunks]
        self.assertGreater(
            max(recovered), 1,
            "every slide collapsed to a single line; the excerpt separator is being stripped",
        )

    def test_the_separator_is_not_treated_as_a_bullet(self):
        from app.source_profile_fallback import _INLINE_BULLET
        self.assertIsNone(_INLINE_BULLET.search("·"), "the excerpt separator is in the bullet class")
        self.assertIsNotNone(_INLINE_BULLET.search("■"), "real bullet glyphs must still be cleaned")


class RecurringFurnitureTests(unittest.TestCase):
    """A running header repeats across a deck; a real checkpoint does not. The
    hardcoded furniture list only knew the CPIT decks, so a Sommerville chapter's
    own footer was chosen as a slide heading."""

    def _synthetic_deck(self, footer: str, slides: int = 20):
        return [
            (i, f"Real heading {i}", f"Real heading {i} · Body sentence number {i} with enough words · {footer}")
            for i in range(1, slides + 1)
        ]

    def test_a_repeated_line_is_identified_without_naming_it(self):
        found = _recurring_furniture(self._synthetic_deck("Chapter 13 Dependability Engineering"))
        self.assertIn("chapter 13 dependability engineering", found)

    def test_content_that_appears_once_is_not_furniture(self):
        found = _recurring_furniture(self._synthetic_deck("Chapter 13 Dependability Engineering"))
        self.assertNotIn("body sentence number 4 with enough words", found)

    def test_a_short_deck_is_left_alone(self):
        """With few slides, repetition is not evidence of chrome."""
        self.assertEqual(_recurring_furniture(self._synthetic_deck("Footer", slides=4)), set())


class ArchivedDeckHeadingTests(unittest.TestCase):
    def test_no_unit_heading_is_a_running_deck_footer(self):
        for pdf in sorted(ARCHIVE.glob("*.pdf")):
            with self.subTest(lecture=pdf.name):
                bundle = SourceBundle(
                    items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
                    lecture_focus="", session_minutes=90,
                )
                profile = build_deterministic_source_profile(bundle, "furniture regression")
                blueprint = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
                _c, chunks = _chunks(pdf)
                furniture = _recurring_furniture(chunks)
                if not furniture:
                    continue
                import re
                for unit in blueprint.units[5:15]:
                    key = re.sub(r"[^a-z0-9]+", " ", unit.title.lower()).strip()
                    self.assertNotIn(key, furniture, f"unit {unit.number} is titled with deck chrome")


if __name__ == "__main__":
    unittest.main()
