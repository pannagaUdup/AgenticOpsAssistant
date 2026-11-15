from app.schemas.ai import Intent, InvestigationRequest, ModelTier, ToolName
from app.services.router import RequestRouter


def request(question: str, include_policy: bool = True) -> InvestigationRequest:
    return InvestigationRequest(
        account_id="acct_001",
        question=question,
        include_policy=include_policy,
    )


def test_router_selects_account_lookup() -> None:
    decision = RequestRouter().route(request("Show the account details"))

    assert decision.intent is Intent.ACCOUNT_LOOKUP
    assert decision.required_tools == [ToolName.GET_ACCOUNT]
    assert decision.model_tier is ModelTier.FAST
    assert decision.requires_approval is False


def test_router_selects_interaction_summary() -> None:
    decision = RequestRouter().route(request("Summarize the interaction history"))

    assert decision.intent is Intent.INTERACTION_SUMMARY
    assert decision.required_tools == [
        ToolName.GET_ACCOUNT,
        ToolName.GET_INTERACTION_HISTORY,
    ]


def test_router_selects_policy_question() -> None:
    decision = RequestRouter().route(request("What does the billing policy allow?"))

    assert decision.intent is Intent.POLICY_QUESTION
    assert decision.required_tools == [ToolName.SEARCH_POLICY]
    assert decision.prompt_name == "policy_qa_system"


def test_router_selects_recommendation_with_policy() -> None:
    decision = RequestRouter().route(request("What should we do next?"))

    assert decision.intent is Intent.RECOMMEND_NEXT_ACTION
    assert ToolName.SEARCH_POLICY in decision.required_tools
    assert decision.model_tier is ModelTier.REASONING
    assert decision.requires_approval is True


def test_router_can_skip_policy_for_recommendation() -> None:
    decision = RequestRouter().route(request("Recommend the next action", include_policy=False))

    assert decision.intent is Intent.RECOMMEND_NEXT_ACTION
    assert ToolName.SEARCH_POLICY not in decision.required_tools


def test_create_task_has_highest_precedence_and_requires_approval() -> None:
    decision = RequestRouter().route(
        request("Create a follow-up task and recommend what we should do")
    )

    assert decision.intent is Intent.CREATE_FOLLOW_UP
    assert ToolName.CREATE_FOLLOW_UP_TASK in decision.required_tools
    assert decision.requires_approval is True


def test_router_marks_unknown_request_unsupported() -> None:
    decision = RequestRouter().route(request("Tell me a joke"))

    assert decision.intent is Intent.UNSUPPORTED
    assert decision.required_tools == []
    assert decision.max_tool_calls == 0
