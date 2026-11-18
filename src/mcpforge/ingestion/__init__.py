"""Multi-source API ingestion and normalization."""

from mcpforge.ingestion.errors import (
    IngestionError,
    ReferenceResolutionError,
    SourceLoadError,
    SpecificationError,
    UnsupportedFormatError,
)
from mcpforge.ingestion.service import detect_format, ingest, ingest_path, parser_for
from mcpforge.ingestion.source import LoadedDocument, Source, SourceKind

__all__ = [
    "IngestionError",
    "LoadedDocument",
    "ReferenceResolutionError",
    "Source",
    "SourceKind",
    "SourceLoadError",
    "SpecificationError",
    "UnsupportedFormatError",
    "detect_format",
    "ingest",
    "ingest_path",
    "parser_for",
]
