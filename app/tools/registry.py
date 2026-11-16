from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from app.schemas.ai import ToolCall, ToolName, ToolResult, ToolStatus

ToolHandler = Callable[[BaseModel], Awaitable[dict[str, Any] | list[dict[str, Any]]]]


class ToolNotFoundError(LookupError):
    """Raised when a tool has not been registered."""


class ToolNotAllowedError(PermissionError):
    """Raised when a tool is outside the current routing decision."""


class ToolApprovalRequiredError(PermissionError):
    """Raised when a side-effecting tool lacks explicit approval."""


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: ToolName
    description: str
    input_model: type[BaseModel]
    handler: ToolHandler
    read_only: bool
    requires_approval: bool


class ToolRegistry:
    def __init__(self) -> None:
        self._definitions: dict[ToolName, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._definitions:
            raise ValueError(f"Tool already registered: {definition.name}")
        self._definitions[definition.name] = definition

    def get(self, name: ToolName) -> ToolDefinition:
        try:
            return self._definitions[name]
        except KeyError as error:
            raise ToolNotFoundError(f"Tool is not registered: {name}") from error

    def allowed_tools(self) -> set[ToolName]:
        return set(self._definitions)

    async def execute(
        self,
        call: ToolCall,
        *,
        allowed_tools: set[ToolName],
        approval_granted: bool = False,
    ) -> ToolResult:
        try:
            definition = self.get(call.tool_name)
            if call.tool_name not in allowed_tools:
                raise ToolNotAllowedError(f"Tool is not allowed: {call.tool_name}")
            if definition.requires_approval and not approval_granted:
                raise ToolApprovalRequiredError(f"Tool requires approval: {call.tool_name}")

            arguments = definition.input_model.model_validate(call.arguments)
            data = await definition.handler(arguments)
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                status=ToolStatus.SUCCESS,
                data=data,
            )
        except ValidationError as error:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                status=ToolStatus.VALIDATION_ERROR,
                error_code="INVALID_TOOL_ARGUMENTS",
                error_message=str(error),
            )
        except (ToolNotAllowedError, ToolApprovalRequiredError) as error:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                status=ToolStatus.VALIDATION_ERROR,
                error_code=type(error).__name__.upper(),
                error_message=str(error),
            )
        except Exception as error:
            return ToolResult(
                call_id=call.call_id,
                tool_name=call.tool_name,
                status=ToolStatus.FAILED,
                error_code="TOOL_EXECUTION_FAILED",
                error_message=str(error),
            )
