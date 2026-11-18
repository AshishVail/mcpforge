"""Normalization of endpoint parameters, bodies, and responses."""

from collections.abc import Mapping
from typing import Any

from mcpforge.domain.enums import ParameterLocation
from mcpforge.domain.models import Parameter, RequestBody, ResponseDefinition
from mcpforge.ingestion.errors import SpecificationError
from mcpforge.ingestion.normalization.references import ReferenceResolver
from mcpforge.ingestion.normalization.schemas import normalize_schema


def _location(value: str) -> ParameterLocation:
    try:
        return ParameterLocation(value)
    except ValueError as exc:
        raise SpecificationError(f"unsupported parameter location: {value!r}") from exc


def normalize_parameter(
    raw: Mapping[str, Any],
    resolver: ReferenceResolver,
) -> Parameter:
    """Normalize an OpenAPI or manual parameter."""

    name = raw.get("name")
    location = raw.get("in", raw.get("location"))
    if not isinstance(name, str) or not isinstance(location, str):
        raise SpecificationError("parameter requires string name and location")

    schema_raw = raw.get("schema")
    if schema_raw is None and isinstance(raw.get("type"), str):
        schema_raw = {
            key: raw[key]
            for key in ("type", "format", "items", "enum", "default", "minimum", "maximum")
            if key in raw
        }

    return Parameter(
        name=name,
        location=_location(location),
        required=bool(raw.get("required", False)),
        description=raw.get("description"),
        schema=normalize_schema(schema_raw or {}, resolver),
        deprecated=bool(raw.get("deprecated", False)),
        example=raw.get("example"),
    )


def normalize_request_body(
    raw: Mapping[str, Any] | None,
    resolver: ReferenceResolver,
) -> RequestBody | None:
    """Normalize an OpenAPI request body or Swagger body parameter."""

    if raw is None:
        return None

    if raw.get("in") == "body":
        schema_raw = raw.get("schema", {})
        return RequestBody(
            required=bool(raw.get("required", False)),
            content_type="application/json",
            schema=normalize_schema(schema_raw, resolver),
            description=raw.get("description"),
        )

    content = raw.get("content")
    if isinstance(content, Mapping) and content:
        content_type, media = next(iter(content.items()))
        media_mapping = media if isinstance(media, Mapping) else {}
        return RequestBody(
            required=bool(raw.get("required", False)),
            content_type=str(content_type),
            schema=normalize_schema(media_mapping.get("schema", {}), resolver),
            description=raw.get("description"),
        )

    raise SpecificationError("request body must define content or a body schema")


def normalize_response(
    status_code: str | int,
    raw: Mapping[str, Any],
    resolver: ReferenceResolver,
    swagger: bool = False,
) -> ResponseDefinition:
    """Normalize one OpenAPI or Swagger response."""

    try:
        status = int(status_code)
    except (TypeError, ValueError) as exc:
        raise SpecificationError(f"invalid response status code: {status_code!r}") from exc

    if swagger:
        schema = raw.get("schema")
        return ResponseDefinition(
            status_code=status,
            description=raw.get("description"),
            content_type="application/json" if schema else None,
            schema=normalize_schema(schema, resolver) if schema is not None else None,
        )

    content = raw.get("content")
    if isinstance(content, Mapping) and content:
        content_type, media = next(iter(content.items()))
        media_mapping = media if isinstance(media, Mapping) else {}
        schema = media_mapping.get("schema")
        return ResponseDefinition(
            status_code=status,
            description=raw.get("description"),
            content_type=str(content_type),
            schema=normalize_schema(schema, resolver) if schema is not None else None,
        )

    return ResponseDefinition(
        status_code=status,
        description=raw.get("description"),
    )
