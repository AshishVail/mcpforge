import pytest
from pydantic import ValidationError

from mcpforge.domain.models import JsonSchema
from mcpforge.domain.parameters import ParameterCollection
from mcpforge.domain.enums import ParameterLocation
from mcpforge.domain.models import Parameter


def test_object_schema_rejects_unknown_required_property() -> None:
    with pytest.raises(ValidationError, match="required fields are not defined"):
        JsonSchema(
            type="object",
            required=["name"],
            properties={},
        )


def test_object_schema_rejects_items() -> None:
    with pytest.raises(ValidationError, match="object schemas cannot define items"):
        JsonSchema(type="object", items={"type": "string"})


def test_parameter_collection_indexes_parameters() -> None:
    collection = ParameterCollection.from_iterable(
        [
            Parameter(
                name="id",
                location=ParameterLocation.PATH,
                required=True,
            ),
            Parameter(name="verbose", location=ParameterLocation.QUERY),
        ]
    )

    assert collection.names() == {"id", "verbose"}
    assert len(collection.by_location(ParameterLocation.PATH)) == 1
    assert len(collection.required()) == 1
