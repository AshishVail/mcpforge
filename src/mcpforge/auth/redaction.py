"""Recursive credential redaction."""

from collections.abc import Mapping, Sequence
from typing import Any

SENSITIVE_NAMES = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "token",
        "password",
        "secret",
        "api_key",
        "api-key",
        "access_token",
        "client_secret",
    }
)
REDACTED = "***REDACTED***"


def redact(value: Any, extra_secrets: Sequence[str] = ()) -> Any:
    """Return a recursively redacted copy of arbitrary diagnostic data."""

    secret_values = tuple(secret for secret in extra_secrets if secret)

    if isinstance(value, Mapping):
        return {
            str(key): (
                REDACTED
                if str(key).lower().replace("-", "_") in SENSITIVE_NAMES
                else redact(child, secret_values)
            )
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [redact(item, secret_values) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item, secret_values) for item in value)
    if isinstance(value, str):
        result = value
        for secret in secret_values:
            result = result.replace(secret, REDACTED)
        return result
    return value
