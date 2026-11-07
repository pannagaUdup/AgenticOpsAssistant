from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.core.exceptions import (
    ExternalServiceInvalidResponseError,
    ExternalServiceTimeoutError,
    ExternalServiceUnavailableError,
)
from app.schemas.account import AccountResponse
from app.services.account_client import AccountClient

router = APIRouter(prefix="/api/v1", tags=["accounts"])


def get_account_client() -> AccountClient:
    settings = get_settings()
    return AccountClient(base_url=settings.account_service_base_url)


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    client: Annotated[AccountClient, Depends(get_account_client)],
) -> AccountResponse:
    try:
        return await client.get_account(account_id)
    except ExternalServiceTimeoutError as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(error),
        ) from error
    except ExternalServiceUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except ExternalServiceInvalidResponseError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error