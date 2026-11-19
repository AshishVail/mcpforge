from mcpforge.config.models import (
    ApiSourceConfig,
    NoAuthConfig,
    ProjectConfig,
)
from mcpforge.domain.enums import HttpMethod
from mcpforge.domain.models import Endpoint
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.generation.models import ToolDefinition
from mcpforge.mcp.adapter import MCPAdapter


class FakeServer:
    def __init__(self) -> None:
        self.registered: list[tuple[str, str]] = []

    def tool(self, *, name: str, description: str):
        def decorator(callback):
            self.registered.append((name, description))
            return callback

        return decorator


def test_adapter_registers_generated_tools() -> None:
    endpoint = Endpoint(
        operation_id="list_users",
        path="/users",
        method=HttpMethod.GET,
    )
    tool = ToolDefinition(
        name="list_users",
        description="List users.",
        endpoint_path="/users",
        method="GET",
        operation_id="list_users",
        input_schema={
            "type": "object",
            "properties": {},
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
    adapter = MCPAdapter(
        ExecutionEngine(config, HTTPClient()),
        [endpoint],
        [tool],
    )
    server = FakeServer()

    adapter.register(server)

    assert server.registered == [("list_users", "List users.")]
