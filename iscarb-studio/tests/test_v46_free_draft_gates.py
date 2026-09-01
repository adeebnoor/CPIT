"""The free, no-API draft has to clear its own gates.

Every deterministic check the free path fails is a check no faculty member can
clear: there is no model in the loop to repair the draft. The audit panel showed
fifty-one of them, dominated by metadata the builder never filled in and by
slides the renderer could not project. These tests hold that closed.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from app import main as engine
from app.deterministic_blueprint_fallback import fit_presenter_text
from app.presenter_v44 import readability_problems, unit_layout, wrap
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import (
    _furniture_keys,
    _recurring_furniture,
    build_deterministic_source_profile,
)
from app.session_gate import session_scope_gate
from app.unit_contract import TAG_OWNERS

LECTURES = Path(__file__).resolve().parents[2] / "lectures" / "cimt"

# Checks the free draft cannot clear on its own, and why:
#  - the three official-ETEC map checks: a locally derived trail never prints an
#    approved SKU/SLO mapping (see test_v43_readiness_and_density), so they fail
#    by design unless the source's own vocabulary triggers the security mapping;
#  - the source-property checks: a two-page syllabus or a one-line slide really
#    cannot fill a teaching slot, and the gate is supposed to say so.
BY_DESIGN = {
    "readiness_refs_exist_in_etec_profile",
    "readiness_exact_official_slo_klo_map",
    "v10_readiness_official_map_exact",
    "no_unresolved_verify_flags",
    "v14_source_supports_ten_teaching_units",
    "v15_complete_20_unit_grammar",
    "v15_unit02_job_is_visible",
    "v15_technical_units_retain_source_detail",
}


def _serve():
    """Wire the served engine (gate v15 + normalizers) at call time.

    Importing it at module scope would rebind the shared engine during
    collection, and the v4.3 suites that import their own served app would then
    assert against this one.
    """
    from app import start_v440  # noqa: F401
    return engine


def _draft(pdf: Path):
    engine_ = _serve()
    bundle = SourceBundle(
        items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
        lecture_focus="", session_minutes=90,
    )
    profile = build_deterministic_source_profile(bundle)
    blueprint = engine_._source_preserving_draft(profile, bundle)
    checks = engine_.deterministic_gate(blueprint, profile, bundle.combined_local_text())
    checks.update(session_scope_gate(blueprint, profile, bundle))
    return profile, blueprint, checks


def _uncondensed(pdf: Path):
    """The same draft before the condensing pass, to compare what it removed."""
    from app.deterministic_blueprint_fallback import build_deterministic_blueprint
    engine_ = _serve()
    bundle = SourceBundle(
        items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
        lecture_focus="", session_minutes=90,
    )
    profile = build_deterministic_source_profile(bundle)
    return engine_.apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)


class FreeDraftGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.drafts = [(p.name, *_draft(p)) for p in sorted(LECTURES.glob("*.pdf"))]
        if not cls.drafts:
            raise unittest.SkipTest("no archived lecture available")

    def test_no_free_draft_fails_a_check_it_could_have_satisfied(self):
        for name, _profile, _bp, checks in self.drafts:
            with self.subTest(lecture=name):
                unexpected = sorted(k for k, v in checks.items() if v is False and k not in BY_DESIGN)
                self.assertEqual(unexpected, [], f"{name} fails checks the builder should satisfy")

    def test_every_unit_records_the_obligations_its_slot_owns(self):
        for name, _profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                for unit in bp.units:
                    owned = {tag for tag, owner in TAG_OWNERS.items() if owner == unit.number}
                    recorded = set(unit.inherited_requirements) | set(unit.elite_requirements)
                    self.assertEqual(owned, recorded, f"unit {unit.number} obligations")

    def test_the_whole_cimt_compass_is_used(self):
        for name, _profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                lenses = {lens for unit in bp.units for lens in unit.cimtlens}
                self.assertEqual(lenses, {"C", "I", "M", "T"})

    def test_only_a_reused_checkpoint_is_flagged_for_review(self):
        """The flag marks a real unresolved decision, not the draft's status."""
        for name, _profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                for unit in bp.units:
                    if unit.verify_before_release:
                        self.assertTrue(6 <= unit.number <= 15, f"unit {unit.number} flagged without a teaching slot")

    def test_the_spine_declares_every_locked_family(self):
        for name, profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                families = [x.name for x in profile.topic_families]
                self.assertEqual(bp.source_topic_families, families)
                self.assertEqual([x.topic_family for x in bp.topic_coverage], families)

    def test_every_teaching_slide_is_projectable(self):
        for name, _profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                self.assertEqual(sorted(readability_problems(bp)), [])

    def test_condensing_never_hollows_a_teaching_slide(self):
        """A slot the source could fill still meets the teaching floor afterwards.

        A slot the source could not fill (a slide carrying nine words) stays thin,
        and the gate reports that as the source property it is.
        """
        for name, _profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                before = _uncondensed(LECTURES / name)
                for unit in bp.units[5:15]:
                    self.assertTrue(unit.core_content, f"unit {unit.number} lost its source content")
                    original = sum(len(str(x).split()) for x in before.units[unit.number - 1].core_content)
                    core_words = sum(len(str(x).split()) for x in unit.core_content)
                    payload = core_words + sum(len(str(x).split()) for x in unit.pedagogy_content)
                    if original >= 12:
                        self.assertGreaterEqual(core_words, 12, f"unit {unit.number} core")
                        self.assertGreaterEqual(payload, 28, f"unit {unit.number} payload")

    def test_a_condensed_slide_records_where_the_checkpoint_continues(self):
        """Merging keeps every word; only a slide that stopped short says so."""
        for name, _profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                before = _uncondensed(LECTURES / name)
                for unit in bp.units[5:15]:
                    original = sum(len(str(x).split()) for x in before.units[unit.number - 1].core_content)
                    kept = sum(len(str(x).split()) for x in unit.core_content)
                    if kept < original:
                        self.assertIn("stays in the source at", unit.evidence,
                                      f"unit {unit.number} was trimmed without saying so")


