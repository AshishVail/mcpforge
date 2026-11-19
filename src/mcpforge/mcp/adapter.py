"""Official MCP SDK adapter."""

from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import Any

from mcpforge.domain.models import Endpoint
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.generation.models import ToolDefinition
from mcpforge.mcp.errors import ToolRegistrationError
from mcpforge.mcp.tools import make_tool_callback


class MCPAdapter:
    """Translate internal tool definitions into official MCP registrations."""

    def __init__(
        self,
        engine: ExecutionEngine,
        endpoints: Iterable[Endpoint],
        tools: Iterable[ToolDefinition],
    ) -> None:
        self.engine = engine
        self.endpoints = tuple(endpoints)
        self.tools = tuple(tools)
        self._endpoint_by_key = {
            self._endpoint_key(endpoint): endpoint
            for endpoint in self.endpoints
        }

    @staticmethod
    def _endpoint_key(endpoint: Endpoint) -> str:
        if endpoint.operation_id:
            return endpoint.operation_id
        return f"{endpoint.method.value}:{endpoint.path}"

    def endpoint_for_tool(self, tool: ToolDefinition) -> Endpoint:
        """Resolve the normalized endpoint represented by a tool."""

        if tool.operation_id:
            endpoint = self._endpoint_by_key.get(tool.operation_id)
            if endpoint is not None:
                return endpoint

        for endpoint in self.endpoints:
            if (
                endpoint.path == tool.endpoint_path
                and endpoint.method.value == tool.method
            ):
                return endpoint

        raise ToolRegistrationError(
            f"no endpoint found for generated tool {tool.name!r}"
        )

    def register(self, server: Any) -> None:
        """Register every generated tool on a FastMCP-compatible server."""

        register = getattr(server, "tool", None)
        if not callable(register):
            raise ToolRegistrationError(
                "MCP server does not expose a callable tool registration method"
            )

        for tool in self.tools:
            endpoint = self.endpoint_for_tool(tool)
            callback = make_tool_callback(tool, endpoint, self.engine)
            self._register_one(register, callback, tool)

    @staticmethod
    def _register_one(
        register: Any,
        callback: Any,
        tool: ToolDefinition,
    ) -> None:
        """Support current and older FastMCP decorator signatures."""

        try:
            result = register(
                name=tool.name,
                description=tool.description,
            )(callback)
        except TypeError:
            try:
                result = register(callback)
            except TypeError as exc:
                raise ToolRegistrationError(
                    f"could not register MCP tool {tool.name!r}"
                ) from exc

        if inspect.isawaitable(result):
            raise ToolRegistrationError(
                f"tool registration unexpectedly returned an awaitable: {tool.name!r}"
            )
