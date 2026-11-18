from functools import lru_cache

from app.core.config import get_settings
from app.llm.fake import FakeLLMProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.provider import LLMProvider
from app.services.router import RequestRouter
from app.services.semantic_classifier import LLMIntentClassifier


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Build one provider for the process; select fake or OpenAI via environment."""
    settings = get_settings()
    if settings.llm_provider.lower() == "openai":
        return OpenAIProvider.from_settings()
    if settings.llm_provider.lower() == "gemini":
        return GeminiProvider.from_settings()
    return FakeLLMProvider()


@lru_cache
def get_request_router() -> RequestRouter:
    provider = get_llm_provider()
    if isinstance(provider, (OpenAIProvider, GeminiProvider)):
        return RequestRouter(async_classifier=LLMIntentClassifier(provider))
    return RequestRouter()
