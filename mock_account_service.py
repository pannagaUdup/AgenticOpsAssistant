from fastapi import FastAPI, HTTPException

from app.schemas.account import AccountResponse

mock_app = FastAPI(title="Mock Account Service")

ACCOUNTS = {
    "acct_001": AccountResponse(
        id="acct_001",
        name="Avery Patel",
        status="active",
        tier="standard",
    )
}


@mock_app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_mock_account(account_id: str) -> AccountResponse:
    account = ACCOUNTS.get(account_id)

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return account
