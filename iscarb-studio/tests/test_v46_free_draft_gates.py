"""The free, no-API draft has to clear its own gates.

Every deterministic check the free path fails is a check no faculty member can
clear: there is no model in the loop to repair the draft. The audit panel showed
fifty-one of them, dominated by metadata the builder never filled in and by
slides the renderer could not project. These tests hold that closed.
"""
from __future__ import annotations

import tempfile
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

    def test_the_gate_and_the_exporter_agree(self):
        """A deck that clears every check has to be one the exporter will render."""
        from app.presenter_v44 import preflight_layout
        for name, _profile, bp, _checks in self.drafts:
            with self.subTest(lecture=name):
                preflight_layout(bp)

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


# A printed chapter, not a slide deck: running headers, numbered sections,
# multi-page prose and captioned vector figures. Built here rather than checked
# in, because the real textbook it stands for is not ours to redistribute.
SECTIONS = [
    ("13.1 Security risk management", [
        "Security risk assessment and management is essential for effective security engineering.",
        "Risk management is concerned with assessing the possible losses that might ensue from attacks.",
        "Preliminary risk assessment identifies generic risks that apply to a system and decides whether",
        "an adequate level of security can be achieved at a reasonable cost.",
        "Life-cycle risk assessment takes place during system development and is principally concerned",
        "with deriving the security requirements the delivered system has to satisfy in operation.",
    ]),
    ("13.2 Design for security", [
        "Architectural design decisions affect the security of an application in ways that are hard to",
        "reverse once the system has been built and deployed to its operational environment.",
        "Protection is organized as a layered architecture where each layer protects the assets behind it.",
        "Distribution decisions determine whether assets are located on a single or on several platforms.",
        "Distributing assets reduces the losses that may arise from a single successful attack, although",
        "it also increases the number of platforms an attacker may choose to target.",
    ]),
    ("13.3 System survivability", [
        "Survivability is the ability of a system to continue to deliver services whilst under attack.",
        "Survivability analysis identifies the critical services, the plausible attacks on them, and the",
        "components that an attacker could compromise to deny those services to legitimate users.",
        "Three complementary strategies for survivability are resistance, recognition and recovery.",
        "Recovery matters most when an attack has already succeeded and the loss must be contained.",
    ]),
]


# A printed page carries far more prose than a slide; the density is what tells
# the profiler it is reading a book rather than a deck.
BODY_LINES_PER_PAGE = 34


