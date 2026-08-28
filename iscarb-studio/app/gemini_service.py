from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypeVar, Type

from pydantic import BaseModel

from .models import SourceProfile, Blueprint, AuditReport
from .prompts import SOURCE_PROFILE_PROMPT, MASTER_PROMPT, AUDIT_PROMPT, REPAIR_PROMPT

T = TypeVar("T", bound=BaseModel)


class GeminiNotConfigured(RuntimeError):
    pass


class GeminiService:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
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

    def _upload(self, file_path: Path):
        return self.client.files.upload(file=str(file_path))

    def _generate_structured(self, *, file_path: Path, prompt: str, schema: Type[T], extra_text: str = "") -> T:
        uploaded = self._upload(file_path)
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[uploaded, prompt, extra_text],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                    "temperature": 0.2,
                },
            )
            if getattr(response, "parsed", None) is not None:
                parsed = response.parsed
                if isinstance(parsed, schema):
                    return parsed
                return schema.model_validate(parsed)
            return schema.model_validate_json(response.text)
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
