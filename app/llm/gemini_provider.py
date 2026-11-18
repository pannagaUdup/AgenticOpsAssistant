import asyncio
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.config import get_settings
from app.llm.errors import LLMProviderConfigurationError, LLMProviderError, LLMProviderResponseError
from app.schemas.ai import ToolName


class GeminiProvider:
    """Google Gemini adapter using Pydantic structured output."""

    def __init__(self, *, api_key: str | None, model: str, client: Any | None = None) -> None:
        if not api_key and client is None:
            raise LLMProviderConfigurationError("GEMINI_API_KEY is required for GeminiProvider")
        self._client = client or genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(api_version="v1beta"),
        )
        self._model = model

    @classmethod
    def from_settings(cls) -> GeminiProvider:
        settings = get_settings()
        return cls(
            api_key=settings.gemini_api_key.get_secret_value()
            if settings.gemini_api_key is not None
            else None,
            model=settings.gemini_model,
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
        contents = (
            f"{system_prompt}\n\n{user_prompt}\n\nAllowed tools for this turn: {allowed_tools}"
        )
        for attempt in range(3):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self._model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=self._gemini_schema(response_model),
                    ),
                )
                break
            except Exception as exc:
                if attempt < 2 and self._is_transient(exc):
                    await asyncio.sleep(2**attempt)
                    continue
                raise LLMProviderError(
                    f"Gemini request failed ({type(exc).__name__}): {exc}"
                ) from exc

        parsed = getattr(response, "parsed", None)
        if parsed is None:
            text = getattr(response, "text", None)
            if not text:
                raise LLMProviderResponseError("Gemini returned no structured response")
            return response_model.model_validate_json(text)
        return response_model.model_validate(parsed)

    @staticmethod
    def _is_transient(error: Exception) -> bool:
        name = type(error).__name__.lower()
        message = str(error).lower()
        return "servererror" in name or "503" in message or "unavailable" in message

    @staticmethod
    def _gemini_schema(response_model: type[BaseModel]) -> dict[str, Any]:
        """Convert Pydantic JSON schema to the subset accepted by Gemini Developer API."""
        schema = response_model.model_json_schema()

        def strip_unsupported(value: Any) -> Any:
            if isinstance(value, dict):
                return {
                    key: strip_unsupported(item)
                    for key, item in value.items()
                    if key != "additionalProperties"
                }
            if isinstance(value, list):
                return [strip_unsupported(item) for item in value]
            return value

        return strip_unsupported(schema)
