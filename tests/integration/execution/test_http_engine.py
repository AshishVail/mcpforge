import httpx
import pytest
import respx

from mcpforge.config.models import (
    ApiSourceConfig,
    HttpConfig,
    NoAuthConfig,
    ProjectConfig,
)
from mcpforge.domain.enums import HttpMethod
from mcpforge.domain.models import Endpoint
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.engine import ExecutionEngine


@pytest.mark.asyncio
@respx.mock
async def test_http_engine_executes_normalized_endpoint() -> None:
    route = respx.get("https://api.example.com/users/123").mock(
        return_value=httpx.Response(200, json={"id": 123})
    )

    config = ProjectConfig(
        source=ApiSourceConfig(
            location="https://api.example.com/openapi.json",
            base_url="https://api.example.com",
        ),
        auth=NoAuthConfig(),
        http=HttpConfig(timeout_seconds=2),
    )
    endpoint = Endpoint(
        operation_id="get_user",
        path="/users/{id}",
        method=HttpMethod.GET,
        parameters=[
            {
                "name": "id",
                "location": "path",
                "required": True,
            }
        ],
    )

    client = HTTPClient(timeout_seconds=2)
    async with client.lifecycle():
        result = await ExecutionEngine(config, client).execute(
            endpoint,
            {"id": 123},
        )

    assert route.called
    assert result["ok"] is True
    assert result["data"] == {"id": 123}
