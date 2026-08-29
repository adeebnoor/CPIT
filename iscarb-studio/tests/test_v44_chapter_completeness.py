from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.deterministic_blueprint_fallback import build_deterministic_blueprint
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile
from app.cimt_native_v43 import export_cimt_presenter_pdf_v43, export_cimt_presenter_pptx_v43, render_cimt_presenter_preview_v43
from app import prompts
from app.main import _ensure_quota_safe_completeness, _major_coverage_gaps


class ChapterCompletenessV44Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lecture_dir = Path(__file__).resolve().parents[2] / 'lectures' / 'cimt'

    def _profile(self, class_no: int):
        path = self.lecture_dir / f'CPIT455-class{class_no}-NooR.pdf'
        bundle = SourceBundle(items=[SourceItem('primary','P1',path.name,path,path.name)], lecture_focus='', session_minutes=90)
        return build_deterministic_source_profile(bundle)

    def test_numbered_chapter_sections_are_major_checkpoints(self):
        expected = {
            2: ['10.1','10.2','10.3','10.4','10.5'],
            3: ['11.1','11.2','11.3','11.4','11.5'],
            4: ['12.1','12.2','12.3','12.4'],
            5: ['13.1','13.2','13.3','13.4','13.5'],
            6: ['14.1','14.2','14.3'],
            7: ['15.1','15.2','15.3','15.4'],
            8: ['16.1','16.2','16.3'],
            9: ['17.1','17.2','17.3','17.4'],
        }
        for class_no, sections in expected.items():
            labels = ' '.join(x.label for x in self._profile(class_no).coverage_items if x.importance == 'major')
            for section in sections:
                self.assertIn(section, labels, f'class {class_no} missing {section}')

    def test_quota_safe_draft_covers_every_major_checkpoint_by_unit15(self):
        for class_no in range(2,10):
            profile = self._profile(class_no)
            bp = build_deterministic_blueprint(profile)
            major = {x.id for x in profile.coverage_items if x.importance == 'major'}
            ledger = {x.coverage_id: x for x in bp.coverage_ledger}
            self.assertEqual(len(bp.units), 20)
            self.assertEqual(sum(u.planned_minutes for u in bp.units), 90)
            self.assertTrue(major.issubset(ledger))
            self.assertTrue(all(ledger[x].first_taught_unit <= 15 for x in major))
            self.assertEqual(bp.readiness_alignment, [])
            self.assertIn('UNVERIFIED', ' '.join(bp.units[18].pedagogy_content).upper())

    def test_quota_during_repair_replaces_incomplete_semantic_draft_with_complete_blocked_draft(self):
        profile = self._profile(2)
        path = self.lecture_dir / 'CPIT455-class2-NooR.pdf'
        bundle = SourceBundle(items=[SourceItem('primary','P1',path.name,path,path.name)], lecture_focus='', session_minutes=90)
        incomplete = build_deterministic_blueprint(profile).model_copy(deep=True)
        major_ids = [x.id for x in profile.coverage_items if x.importance == 'major']
        incomplete.coverage_ledger = [x for x in incomplete.coverage_ledger if x.coverage_id not in set(major_ids[:4])]
        missing, late = _major_coverage_gaps(incomplete, profile)
        self.assertTrue(missing)
        self.assertFalse(late)
        repaired, checks, audit, replaced, original_missing, original_late = _ensure_quota_safe_completeness(
            incomplete, profile, bundle, bundle.combined_local_text(), 'RESOURCE_EXHAUSTED quota exceeded'
        )
        self.assertTrue(replaced)
        self.assertEqual(set(original_missing), set(missing))
        self.assertEqual(original_late, [])
        self.assertEqual(_major_coverage_gaps(repaired, profile), ([], []))
        self.assertEqual(len(repaired.units), 20)
        self.assertEqual(sum(u.planned_minutes for u in repaired.units), 90)
        self.assertEqual(repaired.readiness_alignment, [])
        self.assertFalse(audit.overall_pass)
        self.assertIsInstance(checks, dict)

    def test_quota_during_repair_preserves_already_complete_semantic_draft(self):
        profile = self._profile(2)
        path = self.lecture_dir / 'CPIT455-class2-NooR.pdf'
        bundle = SourceBundle(items=[SourceItem('primary','P1',path.name,path,path.name)], lecture_focus='', session_minutes=90)
        complete = build_deterministic_blueprint(profile)
        result, checks, audit, replaced, missing, late = _ensure_quota_safe_completeness(
            complete, profile, bundle, bundle.combined_local_text(), 'quota exhausted'
        )
        self.assertFalse(replaced)
        self.assertIs(result, complete)
        self.assertEqual((missing, late), ([], []))
        self.assertFalse(audit.overall_pass)
        self.assertIsInstance(checks, dict)

    def test_all_archived_chapters_render_20_slide_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            for class_no in range(2,10):
                bp = build_deterministic_blueprint(self._profile(class_no))
                html = render_cimt_presenter_preview_v43(bp, 'BLOCKED')
                self.assertEqual(html.count('class="slide'), 20)
                self.assertIn('learningStrip', html)
                pdf = export_cimt_presenter_pdf_v43(bp, td / f'c{class_no}.pdf')
                pptx = export_cimt_presenter_pptx_v43(bp, td / f'c{class_no}.pptx')
                self.assertGreater(pdf.stat().st_size, 10000)
                self.assertGreater(pptx.stat().st_size, 20000)

    def test_prompt_contract_contains_all_inherited_and_elite_requirements(self):
        master = prompts.MASTER_PROMPT
        for n in range(1,15): self.assertIn(f'IDR-{n}', master)
        for n in range(1,13): self.assertIn(f'EER-{n}', master)
        for n in range(1,21): self.assertIn(f'UNIT {n}', master)
        self.assertIn('CHAPTER COMPLETENESS PROOF', master)
        self.assertIn('CIMT × LEARN-BY-DOING CLASSROOM CHOREOGRAPHY', master)
        self.assertIn('READINESS AS EVIDENCE, NOT DECORATION', master)


if __name__ == '__main__':
    unittest.main()
