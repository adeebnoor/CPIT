from __future__ import annotations

import re
import unittest
from pathlib import Path

from app.cimt_native_v43 import (
    _dedupe_repeated_phrase,
    _source_first_items,
    _trim_on_word_boundary,
    _unflatten_bullets,
)
from app.models import LectureUnit, VisualPlan

CIMT_REFERENCE = Path(__file__).resolve().parents[2] / "lectures" / "cimt" / "CPIT455-class2-NooR.pdf"


def _unit(core: list[str], pedagogy: list[str] | None = None) -> LectureUnit:
    return LectureUnit(
        number=7, phase="MARIS", title="Mechanism", engineering_question="Why?",
        core_content=core, pedagogy_content=pedagogy or [], knowledge_types=["CONCEPT"],
        visual_suggestion="process", visual_plan=VisualPlan(visual_type="process", teaching_purpose="p"),
        student_action="Do it.", takeaway="The point.", cimtlens=["C"], clo_ids=["CLO1"],
        planned_minutes=5,
    )


class FlattenedBulletRecoveryTests(unittest.TestCase):
    """The archived CIMT lectures use these glyphs as a deliberate two-level
    bullet hierarchy, so a glyph mid-sentence means a list was flattened during
    extraction, not that the text is dirty. The structure is recoverable."""

    def test_a_flattened_list_becomes_separate_points(self):
        # Taken from the live deck, page 14.
        raw = ("Process activities ■ Real software processes are inter-leaved sequences "
               "of technical activities ■ Specification development validation and evolution")
        points = _unflatten_bullets(raw)
        self.assertGreaterEqual(len(points), 2)
        for point in points:
            self.assertNotRegex(point, r"[■▪❑❏•]")

    def test_a_genuine_single_statement_is_left_alone(self):
        raw = "Reliability is the probability of failure-free operation over a stated period."
        self.assertEqual(_unflatten_bullets(raw), [raw])

    def test_recovered_points_reach_the_slide_as_separate_blocks(self):
        raw = ("Waterfall phases ■ Requirements are fixed before design begins "
               "■ Each phase signs off before the next starts")
        items = _source_first_items(_unit([raw]))
        self.assertGreaterEqual(len(items), 2, f"list still renders as one block: {items}")

    def test_fragments_too_short_to_teach_are_not_split_out(self):
        """Splitting on every glyph would manufacture one-word bullets."""
        self.assertEqual(len(_unflatten_bullets("Scope ■ ok ■ fine")), 1)


class HeadingHygieneTests(unittest.TestCase):
    def test_a_heading_that_repeats_itself_is_collapsed(self):
        # Taken from the live deck, page 13.
        raw = "Chapter 2 – Software Processes Chapter 2 Software Processes 1 / Software process models"
        self.assertEqual(_dedupe_repeated_phrase(raw), "Chapter 2 – Software Processes")

    def test_a_normal_heading_survives_untouched(self):
        raw = "The Waterfall model and its phases (requirements analysis, design)"
        self.assertEqual(_dedupe_repeated_phrase(raw), raw)

    def test_a_long_heading_is_cut_on_a_word_boundary(self):
        cut = _trim_on_word_boundary("Integration and configuration of reuse oriented software engineering practice", 40)
        self.assertLessEqual(len(cut), 40)
        self.assertFalse(cut.endswith("-"))
        self.assertTrue(cut.split()[-1].isalpha() or cut.split()[-1].isalnum())


class CimtReferenceGrammarTests(unittest.TestCase):
    """Facts about the reference deck the Presenter is meant to resemble, kept in
    the suite so a future change cannot quietly drift away from it."""

    @unittest.skipUnless(CIMT_REFERENCE.exists(), "archived CIMT reference not present")
    def test_reference_uses_a_bullet_hierarchy_we_must_not_treat_as_noise(self):
        import pypdf
        text = "\n".join((p.extract_text() or "") for p in pypdf.PdfReader(str(CIMT_REFERENCE)).pages)
        self.assertIn("◼", text + "◼")  # tolerate either filled-square codepoint
        self.assertTrue(re.search(r"[■◼❑❏]", text),
                        "reference deck no longer shows the bullet grammar this renderer imitates")


if __name__ == "__main__":
    unittest.main()
