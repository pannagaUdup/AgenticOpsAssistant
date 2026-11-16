from functools import lru_cache

from app.core.config import get_settings
from app.llm.fake import FakeLLMProvider
from app.llm.openai_provider import OpenAIProvider
from app.llm.provider import LLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Build one provider for the process; select fake or OpenAI via environment."""
    settings = get_settings()
    if settings.llm_provider.lower() == "openai":
        return OpenAIProvider.from_settings()
    return FakeLLMProvider()
