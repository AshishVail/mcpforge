"""Endpoint-to-tool generation."""

from collections.abc import Mapping
from typing import Any

from mcpforge.domain.models import ApiDocument
from mcpforge.generation.collisions import unique_names
from mcpforge.generation.descriptions import endpoint_description
from mcpforge.generation.input_schema import build_input_schema
from mcpforge.generation.models import ToolDefinition, ToolParameter


def generate_tools(
    document: ApiDocument,
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[ToolDefinition, ...]:
    """Generate immutable tool definitions from a normalized document."""

    overrides = overrides or {}
    names = unique_names(document.endpoints)
    tools: list[ToolDefinition] = []

    for index, endpoint in enumerate(document.endpoints):
        override = overrides.get(endpoint.operation_id or endpoint.path, {})
        name = str(override.get("name", names[index]))
        description = str(
            override.get(
                "description",
                endpoint_description(
                    endpoint.summary,
                    endpoint.description,
                    endpoint.method.value,
                    endpoint.path,
                ),
            )
        )
        parameters = tuple(
            ToolParameter(
                name=parameter.name,
                location=parameter.location.value,
                required=parameter.required,
                schema=parameter.schema.model_dump(
                    mode="json",
                    by_alias=True,
                    exclude_none=True,
                ),
                description=parameter.description,
            )
            for parameter in endpoint.parameters
        )

        tools.append(
            ToolDefinition(
                name=name,
                description=description,
                endpoint_path=endpoint.path,
                method=endpoint.method.value,
                input_schema=build_input_schema(endpoint),
                parameters=parameters,
                operation_id=endpoint.operation_id,
                deprecated=endpoint.deprecated,
            )
        )
    return tuple(tools)
