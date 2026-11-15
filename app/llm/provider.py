from typing import Protocol, TypeVar

from pydantic import BaseModel

from app.schemas.ai import ToolName

ResponseT = TypeVar("ResponseT", bound=BaseModel)


class LLMProvider(Protocol):
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[ResponseT],
        tools: list[ToolName],
    ) -> ResponseT: ...
