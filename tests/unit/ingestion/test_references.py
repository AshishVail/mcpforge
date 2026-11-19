import pytest

from mcpforge.ingestion.errors import ReferenceResolutionError
from mcpforge.ingestion.normalization.references import ReferenceResolver


def test_resolves_nested_json_pointer() -> None:
    document = {
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                }
            }
        }
    }

    result = ReferenceResolver(document).resolve({"$ref": "#/components/schemas/User"})

    assert result["type"] == "object"
    assert result["properties"]["id"]["type"] == "integer"


def test_detects_reference_cycle() -> None:
    document = {
        "components": {
            "schemas": {
                "A": {"$ref": "#/components/schemas/B"},
                "B": {"$ref": "#/components/schemas/A"},
            }
        }
    }

    with pytest.raises(ReferenceResolutionError, match="cyclic"):
        ReferenceResolver(document).resolve({"$ref": "#/components/schemas/A"})


def test_rejects_external_reference() -> None:
    with pytest.raises(ReferenceResolutionError, match="only local"):
        ReferenceResolver({}).resolve({"$ref": "https://example.com/schema.json"})
