"""Parser protocol."""

from typing import Protocol

from mcpforge.domain.models import ApiDocument
from mcpforge.ingestion.source import LoadedDocument


class Parser(Protocol):
    """Contract implemented by all specification parsers."""

    def parse(self, loaded: LoadedDocument) -> ApiDocument:
        """Convert a loaded document to the normalized domain model."""
        ...
