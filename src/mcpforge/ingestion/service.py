"""High-level source ingestion service."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from mcpforge.domain.models import ApiDocument
from mcpforge.ingestion.errors import SpecificationError, UnsupportedFormatError
from mcpforge.ingestion.loaders.file import load_file
from mcpforge.ingestion.loaders.remote import load_remote
from mcpforge.ingestion.parsers.base import Parser
from mcpforge.ingestion.parsers.manual import ManualParser
from mcpforge.ingestion.parsers.openapi import OpenAPIParser
from mcpforge.ingestion.parsers.swagger import SwaggerParser
from mcpforge.ingestion.source import LoadedDocument, Source


def detect_format(document: Mapping[str, Any]) -> str:
    """Detect the specification format from its top-level marker."""

    if isinstance(document.get("openapi"), str):
        version = document["openapi"]
        if version.startswith(("3.0", "3.1")):
            return "openapi"
    if document.get("swagger") == "2.0":
        return "swagger"
    if isinstance(document.get("endpoints"), list):
        return "manual"
    raise UnsupportedFormatError(
        "unable to detect format; expected OpenAPI, Swagger 2.0, or manual endpoints"
    )


def parser_for(format_name: str) -> Parser:
    """Return a parser for a normalized format name."""

    parsers: dict[str, Parser] = {
        "openapi": OpenAPIParser(),
        "swagger": SwaggerParser(),
        "manual": ManualParser(),
    }
    try:
        return parsers[format_name.lower()]
    except KeyError as exc:
        raise UnsupportedFormatError(f"unsupported specification format: {format_name}") from exc


def _loaded_source(source: Source) -> LoadedDocument:
    if source.kind.value == "file":
        return load_file(source)
    return load_remote(source)


def ingest(source: Source) -> ApiDocument:
    """Load, detect, parse, and validate one API source."""

    loaded = _loaded_source(source)
    format_name = source.format.lower() if source.format else detect_format(loaded.document)
    parser = parser_for(format_name)

    try:
        return parser.parse(loaded)
    except (SpecificationError, ValueError) as exc:
        if isinstance(exc, SpecificationError):
            raise
        raise SpecificationError(f"failed to normalize {source.location} as {format_name}") from exc


def ingest_path(
    location: str | Path,
    *,
    format: str | None = None,
    timeout_seconds: float = 30.0,
    max_bytes: int = 10_000_000,
) -> ApiDocument:
    """Convenience wrapper for ingesting a string or path location."""

    source = Source(
        location=str(location),
        format=format,
        timeout_seconds=timeout_seconds,
        max_bytes=max_bytes,
    )
    return ingest(source)
