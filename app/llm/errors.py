class LLMProviderError(RuntimeError):
    """Base error for failures communicating with a model provider."""


class LLMProviderConfigurationError(LLMProviderError):
    """Raised when the provider cannot be constructed from its configuration."""


class LLMProviderResponseError(LLMProviderError):
    """Raised when a provider returns no usable structured response."""