class SourceFidelityTests(unittest.TestCase):
    """What the deck says about the lecture has to match the lecture."""

    @classmethod
    def setUpClass(cls):
        cls.pdf = LECTURES / "CPIT455-class2-NooR.pdf"
        if not cls.pdf.exists():
            raise unittest.SkipTest("archived lecture unavailable")
        cls.profile, cls.bp, _checks = _draft(cls.pdf)

    def test_the_title_is_the_subject_not_the_session_number(self):
        """"Class2: Dependable Systems" would travel into every derived sentence."""
        self.assertEqual(self.profile.lecture_title, "Dependable Systems")
        self.assertNotIn("class2", self.bp.central_engineering_crisis.lower())
        self.assertNotIn("class2", self.bp.units[0].title.lower())

    def test_the_outcome_the_source_declares_is_the_first_clo(self):
        self.assertEqual(
            self.bp.clOs[0].statement,
            "Design dependability in systems by using redundancy and diversity",
        )
        self.assertIn("PAGE 3", self.bp.clOs[0].evidence_expected)

    def test_the_prediction_gate_does_not_preempt_the_units_that_teach(self):
        """Unit 5 asks for a prediction; it must not print Unit 6 and 7's pages."""
        gate = set(self.bp.units[4].core_content)
        for number in (6, 7):
            taught = set(self.bp.units[number - 1].core_content)
            self.assertFalse(gate & taught, f"unit 5 reprints unit {number}")
        self.assertTrue(self.bp.units[4].core_content, "the prediction gate lost its source framing")

    def test_the_spine_names_the_pages_it_maps(self):
        """A bare [P1] let the visual planner illustrate the spine with any page."""
        from app.source_visuals import anchor_slides
        spine = anchor_slides(self.bp.units[1].source_anchor)
        self.assertTrue(spine)
        self.assertTrue(set(spine) <= {
            page for family in self.profile.topic_families
            for page in anchor_slides(family.source_anchor)
        })

    def test_a_teaching_unit_keeps_the_single_page_anchor_its_figure_needs(self):
        """A multi-page anchor forfeits the source figure; one page per slot."""
        from app.source_visuals import anchor_slides
        single = [u.number for u in self.bp.units[5:15] if len(anchor_slides(u.source_anchor)) == 1]
        self.assertGreaterEqual(len(single), 9, "teaching slots lost their source pages")


class RunningHeaderTests(unittest.TestCase):
    """A chapter header repeats with only its page number changing."""

    def _deck(self, header):
        return [
            (i, f"{header} {366 + i}", f"{header} {366 + i} · Section statement {i} with enough words to teach")
            for i in range(1, 19)
        ]

    def test_a_header_wearing_a_page_number_is_still_one_line(self):
        found = _recurring_furniture(self._deck("Chapter 14 I Security engineering"))
        self.assertTrue(_furniture_keys("Chapter 14 I Security engineering 367") & found)
        self.assertTrue(_furniture_keys("392 Chapter 14 I Security engineering") & found)

    def test_a_numbered_content_line_is_not_chrome(self):
        """The number is part of what the line says, not a page coordinate."""
        deck = [
            (i, f"Step {i}", f"Step {i} · Body sentence number {i} with enough words")
            for i in range(1, 19)
        ]
        found = _recurring_furniture(deck)
        self.assertFalse(_furniture_keys("Body sentence number 4 with enough words") & found)


class LongTokenWrapTests(unittest.TestCase):
    """A source page that cites a link must not drop the slide to 10pt."""

    URL = ("https://softwaredominos.com/home/software-design-development-articles/"
           "part-6-component-based-software-engineering-15-questions-and-answers")

    def test_a_link_is_broken_across_lines_instead_of_running_off_the_page(self):
        lines = wrap(f"Component models {self.URL}", 418, 16)
        self.assertTrue(len(lines) > 1)
        self.assertEqual("".join(lines).replace(" ", ""), f"Component models {self.URL}".replace(" ", ""))

    def test_a_pathological_token_still_trips_the_overflow_guard(self):
        from app.presenter_v44 import _overflows, item_layout
        blocks, _size, fits = item_layout([("", "X" * 2000)], 44, 166, 872, 278)
        self.assertFalse(fits)
        self.assertTrue(_overflows(blocks))


if __name__ == "__main__":
    unittest.main()
