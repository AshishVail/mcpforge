"""Safe remote specification loading without coupling ingestion to HTTPX."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any
from urllib.parse import urlparse

import yaml

from mcpforge.ingestion.errors import SourceLoadError
from mcpforge.ingestion.source import LoadedDocument, Source


def _parse_document(text: str, content_type: str | None, url: str) -> dict[str, Any]:
    try:
        suffix = urlparse(url).path.lower()
        if "json" in (content_type or "").lower() or suffix.endswith(".json"):
            value: Any = json.loads(text)
        else:
            value = yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SourceLoadError("remote specification contains invalid JSON or YAML") from exc

    if not isinstance(value, dict):
        raise SourceLoadError("remote specification root must be a mapping")
    return value


def load_remote(source: Source) -> LoadedDocument:
    """Fetch and parse a remote JSON or YAML specification with a byte limit."""

    if source.kind.value != "url":
        raise SourceLoadError("load_remote requires an HTTP or HTTPS source")

    parsed = urlparse(source.location)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SourceLoadError("remote source must use a valid HTTP or HTTPS URL")

    request = Request(
        source.location,
        headers={
            "Accept": "application/json, application/yaml, text/yaml, */*",
            "User-Agent": "MCPForge/0.1",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=source.timeout_seconds) as response:
            content_type = response.headers.get("Content-Type")
            declared_length = response.headers.get("Content-Length")
            if declared_length and int(declared_length) > source.max_bytes:
                raise SourceLoadError(
                    f"remote specification exceeds the {source.max_bytes}-byte limit"
                )

            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = response.read(min(64 * 1024, source.max_bytes - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > source.max_bytes:
                    raise SourceLoadError(
                        f"remote specification exceeds the {source.max_bytes}-byte limit"
                    )
                chunks.append(chunk)
    except SourceLoadError:
        raise
    except HTTPError as exc:
        raise SourceLoadError(f"remote specification returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise SourceLoadError(f"cannot fetch remote specification: {source.location}") from exc

    try:
        text = b"".join(chunks).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SourceLoadError("remote specification is not valid UTF-8") from exc

    document = _parse_document(text, content_type, source.location)
    return LoadedDocument(document=document, source=source, media_type=content_type)
