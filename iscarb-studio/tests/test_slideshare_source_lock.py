import tempfile
import unittest
from pathlib import Path

from app.models import CoverageItem, SourceProfile, TopicFamily
from app.source_bundle import SourceBundle, SourceItem
from app.source_profile_fallback import build_deterministic_source_profile, reconcile_source_profile

class SlideShareSourceLockTests(unittest.TestCase):
    def _bundle(self):
        td=tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        p=Path(td.name)/'slideshare.txt'
        p.write_text("""1 / 58
SLIDE 1: Chapter 2 Software Processes
SLIDE 3: The software process A structured set of activities required to develop a software system specification design implementation validation evolution process model abstract representation perspective and workflow evidence
SLIDE 7: Software process models waterfall incremental development integration and configuration plan-driven agile large systems combine elements from all models with context and tradeoffs
SLIDE 20: Process activities Real software processes are inter-leaved sequences of technical collaborative and managerial activities specification development validation evolution waterfall sequence incremental interleaving and iteration
SLIDE 56: Key points Software processes are activities involved in producing a software system and general models include waterfall incremental and reuse-oriented development with change
Recommended
SLIDE 59: Ch2 SW Processes.pdf unrelated recommendation card software process models
SLIDE 60: Another recommended presentation software process models
""",encoding='utf-8')
        return SourceBundle(items=[SourceItem('primary','P1','slideshare',p,'slideshare')],lecture_focus='',session_minutes=90)

    def _semantic(self):
        return SourceProfile(
            lecture_title='Chapter 2 Software Processes',course_or_level='SE',weekly_focus='Software Processes',
            topic_families=[TopicFamily(name='Software process',source_anchor='[P1] SLIDE 3',why_important='core')],
            coverage_items=[CoverageItem(id='COV-01',label='Software process definition and activities',knowledge_type='PROCESS',importance='major',source_anchor='[P1] SLIDE 3',why_important='core')],
            technical_boundaries=[],source_warnings=[],session_minutes=90,scope_fit='FIT',in_scope_families=['Software process'],deferred_topics=[],source_conflicts=[],source_manifest=[])

    def test_recommendations_after_real_deck_never_become_p1(self):
        profile=build_deterministic_source_profile(self._bundle())
        text=' '.join(x.label+' '+x.source_anchor for x in profile.coverage_items).lower()
        self.assertNotIn('slide 59',text)
        self.assertNotIn('recommended presentation',text)

    def test_semantic_slide_coordinate_suppresses_raw_duplicate(self):
        profile=reconcile_source_profile(self._semantic(),self._bundle())
        self.assertEqual(len([x for x in profile.coverage_items if x.source_anchor=='[P1] SLIDE 3']),1)

    def test_uncovered_real_major_slide_is_retained_but_key_points_are_supporting(self):
        profile=reconcile_source_profile(self._semantic(),self._bundle())
        majors={x.source_anchor for x in profile.coverage_items if x.importance=='major'}
        self.assertIn('[P1] SLIDE 20',majors)
        self.assertNotIn('[P1] SLIDE 56',majors)
        self.assertFalse(any('SLIDE 59' in x for x in majors))

    def test_semantic_warning_blocks_flattened_host_slides_without_player_metadata(self):
        td=tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        p=Path(td.name)/'flattened-slideshare.txt'
        fixture = (
            "SLIDE 3: Software process definition with specification design implementation validation evolution and process descriptions\n"
            "SLIDE 20: Process activities include specification development validation evolution and interleaved managerial activities\n"
            "SLIDE 71: Comprehensive Overview of Software Processes and Models for Effective Development with process model architecture and testing\n"
            "SLIDE 73: Comprehensive Overview of Software Processes and Models in Modern Development with process model design and validation\n"
        )
        p.write_text(fixture,encoding='utf-8')
        bundle=SourceBundle(items=[SourceItem('primary','P1','slideshare',p,'slideshare')],lecture_focus='',session_minutes=90)
        semantic=self._semantic()
        semantic.source_warnings=[
            'Slides 59 through 92 contain external slide title artifacts and unrelated topic titles/file names which must be filtered out in favor of the core Chapter 2 content (Slides 1-58).'
        ]
        profile=reconcile_source_profile(semantic,bundle)
        anchors={x.source_anchor for x in profile.coverage_items}
        self.assertIn('[P1] SLIDE 20',anchors)
        self.assertNotIn('[P1] SLIDE 71',anchors)
        self.assertNotIn('[P1] SLIDE 73',anchors)

if __name__=='__main__': unittest.main()
