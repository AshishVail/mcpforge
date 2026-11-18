"""Generated MCP tool contracts."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolParameter(BaseModel):
    """AI-facing tool parameter metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str
    location: str
    required: bool = False
    schema: dict[str, Any] = Field(default_factory=dict)
    description: str | None = None


class ToolDefinition(BaseModel):
    """Transport-independent generated tool definition."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: str
    endpoint_path: str
    method: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    parameters: tuple[ToolParameter, ...] = ()
    operation_id: str | None = None
    deprecated: bool = False
