import httpx
import structlog
from pydantic import ValidationError
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.exceptions import (
    ExternalServiceInvalidResponseError,
    ExternalServiceTimeoutError,
    ExternalServiceUnavailableError,
)
from app.schemas.account import AccountResponse

logger = structlog.get_logger(__name__)


class AccountClient:
    def __init__(self, base_url: str, timeout_seconds: float = 2.0) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds

    async def get_account(self, account_id: str) -> AccountResponse:
        logger.info("account_lookup_started", account_id=account_id)
        try:
            response = await self._get_response_with_retry(account_id)
        except httpx.TimeoutException as error:
            raise ExternalServiceTimeoutError(
                f"Account lookup timed out for {account_id}"
            ) from error
        except httpx.HTTPStatusError as error:
            if error.response.status_code in {429, 500, 502, 503, 504}:
                raise ExternalServiceUnavailableError(
                    f"Account service remained unavailable for {account_id}"
                ) from error
            raise ExternalServiceInvalidResponseError(
                f"Account service rejected lookup for {account_id}"
            ) from error
        except httpx.TransportError as error:
            raise ExternalServiceUnavailableError(
                f"Account service could not be reached for {account_id}"
            ) from error

        try:
            account = AccountResponse.model_validate(response.json())
        except (ValidationError, ValueError) as error:
            logger.warning(
                "account_lookup_invalid_response",
                account_id=account_id,
                error_type=type(error).__name__,
            )
            raise ExternalServiceInvalidResponseError(
                f"Account service returned invalid data for {account_id}"
            ) from error

        logger.info(
            "account_lookup_succeeded",
            account_id=account.id,
            account_status=account.status,
        )
        return account

    async def _get_response_with_retry(self, account_id: str) -> httpx.Response:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.1, min=0.1, max=0.5),
            retry=retry_if_exception(self._is_retryable),
            reraise=True,
        ):
            with attempt:
                async with httpx.AsyncClient(
                    base_url=self._base_url,
                    timeout=self._timeout_seconds,
                ) as client:
                    response = await client.get(f"/accounts/{account_id}")
                    response.raise_for_status()
                    return response

        raise RuntimeError("Retry loop finished without returning or raising")

    @staticmethod
    def _is_retryable(error: BaseException) -> bool:
        if isinstance(error, httpx.TransportError):
            return True

        return isinstance(error, httpx.HTTPStatusError) and error.response.status_code in {
            429,
            500,
            502,
            503,
            504,
        }
