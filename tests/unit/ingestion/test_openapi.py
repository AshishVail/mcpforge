from pathlib import Path

from mcpforge.ingestion.loaders.file import load_file
from mcpforge.ingestion.parsers.openapi import OpenAPIParser
from mcpforge.ingestion.source import Source


def test_openapi_parser_normalizes_fixture() -> None:
    path = Path(__file__).parents[2] / "fixtures" / "openapi" / "petstore.yaml"

    document = OpenAPIParser().parse(load_file(Source(str(path))))

    assert document.source_format == "openapi"
    assert document.base_url == "https://api.example.com/v1"
    assert len(document.endpoints) == 2

    get_pet = next(
        endpoint for endpoint in document.endpoints if endpoint.operation_id == "get_pet"
    )

    assert get_pet.parameters[0].name == "pet_id"
    assert get_pet.responses[0].schema is not None
    assert get_pet.responses[0].schema.properties["id"].type == "integer"
