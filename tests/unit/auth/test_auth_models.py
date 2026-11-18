from mcpforge.auth.models import ResolvedAuth


def test_redacted_auth_does_not_expose_values() -> None:
    auth = ResolvedAuth(
        headers={"Authorization": "secret"},
        query={"api_key": "secret"},
        username="user",
        password="password",
    )

    redacted = auth.redacted()

    assert redacted.headers["Authorization"] == "***REDACTED***"
    assert redacted.query["api_key"] == "***REDACTED***"
    assert redacted.password == "***REDACTED***",
