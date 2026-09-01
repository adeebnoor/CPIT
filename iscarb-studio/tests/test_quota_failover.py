"""Use configured capacity; never invent quota or misreport an outage."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from app.gemini_service import GeminiService


class Answer(BaseModel):
    value: int


def service_for(responses):
    service = object.__new__(GeminiService)
    service.model = "gemini-3.5-flash"
    service._source_contents = Mock(return_value=["source"])
    service._remaining_seconds = Mock(return_value=10)
    service._backoff = Mock()
    factory = lambda **kwargs: SimpleNamespace(**kwargs)
    service._types = SimpleNamespace(**{name: factory for name in (
        "GenerateContentConfig", "ThinkingConfig", "HttpOptions", "HttpRetryOptions")})
    service.client = SimpleNamespace(models=SimpleNamespace(generate_content=Mock(side_effect=responses)))
    return service


def request(service, preferred="gemini-3.5-flash"):
    return service._generate_structured(bundle=None, prompt="test", schema=Answer, preferred_model=preferred)


def quota():
    return RuntimeError("RESOURCE_EXHAUSTED: quota exceeded")


def test_all_stage_preferences_can_reach_the_configured_alternative():
    service = object.__new__(GeminiService)
    for preferred in ("auto", "gemini-3.5-flash", "gemini-3.5-flash-lite"):
        assert set(service._models_for(preferred)) == {
            "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"}


def test_exhausted_models_are_not_retried_during_later_stages():
    response = SimpleNamespace(text='{"value":1}')
    service = service_for([quota(), quota(), response, response])
    assert request(service).value == 1
    assert request(service, "gemini-3.5-flash-lite").value == 1
    calls = service.client.models.generate_content.call_args_list
    assert [call.kwargs["model"] for call in calls] == [
        "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.6-flash"]
    service._backoff.assert_not_called()


def test_full_quota_exhaustion_stops_without_another_provider_call():
    service = service_for([quota(), quota(), quota()])
    for _ in range(2):
        with pytest.raises(RuntimeError, match="quota is exhausted for every model"):
            request(service)
    assert service.client.models.generate_content.call_count == 3


def test_mixed_capacity_errors_are_not_falsely_called_full_quota_exhaustion():
    service = service_for([quota()] + [RuntimeError("503 Service Unavailable")] * 6)
    with pytest.raises(RuntimeError, match="503 Service Unavailable"):
        request(service)
    assert service._quota_exhausted_models == {"gemini-3.5-flash"}
