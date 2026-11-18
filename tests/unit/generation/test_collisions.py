from mcpforge.domain.enums import HttpMethod
from mcpforge.domain.models import Endpoint
from mcpforge.generation.collisions import unique_names


def test_collisions_get_numeric_suffixes() -> None:
    endpoints = [
        Endpoint(path="/users", method=HttpMethod.GET),
        Endpoint(path="/users", method=HttpMethod.GET),
    ]

    assert unique_names(endpoints) == {0: "list_user", 1: "list_user_2"}
