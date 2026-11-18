"""Typer application entry point."""

from typing import Annotated

import typer

from mcpforge import __version__
from mcpforge.cli.output import console

app = typer.Typer(
    name="mcpforge",
    help="Turn any REST API into an AI-ready MCP server.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def callback(
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the MCPForge version."),
    ] = False,
) -> None:
    """MCPForge command-line interface."""

    if version:
        console.print(f"MCPForge {__version__}")
        raise typer.Exit()


def main() -> None:
    """Run the command-line application."""

    app()
