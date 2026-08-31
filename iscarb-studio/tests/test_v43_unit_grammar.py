"""The 20-unit grammar must be visible to the learner, not just structural.

A deck that exports twenty pages has not honoured the unit contract if eight of
its ten teaching units ask the same templated question of the same material.
These tests pin the three defects that produced exactly that.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from app.deterministic_blueprint_fallback import (
    _MOVE_FOR_SLOT,
    _MOVES_BY_NAME,
    _as_noun_phrase,
    _fill_rows,
    build_deterministic_blueprint,
)
from app.session_gate import apply_90_minute_timebox
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import _is_title_like, build_deterministic_source_profile

LECTURES = Path(__file__).resolve().parents[2] / "lectures" / "cimt"


def _blueprint(pdf: Path):
    bundle = SourceBundle(
        items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
        lecture_focus="",
        session_minutes=90,
    )
    profile = build_deterministic_source_profile(bundle, "unit grammar tests")
    return apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)


class TeachingMoveContractTests(unittest.TestCase):
    def test_every_teaching_slot_has_a_named_move(self):
        self.assertEqual(sorted(_MOVE_FOR_SLOT), list(range(6, 16)))

    def test_each_slot_owns_a_distinct_move(self):
        self.assertEqual(len(set(_MOVE_FOR_SLOT.values())), len(_MOVE_FOR_SLOT))

    def test_every_mapped_move_exists(self):
        for slot, name in _MOVE_FOR_SLOT.items():
            self.assertIn(name, _MOVES_BY_NAME, f"slot {slot} maps to unknown move {name!r}")

    def test_contracted_slots_keep_their_contracted_move(self):
        # prompts.py section 10: slot 8 owes an alternative and its trade-off,
        # slot 9 owes measurement and falsification, slot 15 owes an audit.
        self.assertEqual(_MOVE_FOR_SLOT[8], "alternative")
        self.assertEqual(_MOVE_FOR_SLOT[9], "evidence")
        self.assertEqual(_MOVE_FOR_SLOT[15], "verification")


class NounPhraseTests(unittest.TestCase):
    def test_interrogative_heading_is_reduced_to_its_subject(self):
        # "How does What is dependability actually work" was shipping to learners.
        self.assertEqual(_as_noun_phrase("What is dependability"), "dependability")
        self.assertEqual(_as_noun_phrase("Why do systems fail?"), "systems fail")

    def test_plain_heading_is_untouched(self):
        self.assertEqual(_as_noun_phrase("10.5 Formal methods"), "10.5 Formal methods")

    def test_reduction_is_refused_when_nothing_substantive_survives(self):
        self.assertEqual(_as_noun_phrase("What is it"), "What is it")


class TitleLikeTests(unittest.TestCase):
    def test_two_word_heading_is_accepted(self):
        # The old three-word floor rejected this and took the body line below it.
        self.assertTrue(_is_title_like("Cost/dependability curve"))

    def test_wrapped_body_line_is_rejected(self):
        self.assertFalse(_is_title_like("Because of very high costs of"))
        self.assertFalse(_is_title_like("dependability achievement, it"))

    def test_sentence_continuation_is_rejected(self):
        self.assertFalse(_is_title_like("representation and analysis"))


class FillRowTests(unittest.TestCase):
    class Row:
        def __init__(self, label, why=""):
            self.label = label
            self.why_important = why

    def test_holes_take_checkpoints_no_slot_already_owns(self):
        owned = self.Row("owned", "x" * 10)
        spare_a = self.Row("spare-a", "y" * 40)
        spare_b = self.Row("spare-b", "z" * 20)
        rows = [owned, spare_a, spare_b]
        groups = [[owned], [], []]
        fill = _fill_rows(groups, rows)
        self.assertEqual([r.label for r in fill], ["spare-a", "spare-b"])

    def test_repeats_are_spread_when_material_runs_out(self):
        a, b = self.Row("a", "aa"), self.Row("b", "bb")
        groups = [[a], [b], [], []]
        fill = _fill_rows(groups, [a, b])
        self.assertEqual(len(fill), 2)
        self.assertEqual(len({id(r) for r in fill}), 2, "both holes took the same row")

    def test_no_holes_needs_no_fill(self):
        a = self.Row("a", "aa")
        self.assertEqual(_fill_rows([[a]], [a]), [])


class RenderedGrammarTests(unittest.TestCase):
    """The contract has to survive the whole build, not just the helpers."""

    @classmethod
    def setUpClass(cls):
        pdf = LECTURES / "CPIT455-class2-NooR.pdf"
        if not pdf.exists():  # pragma: no cover - source bundle not checked out
            raise unittest.SkipTest(f"missing reference lecture {pdf}")
        cls.units = _blueprint(pdf).units

    def teaching(self):
        return self.units[5:15]

    def test_every_teaching_unit_asks_a_different_question(self):
        questions = [u.engineering_question for u in self.teaching()]
        self.assertEqual(len(set(questions)), 10, f"repeated questions: {questions}")

    def test_the_generic_template_is_gone(self):
        for u in self.teaching():
            self.assertNotIn("change the engineering decision", u.engineering_question)

    def test_every_teaching_unit_sets_a_different_task(self):
        actions = [u.student_action for u in self.teaching()]
        self.assertEqual(len(set(actions)), 10, f"repeated actions: {actions}")

    def test_no_checkpoint_is_taught_three_times(self):
        anchors = [u.source_anchor for u in self.teaching()]
        worst = max(anchors.count(a) for a in set(anchors))
        self.assertLessEqual(worst, 2, f"a checkpoint fills too many slots: {anchors}")

    def test_no_unit_title_is_a_mid_sentence_fragment(self):
        tail = {"of", "for", "to", "the", "a", "an", "and", "or", "in",
                "on", "at", "by", "with", "from", "that", "is", "are"}
        for u in self.units:
            last = u.title.strip().rstrip(":").split()[-1].lower()
            self.assertNotIn(last, tail, f"unit {u.number} title trails off: {u.title!r}")

    def test_questions_do_not_stack_two_interrogatives(self):
        for u in self.teaching():
            self.assertNotRegex(
                u.engineering_question,
                r"(?i)\b(how|what|where|why|when)\b[^?]*\bwhat is\b",
                f"unit {u.number}: {u.engineering_question!r}",
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()


class ThinSourceTests(unittest.TestCase):
    """A source with nothing to teach must say so, not ship a full deck quietly."""

    @classmethod
    def setUpClass(cls):
        cls.thin = LECTURES / "CPIT455-Into-story-NooR.pdf"
        cls.real = LECTURES / "CPIT455-class1-NooR.pdf"
        for p in (cls.thin, cls.real):
            if not p.exists():  # pragma: no cover - source bundle not checked out
                raise unittest.SkipTest(f"missing reference lecture {p}")

    @staticmethod
    def _profile_and_checks(pdf: Path):
        from app.gate_v14 import deterministic_gate

        bundle = SourceBundle(
            items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
            lecture_focus="",
            session_minutes=90,
        )
        profile = build_deterministic_source_profile(bundle, "thin source tests")
        bp = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
        return profile, deterministic_gate(bp, profile, bundle.combined_local_text())

    def test_a_syllabus_header_fails_the_named_check(self):
        # Two pages of course metadata previously produced twenty units and
        # reported scope_fit FIT, with no check naming the real problem.
        _, checks = self._profile_and_checks(self.thin)
        self.assertIn("v14_source_supports_ten_teaching_units", checks)
        self.assertFalse(checks["v14_source_supports_ten_teaching_units"])

    def test_a_syllabus_header_warns_in_words_faculty_can_act_on(self):
        profile, _ = self._profile_and_checks(self.thin)
        warnings = [w for w in profile.source_warnings if "SOURCE TOO THIN" in w]
        self.assertTrue(warnings, "no thin-source warning was emitted")
        self.assertIn("syllabus", warnings[0].lower())

    def test_the_thinnest_real_lecture_still_passes(self):
        # class1 yields four major checkpoints - the floor must not catch it.
        profile, checks = self._profile_and_checks(self.real)
        self.assertTrue(checks["v14_source_supports_ten_teaching_units"])
        self.assertFalse([w for w in profile.source_warnings if "SOURCE TOO THIN" in w])
