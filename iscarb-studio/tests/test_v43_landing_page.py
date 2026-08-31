"""The faculty landing page is the first thing a lecturer sees.

These are static assertions on the served markup rather than browser tests, so
they run in CI without a browser. They pin defects found by rendering the page:
form controls with no accessible name, a nav link pointing at a hidden element,
and a card styled with the dark base palette while the KAU skin is active.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "iscarb-studio/app/static/index_v410.html"
SKIN = ROOT / "iscarb-studio/app/static/kau_identity_v410.css"


class FormAccessibilityTests(unittest.TestCase):
    """Every compile control had a bare <label>, so nothing announced a name."""

    CONTROLS = ["primaryFile", "primaryUrl", "supportFiles", "supportUrls",
                "focus", "model", "repair"]

    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_every_control_has_a_label_bound_to_it(self):
        for control in self.CONTROLS:
            self.assertIn(f'<label for="{control}">', self.html,
                          f"{control} has no label bound to it")

    def test_every_labelled_control_actually_exists(self):
        for control in re.findall(r'<label for="([^"]+)"', self.html):
            self.assertRegex(self.html, rf'id="{re.escape(control)}"',
                             f"label points at missing control {control!r}")

    def test_no_bare_labels_remain(self):
        self.assertNotIn("<label>", self.html)


class OutputsSectionTests(unittest.TestCase):
    """The nav promised Outputs; the only #outputs was hidden until a compile."""

    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_outputs_is_a_standalone_section(self):
        self.assertIn('<section class="section" id="outputs">', self.html)

    def test_the_results_grid_no_longer_claims_that_id(self):
        self.assertIn('class="assets" id="outputAssets"', self.html)
        self.assertNotIn('class="assets" id="outputs"', self.html)

    def test_the_script_writes_to_the_renamed_grid(self):
        self.assertIn("getElementById('outputAssets')", self.html)
        self.assertNotIn("getElementById('outputs')", self.html)

    def test_no_element_id_is_used_twice(self):
        ids = re.findall(r'\sid="([^"]+)"', self.html)
        self.assertEqual(sorted(ids), sorted(set(ids)), "duplicate element id")

    def test_every_in_page_nav_link_has_a_target(self):
        for href in re.findall(r'<a href="#([^"]+)"', self.html):
            self.assertRegex(self.html, rf'id="{re.escape(href)}"',
                             f"nav link #{href} has no target")


class SkinConsistencyTests(unittest.TestCase):
    """A new card must follow the active skin, not the dark base literals."""

    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.css = SKIN.read_text(encoding="utf-8")

    def test_deliverable_cards_use_theme_tokens(self):
        rule = re.search(r"\.deliverable\{[^}]*\}", self.html)
        self.assertIsNotNone(rule, "no .deliverable rule in the base stylesheet")
        body = rule.group(0)
        self.assertIn("var(--panel)", body)
        self.assertIn("var(--line)", body)
        self.assertNotRegex(body, r"#[0-9a-fA-F]{3,6}",
                            "hard-coded colour would ignore the active skin")

    def test_the_skin_whitens_the_new_card_with_its_siblings(self):
        block = re.search(r"((?:\.[\w-]+,\s*)+\.[\w-]+)\s*\{\s*background:rgba\(255,255,255,\.93\)", self.css)
        self.assertIsNotNone(block, "card background group not found in the skin")
        self.assertIn(".deliverable", block.group(1))

    def test_small_labels_clear_wcag_aa_on_white(self):
        # --kau-green (#208D44) on white measures 4.24:1 at 9px; AA needs 4.5.
        for selector in (".source small", ".deliverable small"):
            self.assertIn(f"{selector}{{color:var(--kau-deep-green)!important}}", self.css)


class HeroScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_headline_does_not_dominate_the_fold(self):
        # 7.2vw rendered the headline at 104px on a 1440 viewport, pushing the
        # lead, the CTAs and the contract card below the fold.
        match = re.search(r"\.hero h1\{font-size:clamp\(([^)]+)\)", self.html)
        self.assertIsNotNone(match)
        viewport_step = re.search(r"([\d.]+)vw", match.group(1))
        self.assertIsNotNone(viewport_step)
        self.assertLessEqual(float(viewport_step.group(1)), 5.0)

    def test_mobile_overflow_guards_survive(self):
        self.assertIn("html,body{max-width:100%;overflow-x:hidden}", self.html)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
