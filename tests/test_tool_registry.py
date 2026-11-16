import pytest

from app.schemas.ai import ToolCall, ToolName, ToolStatus
from app.tools.registry import ToolDefinition, ToolRegistry
from app.tools.schemas import CreateFollowUpTaskInput, GetAccountInput


async def account_handler(arguments: GetAccountInput) -> dict[str, str]:
    return {"account_id": arguments.account_id, "status": "active"}


async def task_handler(arguments: CreateFollowUpTaskInput) -> dict[str, str]:
    return {"task_id": "task_001", "account_id": arguments.account_id}


def make_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name=ToolName.GET_ACCOUNT,
            description="Retrieve an account.",
            input_model=GetAccountInput,
            handler=account_handler,
            read_only=True,
            requires_approval=False,
        )
    )
    registry.register(
        ToolDefinition(
            name=ToolName.CREATE_FOLLOW_UP_TASK,
            description="Create a follow-up task.",
            input_model=CreateFollowUpTaskInput,
            handler=task_handler,
            read_only=False,
            requires_approval=True,
        )
    )
    return registry


@pytest.mark.asyncio
async def test_registry_validates_and_executes_allowed_tool() -> None:
    result = await make_registry().execute(
        ToolCall(
            call_id="call_001",
            tool_name=ToolName.GET_ACCOUNT,
            arguments={"account_id": "acct_001"},
        ),
        allowed_tools={ToolName.GET_ACCOUNT},
    )

    assert result.status is ToolStatus.SUCCESS
    assert result.data == {"account_id": "acct_001", "status": "active"}


@pytest.mark.asyncio
async def test_registry_rejects_invalid_arguments() -> None:
    result = await make_registry().execute(
        ToolCall(call_id="call_002", tool_name=ToolName.GET_ACCOUNT, arguments={}),
        allowed_tools={ToolName.GET_ACCOUNT},
    )

    assert result.status is ToolStatus.VALIDATION_ERROR
    assert result.error_code == "INVALID_TOOL_ARGUMENTS"


@pytest.mark.asyncio
async def test_registry_rejects_tool_outside_allow_list() -> None:
    result = await make_registry().execute(
        ToolCall(
            call_id="call_003",
            tool_name=ToolName.GET_ACCOUNT,
            arguments={"account_id": "acct_001"},
        ),
        allowed_tools=set(),
    )

    assert result.status is ToolStatus.VALIDATION_ERROR
    assert result.error_code == "TOOLNOTALLOWEDERROR"


@pytest.mark.asyncio
async def test_registry_requires_approval_for_side_effect() -> None:
    result = await make_registry().execute(
        ToolCall(
            call_id="call_004",
            tool_name=ToolName.CREATE_FOLLOW_UP_TASK,
            arguments={
                "account_id": "acct_001",
                "title": "Review account",
                "description": "Review the account.",
                "idempotency_key": "investigation_001",
            },
        ),
        allowed_tools={ToolName.CREATE_FOLLOW_UP_TASK},
    )

    assert result.status is ToolStatus.VALIDATION_ERROR
    assert result.error_code == "TOOLAPPROVALREQUIREDERROR"


@pytest.mark.asyncio
async def test_registry_executes_side_effect_only_with_approval() -> None:
    result = await make_registry().execute(
        ToolCall(
            call_id="call_005",
            tool_name=ToolName.CREATE_FOLLOW_UP_TASK,
            arguments={
                "account_id": "acct_001",
                "title": "Review account",
                "description": "Review the account.",
                "idempotency_key": "investigation_001",
            },
        ),
        allowed_tools={ToolName.CREATE_FOLLOW_UP_TASK},
        approval_granted=True,
    )

    assert result.status is ToolStatus.SUCCESS
    assert result.data == {"task_id": "task_001", "account_id": "acct_001"}
