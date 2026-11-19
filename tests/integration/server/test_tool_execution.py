import httpx
import pytest
import respx

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
from mcpforge.mcp.tools import make_tool_callback


@pytest.mark.asyncio
@respx.mock
async def test_mcp_tool_callback_executes_upstream_request() -> None:
    route = respx.get("https://api.example.com/users/42").mock(
        return_value=httpx.Response(200, json={"id": 42})
    )

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
    tool = ToolDefinition(
        name="get_user",
        description="Get a user.",
        endpoint_path="/users/{id}",
        method="GET",
        operation_id="get_user",
        input_schema={
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
            "additionalProperties": False,
        },
    )
    config = ProjectConfig(
        source=ApiSourceConfig(
            location="https://api.example.com/openapi.json",
            base_url="https://api.example.com",
        ),
        auth=NoAuthConfig(),
    )
    client = HTTPClient()
    async with client.lifecycle():
        callback = make_tool_callback(
            tool,
            endpoint,
            ExecutionEngine(config, client),
        )
        result = await callback({"id": 42})

    assert route.called
    assert result["ok"] is True
    assert result["data"] == {"id": 42}
