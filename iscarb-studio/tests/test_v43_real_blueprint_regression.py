from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.start_v430 import app
from tests.v43_fixture import make_blueprint


class RealBlueprintPresenterRegressionTests(unittest.TestCase):
    """Regression for the real Security Engineering production failure.

    v4.2's card renderer assumed a trade-off unit always had at least two
    core_content values. A real Gemini-generated unit 10 had an empty
    core_content list and the HTML presenter raised IndexError while all file
    exports still worked. v4.3 must remain tolerant of sparse authored content.
    """

    def test_sparse_tradeoff_unit_never_crashes_presenter_or_exports(self):
        bp = make_blueprint()
        unit = bp.units[9]
        unit.title = 'MARIS Senior Design Review'
        unit.core_content = []
        unit.visual_plan.visual_type = 'trade-off'
        unit.visual_plan.reuse_mode = 'NEW'
        unit.visual_plan.focal_elements = [
            'Knowns', 'Unknowns', 'Decision-sensitive unknowns', 'Monitored metrics'
        ]

        client = TestClient(app, raise_server_exceptions=False)
        raw = bp.model_dump_json(by_alias=True).encode('utf-8')
        r = client.post(
            '/api/render-blueprint',
            files={'blueprint_file': ('real-regression.json', raw, 'application/json')},
        )
        self.assertEqual(r.status_code, 200, r.text)
        job_id = r.json()['job_id']

        presenter = client.get(f'/api/jobs/{job_id}/presenter')
        self.assertEqual(presenter.status_code, 200, presenter.text[:500])
        self.assertIn('CIMT-native Presenter', presenter.text)

        for fmt in ('pptx', 'presenter-pdf', 'pdf', 'docx', 'student', 'json'):
            out = client.get(f'/api/jobs/{job_id}/export/{fmt}')
            self.assertEqual(out.status_code, 200, f'{fmt}: {out.text[:500]}')
            self.assertGreater(len(out.content), 500, fmt)


if __name__ == '__main__':
    unittest.main()
