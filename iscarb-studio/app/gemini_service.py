from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import TypeVar, Type

from pydantic import BaseModel, ValidationError

from .models import SourceProfile, Blueprint, AuditReport
from .prompts import SOURCE_PROFILE_PROMPT, MASTER_PROMPT, AUDIT_PROMPT, REPAIR_PROMPT

T = TypeVar("T", bound=BaseModel)


class GeminiNotConfigured(RuntimeError):
    pass


class GeminiService:
    """Fast, source-grounded Gemini client with one source upload per job.

    v1.2 deliberately performs schema validation locally. Large nested server-side
    response schemas can trigger INVALID_ARGUMENT even when the JSON schema is
    logically valid. We still request application/json and validate every result
    with Pydantic before it can enter the ISCARB release pipeline.
    """

    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            raise GeminiNotConfigured("GEMINI_API_KEY is not configured.")
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except Exception as exc:
            raise GeminiNotConfigured(
                "google-genai is not installed. Run: pip install -r requirements.txt"
            ) from exc
        self._types = types
        self.client = genai.Client(api_key=self.api_key)
        self._uploaded = None
        self._uploaded_path: str | None = None

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        code = getattr(exc, "code", None)
        if code in {429, 500, 502, 503, 504}:
            return True
        text = str(exc).lower()
        return any(marker in text for marker in (
            "429", "500", "502", "503", "504", "unavailable", "high demand",
            "temporarily overloaded", "resource exhausted", "rate limit",
            "internal server error",
        ))

    @staticmethod
    def _backoff(attempt: int) -> None:
        # Keep the UI responsive. One short retry before moving to a fallback.
        time.sleep(1.5 * (attempt + 1))

    def _source_content(self, file_path: Path):
        """Use text directly for extracted web sources; upload binary docs once."""
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md"}:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            return "WEEKLY SOURCE (authoritative technical source):\n\n" + text[:350_000]

        resolved = str(file_path.resolve())
        if self._uploaded is not None and self._uploaded_path == resolved:
            return self._uploaded

        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                self._uploaded = self.client.files.upload(file=str(file_path))
                self._uploaded_path = resolved
                return self._uploaded
            except Exception as exc:
                last_exc = exc
                if not self._is_retryable(exc) or attempt == 1:
                    raise
                self._backoff(attempt)
        raise last_exc or RuntimeError("Source upload failed")

    def close(self) -> None:
        if self._uploaded is not None:
            try:
                self.client.files.delete(name=self._uploaded.name)
            except Exception:
                pass
            self._uploaded = None
            self._uploaded_path = None

    def _models_for(self, preferred: str) -> list[str]:
        # Reliability first. Do not spend minutes retrying one overloaded model.
        ordered = [preferred]
        if preferred == "gemini-3.7-flash":
            ordered += ["gemini-3.6-flash", "gemini-3.5-flash"]
        elif preferred == "gemini-3.6-flash":
            ordered += ["gemini-3.5-flash", "gemini-3.5-flash-lite"]
        elif preferred == "gemini-3.5-flash-lite":
            ordered += ["gemini-3.5-flash", "gemini-3.6-flash"]
        else:
            ordered += ["gemini-3.6-flash", "gemini-3.5-flash"]
        result: list[str] = []
        for m in ordered:
            if m not in result:
                result.append(m)
        return result

    @staticmethod
    def _compact_schema(schema: Type[T]) -> str:
        # The schema is guidance in the prompt; Pydantic remains the hard validator.
        raw = schema.model_json_schema(by_alias=True)
        return json.dumps(raw, ensure_ascii=False, separators=(",", ":"))

    def _generate_structured(
        self,
        *,
        file_path: Path,
        prompt: str,
        schema: Type[T],
        extra_text: str = "",
        preferred_model: str | None = None,
        thinking_level: str = "low",
    ) -> T:
        source = self._source_content(file_path)
        model = preferred_model or self.model
        schema_text = self._compact_schema(schema)
        full_prompt = (
            prompt
            + extra_text
            + "\n\nOUTPUT CONTRACT: Return ONLY one JSON object. It must validate against this JSON schema. "
            + "Do not use markdown fences.\nJSON_SCHEMA:\n"
            + schema_text
        )

        last_exc: Exception | None = None
        last_text = ""
        for candidate in self._models_for(model):
            for attempt in range(2):
                try:
                    config = self._types.GenerateContentConfig(
                        response_mime_type="application/json",
                        thinking_config=self._types.ThinkingConfig(thinking_level=thinking_level),
                    )
                    response = self.client.models.generate_content(
                        model=candidate,
                        contents=[source, full_prompt],
                        config=config,
                    )
                    last_text = response.text or ""
                    try:
                        return schema.model_validate_json(last_text)
                    except ValidationError as validation_exc:
                        # One concise format repair. No expensive semantic re-generation here.
                        if attempt == 0:
                            full_prompt += (
                                "\n\nYour previous JSON failed local validation. Correct ONLY the JSON structure and return the complete object."
                                "\nVALIDATION_ERROR:\n" + str(validation_exc)[:1800]
                                + "\nPREVIOUS_JSON:\n" + last_text[:40_000]
                            )
                            continue
                        raise RuntimeError(
                            f"Gemini returned JSON that did not match the required ISCARB structure: {validation_exc}"
                        ) from validation_exc
                except Exception as exc:
                    last_exc = exc
                    if isinstance(exc, RuntimeError) and "did not match" in str(exc):
                        raise
                    if not self._is_retryable(exc):
                        # A non-transient request error will usually affect every model.
                        raise
                    if attempt == 0:
                        self._backoff(attempt)
                        continue
                    break

        if last_exc is not None:
            raise last_exc
        raise RuntimeError(f"No Gemini model completed the request. Last output: {last_text[:500]}")

    def profile_source(self, file_path: Path) -> SourceProfile:
        return self._generate_structured(
            file_path=file_path,
            prompt=SOURCE_PROFILE_PROMPT,
            schema=SourceProfile,
            preferred_model="gemini-3.5-flash-lite",
            thinking_level="minimal",
        )

    def generate_blueprint(self, file_path: Path, profile: SourceProfile) -> Blueprint:
        extra = "\nSOURCE PROFILE (coverage checklist):\n" + profile.model_dump_json(indent=2)
        return self._generate_structured(
            file_path=file_path,
            prompt=MASTER_PROMPT,
            schema=Blueprint,
            extra_text=extra,
            preferred_model=self.model,
            thinking_level="low",
        )

    def audit(self, file_path: Path, blueprint: Blueprint, deterministic_failures: list[str] | None = None) -> AuditReport:
        extra = (
            "\nCANDIDATE BLUEPRINT:\n"
            + blueprint.model_dump_json(by_alias=True, indent=2)
            + "\nDETERMINISTIC CHECK FAILURES:\n"
            + json.dumps(deterministic_failures or [], ensure_ascii=False)
        )
        return self._generate_structured(
            file_path=file_path,
            prompt=AUDIT_PROMPT,
            schema=AuditReport,
            extra_text=extra,
            preferred_model="gemini-3.5-flash-lite",
            thinking_level="minimal",
        )

    def repair(self, file_path: Path, blueprint: Blueprint, audit: AuditReport, deterministic_failures: list[str]) -> Blueprint:
        extra = (
            "\nCURRENT BLUEPRINT:\n"
            + blueprint.model_dump_json(by_alias=True, indent=2)
            + "\nAUDIT REPORT:\n"
            + audit.model_dump_json(indent=2)
            + "\nDETERMINISTIC FAILURES:\n"
            + json.dumps(deterministic_failures, ensure_ascii=False)
        )
        return self._generate_structured(
            file_path=file_path,
            prompt=REPAIR_PROMPT,
            schema=Blueprint,
            extra_text=extra,
            preferred_model=self.model,
            thinking_level="low",
        )
