from pathlib import Path

from mcpforge.ingestion.loaders.file import load_file
from mcpforge.ingestion.parsers.swagger import SwaggerParser
from mcpforge.ingestion.source import Source


def test_swagger_parser_normalizes_fixture() -> None:
    path = Path(__file__).parents[2] / "fixtures" / "swagger" / "petstore.yaml"

    document = SwaggerParser().parse(load_file(Source(str(path))))

    assert document.source_format == "swagger"
    assert document.base_url == "https://api.example.com/v1"
    assert len(document.endpoints) == 2

    create_pet = next(
        endpoint for endpoint in document.endpoints if endpoint.operation_id == "create_pet"
    )
    assert create_pet.request_body is not None
    assert create_pet.request_body.schema.properties["name"].type == "string"
