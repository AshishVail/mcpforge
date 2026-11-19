from mcpforge.security.redaction import REDACTED, redact_secrets


def test_redacts_sensitive_mapping_keys() -> None:
    result = redact_secrets(
        {
            "headers": {
                "Authorization": "Bearer secret",
                "X-Request-ID": "safe",
            },
            "nested": [{"password": "secret"}],
        }
    )

    assert result["headers"]["Authorization"] == REDACTED
    assert result["headers"]["X-Request-ID"] == "safe"
    assert result["nested"][0]["password"] == REDACTED


def test_redacts_known_secret_values() -> None:
    assert redact_secrets("token=secret-value", ["secret-value"]) == ("token=***REDACTED***")
