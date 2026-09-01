from __future__ import annotations

import unittest
from pathlib import Path


class RepositoryHygieneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]

    def test_public_launcher_is_current(self):
        t = (self.root / 'iscarb.html').read_text(encoding='utf-8')
        self.assertIn('?v=4.4.0', t)
        self.assertNotIn('?v=3.3', t)

    def test_archive_back_links_have_real_target(self):
        self.assertIn('id="evolution"', (self.root / 'index.html').read_text(encoding='utf-8'))
        for name in ('cimt.html', 'imam.html'):
            t = (self.root / name).read_text(encoding='utf-8')
            self.assertIn('index.html#evolution', t)
            self.assertNotIn('index.html#frameworks', t)

    def test_no_windows_local_urls_remain(self):
        for page in (self.root / 'slides').glob('*.html'):
            t = page.read_text(encoding='utf-8', errors='replace')
            self.assertNotIn('file:///', t, page.name)
            self.assertNotIn('C:/Users/', t, page.name)

    def test_quota_profile_fallback_is_wired(self):
        t = (self.root / 'iscarb-studio/app/main.py').read_text(encoding='utf-8')
        self.assertIn('build_deterministic_source_profile', t)
        self.assertIn('profile = build_deterministic_source_profile(bundle, str(exc))', t)

    def test_source_crop_preserves_horizontal_extent(self):
        t = (self.root / 'iscarb-studio/app/cimt_native_v43.py').read_text(encoding='utf-8')
        self.assertIn('box = (0, int(h * 0.17), w, int(h * 0.925))', t)
        self.assertNotIn('int(w * 0.035), int(h * 0.17), int(w * 0.965)', t)

    def test_mobile_overflow_guards_are_active(self):
        ui = (self.root / 'iscarb-studio/app/static/index_v410.html').read_text(encoding='utf-8')
        presenter = (self.root / 'iscarb-studio/app/cimt_native_v43.py').read_text(encoding='utf-8')
        self.assertIn('html,body{max-width:100%;overflow-x:hidden}', ui)
        self.assertIn('input[type=file]{overflow:hidden', ui)
        self.assertIn('html,body,.deck,.stage{{max-width:100%;overflow-x:hidden}}', presenter)

    def test_gitignore_covers_runtime_artifacts(self):
        t = (self.root / '.gitignore').read_text(encoding='utf-8')
        for s in ('__pycache__/', '*.py[cod]', 'iscarb-studio/data/', 'iscarb-studio/.env'):
            self.assertIn(s, t)


if __name__ == '__main__':
    unittest.main()
