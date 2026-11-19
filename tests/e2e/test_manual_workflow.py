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
from mcpforge.generation.service import generate_tools
from mcpforge.ingestion.service import ingest_path
from mcpforge.mcp.tools import make_tool_callback


@pytest.mark.asyncio
@respx.mock
async def test_manual_yaml_to_mcp_tool_execution(tmp_path) -> None:
    specification = tmp_path / "manual.yaml"
    specification.write_text(
        """
name: Manual E2E API
base_url: https://api.example.com
endpoints:
  - operation_id: get_health
    method: GET
    path: /health
    responses:
      - status_code: 200
        description: Healthy
""",
        encoding="utf-8",
    )

    route = respx.get("https://api.example.com/health").mock(
        return_value=httpx.Response(
            200,
            json={"status": "healthy"},
        )
    )

    document = ingest_path(specification, format="manual")
    filtered = filter_document(document)
    tools = generate_tools(filtered)

    assert len(tools) == 1
    assert tools[0].name == "get_health"

    config = ProjectConfig(
        source=ApiSourceConfig(
            location=str(specification),
            format="manual",
            base_url="https://api.example.com",
        ),
        auth=NoAuthConfig(),
    )

    async with HTTPClient().lifecycle() as client:
        callback = make_tool_callback(
            tools[0],
            filtered.endpoints[0],
            ExecutionEngine(config, client),
        )
        result = await callback()

    assert route.called
    assert result["ok"] is True
    assert result["data"] == {"status": "healthy"}
