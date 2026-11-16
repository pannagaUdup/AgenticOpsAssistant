from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Intent(StrEnum):
    ACCOUNT_LOOKUP = "account_lookup"
    INTERACTION_SUMMARY = "interaction_summary"
    POLICY_QUESTION = "policy_question"
    RECOMMEND_NEXT_ACTION = "recommend_next_action"
    CREATE_FOLLOW_UP = "create_follow_up"
    UNSUPPORTED = "unsupported"


class ModelTier(StrEnum):
    FAST = "fast"
    STANDARD = "standard"
    REASONING = "reasoning"


class ToolName(StrEnum):
    GET_ACCOUNT = "get_account"
    GET_INTERACTION_HISTORY = "get_interaction_history"
    SEARCH_POLICY = "search_policy"
    CREATE_FOLLOW_UP_TASK = "create_follow_up_task"


class ToolStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class InvestigationRequest(BaseModel):
    account_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=4_000)
    include_policy: bool = True
    requested_action: str | None = Field(default=None, max_length=1_000)


class RoutingDecision(BaseModel):
    intent: Intent
    required_tools: list[ToolName] = Field(default_factory=list)
    model_tier: ModelTier
    prompt_name: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    requires_approval: bool
    max_tool_calls: int = Field(default=5, ge=0, le=20)


class IntentClassification(BaseModel):
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = Field(min_length=1)


class ToolCall(BaseModel):
    call_id: str = Field(min_length=1)
    tool_name: ToolName
    arguments: dict[str, object]


class ToolResult(BaseModel):
    call_id: str = Field(min_length=1)
    tool_name: ToolName
    status: ToolStatus
    data: dict[str, object] | list[dict[str, object]] | None = None
    error_code: str | None = None
    error_message: str | None = None


class EvidenceReference(BaseModel):
    evidence_id: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    title: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    excerpt: str = Field(min_length=1)


class ProposedFollowUpTask(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2_000)
    due_at: datetime | None = None
    reason: str = Field(min_length=1, max_length=1_000)


class RecommendationResponse(BaseModel):
    summary: str = Field(min_length=1, max_length=4_000)
    recommendation: str = Field(min_length=1, max_length=4_000)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    proposed_task: ProposedFollowUpTask | None = None
    requires_approval: bool
    evidence_sufficient: bool
    limitations: list[str] = Field(default_factory=list)


class AgentTurn(BaseModel):
    tool_call: ToolCall | None = None
    final_response: RecommendationResponse | None = None

    def model_post_init(self, __context: object) -> None:
        if (self.tool_call is None) == (self.final_response is None):
            raise ValueError("AgentTurn must contain exactly one of tool_call or final_response")


class ApprovalRequest(BaseModel):
    recommendation_id: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    proposed_task: ProposedFollowUpTask
    status: ApprovalStatus = ApprovalStatus.PENDING
    expires_at: datetime | None = None


class ApprovalDecision(BaseModel):
    approval_id: str = Field(min_length=1)
    status: ApprovalStatus
    decided_by: str = Field(min_length=1)
    comment: str | None = Field(default=None, max_length=1_000)


class InvestigationState(BaseModel):
    investigation_id: str = Field(min_length=1)
    request: InvestigationRequest
    routing: RoutingDecision | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    recommendation: RecommendationResponse | None = None
    approval: ApprovalRequest | None = None
    completed: bool = False
