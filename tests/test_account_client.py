import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.core.exceptions import (
    ExternalServiceInvalidResponseError,
    ExternalServiceTimeoutError,
    ExternalServiceUnavailableError,
)
from app.main import app
from app.services.account_client import AccountClient


@respx.mock
@pytest.mark.asyncio
async def test_get_account_converts_timeout_to_domain_error() -> None:
    respx.get("https://accounts.example.test/accounts/acct_001").mock(
        side_effect=httpx.ReadTimeout("Upstream service did not respond")
    )
    client = AccountClient(base_url="https://accounts.example.test")

    with pytest.raises(ExternalServiceTimeoutError):
        await client.get_account("acct_001")


@respx.mock
@pytest.mark.asyncio
async def test_get_account_rejects_malformed_upstream_data() -> None:
    respx.get("https://accounts.example.test/accounts/acct_001").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "acct_001",
                "name": "Avery Patel",
                "status": "active",
                # "tier" is deliberately missing
            },
        )
    )
    client = AccountClient(base_url="https://accounts.example.test")

    with pytest.raises(ExternalServiceInvalidResponseError):
        await client.get_account("acct_001")


@respx.mock
@pytest.mark.asyncio
async def test_get_account_retries_three_times_before_failing() -> None:
    route = respx.get("https://accounts.example.test/accounts/acct_001").mock(
        return_value=httpx.Response(503)
    )
    client = AccountClient(base_url="https://accounts.example.test")

    with pytest.raises(ExternalServiceUnavailableError):
        await client.get_account("acct_001")

    assert route.call_count == 3


def test_account_endpoint_returns_database_account() -> None:
    response = TestClient(app).get("/api/v1/accounts/acct_001")

    assert response.status_code == 200
    assert response.json()["external_id"] == "acct_001"
    assert response.json()["name"] == "Avery Patel"
