from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.account_repository import get_account_by_external_id
from app.schemas.account import AccountRead

router = APIRouter(prefix="/api/v1", tags=["accounts"])


@router.get(
    "/accounts/{external_id}",
    response_model=AccountRead,
)
async def get_account(
    external_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AccountRead:
    account = await get_account_by_external_id(session, external_id)

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account {external_id} not found",
        )

    return account
