from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import TypeVar, Type

from pydantic import BaseModel, ValidationError

from .models import SourceProfile, Blueprint, AuditReport
from .prompts import SOURCE_PROFILE_PROMPT, MASTER_PROMPT, AUDIT_PROMPT, REPAIR_PROMPT
from .readiness import READINESS_CONTEXT
from .readiness_map import READINESS_KLO_MAP_CONTEXT
from .quality_rules import QUALITY_ADDENDUM, AUDIT_ADDENDUM, REPAIR_ADDENDUM
from .source_bundle import SourceBundle

T = TypeVar("T", bound=BaseModel)


class GeminiNotConfigured(RuntimeError):
    pass


class GeminiService:
    """Source-grounded Gemini client for one 90-minute multi-source lecture bundle.

    Quota policy:
    - source profiling uses Flash-Lite;
    - semantic audit uses 3.5 Flash;
    - the selected full model (normally 3.6 Flash) is reserved for blueprint generation
      and, only when necessary, repair;
    - free-tier quota exhaustion skips immediately to the next eligible model instead
      of repeatedly burning requests on the exhausted model.
    """

    def __init__(self, model: str | None = None):
        self.model = model or "gemini-3.6-flash"
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            raise GeminiNotConfigured("GEMINI_API_KEY is not configured.")
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except Exception as exc:
            raise GeminiNotConfigured("google-genai is not installed. Run: pip install -r requirements.txt") from exc
        self._types = types
        self.client = genai.Client(api_key=self.api_key)
        self._uploaded: dict[str, object] = {}
        self.active_model = self.model

    @staticmethod
    def _is_quota_exhausted(exc: Exception) -> bool:
        text = str(exc).lower()
        return any(marker in text for marker in (
            "resource_exhausted",
            "quota exceeded",
            "free_tier_requests",
            "generatecontentinputtokenspermodel",
            "generaterequestsperdayperprojectpermodel",
        ))

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        if GeminiService._is_quota_exhausted(exc):
            return False
        code = getattr(exc, "code", None)
        if code in {429, 500, 502, 503, 504}:
            return True
        text = str(exc).lower()
        return any(marker in text for marker in (
            "429", "500", "502", "503", "504", "unavailable", "high demand",
            "temporarily overloaded", "rate limit", "internal server error",
        ))

    @staticmethod
    def _backoff(attempt: int) -> None:
        time.sleep(1.25 * (attempt + 1))

    def _upload(self, path: Path):
        key = str(path.resolve())
        if key in self._uploaded:
            return self._uploaded[key]
        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                uploaded = self.client.files.upload(file=str(path))
                self._uploaded[key] = uploaded
                return uploaded
            except Exception as exc:
                last_exc = exc
                if self._is_quota_exhausted(exc):
                    raise
                if not self._is_retryable(exc) or attempt == 1:
                    raise
                self._backoff(attempt)
        raise last_exc or RuntimeError("Source upload failed")

    def _source_contents(self, bundle: SourceBundle) -> list[object]:
        contents: list[object] = [bundle.manifest_text()]
        for item in bundle.items:
            contents.append(f"\nBEGIN SOURCE {item.label}\n")
            suffix = item.path.suffix.lower()
            if suffix in {".txt", ".md"}:
                text = item.path.read_text(encoding="utf-8", errors="replace")
                contents.append(text[:300_000])
            else:
                contents.append(self._upload(item.path))
            contents.append(f"\nEND SOURCE [{item.source_id}]\n")
        return contents

    def close(self) -> None:
        for uploaded in list(self._uploaded.values()):
            try:
                self.client.files.delete(name=uploaded.name)  # type: ignore[attr-defined]
            except Exception:
                pass
        self._uploaded.clear()

    def _models_for(self, preferred: str) -> list[str]:
        # Keep profiling/auditing away from the 3.6 pool whenever possible so the
        # premium quota is spent on the actual lecture, not on orchestration.
        if preferred == "gemini-3.7-flash":
            ordered = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"]
        elif preferred == "gemini-3.6-flash":
            ordered = ["gemini-3.6-flash", "gemini-3.5-flash"]
        elif preferred == "gemini-3.5-flash":
            ordered = ["gemini-3.5-flash", "gemini-3.5-flash-lite"]
        elif preferred == "gemini-3.5-flash-lite":
            ordered = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
        else:
            ordered = [preferred, "gemini-3.5-flash"]
        result: list[str] = []
        for m in ordered:
            if m not in result:
                result.append(m)
        return result

    @staticmethod
    def _compact_schema(schema: Type[T]) -> str:
        raw = schema.model_json_schema(by_alias=True)
        return json.dumps(raw, ensure_ascii=False, separators=(",", ":"))

    def _generate_structured(
        self,
        *,
        bundle: SourceBundle,
        prompt: str,
        schema: Type[T],
        extra_text: str = "",
        preferred_model: str | None = None,
        thinking_level: str = "low",
    ) -> T:
        source_contents = self._source_contents(bundle)
        model = preferred_model or self.model
        schema_text = self._compact_schema(schema)
        base_prompt = (
            prompt + extra_text
            + "\n\nOUTPUT CONTRACT: Return ONLY one JSON object validating against this schema. No markdown fences."
            + "\nJSON_SCHEMA:\n" + schema_text
        )

        last_exc: Exception | None = None
        last_text = ""
        quota_exhausted_models: list[str] = []

        for candidate in self._models_for(model):
            full_prompt = base_prompt
            for attempt in range(2):
                try:
                    config = self._types.GenerateContentConfig(
                        response_mime_type="application/json",
                        thinking_config=self._types.ThinkingConfig(thinking_level=thinking_level),
                    )
                    response = self.client.models.generate_content(
                        model=candidate,
                        contents=[*source_contents, full_prompt],
                        config=config,
                    )
                    self.active_model = candidate
                    last_text = response.text or ""
                    try:
                        return schema.model_validate_json(last_text)
                    except ValidationError as validation_exc:
                        if attempt == 0:
                            full_prompt += (
                                "\n\nFORMAT REPAIR ONLY: Previous JSON failed local validation. Return the complete corrected JSON object."
                                "\nVALIDATION_ERROR:\n" + str(validation_exc)[:2400]
                                + "\nPREVIOUS_JSON:\n" + last_text[:50_000]
                            )
                            continue
                        raise RuntimeError(
                            f"Gemini returned JSON that did not match the required ISCARB structure: {validation_exc}"
                        ) from validation_exc
                except Exception as exc:
                    last_exc = exc
                    if isinstance(exc, RuntimeError) and "did not match" in str(exc):
                        raise
                    if self._is_quota_exhausted(exc):
                        quota_exhausted_models.append(candidate)
                        break  # immediately try the next model; no pointless sleep/retry
                    if not self._is_retryable(exc):
                        raise
                    if attempt == 0:
                        self._backoff(attempt)
                        continue
                    break

        if quota_exhausted_models and last_exc is not None:
            names = ", ".join(dict.fromkeys(quota_exhausted_models))
            raise RuntimeError(
                "Gemini free-tier quota is currently exhausted for the available model pool "
                f"({names}). ISCARB did not keep retrying and consuming quota. "
                "Wait for the quota window to reset or enable billing / a higher Gemini quota, then run the lecture again."
            ) from last_exc
        if last_exc is not None:
            raise last_exc
        raise RuntimeError(f"No Gemini model completed the request. Last output: {last_text[:500]}")

    def profile_source(self, bundle: SourceBundle) -> SourceProfile:
        result = self._generate_structured(
            bundle=bundle,
            prompt=SOURCE_PROFILE_PROMPT,
            schema=SourceProfile,
            extra_text="\n\nBUNDLE MANIFEST:\n" + bundle.manifest_text(),
            preferred_model="gemini-3.5-flash-lite",
            thinking_level="minimal",
        )
        result.session_minutes = 90
        result.source_manifest = bundle.manifest_lines()
        if not result.in_scope_families:
            result.in_scope_families = [x.name for x in result.topic_families]
        return result

    def generate_blueprint(self, bundle: SourceBundle, profile: SourceProfile) -> Blueprint:
        extra = (
            "\nSOURCE PROFILE (90-minute full-coverage contract):\n" + profile.model_dump_json(indent=2)
            + "\n\nBUNDLE MANIFEST:\n" + bundle.manifest_text()
            + "\n\nETEC IT 2025 READINESS PROFILE (alignment authority only):\n" + READINESS_CONTEXT
            + "\n\nOFFICIAL ETEC SLO-TO-KLO MAP (must be copied exactly; do not infer):\n" + READINESS_KLO_MAP_CONTEXT
        )
        return self._generate_structured(
            bundle=bundle,
            prompt=MASTER_PROMPT + QUALITY_ADDENDUM,
            schema=Blueprint,
            extra_text=extra,
            preferred_model=self.model,
            thinking_level="low",
        )

    def audit(self, bundle: SourceBundle, blueprint: Blueprint, deterministic_failures: list[str] | None = None) -> AuditReport:
        extra = (
            "\nBUNDLE MANIFEST:\n" + bundle.manifest_text()
            + "\nETEC IT 2025 READINESS PROFILE:\n" + READINESS_CONTEXT
            + "\nOFFICIAL ETEC SLO-TO-KLO MAP:\n" + READINESS_KLO_MAP_CONTEXT
            + "\nCANDIDATE BLUEPRINT:\n" + blueprint.model_dump_json(by_alias=True, indent=2)
            + "\nDETERMINISTIC CHECK FAILURES:\n" + json.dumps(deterministic_failures or [], ensure_ascii=False)
        )
        # Audit on a separate model pool so 3.6 quota is reserved for generation/repair.
        return self._generate_structured(
            bundle=bundle,
            prompt=AUDIT_PROMPT + AUDIT_ADDENDUM,
            schema=AuditReport,
            extra_text=extra,
            preferred_model="gemini-3.5-flash",
            thinking_level="low",
        )

    def repair(self, bundle: SourceBundle, blueprint: Blueprint, audit: AuditReport, deterministic_failures: list[str]) -> Blueprint:
        extra = (
            "\nBUNDLE MANIFEST:\n" + bundle.manifest_text()
            + "\nETEC IT 2025 READINESS PROFILE:\n" + READINESS_CONTEXT
            + "\nOFFICIAL ETEC SLO-TO-KLO MAP:\n" + READINESS_KLO_MAP_CONTEXT
            + "\nCURRENT BLUEPRINT:\n" + blueprint.model_dump_json(by_alias=True, indent=2)
            + "\nAUDIT REPORT:\n" + audit.model_dump_json(indent=2)
            + "\nDETERMINISTIC FAILURES:\n" + json.dumps(deterministic_failures, ensure_ascii=False)
        )
        return self._generate_structured(
            bundle=bundle,
            prompt=REPAIR_PROMPT + REPAIR_ADDENDUM,
            schema=Blueprint,
            extra_text=extra,
            preferred_model=self.model,
            thinking_level="low",
        )
