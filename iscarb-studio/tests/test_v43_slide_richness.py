from __future__ import annotations

import unittest
from pathlib import Path

from app.cimt_native_v43 import _source_first_items
from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.gate_v14 import deterministic_gate as gate_v14
from app.models import LectureUnit, VisualPlan
from app.session_gate import apply_90_minute_timebox
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile

LECTURES = Path(__file__).resolve().parents[2] / "lectures" / "cimt"
MIN_BOXES = 3


def _unit(number: int, core: list[str], pedagogy: list[str]) -> LectureUnit:
    return LectureUnit(
        number=number, phase="MARIS", title="Mechanism", engineering_question="Why?",
        core_content=core, pedagogy_content=pedagogy, knowledge_types=["CONCEPT"],
        visual_suggestion="process", visual_plan=VisualPlan(visual_type="process", teaching_purpose="p"),
        student_action="Do the thing.", takeaway="The point.", cimtlens=["C"], clo_ids=["CLO1"],
        planned_minutes=5,
    )


class ScaffoldingReachesTheSlideTests(unittest.TestCase):
    """Scaffolding used to be dropped whenever a unit had any source content, so a
    unit with one source line rendered as a single oversized box."""

    def test_scaffolding_is_shown_beside_source_content(self):
        unit = _unit(7, ["Reliability is the probability of failure-free operation."],
                     ["Trace the mechanism step by step.", "Name the step that fails first.",
                      "State the evidence that would refute you."])
        items = _source_first_items(unit)
        self.assertGreaterEqual(len(items), 4, f"scaffolding was dropped: {items}")

    def test_source_content_still_leads_the_slide(self):
        unit = _unit(7, ["SOURCE CLAIM: the mechanism as the chapter states it."],
                     ["ISCARB scaffolding step."])
        items = _source_first_items(unit)
        self.assertIn("mechanism as the chapter states it", items[0][1])

    def test_scaffolding_is_labelled_so_it_is_not_read_as_a_source_claim(self):
        unit = _unit(7, ["A source line."], ["A bare scaffolding line with no heading of its own."])
        labels = [label for label, _ in _source_first_items(unit)]
        self.assertTrue(any(label.startswith("ISCARB STEP") for label in labels), labels)

    def test_a_unit_without_source_content_still_renders(self):
        unit = _unit(17, [], ["Only scaffolding here.", "And a second step."])
        self.assertEqual(len(_source_first_items(unit)), 2)


class ArchivedDeckRichnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decks = []
        for pdf in sorted(LECTURES.glob("*.pdf")):
            bundle = SourceBundle(
                items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
                lecture_focus="", session_minutes=90,
            )
            profile = build_deterministic_source_profile(bundle, "richness regression")
            blueprint = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
            cls.decks.append((pdf.name, blueprint, profile, bundle.combined_local_text()))

    def test_no_source_teaching_slide_is_one_oversized_box(self):
        for name, bp, _profile, _text in self.decks:
            with self.subTest(lecture=name):
                for unit in bp.units[5:15]:
                    drawn = len(_source_first_items(unit))
                    self.assertGreaterEqual(
                        drawn, MIN_BOXES,
                        f"unit {unit.number} ({unit.title[:40]}) draws {drawn} box(es)",
                    )

    def test_density_gate_counts_items_not_only_words(self):
        """One long sentence clears any word floor and is still a single box."""
        _name, bp, profile, text = self.decks[-1]
        self.assertTrue(gate_v14(bp, profile, text).get("v14_technical_units_have_teaching_density"))

        wordy = bp.model_copy(deep=True)
        target = wordy.units[7]
        target.core_content = [" ".join(["reliability"] * 40)]
        target.pedagogy_content = []
        if target.visual_plan:
            target.visual_plan.source_visual_available = False
        self.assertFalse(
            gate_v14(wordy, profile, text).get("v14_technical_units_have_teaching_density"),
            "a 40-word single box still passes the density rule",
        )


if __name__ == "__main__":
    unittest.main()


class PromptGranularityContractTests(unittest.TestCase):
    """The unit functions named structured elements but never said they must be
    separate entries, so the model collapsed each into one prose line and the
    teaching span rendered as ten single-box slides."""

    @classmethod
    def setUpClass(cls):
        from app import prompts
        cls.master = prompts.MASTER_PROMPT

    def test_structured_functions_must_become_separate_entries(self):
        self.assertIn("EACH named element is its OWN core_content entry", self.master)

    def test_teaching_span_has_a_minimum_visible_entry_count(self):
        self.assertIn("Units 6-15 MUST each carry at least three learner-visible entries", self.master)

    def test_thin_sources_are_scaffolded_rather_than_padded(self):
        """Reaching the count by inventing source content would be worse than a
        sparse slide, so the contract has to forbid it explicitly."""
        self.assertIn("Never pad", self.master)
        self.assertIn("the source does not support", self.master)

    def test_the_count_matches_what_the_gate_enforces(self):
        from app.gate_v14 import MIN_TEACHING_ITEMS
        self.assertEqual(MIN_TEACHING_ITEMS, 3, "prompt and gate disagree on the floor")
