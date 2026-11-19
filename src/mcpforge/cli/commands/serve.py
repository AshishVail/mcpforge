"""The serve command."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from mcpforge.mcp.transports import Transport
from mcpforge.runtime.application import RuntimeApplication

app = typer.Typer(name="serve", help="Start the MCP server.")


@app.callback(invoke_without_command=True)
def serve(
    config: Annotated[Path, typer.Option("--config")] = Path("mcpforge.yaml"),
    transport: Annotated[
        Transport,
        typer.Option("--transport"),
    ] = Transport.STDIO,
    host: Annotated[str, typer.Option("--host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", min=1, max=65535)] = 8000,
) -> None:
    """Start an MCP server over stdio or streamable HTTP."""

    async def run() -> None:
        async with RuntimeApplication.from_config(config) as application:
            application.serve(transport, host=host, port=port)

    asyncio.run(run())
