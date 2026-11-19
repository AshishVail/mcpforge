"""The test command."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from mcpforge.cli.output import print_success
from mcpforge.config.loader import load_config
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.filtering.evaluator import filter_document
from mcpforge.ingestion.service import ingest_path

app = typer.Typer(name="test", help="Test API connectivity and authentication.")


@app.callback(invoke_without_command=True)
def test(
    config: Annotated[Path, typer.Option("--config")] = Path("mcpforge.yaml"),
    operation: Annotated[str | None, typer.Option("--operation")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Execute a selected safe endpoint or perform a dry run."""

    try:
        project = load_config(config)
        document = ingest_path(
            project.source.location,
            format=project.source.format,
            timeout_seconds=project.source.timeout_seconds,
        )
        document = filter_document(document, project.filters, project.security)
        endpoint = next(
            (
                item
                for item in document.endpoints
                if operation is None or item.operation_id == operation or item.path == operation
            ),
            None,
        )
        if endpoint is None:
            raise ValueError("no matching enabled operation found")

        if dry_run:
            print_success(f"Dry run valid for {endpoint.method.value} {endpoint.path}")
            return

        async def execute() -> dict[str, object]:
            async with HTTPClient(
                timeout_seconds=project.http.timeout_seconds,
                verify_tls=project.http.verify_tls,
            ).lifecycle() as client:
                return await ExecutionEngine(project, client).execute(endpoint, {})

        result = asyncio.run(execute())
        print_success(f"Connectivity successful: status {result.get('status_code')}")
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc
