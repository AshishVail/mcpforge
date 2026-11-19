"""MCP server construction."""

from typing import Any

from mcpforge.domain.models import Endpoint
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.generation.models import ToolDefinition
from mcpforge.mcp.adapter import MCPAdapter
from mcpforge.mcp.transports import Transport, run_transport


def create_sdk_server(
    *,
    name: str = "mcpforge",
) -> Any:
    """Create an official FastMCP server instance."""

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "The official MCP SDK is required to create an MCP server"
        ) from exc

    return FastMCP(name)


def create_server(
    *,
    engine: ExecutionEngine,
    endpoints: tuple[Endpoint, ...],
    tools: tuple[ToolDefinition, ...],
    name: str = "mcpforge",
) -> Any:
    """Create an SDK server and register generated tools."""

    server = create_sdk_server(name=name)
    MCPAdapter(engine, endpoints, tools).register(server)
    return server


def serve_server(
    server: Any,
    transport: Transport | str,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> Any:
    """Run a configured MCP server."""

    return run_transport(server, transport, host=host, port=port)
