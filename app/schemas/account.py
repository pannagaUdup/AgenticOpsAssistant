from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: str = Field(min_length=1)
    tier: str = Field(min_length=1)