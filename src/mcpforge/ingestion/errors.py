"""Errors raised by the API ingestion pipeline."""

from mcpforge.domain.errors import MCPForgeError


class IngestionError(MCPForgeError):
    """Base error for source loading, parsing, and normalization failures."""


class SourceLoadError(IngestionError):
    """Raised when an API specification cannot be loaded safely."""


class UnsupportedFormatError(IngestionError):
    """Raised when a source format cannot be detected or is unsupported."""


class SpecificationError(IngestionError):
    """Raised when a specification is malformed or semantically invalid."""


class ReferenceResolutionError(SpecificationError):
    """Raised when a local JSON Pointer cannot be resolved safely."""
