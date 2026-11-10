from pydantic import BaseModel, ConfigDict, Field


class AccountResponse(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: str = Field(min_length=1)
    tier: str = Field(min_length=1)


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    external_id: str
    name: str
    status: str
    tier: str
