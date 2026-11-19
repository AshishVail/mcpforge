"""Generated-tool invocation and argument validation."""

from collections.abc import Awaitable, Callable, Mapping
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, ValidationError, create_model

from mcpforge.domain.models import Endpoint
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.execution.errors import ExecutionFailure
from mcpforge.generation.models import ToolDefinition
from mcpforge.mcp.errors import failure_result


class ToolInvocationError(Exception):
    """Raised when tool arguments are invalid."""


class ToolInvocation(BaseModel):
    """Validated invocation arguments."""

    model_config = ConfigDict(extra="forbid")

    values: dict[str, Any]


def _annotation_for_schema(schema: Mapping[str, Any]) -> Any:
    schema_type = schema.get("type")

    if schema_type == "string":
        return str
    if schema_type == "integer":
        return int
    if schema_type == "number":
        return float
    if schema_type == "boolean":
        return bool
    if schema_type == "array":
        return list
    if schema_type == "object":
        return dict
    return Any


def _argument_model(tool: ToolDefinition) -> type[BaseModel]:
    """Create a strict Pydantic model from a generated tool schema."""

    properties = tool.input_schema.get("properties", {})
    required = set(tool.input_schema.get("required", []))
    fields: dict[str, tuple[Any, Any]] = {}

    for name, schema in properties.items():
        annotation = _annotation_for_schema(schema)
        default = ... if name in required else None
        fields[name] = (annotation, default)

    return cast(
        type[BaseModel],
        create_model(  # type: ignore[call-overload]
            f"{tool.name.title().replace('_', '')}Arguments",
            __config__=ConfigDict(extra="forbid"),
            **fields,
        ),
    )


def validate_tool_arguments(
    tool: ToolDefinition,
    arguments: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate and normalize arguments against a generated tool schema."""

    model = _argument_model(tool)

    try:
        validated = model.model_validate(dict(arguments or {}))
    except ValidationError as exc:
        raise ToolInvocationError(str(exc)) from exc

    return dict(validated.model_dump(exclude_none=False))


def make_tool_callback(
    tool: ToolDefinition,
    endpoint: Endpoint,
    engine: ExecutionEngine,
) -> Callable[[Mapping[str, Any] | None], Awaitable[dict[str, Any]]]:
    """Create the async callback used by the MCP adapter."""

    async def callback(arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
        try:
            values = validate_tool_arguments(tool, arguments)
        except ToolInvocationError as exc:
            return {
                "ok": False,
                "error": {
                    "category": "tool_validation_error",
                    "message": str(exc),
                    "retryable": False,
                },
            }

        try:
            return await engine.execute(endpoint, values)
        except ExecutionFailure as exc:
            return failure_result(exc)

    callback.__name__ = tool.name
    callback.__doc__ = tool.description
    return callback
