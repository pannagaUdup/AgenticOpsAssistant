class ExternalServiceError(Exception):
    """Base exception for external account-service failures."""


class ExternalServiceTimeoutError(ExternalServiceError):
    """Raised when the account service exceeds the configured timeout."""


class ExternalServiceUnavailableError(ExternalServiceError):
    """Raised when the account service remains unavailable after retries."""


class ExternalServiceInvalidResponseError(ExternalServiceError):
    """Raised when the account service returns invalid data."""
