"""AI-facing JSON Schema generation."""

from typing import Any

from mcpforge.domain.models import Endpoint, JsonSchema


def schema_to_json(schema: JsonSchema) -> dict[str, Any]:
    """Serialize a normalized schema into JSON Schema form."""

    result: dict[str, Any] = {}
    for key, value in schema.model_dump(by_alias=True, exclude_none=True).items():
        if key == "properties":
            result[key] = {
                name: schema_to_json(JsonSchema.model_validate(child))
                for name, child in value.items()
            }
        elif key == "items" and value is not None:
            result[key] = schema_to_json(JsonSchema.model_validate(value))
        else:
            result[key] = value
    return result


def build_input_schema(endpoint: Endpoint) -> dict[str, Any]:
    """Combine location parameters and body into one strict object schema."""

    properties: dict[str, Any] = {}
    required: list[str] = []

    for parameter in endpoint.parameters:
        properties[parameter.name] = schema_to_json(parameter.schema)
        if parameter.description:
            properties[parameter.name]["description"] = parameter.description
        if parameter.required:
            required.append(parameter.name)

    if endpoint.request_body is not None:
        body_schema = schema_to_json(endpoint.request_body.schema)
        properties["body"] = body_schema
        if endpoint.request_body.description:
            properties["body"]["description"] = endpoint.request_body.description
        if endpoint.request_body.required:
            required.append("body")

    result: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        result["required"] = required
    return result
