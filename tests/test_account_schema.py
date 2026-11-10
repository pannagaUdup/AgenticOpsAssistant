import pytest
from pydantic import ValidationError

from app.models.account import Account
from app.schemas.account import AccountResponse


def test_account_response_accepts_valid_data() -> None:
    account = AccountResponse.model_validate(
        {
            "id": "acct_001",
            "name": "Avery Patel",
            "status": "active",
            "tier": "standard",
        }
    )

    assert account.id == "acct_001"
    assert account.status == "active"


def test_account_response_rejects_missing_tier() -> None:
    with pytest.raises(ValidationError):
        AccountResponse.model_validate(
            {
                "id": "acct_001",
                "name": "Avery Patel",
                "status": "active",
            }
        )


def test_account_can_be_created_from_validated_response() -> None:
    response = AccountResponse(
        id="acct_001",
        name="Avery Patel",
        status="active",
        tier="standard",
    )

    account = Account.from_response(response)

    assert account.id == "acct_001"
    assert account.name == "Avery Patel"
