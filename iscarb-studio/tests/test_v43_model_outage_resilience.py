from __future__ import annotations

import unittest
from pathlib import Path

from app import main as engine
from app.main import _is_model_unavailable, _is_quota_error
from app.source_bundle import SourceBundle, SourceItem
from app.storage import load_job, save_job
from app.models import JobState

LECTURE = Path(__file__).resolve().parents[2] / "lectures" / "cimt" / "CPIT455-class2-NooR.pdf"


class OutageClassificationTests(unittest.TestCase):
    """A sustained capacity failure is as fatal to a faculty job as no quota."""

    def test_quota_exhaustion_reaches_the_fallback(self):
        for message in ("RESOURCE_EXHAUSTED: quota exceeded", "free_tier_requests limit hit"):
            with self.subTest(message=message):
                self.assertTrue(_is_model_unavailable(RuntimeError(message)))

    def test_sustained_capacity_failure_also_reaches_the_fallback(self):
        for message in (
            "503 Service Unavailable",
            "The model is overloaded. temporarily overloaded",
            "429 rate limit exceeded",
            "500 Internal server error",
        ):
            with self.subTest(message=message):
                self.assertFalse(_is_quota_error(RuntimeError(message)), "should not be read as a quota error")
                self.assertTrue(_is_model_unavailable(RuntimeError(message)), "must still reach the fallback")

    def test_pipeline_defects_still_surface(self):
        for exc in (AttributeError("'NoneType' object has no attribute 'units'"), KeyError("clOs")):
            with self.subTest(exc=exc):
                self.assertFalse(_is_model_unavailable(exc), "a defect in our own code must not be masked")


class OutageCompileTests(unittest.TestCase):
    """A live outage must still hand the faculty member a usable draft."""

    def _run_with_outage(self, message: str) -> JobState:
        class OutagedService:
            def __init__(self, *_a, **_k):
                pass

            def profile_source(self, *_a, **_k):
                raise RuntimeError(message)

            def generate_blueprint(self, *_a, **_k):
                raise RuntimeError(message)

            def audit_blueprint(self, *_a, **_k):
                raise RuntimeError(message)

            def close(self):
                pass

        bundle = SourceBundle(
            items=[SourceItem("primary", "P1", LECTURE.name, LECTURE, LECTURE.name)],
            lecture_focus="",
            session_minutes=90,
        )
        job_id = "outage_regression_" + str(abs(hash(message)) % 10**8)
        save_job(JobState(id=job_id, status="queued", progress=0, message="", filename=LECTURE.name, model="auto"))
        original = engine.GeminiService
        engine.GeminiService = OutagedService
        try:
            engine._compile(job_id, bundle, "auto", 0)
        finally:
            engine.GeminiService = original
        return load_job(job_id)

    def test_capacity_outage_produces_a_blocked_draft_not_an_error(self):
        job = self._run_with_outage("503 Service Unavailable: model temporarily overloaded")
        self.assertNotEqual(job.status, "error", job.message)
        self.assertEqual(job.status, "blocked")
        self.assertIsNotNone(job.blueprint, "faculty must still receive a source-complete draft")
        self.assertEqual(len(job.blueprint.units), 20)
        self.assertEqual(sum(u.planned_minutes for u in job.blueprint.units), 90)
        self.assertNotIn("RELEASE", (job.message or "").replace("RELEASE is forbidden", ""))

    def test_quota_outage_still_produces_a_blocked_draft(self):
        job = self._run_with_outage("RESOURCE_EXHAUSTED: quota exceeded")
        self.assertEqual(job.status, "blocked", job.message)
        self.assertIsNotNone(job.blueprint)
        self.assertEqual(len(job.blueprint.units), 20)


if __name__ == "__main__":
    unittest.main()
