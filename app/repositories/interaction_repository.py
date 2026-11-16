from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Interaction


async def list_interactions_for_account(
    session: AsyncSession,
    account_id: UUID,
    *,
    limit: int,
    offset: int,
) -> list[Interaction]:
    result = await session.execute(
        select(Interaction)
        .where(Interaction.account_id == account_id)
        .order_by(Interaction.occurred_at.desc(), Interaction.id)
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())
