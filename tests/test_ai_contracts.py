import pytest
from pydantic import ValidationError

from app.llm.fake import FakeLLMProvider
from app.schemas.ai import (
    EvidenceReference,
    Intent,
    InvestigationRequest,
    ModelTier,
    RecommendationResponse,
    RoutingDecision,
    ToolName,
)


def test_investigation_request_requires_question() -> None:
    with pytest.raises(ValidationError):
        InvestigationRequest(account_id="acct_001", question="")


def test_routing_decision_declares_tools_and_approval() -> None:
    decision = RoutingDecision(
        intent=Intent.RECOMMEND_NEXT_ACTION,
        required_tools=[ToolName.GET_ACCOUNT, ToolName.SEARCH_POLICY],
        model_tier=ModelTier.REASONING,
        prompt_name="recommendation_system",
        prompt_version="v1",
        requires_approval=True,
    )

    assert ToolName.SEARCH_POLICY in decision.required_tools
    assert decision.requires_approval is True


def test_evidence_rejects_invalid_page_number() -> None:
    with pytest.raises(ValidationError):
        EvidenceReference(
            evidence_id="policy_chunk_1",
            source_type="policy_document",
            source_id="policy_1",
            page_number=0,
            excerpt="Policy text",
        )


@pytest.mark.asyncio
async def test_fake_provider_returns_validated_recommendation() -> None:
    provider = FakeLLMProvider()

    response = await provider.generate_structured(
        system_prompt="system",
        user_prompt="investigate acct_001",
        response_model=RecommendationResponse,
        tools=[],
    )

    assert response.confidence == 0.75
    assert response.evidence_sufficient is False


@pytest.mark.asyncio
async def test_fake_provider_rejects_unsupported_response_model() -> None:
    provider = FakeLLMProvider()

    with pytest.raises(ValueError):
        await provider.generate_structured(
            system_prompt="system",
            user_prompt="request",
            response_model=InvestigationRequest,
            tools=[],
        )
