from mcpforge.domain.enums import HttpMethod, ParameterLocation
from mcpforge.domain.models import Endpoint, Parameter
from mcpforge.generation.naming import default_tool_name


def test_operation_id_has_priority() -> None:
    assert (
        default_tool_name(
            Endpoint(
                operation_id="getUserProfile",
                path="/users/{id}",
                method=HttpMethod.GET,
                parameters=[
                    Parameter(name="id", location=ParameterLocation.PATH, required=True)
                ],
            )
        )
        == "get_user_profile"
    )


def test_collection_and_item_names_are_deterministic() -> None:
    assert default_tool_name(Endpoint(path="/users", method=HttpMethod.GET)) == "list_user"
    assert (
        default_tool_name(
            Endpoint(
                path="/users/{id}",
                method=HttpMethod.GET,
                parameters=[
                    Parameter(name="id", location=ParameterLocation.PATH, required=True)
                ],
            )
        )
        == "get_user"
    )
