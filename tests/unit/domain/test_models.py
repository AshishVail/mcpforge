import pytest
from pydantic import ValidationError

from mcpforge.domain.enums import HttpMethod, ParameterLocation
from mcpforge.domain.models import Endpoint, Parameter


def test_valid_endpoint_round_trips() -> None:
    endpoint = Endpoint(
        operation_id="get_user",
        path="/users/{id}",
        method=HttpMethod.GET,
        parameters=[
            Parameter(
                name="id",
                location=ParameterLocation.PATH,
                required=True,
            )
        ],
    )

    dumped = endpoint.model_dump(mode="json")

    assert dumped["path"] == "/users/{id}"
    assert dumped["method"] == "GET"


def test_path_parameter_must_be_required() -> None:
    with pytest.raises(ValidationError, match="path parameters must be required"):
        Parameter(name="id", location=ParameterLocation.PATH)


def test_endpoint_rejects_missing_path_parameter() -> None:
    with pytest.raises(ValidationError, match="path parameters are not defined"):
        Endpoint(path="/users/{id}", method=HttpMethod.GET)


def test_endpoint_rejects_duplicate_parameters() -> None:
    parameter = Parameter(name="limit", location=ParameterLocation.QUERY)

    with pytest.raises(ValidationError, match="duplicate parameter names"):
        Endpoint(
            path="/users",
            method=HttpMethod.GET,
            parameters=[parameter, parameter],
        )
