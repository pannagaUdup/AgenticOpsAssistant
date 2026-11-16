from datetime import datetime

from pydantic import BaseModel, Field


class GetAccountInput(BaseModel):
    account_id: str = Field(min_length=1)


class GetInteractionHistoryInput(BaseModel):
    account_id: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchPolicyInput(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    document_id: str | None = Field(default=None, min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class CreateFollowUpTaskInput(BaseModel):
    account_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2_000)
    due_at: datetime | None = None
    idempotency_key: str = Field(min_length=1, max_length=200)
