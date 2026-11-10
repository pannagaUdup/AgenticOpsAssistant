import pytest

from app.core.exceptions import (
    ExternalServiceError,
    ExternalServiceTimeoutError,
)


def test_timeout_error_is_an_external_service_error() -> None:
    with pytest.raises(ExternalServiceError):
        raise ExternalServiceTimeoutError("Account lookup timed out")
