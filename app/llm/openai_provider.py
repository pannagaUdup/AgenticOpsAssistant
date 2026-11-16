from typing import Any

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel

from app.core.config import get_settings
from app.llm.errors import (
    LLMProviderConfigurationError,
    LLMProviderError,
    LLMProviderResponseError,
)
from app.schemas.ai import ToolName


class OpenAIProvider:
    """OpenAI Responses API adapter implementing the application's provider contract."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        client: AsyncOpenAI | Any | None = None,
    ) -> None:
        if not api_key and client is None:
            raise LLMProviderConfigurationError("OPENAI_API_KEY is required for OpenAIProvider")
        self._client = client or AsyncOpenAI(api_key=api_key)
        self._model = model

    @classmethod
    def from_settings(cls) -> OpenAIProvider:
        settings = get_settings()
        return cls(
            api_key=settings.openai_api_key.get_secret_value()
            if settings.openai_api_key is not None
            else None,
            model=settings.openai_model,
        )

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
        tools: list[ToolName],
    ) -> BaseModel:
        allowed_tools = ", ".join(tool.value for tool in tools) or "none"
        prompt = f"{user_prompt}\n\nAllowed tools for this turn: {allowed_tools}"
        try:
            response = await self._client.responses.parse(
                model=self._model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                text_format=response_model,
            )
        except (APITimeoutError, APIConnectionError, RateLimitError) as exc:
            raise LLMProviderError("OpenAI request could not be completed") from exc
        except APIStatusError as exc:
            raise LLMProviderError(f"OpenAI request failed with status {exc.status_code}") from exc

        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise LLMProviderResponseError("OpenAI returned no structured response")
        return response_model.model_validate(parsed)
