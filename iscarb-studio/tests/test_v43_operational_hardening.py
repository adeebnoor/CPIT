from __future__ import annotations

import io
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import storage
from app.main import MAX_UPLOAD_BYTES
from app.start_v430 import app

ROOT = Path(__file__).resolve().parents[2]


class UploadCeilingTests(unittest.TestCase):
    """One oversized source must not be allowed to consume the shared disk."""

    def setUp(self):
        self.client = TestClient(app)

    def test_oversized_primary_source_is_refused(self):
        payload = b"A" * (MAX_UPLOAD_BYTES + 1024)
        before = set(storage.UPLOADS.iterdir()) if storage.UPLOADS.exists() else set()
        r = self.client.post(
            "/api/compile",
            files={"primary_lecture": ("huge.txt", io.BytesIO(payload), "text/plain")},
        )
        self.assertEqual(r.status_code, 413, r.text)
        self.assertIn("larger than", r.json()["detail"])
        after = set(storage.UPLOADS.iterdir()) if storage.UPLOADS.exists() else set()
        for job_dir in after - before:
            leftover = list(job_dir.rglob("*")) if job_dir.is_dir() else [job_dir]
            self.assertEqual([f for f in leftover if f.is_file()], [], "partial upload was not cleaned up")

    def test_source_within_the_ceiling_is_still_accepted(self):
        r = self.client.post(
            "/api/compile",
            files={"primary_lecture": ("small.txt", io.BytesIO(b"lecture text " * 64), "text/plain")},
        )
        self.assertEqual(r.status_code, 200, r.text)
        self.assertIn("job_id", r.json())


class SecurityHeaderTests(unittest.TestCase):
    """Every faculty-facing response carries the baseline browser protections."""

    def setUp(self):
        self.client = TestClient(app)

    def test_baseline_headers_on_every_surface(self):
        for path in ("/", "/api/health", "/starter-kit"):
            with self.subTest(path=path):
                h = self.client.get(path).headers
                self.assertEqual(h.get("X-Content-Type-Options"), "nosniff")
                self.assertEqual(h.get("Referrer-Policy"), "strict-origin-when-cross-origin")
                self.assertEqual(h.get("Content-Security-Policy"), "frame-ancestors 'self'")
                self.assertEqual(h.get("X-Frame-Options"), "SAMEORIGIN")


class RetentionTests(unittest.TestCase):
    """Stale artifacts expire; work from the current session survives."""

    def test_prune_removes_only_expired_entries(self):
        storage.EXPORTS.mkdir(parents=True, exist_ok=True)
        fresh = storage.EXPORTS / "retention_fresh.marker"
        stale = storage.EXPORTS / "retention_stale.marker"
        fresh.write_text("keep", encoding="utf-8")
        stale.write_text("drop", encoding="utf-8")
        old = time.time() - (storage.RETENTION_HOURS + 24) * 3600
        import os
        os.utime(stale, (old, old))
        try:
            storage.prune_expired()
            self.assertTrue(fresh.exists(), "current-session output must survive pruning")
            self.assertFalse(stale.exists(), "expired output must be pruned")
        finally:
            fresh.unlink(missing_ok=True)
            stale.unlink(missing_ok=True)

    def test_rasterized_visual_cache_also_expires(self):
        """Source pages render at 2.6x now, so this directory is the largest one."""
        storage.VISUAL_CACHE.mkdir(parents=True, exist_ok=True)
        stale = storage.VISUAL_CACHE / "retention_stale_cache"
        stale.mkdir(exist_ok=True)
        (stale / "slide-001.png").write_bytes(b"x" * 2048)
        old_time = time.time() - (storage.RETENTION_HOURS + 24) * 3600
        import os
        os.utime(stale, (old_time, old_time))
        try:
            storage.prune_expired()
            self.assertFalse(stale.exists(), "expired raster cache must be pruned")
        finally:
            import shutil
            shutil.rmtree(stale, ignore_errors=True)

    def test_prune_is_disabled_when_retention_is_zero(self):
        original = storage.RETENTION_HOURS
        storage.RETENTION_HOURS = 0
        try:
            self.assertEqual(storage.prune_expired(), 0)
        finally:
            storage.RETENTION_HOURS = original


class AccessibleStatusTests(unittest.TestCase):
    """Compile progress changes without a page load, so it must be announced."""

    def setUp(self):
        self.client = TestClient(app)

    def test_progress_and_error_regions_are_live(self):
        html = self.client.get("/").text
        self.assertIn('role="status"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn('role="alert"', html)
        self.assertIn('aria-live="assertive"', html)

    def test_served_interface_states_no_superseded_gate_version(self):
        html = self.client.get("/").text
        for superseded in ("Gate v12", "Gate v13"):
            self.assertNotIn(superseded, html, f"interface still advertises {superseded}")
        self.assertIn("Gate v14", html)


class DeploymentHygieneTests(unittest.TestCase):
    def test_dependencies_carry_upper_bounds(self):
        for line in (ROOT / "iscarb-studio/requirements.txt").read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            self.assertIn("<", line, f"{line} can absorb an unreviewed major release")

    def test_image_does_not_run_as_root(self):
        dockerfile = (ROOT / "iscarb-studio/Dockerfile").read_text(encoding="utf-8")
        self.assertIn("USER iscarb", dockerfile)

    def test_build_context_excludes_runtime_and_secrets(self):
        ignored = (ROOT / "iscarb-studio/.dockerignore").read_text(encoding="utf-8").split()
        for entry in ("data", ".env", ".git"):
            self.assertIn(entry, ignored)


if __name__ == "__main__":
    unittest.main()


class DeployIdentityTests(unittest.TestCase):
    """PUBLIC_VERSION is pinned in render.yaml, so it cannot distinguish a fresh
    deploy from a stale one. Two live validation runs were misread before the
    health payload reported the commit it is actually serving."""

    def setUp(self):
        self.client = TestClient(app)

    def test_health_reports_the_build_it_is_serving(self):
        body = self.client.get("/api/health").json()
        self.assertIn("build_commit", body)
        self.assertIn("build_branch", body)

    def test_build_is_reported_honestly_when_not_a_render_deploy(self):
        body = self.client.get("/api/health").json()
        self.assertIn("unknown", body["build_commit"])

    def test_render_commit_is_surfaced_when_present(self):
        import os
        from app import start_v430
        os.environ["RENDER_GIT_COMMIT"] = "abcdef1234567890"
        os.environ["RENDER_GIT_BRANCH"] = "main"
        try:
            build = start_v430._deployed_build()
            self.assertEqual(build["build_commit"], "abcdef123456")
            self.assertEqual(build["build_branch"], "main")
        finally:
            os.environ.pop("RENDER_GIT_COMMIT", None)
            os.environ.pop("RENDER_GIT_BRANCH", None)
