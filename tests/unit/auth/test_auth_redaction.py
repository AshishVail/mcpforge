from mcpforge.auth.redaction import redact


def test_redacts_sensitive_mapping_keys() -> None:
    result = redact(
        {
            "headers": {
                "Authorization": "Bearer secret",
                "X-Request-ID": "safe",
            },
            "nested": [{"password": "secret"}],
        }
    )

    assert result["headers"]["Authorization"] == "***REDACTED***"
    assert result["headers"]["X-Request-ID"] == "safe"
    assert result["nested"][0]["password"] == "***REDACTED***"


def test_redacts_known_secret_values_inside_strings() -> None:
    assert redact("token=secret-value", ["secret-value"]) == "token=***REDACTED***"
