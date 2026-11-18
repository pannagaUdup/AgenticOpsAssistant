from app.schemas.ai import (
    Intent,
    InvestigationRequest,
    ModelTier,
    RoutingDecision,
    ToolName,
)
from app.services.classifier import (
    AsyncSemanticIntentClassifier,
    HybridIntentClassifier,
    SemanticIntentClassifier,
)


class RequestRouter:
    """Selects a bounded workflow before any model or tool call is made."""

    def __init__(
        self,
        classifier: SemanticIntentClassifier | None = None,
        async_classifier: AsyncSemanticIntentClassifier | None = None,
    ) -> None:
        self._classifier = HybridIntentClassifier(classifier)
        self._async_classifier = async_classifier

    def route(self, request: InvestigationRequest) -> RoutingDecision:
        intent = self._classifier.classify(request).intent
        return self._route_from_intent(intent, request)

    def _route_from_intent(self, intent: Intent, request: InvestigationRequest) -> RoutingDecision:
        if intent is Intent.ACCOUNT_LOOKUP:
            return self._decision(
                intent=intent,
                tools=[ToolName.GET_ACCOUNT],
                model_tier=ModelTier.FAST,
                prompt_name="investigation_system",
                requires_approval=False,
                max_tool_calls=2,
            )

        if intent is Intent.INTERACTION_SUMMARY:
            return self._decision(
                intent=intent,
                tools=[ToolName.GET_ACCOUNT, ToolName.GET_INTERACTION_HISTORY],
                model_tier=ModelTier.STANDARD,
                prompt_name="investigation_system",
                requires_approval=False,
                max_tool_calls=4,
            )

        if intent is Intent.POLICY_QUESTION:
            return self._decision(
                intent=intent,
                tools=[ToolName.SEARCH_POLICY],
                model_tier=ModelTier.STANDARD,
                prompt_name="policy_qa_system",
                requires_approval=False,
                max_tool_calls=3,
            )

        if intent is Intent.RECOMMEND_NEXT_ACTION:
            tools = [ToolName.GET_ACCOUNT, ToolName.GET_INTERACTION_HISTORY]
            if request.include_policy:
                tools.append(ToolName.SEARCH_POLICY)

            return self._decision(
                intent=intent,
                tools=tools,
                model_tier=ModelTier.REASONING,
                prompt_name="recommendation_system",
                requires_approval=True,
                max_tool_calls=6,
            )

        if intent is Intent.CREATE_FOLLOW_UP:
            return self._decision(
                intent=intent,
                tools=[
                    ToolName.GET_ACCOUNT,
                    ToolName.GET_INTERACTION_HISTORY,
                    ToolName.CREATE_FOLLOW_UP_TASK,
                ],
                model_tier=ModelTier.REASONING,
                prompt_name="recommendation_system",
                requires_approval=True,
                max_tool_calls=6,
            )

        return self._decision(
            intent=Intent.UNSUPPORTED,
            tools=[],
            model_tier=ModelTier.FAST,
            prompt_name="classification_system",
            requires_approval=False,
            max_tool_calls=0,
        )

    async def route_async(self, request: InvestigationRequest) -> RoutingDecision:
        classification = await self._classifier.classify_async(request, self._async_classifier)
        return self._decision_for_intent(classification.intent, request)

    def _decision_for_intent(
        self, intent: Intent, request: InvestigationRequest
    ) -> RoutingDecision:
        return self._route_from_intent(intent, request)

    @staticmethod
    def _decision(
        *,
        intent: Intent,
        tools: list[ToolName],
        model_tier: ModelTier,
        prompt_name: str,
        requires_approval: bool,
        max_tool_calls: int,
    ) -> RoutingDecision:
        return RoutingDecision(
            intent=intent,
            required_tools=tools,
            model_tier=model_tier,
            prompt_name=prompt_name,
            prompt_version="v1",
            requires_approval=requires_approval,
            max_tool_calls=max_tool_calls,
        )
