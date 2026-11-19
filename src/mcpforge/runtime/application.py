"""High-level MCPForge runtime application."""

from pathlib import Path
from typing import Any

from mcpforge.generation.models import ToolDefinition
from mcpforge.mcp.transports import Transport, run_transport
from mcpforge.runtime.dependencies import (
    RuntimeDependencies,
    build_dependencies,
)
from mcpforge.runtime.lifecycle import RuntimeLifecycle


class RuntimeApplication:
    """Coordinate configuration, ingestion, execution, and MCP serving."""

    def __init__(
        self,
        dependencies: RuntimeDependencies,
    ) -> None:
        self.dependencies = dependencies
        self.lifecycle = RuntimeLifecycle(dependencies.client)

    @classmethod
    def from_config(
        cls,
        config_path: str | Path = "mcpforge.yaml",
    ) -> "RuntimeApplication":
        """Build an application from a project configuration file."""

        return cls(build_dependencies(config_path))

    @property
    def server(self) -> Any:
        """Return the configured MCP server."""

        return self.dependencies.server

    @property
    def tools(self) -> tuple[ToolDefinition, ...]:
        """Return generated tool definitions."""

        return self.dependencies.tools

    async def start(self) -> None:
        """Start shared runtime resources."""

        await self.lifecycle.start()

    async def close(self) -> None:
        """Close shared runtime resources."""

        await self.lifecycle.close()

    async def __aenter__(self) -> "RuntimeApplication":
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        await self.close()

    def serve(
        self,
        transport: Transport | str = Transport.STDIO,
        *,
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> Any:
        """Run the MCP transport after resources have been started."""

        return run_transport(
            self.server,
            transport,
            host=host,
            port=port,
        )
