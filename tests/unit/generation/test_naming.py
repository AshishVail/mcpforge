from mcpforge.domain.enums import HttpMethod
from mcpforge.domain.models import Endpoint
from mcpforge.generation.naming import default_tool_name


def test_operation_id_has_priority() -> None:
    assert (
        default_tool_name(
            Endpoint(operation_id="getUserProfile", path="/users/{id}", method=HttpMethod.GET)
        )
        == "get_user_profile"
    )


def test_collection_and_item_names_are_deterministic() -> None:
    assert default_tool_name(Endpoint(path="/users", method=HttpMethod.GET)) == "list_user"
    assert default_tool_name(Endpoint(path="/users/{id}", method=HttpMethod.GET)) == "get_user"
