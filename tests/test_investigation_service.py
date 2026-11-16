import pytest

from app.llm.fake import FakeLLMProvider
from app.schemas.ai import (
    AgentTurn,
    InvestigationRequest,
    RecommendationResponse,
    ToolCall,
    ToolName,
)
from app.services.investigation import InvestigationService
from app.tools.registry import ToolDefinition, ToolRegistry
from app.tools.schemas import GetAccountInput


async def account_handler(arguments: GetAccountInput) -> dict[str, str]:
    return {"account_id": arguments.account_id, "status": "active"}


def registry() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register(
        ToolDefinition(
            name=ToolName.GET_ACCOUNT,
            description="Retrieve an account.",
            input_model=GetAccountInput,
            handler=account_handler,
            read_only=True,
            requires_approval=False,
        )
    )
    return tools


def request(question: str = "Show the account details") -> InvestigationRequest:
    return InvestigationRequest(
        account_id="acct_001",
        question=question,
        include_policy=False,
    )


@pytest.mark.asyncio
async def test_investigation_returns_direct_final_response() -> None:
    service = InvestigationService(
        provider=FakeLLMProvider(),
        tool_registry=registry(),
    )

    state = await service.investigate(request())

    assert state.completed is True
    assert len(state.tool_calls) == 1
    assert state.tool_results[0].data == {"account_id": "acct_001", "status": "active"}
    assert state.recommendation is not None


@pytest.mark.asyncio
async def test_investigation_executes_tool_then_returns_final_response() -> None:
    final = RecommendationResponse(
        summary="Account is active.",
        recommendation="Review the latest account activity.",
        confidence=0.9,
        requires_approval=False,
        evidence_sufficient=True,
    )
    provider = FakeLLMProvider(
        responses=[
            AgentTurn(
                tool_call=ToolCall(
                    call_id="call_001",
                    tool_name=ToolName.GET_ACCOUNT,
                    arguments={"account_id": "acct_001"},
                )
            ),
            AgentTurn(final_response=final),
        ]
    )
    service = InvestigationService(provider=provider, tool_registry=registry())

    state = await service.investigate(request("What should we do next for this account?"))

    assert state.completed is True
    assert len(state.tool_calls) == 1
    assert state.tool_results[0].data == {"account_id": "acct_001", "status": "active"}
    assert state.recommendation == final
