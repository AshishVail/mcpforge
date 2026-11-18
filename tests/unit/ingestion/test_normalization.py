from mcpforge.domain.enums import HttpMethod, OperationSafety, ParameterLocation
from mcpforge.ingestion.normalization.operation import (
    endpoint_from_operation,
    operation_safety,
)
from mcpforge.ingestion.normalization.references import ReferenceResolver
from mcpforge.ingestion.normalization.schemas import normalize_schema


def test_normalizes_object_schema() -> None:
    schema = normalize_schema(
        {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
    )

    assert schema.type == "object"
    assert schema.required == ["name"]
    assert schema.properties["name"].type == "string"


def test_operation_safety() -> None:
    assert operation_safety(HttpMethod.GET) is OperationSafety.READ
    assert operation_safety(HttpMethod.POST) is OperationSafety.WRITE
    assert operation_safety(HttpMethod.DELETE) is OperationSafety.DELETE


def test_normalizes_endpoint_parameters_and_body() -> None:
    endpoint = endpoint_from_operation(
        path="/users/{id}",
        method="POST",
        raw={
            "parameters": [
                {
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}},
                        }
                    }
                },
            },
            "responses": {"201": {"description": "Created"}},
        },
        resolver=ReferenceResolver({}),
    )

    assert endpoint.method is HttpMethod.POST
    assert endpoint.parameters[0].location is ParameterLocation.PATH
    assert endpoint.request_body is not None
    assert endpoint.request_body.required is True
