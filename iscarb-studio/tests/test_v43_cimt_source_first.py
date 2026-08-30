from __future__ import annotations

import unittest

from app.cimt_native_v43 import _display_question, _display_title, _spec
from app.gate_v14 import deterministic_gate
from tests.v43_fixture import make_blueprint


class CimtSourceFirstRegressionTests(unittest.TestCase):
    def test_visual_plan_drives_real_technical_unit_not_unit_number(self):
        bp = make_blueprint()
        u = bp.units[5]  # Unit 6 used to be hard-wired to a dependability cost curve.
        u.title = 'Mechanism Deep Dive: Integration and Configuration'
        u.core_content = [
            'Integration and configuration: systems are assembled from reusable components.',
            'Types of reusable software: COTS applications, component frameworks, and web services.',
            'Key process stages: discovery, configuration, and adaptation.',
        ]
        u.visual_plan.visual_type = 'process'
        u.visual_plan.focal_elements = ['Discovery', 'Configuration', 'Adaptation']
        kind, items = _spec(bp, u)
        self.assertEqual(kind, 'chain')
        labels = [x[0] for x in items]
        # Source content leads the slide, in source order. Scaffolding may follow
        # it (that is what fills the rest of the slide) but must never displace it.
        self.assertEqual(labels[:3], ['INTEGRATION AND CONFIGURATION', 'TYPES OF REUSABLE SOFTWARE', 'KEY PROCESS STAGES'])
        for extra in labels[3:]:
            self.assertTrue(extra.startswith('ISCARB STEP'), f'unlabelled non-source item: {extra}')

    def test_framework_first_titles_are_projected_to_source_first_classroom_titles(self):
        bp = make_blueprint()
        u14 = bp.units[13]
        u14.title = 'Practitioner Wellbeing: Cognitive Load and Alert Burden in Process Management'
        u14.core_content = [
            'Incremental development problems: lack of visibility and structural degradation requiring refactoring.',
            'Process metrics: time, resources, and defect occurrences.',
        ]
        u14.visual_plan.visual_type = 'trade-off'
        self.assertEqual(_display_title(bp, u14), 'Incremental Development: Visibility, Structure, and Refactoring')
        self.assertNotIn('wellbeing', _display_title(bp, u14).lower())

        u15 = bp.units[14]
        u15.title = 'Critical AI Literacy & SEI Maturity Framework Auditing'
        u15.core_content = ['SEI Capability Maturity Model levels: Initial, Repeatable, Defined, Managed, Optimising.']
        u15.visual_plan.visual_type = 'concept-map'
        self.assertEqual(_display_title(bp, u15), 'Process Maturity: From Initial to Optimising')
        self.assertEqual(_spec(bp, u15)[0], 'stack')

    def test_presenter_removes_synthetic_percentages(self):
        bp = make_blueprint()
        u = bp.units[4]
        u.engineering_question = 'If requirements volatility exceeds 30% after design, what changes?'
        self.assertNotIn('30%', _display_question(u))

    def test_gate_rejects_framework_first_title_and_unsourced_numeric_precision(self):
        bp = make_blueprint()
        bp.units[13].title = 'Practitioner Wellbeing: Cognitive Load'
        bp.units[13].student_action = 'Allocate 20% of sprint capacity without source evidence.'
        checks = deterministic_gate(bp, None, 'primary source text without numeric threshold')
        self.assertFalse(checks['v14_source_first_learner_titles'])
        self.assertFalse(checks['v14_no_unsourced_numeric_precision'])


if __name__ == '__main__':
    unittest.main()
