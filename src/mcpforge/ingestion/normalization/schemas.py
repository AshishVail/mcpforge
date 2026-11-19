"""Conversion of OpenAPI, Swagger, and manual schemas."""

from collections.abc import Mapping
from typing import Any

from mcpforge.domain.models import JsonSchema
from mcpforge.ingestion.normalization.references import ReferenceResolver


def normalize_schema(
    raw: Any,
    resolver: ReferenceResolver | None = None,
) -> JsonSchema:
    """Convert an arbitrary JSON Schema-like object into ``JsonSchema``."""

    if raw is None:
        return JsonSchema()

    if isinstance(raw, bool):
        return JsonSchema(type="boolean" if raw else None)

    if not isinstance(raw, Mapping):
        raise ValueError("schema must be a mapping")

    resolved: Mapping[str, Any]
    if resolver is not None:
        resolved_value = resolver.resolve(raw)
        if not isinstance(resolved_value, Mapping):
            raise ValueError("resolved schema must be a mapping")
        resolved = resolved_value
    else:
        resolved = raw

    properties_raw = resolved.get("properties", {})
    properties = (
        {str(name): normalize_schema(value, resolver) for name, value in properties_raw.items()}
        if isinstance(properties_raw, Mapping)
        else {}
    )

    items_raw = resolved.get("items")
    items = normalize_schema(items_raw, resolver) if items_raw is not None else None

    known = {
        "type",
        "title",
        "description",
        "format",
        "enum",
        "default",
        "required",
        "properties",
        "items",
        "additionalProperties",
    }
    extras = {
        str(key): value for key, value in resolved.items() if key not in known and key != "$ref"
    }

    return JsonSchema(
        type=resolved.get("type"),
        title=resolved.get("title"),
        description=resolved.get("description"),
        format=resolved.get("format"),
        enum=list(resolved["enum"]) if isinstance(resolved.get("enum"), list) else None,
        default=resolved.get("default"),
        required=list(resolved.get("required", [])),
        properties=properties,
        items=items,
        additional_properties=(
            normalize_schema(resolved["additionalProperties"], resolver)
            if isinstance(resolved.get("additionalProperties"), Mapping)
            else resolved.get("additionalProperties")
        ),
        **extras,
    )
