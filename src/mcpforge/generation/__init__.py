"""MCP tool generation."""

from mcpforge.generation.collisions import unique_names
from mcpforge.generation.descriptions import endpoint_description
from mcpforge.generation.input_schema import build_input_schema, schema_to_json
from mcpforge.generation.models import ToolDefinition, ToolParameter
from mcpforge.generation.naming import default_tool_name
from mcpforge.generation.service import generate_tools

__all__ = [
    "ToolDefinition",
    "ToolParameter",
    "build_input_schema",
    "default_tool_name",
    "endpoint_description",
    "generate_tools",
    "schema_to_json",
    "unique_names",
]
