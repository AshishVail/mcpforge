"""The init command."""

from pathlib import Path
from typing import Annotated

import typer

from mcpforge.cli.output import print_success
from mcpforge.cli.scaffold import scaffold_project

app = typer.Typer(name="init", help="Create a new MCPForge project.")


@app.callback(invoke_without_command=True)
def init(
    directory: Annotated[
        Path,
        typer.Argument(help="Project directory.", exists=False),
    ] = Path("."),
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing generated files."),
    ] = False,
    with_example: Annotated[
        bool,
        typer.Option("--with-example/--without-example"),
    ] = True,
) -> None:
    """Scaffold a configuration and optional example specification."""

    try:
        files = scaffold_project(
            directory,
            force=force,
            with_example=with_example,
        )
    except FileExistsError as exc:
        raise typer.BadParameter(str(exc)) from exc

    for path in files:
        print_success(f"Created {path}")
