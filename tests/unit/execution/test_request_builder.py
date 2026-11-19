from mcpforge.auth.models import ResolvedAuth
from mcpforge.domain.enums import HttpMethod, ParameterLocation
from mcpforge.domain.models import Endpoint, Parameter
from mcpforge.execution.request_builder import build_request


def test_build_request_maps_all_argument_locations() -> None:
    endpoint = Endpoint(
        path="/users/{id}",
        method=HttpMethod.POST,
        parameters=[
            Parameter(
                name="id",
                location=ParameterLocation.PATH,
                required=True,
            ),
            Parameter(
                name="limit",
                location=ParameterLocation.QUERY,
            ),
            Parameter(
                name="X-Trace-ID",
                location=ParameterLocation.HEADER,
            ),
            Parameter(
                name="session",
                location=ParameterLocation.COOKIE,
            ),
        ],
    )

    request = build_request(
        endpoint,
        "https://api.example.com/v1",
        {
            "id": "a/b",
            "limit": 10,
            "X-Trace-ID": "trace",
            "session": "cookie-value",
            "body": {"name": "Ada"},
        },
        ResolvedAuth(headers={"Authorization": "Bearer token"}),
    )

    assert request.url.endswith("/users/a%2Fb")
    assert request.params["limit"] == 10
    assert request.headers["Authorization"] == "Bearer token"
    assert request.cookies["session"] == "cookie-value"
    assert request.json_body == {"name": "Ada"}
