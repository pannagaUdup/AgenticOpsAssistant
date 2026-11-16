from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.account_repository import get_account_by_external_id
from app.repositories.interaction_repository import list_interactions_for_account
from app.schemas.account import AccountRead
from app.schemas.ai import ToolName
from app.schemas.interaction import InteractionRead
from app.tools.registry import ToolDefinition, ToolRegistry
from app.tools.schemas import (
    GetAccountInput,
    GetInteractionHistoryInput,
    SearchPolicyInput,
)


async def _get_account(arguments: GetAccountInput, session: AsyncSession) -> dict:
    account = await get_account_by_external_id(session, arguments.account_id)
    if account is None:
        raise LookupError(f"Account not found: {arguments.account_id}")
    return AccountRead.model_validate(account).model_dump(mode="json")


async def _get_interaction_history(
    arguments: GetInteractionHistoryInput,
    session: AsyncSession,
) -> list[dict]:
    account = await get_account_by_external_id(session, arguments.account_id)
    if account is None:
        raise LookupError(f"Account not found: {arguments.account_id}")

    interactions = await list_interactions_for_account(
        session,
        account.id,
        limit=arguments.limit,
        offset=arguments.offset,
    )
    return [InteractionRead.model_validate(item).model_dump(mode="json") for item in interactions]


async def _search_policy(arguments: SearchPolicyInput) -> list[dict]:
    del arguments
    raise NotImplementedError("Policy retrieval will be implemented in the RAG phase")


def build_read_tool_registry(session: AsyncSession) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name=ToolName.GET_ACCOUNT,
            description="Retrieve account details by external account ID.",
            input_model=GetAccountInput,
            handler=lambda arguments: _get_account(cast(GetAccountInput, arguments), session),
            read_only=True,
            requires_approval=False,
        )
    )
    registry.register(
        ToolDefinition(
            name=ToolName.GET_INTERACTION_HISTORY,
            description="Retrieve recent customer interactions for an account.",
            input_model=GetInteractionHistoryInput,
            handler=lambda arguments: _get_interaction_history(
                cast(GetInteractionHistoryInput, arguments), session
            ),
            read_only=True,
            requires_approval=False,
        )
    )
    registry.register(
        ToolDefinition(
            name=ToolName.SEARCH_POLICY,
            description="Search policy evidence; implementation is added in the RAG phase.",
            input_model=SearchPolicyInput,
            handler=lambda arguments: _search_policy(cast(SearchPolicyInput, arguments)),
            read_only=True,
            requires_approval=False,
        )
    )
    return registry
