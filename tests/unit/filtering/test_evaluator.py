from mcpforge.config.models import EndpointFilterConfig, SecurityConfig
from mcpforge.domain.enums import HttpMethod
from mcpforge.domain.models import ApiDocument, Endpoint


def test_filter_document_applies_exclusions_and_safety() -> None:
    from mcpforge.filtering import filter_document

    document = ApiDocument(
        endpoints=[
            Endpoint(path="/users", method=HttpMethod.GET, tags=["public"]),
            Endpoint(path="/admin", method=HttpMethod.GET, tags=["admin"]),
            Endpoint(path="/users", method=HttpMethod.POST, tags=["public"]),
        ]
    )
    result = filter_document(
        document,
        EndpointFilterConfig(exclude_tags=["admin"]),
        SecurityConfig(),
    )

    assert len(result.endpoints) == 1
    assert result.endpoints[0].method is HttpMethod.GET


def test_include_paths_are_allowlist_filters() -> None:
    from mcpforge.filtering import filter_document

    document = ApiDocument(
        endpoints=[
            Endpoint(path="/users", method=HttpMethod.GET),
            Endpoint(path="/orders", method=HttpMethod.GET),
        ]
    )
    result = filter_document(
        document,
        EndpointFilterConfig(include_paths=["/users"]),
        SecurityConfig(),
    )

    assert [item.path for item in result.endpoints] == ["/users"]
