"""Source and loaded-document contracts."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class SourceKind(StrEnum):
    """Supported source locations."""

    FILE = "file"
    URL = "url"


@dataclass(frozen=True, slots=True)
class Source:
    """A local or remote API specification source."""

    location: str
    format: str | None = None
    timeout_seconds: float = 30.0
    max_bytes: int = 10_000_000

    @property
    def kind(self) -> SourceKind:
        """Return whether the source is local or remote."""

        parsed = urlparse(self.location)
        if parsed.scheme in {"http", "https"}:
            return SourceKind.URL
        return SourceKind.FILE

    @property
    def path(self) -> Path:
        """Return the local path representation."""

        if self.kind is not SourceKind.FILE:
            raise ValueError("remote sources do not have a local path")
        return Path(self.location)


@dataclass(frozen=True, slots=True)
class LoadedDocument:
    """Raw parsed source content and loading metadata."""

    document: dict[str, Any]
    source: Source
    media_type: str | None = None
