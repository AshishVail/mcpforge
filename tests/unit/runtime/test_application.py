from unittest.mock import AsyncMock

import pytest

from mcpforge.config.models import (
    ApiSourceConfig,
    NoAuthConfig,
    ProjectConfig,
)
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.generation.models import ToolDefinition
from mcpforge.runtime.application import RuntimeApplication
from mcpforge.runtime.dependencies import RuntimeDependencies


@pytest.mark.asyncio
async def test_application_manages_dependency_lifecycle() -> None:
    config = ProjectConfig(
        source=ApiSourceConfig(
            location="https://api.example.com/openapi.json",
            base_url="https://api.example.com",
        ),
        auth=NoAuthConfig(),
    )
    client = HTTPClient()
    client.start = AsyncMock()
    client.close = AsyncMock()

    dependencies = RuntimeDependencies(
        config=config,
        client=client,
        engine=ExecutionEngine(config, client),
        tools=(),
        server=object(),
        logger=__import__("logging").getLogger("test"),
    )
    application = RuntimeApplication(dependencies)

    async with application:
        client.start.assert_awaited_once()

    client.close.assert_awaited_once()


def test_application_exposes_server_and_tools() -> None:
    config = ProjectConfig(
        source=ApiSourceConfig(
            location="https://api.example.com/openapi.json",
            base_url="https://api.example.com",
        ),
        auth=NoAuthConfig(),
    )
    server = object()
    tool = ToolDefinition(
        name="list_users",
        description="List users.",
        endpoint_path="/users",
        method="GET",
    )
    client = HTTPClient()
    dependencies = RuntimeDependencies(
        config=config,
        client=client,
        engine=ExecutionEngine(config, client),
        tools=(tool,),
        server=server,
        logger=__import__("logging").getLogger("test"),
    )

    application = RuntimeApplication(dependencies)

    assert application.server is server
    assert application.tools == (tool,)
