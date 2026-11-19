import pytest

from mcpforge.config.models import (
    ApiSourceConfig,
    NoAuthConfig,
    ProjectConfig,
)
from mcpforge.domain.enums import HttpMethod, ParameterLocation
from mcpforge.domain.models import Endpoint, Parameter
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.generation.models import ToolDefinition
from mcpforge.mcp.tools import ToolInvocationError, validate_tool_arguments


def make_tool() -> ToolDefinition:
    return ToolDefinition(
        name="get_user",
        description="Get a user.",
        endpoint_path="/users/{id}",
        method="GET",
        input_schema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    )


def test_validate_tool_arguments() -> None:
    assert validate_tool_arguments(make_tool(), {"id": 10}) == {"id": 10}


def test_validate_tool_arguments_rejects_missing_required_field() -> None:
    with pytest.raises(ToolInvocationError):
        validate_tool_arguments(make_tool(), {})


def test_validate_tool_arguments_rejects_unknown_field() -> None:
    with pytest.raises(ToolInvocationError):
        validate_tool_arguments(make_tool(), {"id": 10, "unknown": True})


def test_endpoint_contract_can_be_created_for_tool_execution() -> None:
    endpoint = Endpoint(
        operation_id="get_user",
        path="/users/{id}",
        method=HttpMethod.GET,
        parameters=[
            Parameter(
                name="id",
                location=ParameterLocation.PATH,
                required=True,
            )
        ],
    )
    config = ProjectConfig(
        source=ApiSourceConfig(
            location="https://api.example.com/openapi.json",
            base_url="https://api.example.com",
        ),
        auth=NoAuthConfig(),
    )
    engine = ExecutionEngine(config, HTTPClient())

    assert endpoint.operation_id == "get_user"
    assert engine.client is not None
