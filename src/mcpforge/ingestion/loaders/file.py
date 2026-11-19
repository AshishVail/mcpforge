"""Safe local specification loading."""

import json
from pathlib import Path
from typing import Any

import yaml

from mcpforge.ingestion.errors import SourceLoadError
from mcpforge.ingestion.source import LoadedDocument, Source


def _parse_document(text: str, suffix: str) -> dict[str, Any]:
    try:
        value: Any = json.loads(text) if suffix.lower() == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SourceLoadError("local specification contains invalid JSON or YAML") from exc

    if not isinstance(value, dict):
        raise SourceLoadError("specification root must be a mapping")
    return value


def load_file(source: Source) -> LoadedDocument:
    """Read and parse a local JSON or YAML specification."""

    if source.kind.value != "file":
        raise SourceLoadError("load_file requires a local file source")

    path = Path(source.location)
    if not path.is_file():
        raise SourceLoadError(f"specification file does not exist: {path}")

    try:
        size = path.stat().st_size
    except OSError as exc:
        raise SourceLoadError(f"cannot inspect specification file: {path}") from exc

    if size > source.max_bytes:
        raise SourceLoadError(f"specification file exceeds the {source.max_bytes}-byte limit")

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SourceLoadError(f"cannot read specification file: {path}") from exc

    document = _parse_document(text, path.suffix)
    return LoadedDocument(document=document, source=source)
