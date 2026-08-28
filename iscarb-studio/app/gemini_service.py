from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import TypeVar, Type

from pydantic import BaseModel

from .models import SourceProfile, Blueprint, AuditReport
from .prompts import SOURCE_PROFILE_PROMPT, MASTER_PROMPT, AUDIT_PROMPT, REPAIR_PROMPT

T = TypeVar("T", bound=BaseModel)


class GeminiNotConfigured(RuntimeError):
    pass


class GeminiService:
    """Source-grounded Gemini client with transient-error retries and model failover."""

    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
        self.active_model = self.model
        fallback_env = os.getenv(
            "GEMINI_FALLBACK_MODELS",
            "gemini-3.6-flash,gemini-3.5-flash",
        )
        self.fallback_models = [m.strip() for m in fallback_env.split(",") if m.strip()]
        self.deprioritized_models: set[str] = set()
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            raise GeminiNotConfigured("GEMINI_API_KEY is not configured.")
        try:
            from google import genai  # type: ignore
        except Exception as exc:
            raise GeminiNotConfigured(
                "google-genai is not installed. Run: pip install -r requirements.txt"
            ) from exc
        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        code = getattr(exc, "code", None)
        if code in {429, 500, 502, 503, 504}:
            return True
        text = str(exc).lower()
        return any(
            marker in text
            for marker in (
                "429",
                "500",
                "502",
                "503",
                "504",
                "unavailable",
                "high demand",
                "temporarily overloaded",
                "resource exhausted",
                "rate limit",
                "internal server error",
            )
        )

    @staticmethod
    def _sleep_for(attempt: int) -> None:
        # Short exponential backoff: 2s, 4s, 8s.
        time.sleep(2 ** (attempt + 1))

    def _upload(self, file_path: Path):
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                return self.client.files.upload(file=str(file_path))
            except Exception as exc:
                last_exc = exc
                if not self._is_retryable(exc) or attempt == 2:
                    raise
                self._sleep_for(attempt)
        assert last_exc is not None
        raise last_exc

    def _candidate_models(self) -> list[str]:
        ordered = [self.active_model, *self.fallback_models]
        seen: set[str] = set()
        result: list[str] = []
        for name in ordered:
            if not name or name in seen or name in self.deprioritized_models:
                continue
            seen.add(name)
            result.append(name)
        # Always retain the active model as a last-resort candidate if everything was deprioritized.
        if not result:
            result = [self.active_model]
        return result

    def _generate_structured(self, *, file_path: Path, prompt: str, schema: Type[T], extra_text: str = "") -> T:
        uploaded = self._upload(file_path)
        last_exc: Exception | None = None
        try:
            for candidate in self._candidate_models():
                exhausted_transient_failure = False
                for attempt in range(3):
                    try:
                        response = self.client.models.generate_content(
                            model=candidate,
                            contents=[uploaded, prompt, extra_text],
                            config={
                                "response_mime_type": "application/json",
                                "response_schema": schema,
                            },
                        )
                        self.active_model = candidate
                        if getattr(response, "parsed", None) is not None:
                            parsed = response.parsed
                            if isinstance(parsed, schema):
                                return parsed
                            return schema.model_validate(parsed)
                        return schema.model_validate_json(response.text)
                    except Exception as exc:
                        last_exc = exc
                        if not self._is_retryable(exc):
                            raise
                        if attempt < 2:
                            self._sleep_for(attempt)
                            continue
                        exhausted_transient_failure = True

                if exhausted_transient_failure:
                    # Avoid repeatedly returning to an overloaded model during the same lecture job.
                    self.deprioritized_models.add(candidate)
                    continue

            if last_exc is not None:
                raise last_exc
            raise RuntimeError("No Gemini model candidate was available.")
        finally:
            try:
                self.client.files.delete(name=uploaded.name)
            except Exception:
                pass

    def profile_source(self, file_path: Path) -> SourceProfile:
        return self._generate_structured(file_path=file_path, prompt=SOURCE_PROFILE_PROMPT, schema=SourceProfile)

    def generate_blueprint(self, file_path: Path, profile: SourceProfile) -> Blueprint:
        extra = "\nSOURCE PROFILE (coverage checklist):\n" + profile.model_dump_json(indent=2)
        return self._generate_structured(file_path=file_path, prompt=MASTER_PROMPT, schema=Blueprint, extra_text=extra)

    def audit(self, file_path: Path, blueprint: Blueprint, deterministic_failures: list[str] | None = None) -> AuditReport:
        extra = (
            "\nCANDIDATE BLUEPRINT:\n"
            + blueprint.model_dump_json(by_alias=True, indent=2)
            + "\nDETERMINISTIC CHECK FAILURES:\n"
            + json.dumps(deterministic_failures or [], ensure_ascii=False)
        )
        return self._generate_structured(file_path=file_path, prompt=AUDIT_PROMPT, schema=AuditReport, extra_text=extra)

    def repair(self, file_path: Path, blueprint: Blueprint, audit: AuditReport, deterministic_failures: list[str]) -> Blueprint:
        extra = (
            "\nCURRENT BLUEPRINT:\n"
            + blueprint.model_dump_json(by_alias=True, indent=2)
            + "\nAUDIT REPORT:\n"
            + audit.model_dump_json(indent=2)
            + "\nDETERMINISTIC FAILURES:\n"
            + json.dumps(deterministic_failures, ensure_ascii=False)
        )
        return self._generate_structured(file_path=file_path, prompt=REPAIR_PROMPT, schema=Blueprint, extra_text=extra)
