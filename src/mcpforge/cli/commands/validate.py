"""The validate command."""

from pathlib import Path
from typing import Annotated

import typer

from mcpforge.config.loader import load_config
from mcpforge.filtering.evaluator import filter_document
from mcpforge.generation.service import generate_tools
from mcpforge.ingestion.service import ingest_path
from mcpforge.cli.output import print_success

app = typer.Typer(name="validate", help="Validate project configuration and source.")


@app.callback(invoke_without_command=True)
def validate(
    config: Annotated[Path, typer.Option("--config")] = Path("mcpforge.yaml"),
    strict: Annotated[bool, typer.Option("--strict")] = False,
) -> None:
    """Validate configuration, ingestion, filtering, and tool generation."""

    try:
        project = load_config(config)
        document = ingest_path(
            project.source.location,
            format=project.source.format,
            timeout_seconds=project.source.timeout_seconds,
        )
        filtered = filter_document(document, project.filters, project.security)
        tools = generate_tools(filtered)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc

    if strict and not tools:
        raise typer.BadParameter("strict validation produced no enabled tools")

    print_success(
        f"Configuration valid: {len(filtered.endpoints)} endpoint(s), "
        f"{len(tools)} tool(s)"
    )
