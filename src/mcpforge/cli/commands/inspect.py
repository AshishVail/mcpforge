"""The inspect command."""

from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from mcpforge.cli.output import console
from mcpforge.config.loader import load_config
from mcpforge.filtering.evaluator import filter_document
from mcpforge.generation.service import generate_tools
from mcpforge.ingestion.service import ingest_path

app = typer.Typer(name="inspect", help="Inspect endpoints and generated tools.")


@app.callback(invoke_without_command=True)
def inspect(
    config: Annotated[Path, typer.Option("--config")] = Path("mcpforge.yaml"),
    output: Annotated[str, typer.Option("--format")] = "table",
) -> None:
    """Display the filtered endpoint and tool inventory."""

    try:
        project = load_config(config)
        document = ingest_path(
            project.source.location,
            format=project.source.format,
            timeout_seconds=project.source.timeout_seconds,
        )
        document = filter_document(document, project.filters, project.security)
        tools = generate_tools(document)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc

    rows = [
        {
            "method": endpoint.method.value,
            "path": endpoint.path,
            "tool": tool.name,
            "safety": (endpoint.safety.value if endpoint.safety else "read"),
        }
        for endpoint, tool in zip(document.endpoints, tools, strict=True)
    ]

    if output.lower() == "json":
        import json

        typer.echo(json.dumps(rows, indent=2))
        return

    table = Table("Method", "Path", "Tool", "Safety")
    for row in rows:
        table.add_row(row["method"], row["path"], row["tool"], row["safety"])
    console.print(table)
