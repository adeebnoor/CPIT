from __future__ import annotations

import unittest
from pathlib import Path

from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.gate_v14 import deterministic_gate as gate_v14
from app.session_gate import apply_90_minute_timebox
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile

LECTURES = Path(__file__).resolve().parents[2] / "lectures" / "cimt"


def _build(pdf: Path):
    bundle = SourceBundle(
        items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)],
        lecture_focus="",
        session_minutes=90,
    )
    profile = build_deterministic_source_profile(bundle, "readiness regression")
    blueprint = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
    checks = gate_v14(blueprint, profile, bundle.combined_local_text())
    return blueprint, checks


class ReadinessEvidenceTrailTests(unittest.TestCase):
    """The fallback used to publish readiness_alignment = [], which showed faculty
    nothing about what the lecture can and cannot evidence."""

    @classmethod
    def setUpClass(cls):
        cls.results = [(p.name, *_build(p)) for p in sorted(LECTURES.glob("*.pdf"))]

    def test_every_lecture_carries_a_readiness_trail(self):
        for name, bp, _checks in self.results:
            with self.subTest(lecture=name):
                self.assertTrue(bp.readiness_alignment, "readiness trail is empty")

    def test_trail_points_at_units_that_actually_produce_an_artifact(self):
        for name, bp, _checks in self.results:
            with self.subTest(lecture=name):
                for alignment in bp.readiness_alignment:
                    self.assertTrue(alignment.evidence_units)
                    for n in alignment.evidence_units:
                        unit = bp.units[n - 1]
                        self.assertTrue(unit.evidence.strip(), f"unit {n} claims evidence but records none")
                        self.assertTrue(unit.student_action.strip(), f"unit {n} has no learner action")

    def test_readiness_gate_checks_pass_on_the_trail(self):
        for name, _bp, checks in self.results:
            with self.subTest(lecture=name):
                for key in (
                    "readiness_alignment_present",
                    "v11_readiness_trace_visible",
                    "v14_readiness_is_evidence_backed",
                ):
                    self.assertTrue(checks.get(key), f"{key} still fails")

    def test_trail_never_claims_an_approved_etec_mapping(self):
        """A locally derived trail must not read as standardized alignment."""
        for name, bp, _checks in self.results:
            with self.subTest(lecture=name):
                for alignment in bp.readiness_alignment:
                    self.assertEqual(alignment.strength, "supporting")
                    joined = " ".join([*alignment.slo_refs, *alignment.klo_refs, alignment.sku]).upper()
                    self.assertIn("UNVERIFIED", joined, "an unapproved mapping is presented as approved")


class PresenterDensityTests(unittest.TestCase):
    """A slide holding one sentence in a large box is a blank teaching minute."""

    @classmethod
    def setUpClass(cls):
        cls.results = [(p.name, *_build(p)) for p in sorted(LECTURES.glob("*.pdf"))]

    def test_no_unit_is_a_near_empty_slide(self):
        for name, bp, _checks in self.results:
            with self.subTest(lecture=name):
                for unit in bp.units:
                    words = sum(len(str(x).split()) for x in (*unit.core_content, *unit.pedagogy_content))
                    self.assertGreaterEqual(
                        words, 12, f"unit {unit.number} ({unit.title[:40]}) carries {words} words"
                    )

    def test_a_source_visual_no_longer_exempts_a_unit_from_teaching(self):
        # The density rule only engages for a source rich enough to fill the
        # teaching span, so this needs a chapter deck, not a kickoff deck.
        for pdf in sorted(LECTURES.glob("*.pdf")):
            bundle = SourceBundle(
                items=[SourceItem("primary", "P1", pdf.name, pdf, pdf.name)], lecture_focus="", session_minutes=90
            )
            profile = build_deterministic_source_profile(bundle, "density regression")
            if len([x for x in profile.coverage_items if x.importance == "major"]) >= 6:
                break
        else:
            self.skipTest("no archived lecture has enough major checkpoints")

        blueprint = apply_90_minute_timebox(build_deterministic_blueprint(profile), profile, bundle)
        source_text = bundle.combined_local_text()
        self.assertTrue(
            gate_v14(blueprint, profile, source_text).get("v14_technical_units_have_teaching_density") is not None
        )

        thin = blueprint.model_copy(deep=True)
        target = thin.units[7]
        target.core_content = ["One short line."]
        target.pedagogy_content = []
        if target.visual_plan:
            target.visual_plan.source_visual_available = True
        checks = gate_v14(thin, profile, source_text)
        self.assertFalse(
            checks.get("v14_technical_units_have_teaching_density"),
            "a source image still exempts an empty unit from teaching",
        )

    def test_learner_activities_are_specific_not_one_repeated_sentence(self):
        for name, bp, _checks in self.results:
            with self.subTest(lecture=name):
                actions = [u.student_action for u in bp.units[5:15]]
                self.assertGreater(len(set(actions)), 4, "the TRY activity is boilerplate across the deck")


if __name__ == "__main__":
    unittest.main()
