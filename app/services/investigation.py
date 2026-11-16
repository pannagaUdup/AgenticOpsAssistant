import json
from uuid import uuid4

from app.llm.provider import LLMProvider
from app.prompts import PromptRegistry
from app.schemas.ai import (
    AgentTurn,
    Intent,
    InvestigationRequest,
    InvestigationState,
    RecommendationResponse,
    ToolCall,
    ToolName,
    ToolStatus,
)
from app.services.router import RequestRouter
from app.tools.registry import ToolRegistry


class InvestigationService:
    """Runs a bounded model → tool → result loop for one investigation."""

    def __init__(
        self,
        *,
        provider: LLMProvider,
        tool_registry: ToolRegistry,
        router: RequestRouter | None = None,
        prompt_registry: PromptRegistry | None = None,
    ) -> None:
        self._provider = provider
        self._tool_registry = tool_registry
        self._router = router or RequestRouter()
        self._prompt_registry = prompt_registry or PromptRegistry()

    async def investigate(self, request: InvestigationRequest) -> InvestigationState:
        routing = self._router.route(request)
        state = InvestigationState(
            investigation_id=str(uuid4()),
            request=request,
            routing=routing,
        )
        prompt = self._prompt_registry.load(routing.prompt_name, routing.prompt_version)

        if routing.intent is Intent.ACCOUNT_LOOKUP:
            return await self._direct_account_lookup(state, request, prompt.content)

        conversation = request.question
        seen_calls: set[tuple[str, str]] = set()

        for _ in range(routing.max_tool_calls + 1):
            turn = await self._provider.generate_structured(
                system_prompt=prompt.content,
                user_prompt=conversation,
                response_model=AgentTurn,
                tools=routing.required_tools,
            )

            if turn.final_response is not None:
                state.recommendation = turn.final_response
                state.completed = True
                return state

            tool_call = self._require_tool_call(turn)
            call_key = (tool_call.tool_name.value, json.dumps(tool_call.arguments, sort_keys=True))
            if call_key in seen_calls:
                state.recommendation = self._failure_recommendation(
                    "The model repeated the same tool call, so the investigation "
                    "was stopped safely."
                )
                state.completed = True
                return state

            seen_calls.add(call_key)
            state.tool_calls.append(tool_call)
            result = await self._tool_registry.execute(
                tool_call,
                allowed_tools=set(routing.required_tools),
            )
            state.tool_results.append(result)
            conversation = json.dumps(
                {
                    "original_question": request.question,
                    "latest_tool_result": result.model_dump(mode="json"),
                }
            )

        state.recommendation = self._failure_recommendation(
            "The investigation reached its maximum tool-call limit."
        )
        state.completed = True
        return state

    async def _direct_account_lookup(
        self,
        state: InvestigationState,
        request: InvestigationRequest,
        _prompt_content: str,
    ) -> InvestigationState:
        """Execute an unambiguous read without spending a model call."""
        tool_call = ToolCall(
            call_id="direct-account-lookup",
            tool_name=ToolName.GET_ACCOUNT,
            arguments={"account_id": request.account_id},
        )
        result = await self._tool_registry.execute(
            tool_call,
            allowed_tools={ToolName.GET_ACCOUNT},
        )
        state.tool_calls.append(tool_call)
        state.tool_results.append(result)

        if result.status is not ToolStatus.SUCCESS or not isinstance(result.data, dict):
            state.recommendation = self._failure_recommendation(
                result.error_message or "The account lookup failed."
            )
        else:
            account = result.data
            state.recommendation = RecommendationResponse(
                summary=f"Account {account.get('id', request.account_id)} was found.",
                recommendation=(
                    f"The account is {account.get('status', 'unknown')} and belongs to the "
                    f"{account.get('tier', 'unknown')} tier."
                ),
                confidence=1.0,
                evidence_sufficient=True,
                requires_approval=False,
                limitations=["This direct lookup did not require model reasoning."],
            )
        state.completed = True
        return state

    @staticmethod
    def _require_tool_call(turn: AgentTurn) -> ToolCall:
        if turn.tool_call is None:
            raise RuntimeError("Agent turn contained neither a tool call nor a final response")
        return turn.tool_call

    @staticmethod
    def _failure_recommendation(reason: str) -> RecommendationResponse:
        return RecommendationResponse(
            summary="The investigation could not complete safely.",
            recommendation=(
                "Review the investigation state and retry after correcting the workflow input."
            ),
            confidence=0.0,
            requires_approval=False,
            evidence_sufficient=False,
            limitations=[reason],
        )