def _prose(lines: list[str], count: int) -> list[str]:
    """Distinct lines: the profiler drops repeats, and a page of repeats is thin."""
    openers = ["In practice,", "For this reason,", "As a result,", "In the same way,", "By contrast,", "More precisely,"]
    out = []
    while len(out) < count:
        opener = openers[len(out) // max(1, len(lines)) % len(openers)]
        line = lines[len(out) % len(lines)]
        out.append(f"{opener} {line[0].lower()}{line[1:]}" if len(out) >= len(lines) else line)
        if len(out) >= count:
            break
    return out


def _write_chapter(path: Path) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdf_canvas
    c = pdf_canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    page_no = 366

    def opener():
        c.setFont("Helvetica-Bold", 22)
        c.drawString(70, height - 120, "Security engineering")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(70, height - 170, "Objectives")
        c.setFont("Helvetica", 10)
        y = height - 195
        for line in [
            "The objective of this chapter is to introduce issues that should be considered when",
            "designing secure application systems. When you have read this chapter you will:",
            "understand the difference between application security and infrastructure security;",
            "know how security risk assessment is used in the specification of security requirements;",
            "be aware of a set of design guidelines for secure systems engineering;",
            "understand the notion of system survivability and be able to identify survivable services.",
        ]:
            c.drawString(70, y, line)
            y -= 16
        c.showPage()

    def header(number):
        c.setFont("Helvetica", 9)
        if number % 2:
            c.drawString(70, height - 60, f"{number} Chapter 13 I Security engineering")
        else:
            c.drawRightString(width - 70, height - 60, f"13.1 I Security risk management {number}")

    def body(lines, start_y):
        c.setFont("Helvetica", 10)
        y = start_y
        for line in lines:
            c.drawString(70, y, line)
            y -= 15
        return y

    opener()
    for index, (title, lines) in enumerate(SECTIONS):
        page_no += 1
        header(page_no)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(70, height - 110, title)
        y = body(_prose(lines, BODY_LINES_PER_PAGE - 6), height - 140)
        if index == 1:
            top = y - 30
            for column, label in enumerate(("Platform protection", "Application protection", "Record protection")):
                x = 150 + column * 130
                c.rect(x, top - 40, 110, 40)
                c.setFont("Helvetica", 8)
                c.drawCentredString(x + 55, top - 24, label)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(70, top - 70, "Figure 13.4")
            c.setFont("Helvetica", 9)
            c.drawString(130, top - 70, "A layered protection architecture")
        c.showPage()
        page_no += 1
        header(page_no)
        body(_prose(lines, BODY_LINES_PER_PAGE), height - 110)
        c.showPage()

    page_no += 1
    header(page_no)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(70, height - 110, "Key Points")
    c.setFont("Helvetica", 10)
    y = height - 140
    for line in [
        "Security engineering focuses on systems that can resist malicious attacks.",
        "Risk management assesses the losses that might follow an attack on the system.",
        "A layered protection architecture protects assets behind successive barriers.",
        "Survivability strategies are resistance, recognition and recovery.",
    ]:
        c.drawString(70, y, line)
        y -= 16
    c.showPage()
    c.save()
    return path


class BookChapterTests(unittest.TestCase):
    """A book chapter is not a slide deck; both have to compile."""

    @classmethod
    def setUpClass(cls):
        cls._dir = tempfile.TemporaryDirectory()
        cls.book = _write_chapter(Path(cls._dir.name) / "chapter.pdf")
        cls.profile, cls.bp, cls.checks = _draft(cls.book)

    @classmethod
    def tearDownClass(cls):
        cls._dir.cleanup()

    def test_the_chapter_compiles_without_avoidable_failures(self):
        unexpected = sorted(k for k, v in self.checks.items() if v is False and k not in BY_DESIGN)
        self.assertEqual(unexpected, [])

    def test_units_are_titled_with_the_chapters_own_sections(self):
        """Page chunking titled units with the first wrapped line of prose."""
        titles = " | ".join(u.title for u in self.bp.units[5:15])
        for section, _lines in SECTIONS:
            self.assertIn(section, titles, f"{section} is not taught under its own heading")

    def test_a_running_header_is_never_a_unit_heading(self):
        for unit in self.bp.units:
            self.assertNotIn("Chapter 13 I", unit.title)
            self.assertNotIn("13.1 I Security risk management", unit.title)

    def test_the_chapters_figure_reaches_the_deck(self):
        from app.source_visuals import FIGURE_KIND, load_registry
        registry = load_registry(self.bp, source_root=self.book)
        figures = [a for a in registry.assets if a.source_kind == FIGURE_KIND]
        self.assertTrue(figures, "the chapter's diagram was never cropped out of its page")
        self.assertTrue(figures[0].alt_text.startswith("Figure 13.4"), figures[0].alt_text[:60])
        from PIL import Image
        with Image.open(figures[0].local_path) as im:
            self.assertGreaterEqual(im.size[0], 1100, "the crop is too small to fill the canvas")

    def test_a_page_of_running_prose_never_fills_the_canvas(self):
        """Enlarged to the slide it is a wall of 10pt text, and it is not a figure."""
        from app.source_visuals import FIGURE_KIND, load_registry
        from app.source_visuals_v42 import _is_text_wall, _is_portrait
        registry = load_registry(self.bp, source_root=self.book)
        pages = [a for a in registry.assets if a.source_kind != FIGURE_KIND]
        self.assertTrue(all(_is_portrait(a) for a in pages), "a printed page should read as portrait")
        self.assertTrue(any(_is_text_wall(a) for a in pages), "prose pages are being offered as visuals")


class ClosingPointsTests(unittest.TestCase):
    """The lecture summarizes itself; that summary belongs in the closing unit."""

    def test_the_sources_own_take_home_points_close_the_deck(self):
        pdf = LECTURES / "CPIT455-class2-NooR.pdf"
        if not pdf.exists():
            self.skipTest("archived lecture unavailable")
        _profile, bp, _checks = _draft(pdf)
        closing = bp.units[19]
        self.assertIn("PAGE 3", closing.source_anchor)
        blob = " ".join(closing.core_content).lower()
        self.assertIn("redundancy and diversity improve system dependability", blob)


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
