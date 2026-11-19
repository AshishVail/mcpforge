import httpx
import pytest
import respx

from mcpforge.config.models import (
    ApiSourceConfig,
    NoAuthConfig,
    ProjectConfig,
)
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.filtering.evaluator import filter_document
from mcpforge.generation.models import ToolDefinition
from mcpforge.generation.service import generate_tools
from mcpforge.ingestion.service import ingest_path
from mcpforge.mcp.tools import make_tool_callback


@pytest.mark.asyncio
@respx.mock
async def test_openapi_to_mcp_tool_execution(tmp_path) -> None:
    specification = tmp_path / "openapi.yaml"
    specification.write_text(
        """
openapi: 3.0.3
info:
  title: E2E API
  version: "1.0.0"
servers:
  - url: https://api.example.com
paths:
  /users/{id}:
    get:
      operationId: get_user
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        "200":
          description: User
""",
        encoding="utf-8",
    )

    route = respx.get("https://api.example.com/users/42").mock(
        return_value=httpx.Response(
            200,
            json={"id": 42},
        )
    )

    document = ingest_path(specification, format="openapi")
    document = document.model_copy(update={"base_url": "https://api.example.com"})
    filtered = filter_document(document)
    tools = generate_tools(filtered)

    assert len(tools) == 1
    assert isinstance(tools[0], ToolDefinition)
    assert tools[0].name == "get_user"

    config = ProjectConfig(
        source=ApiSourceConfig(
            location=str(specification),
            format="openapi",
            base_url="https://api.example.com",
        ),
        auth=NoAuthConfig(),
    )

    endpoint = filtered.endpoints[0]
    async with HTTPClient().lifecycle() as client:
        callback = make_tool_callback(
            tools[0],
            endpoint,
            ExecutionEngine(config, client),
        )
        result = await callback({"id": 42})

    assert route.called
    assert result["ok"] is True
    assert result["data"] == {"id": 42}
