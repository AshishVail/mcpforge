"""The run command."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from mcpforge.config.loader import DEFAULT_CONFIG_FILENAME
from mcpforge.config.models import ProjectConfig
from mcpforge.mcp.transports import Transport
from mcpforge.runtime.application import RuntimeApplication
from mcpforge.runtime.dependencies import build_dependencies

app = typer.Typer(name="run", help="Import, validate, generate, and serve.")


@app.callback(invoke_without_command=True)
def run(
    source: Annotated[str | None, typer.Argument(help="Specification path or URL.")] = None,
    config: Annotated[Path, typer.Option("--config")] = Path(DEFAULT_CONFIG_FILENAME),
    transport: Annotated[Transport, typer.Option("--transport")] = Transport.STDIO,
    host: Annotated[str, typer.Option("--host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", min=1, max=65535)] = 8000,
) -> None:
    """Run an existing project or replace its source for this invocation."""

    if source is not None:
        project = ProjectConfig.model_validate(
            {
                "source": {"location": source},
            }
        )
        dependencies = build_dependencies(config)
        dependencies.config = project  # type: ignore[misc]
        application = RuntimeApplication(dependencies)
    else:
        application = RuntimeApplication.from_config(config)

    async def serve() -> None:
        async with application:
            application.serve(transport, host=host, port=port)

    asyncio.run(serve())
