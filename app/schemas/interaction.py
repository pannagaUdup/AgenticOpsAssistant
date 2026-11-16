from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    interaction_type: str
    summary: str
    occurred_at: datetime
