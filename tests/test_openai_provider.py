from types import SimpleNamespace

import pytest

from app.llm.errors import LLMProviderConfigurationError, LLMProviderResponseError
from app.llm.openai_provider import OpenAIProvider
from app.schemas.ai import RecommendationResponse


class FakeResponses:
    def __init__(self, parsed: object) -> None:
        self.parsed = parsed
        self.kwargs: dict[str, object] = {}

    async def parse(self, **kwargs: object) -> SimpleNamespace:
        self.kwargs = kwargs
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, parsed: object) -> None:
        self.responses = FakeResponses(parsed)


@pytest.mark.asyncio
async def test_provider_parses_structured_response_and_passes_prompt_context() -> None:
    expected = RecommendationResponse(
        summary="summary",
        recommendation="recommendation",
        confidence=0.8,
        evidence=[],
        proposed_task=None,
        requires_approval=False,
        evidence_sufficient=False,
        limitations=[],
    )
    client = FakeClient(expected)
    provider = OpenAIProvider(api_key=None, model="test-model", client=client)

    result = await provider.generate_structured(
        system_prompt="system",
        user_prompt="user",
        response_model=RecommendationResponse,
        tools=[],
    )

    assert result == expected
    assert client.responses.kwargs["model"] == "test-model"
    assert "Allowed tools for this turn: none" in str(client.responses.kwargs["input"])


@pytest.mark.asyncio
async def test_provider_rejects_empty_structured_response() -> None:
    provider = OpenAIProvider(api_key=None, model="test-model", client=FakeClient(None))

    with pytest.raises(LLMProviderResponseError):
        await provider.generate_structured(
            system_prompt="system",
            user_prompt="user",
            response_model=RecommendationResponse,
            tools=[],
        )


def test_provider_requires_api_key_without_injected_client() -> None:
    with pytest.raises(LLMProviderConfigurationError):
        OpenAIProvider(api_key=None, model="test-model")
