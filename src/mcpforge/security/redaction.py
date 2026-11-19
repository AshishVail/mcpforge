"""Security-layer recursive secret redaction."""

from collections.abc import Mapping, Sequence
from typing import Any

REDACTED = "***REDACTED***"

_SENSITIVE_KEYS = frozenset(
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
        "refresh_token",
        "client_secret",
    }
)


def _normalized_key(value: object) -> str:
    return str(value).strip().lower().replace("-", "_")


def redact_secrets(
    value: Any,
    secrets: Sequence[str] = (),
) -> Any:
    """Recursively redact sensitive keys and known secret values."""

    clean_secrets = tuple(secret for secret in secrets if secret)

    if isinstance(value, Mapping):
        return {
            key: (
                REDACTED
                if _normalized_key(key) in _SENSITIVE_KEYS
                else redact_secrets(child, clean_secrets)
            )
            for key, child in value.items()
        }

    if isinstance(value, list):
        return [redact_secrets(item, clean_secrets) for item in value]

    if isinstance(value, tuple):
        return tuple(redact_secrets(item, clean_secrets) for item in value)

    if isinstance(value, str):
        result = value
        for secret in clean_secrets:
            result = result.replace(secret, REDACTED)
        return result

    return value
