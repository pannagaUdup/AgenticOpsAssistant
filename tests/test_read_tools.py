import pytest
import pytest_asyncio

from app.db.session import AsyncSessionFactory, engine
from app.schemas.ai import ToolCall, ToolName, ToolStatus
from app.tools.read_tools import build_read_tool_registry


@pytest_asyncio.fixture(autouse=True)
async def dispose_database_engine() -> None:
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_account_tool_reads_postgres_account() -> None:
    async with AsyncSessionFactory() as session:
        result = await build_read_tool_registry(session).execute(
            ToolCall(
                call_id="read_001",
                tool_name=ToolName.GET_ACCOUNT,
                arguments={"account_id": "acct_001"},
            ),
            allowed_tools={ToolName.GET_ACCOUNT},
        )

    assert result.status is ToolStatus.SUCCESS
    assert result.data["external_id"] == "acct_001"


@pytest.mark.asyncio
async def test_interaction_tool_reads_paginated_history() -> None:
    async with AsyncSessionFactory() as session:
        result = await build_read_tool_registry(session).execute(
            ToolCall(
                call_id="read_002",
                tool_name=ToolName.GET_INTERACTION_HISTORY,
                arguments={"account_id": "acct_001", "limit": 1, "offset": 0},
            ),
            allowed_tools={ToolName.GET_INTERACTION_HISTORY},
        )

    assert result.status is ToolStatus.SUCCESS
    assert isinstance(result.data, list)
    assert len(result.data) <= 1


@pytest.mark.asyncio
async def test_policy_tool_is_explicitly_deferred_to_rag() -> None:
    async with AsyncSessionFactory() as session:
        result = await build_read_tool_registry(session).execute(
            ToolCall(
                call_id="read_003",
                tool_name=ToolName.SEARCH_POLICY,
                arguments={"query": "billing adjustment"},
            ),
            allowed_tools={ToolName.SEARCH_POLICY},
        )

    assert result.status is ToolStatus.FAILED
    assert result.error_code == "TOOL_EXECUTION_FAILED"
