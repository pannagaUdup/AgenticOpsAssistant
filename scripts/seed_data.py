import asyncio
from datetime import UTC, datetime

from sqlalchemy import select

from app.db.models import Account, FollowUpTask, Interaction, User
from app.db.session import AsyncSessionFactory


async def seed() -> None:
    async with AsyncSessionFactory() as session:
        users = [
            ("alex@example.test",),
            ("priya@example.test",),
            ("sam@example.test",),
        ]

        for (email,) in users:
            existing_user = await session.scalar(select(User).where(User.email == email))
            if existing_user is None:
                session.add(User(email=email))

        accounts_data = [
            ("acct_001", "Avery Patel", "active", "standard"),
            ("acct_002", "Jordan Lee", "active", "premium"),
            ("acct_003", "Morgan Chen", "inactive", "standard"),
        ]

        accounts: dict[str, Account] = {}

        for external_id, name, status, tier in accounts_data:
            account = await session.scalar(
                select(Account).where(Account.external_id == external_id)
            )

            if account is None:
                account = Account(
                    external_id=external_id,
                    name=name,
                    status=status,
                    tier=tier,
                )
                session.add(account)
                await session.flush()

            accounts[external_id] = account

        interactions_data = [
            ("acct_001", "email", "Customer asked about a billing adjustment."),
            ("acct_001", "call", "Support reviewed the account and promised a follow-up."),
            ("acct_002", "chat", "Customer requested an upgrade to premium support."),
            ("acct_003", "email", "Customer notified support that the account is inactive."),
        ]

        for external_id, interaction_type, summary in interactions_data:
            account = accounts[external_id]

            existing_interaction = await session.scalar(
                select(Interaction).where(
                    Interaction.account_id == account.id,
                    Interaction.summary == summary,
                )
            )

            if existing_interaction is None:
                session.add(
                    Interaction(
                        account_id=account.id,
                        interaction_type=interaction_type,
                        summary=summary,
                        occurred_at=datetime.now(UTC),
                    )
                )

        tasks_data = [
            ("acct_001", "Review billing adjustment", "open"),
            ("acct_002", "Confirm premium-support upgrade", "pending"),
            ("acct_003", "Contact inactive customer", "open"),
        ]

        for external_id, title, task_status in tasks_data:
            account = accounts[external_id]

            existing_task = await session.scalar(
                select(FollowUpTask).where(
                    FollowUpTask.account_id == account.id,
                    FollowUpTask.title == title,
                )
            )

            if existing_task is None:
                session.add(
                    FollowUpTask(
                        account_id=account.id,
                        title=title,
                        description=f"Follow up with {account.name}.",
                        status=task_status,
                    )
                )

        await session.commit()

    print("Synthetic seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
