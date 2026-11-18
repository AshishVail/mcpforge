from mcpforge.domain.enums import HttpMethod, ParameterLocation
from mcpforge.domain.models import Endpoint, JsonSchema, Parameter, RequestBody
from mcpforge.generation.input_schema import build_input_schema


def test_input_schema_contains_parameters_and_body() -> None:
    result = build_input_schema(
        Endpoint(
            path="/users/{id}",
            method=HttpMethod.POST,
            parameters=[
                Parameter(
                    name="id",
                    location=ParameterLocation.PATH,
                    required=True,
                    schema=JsonSchema(type="string"),
                )
            ],
            request_body=RequestBody(
                required=True,
                schema=JsonSchema(
                    type="object",
                    required=["name"],
                    properties={"name": JsonSchema(type="string")},
                ),
            ),
        )
    )

    assert result["required"] == ["id", "body"]
    assert result["properties"]["id"]["type"] == "string"
    assert result["properties"]["body"]["properties"]["name"]["type"] == "string"
