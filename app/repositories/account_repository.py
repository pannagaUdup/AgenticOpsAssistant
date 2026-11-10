from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Account


async def get_account_by_external_id(
    session: AsyncSession,
    external_id: str,
) -> Account | None:
    result = await session.execute(select(Account).where(Account.external_id == external_id))
    return result.scalar_one_or_none()
