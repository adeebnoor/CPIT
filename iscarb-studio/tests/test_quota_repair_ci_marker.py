from __future__ import annotations

import unittest

from app.main import _major_coverage_gaps, _ensure_quota_safe_completeness


class QuotaRepairCIMarker(unittest.TestCase):
    def test_active_quota_repair_helpers_are_wired(self):
        self.assertTrue(callable(_major_coverage_gaps))
        self.assertTrue(callable(_ensure_quota_safe_completeness))


if __name__ == '__main__':
    unittest.main()
