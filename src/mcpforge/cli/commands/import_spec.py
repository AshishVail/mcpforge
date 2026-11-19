"""The import command."""

from typing import Annotated

import typer

from mcpforge.ingestion.service import ingest_path

app = typer.Typer(
    name="import",
    help="Load and normalize an API specification.",
)


@app.command()
def import_spec(
    source: Annotated[str, typer.Argument(help="Local path or HTTP(S) URL.")],
    format: Annotated[
        str | None,
        typer.Option("--format", help="openapi, swagger, or manual."),
    ] = None,
    timeout: Annotated[
        float,
        typer.Option("--timeout", min=0.1, max=300.0),
    ] = 30.0,
) -> None:
    """Parse a source and display its normalized endpoint count."""

    try:
        document = ingest_path(
            source,
            format=format,
            timeout_seconds=timeout,
        )
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(
        f"Imported {document.source_format or 'unknown'} specification: "
        f"{len(document.endpoints)} endpoint(s)"
    )
