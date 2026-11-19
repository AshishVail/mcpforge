"""Safe diagnostics for execution and configuration."""

from typing import Any

from mcpforge.auth.models import ResolvedAuth
from mcpforge.observability.events import ExecutionEvent
from mcpforge.security.redaction import redact_secrets


def auth_summary(auth: ResolvedAuth) -> dict[str, Any]:
    """Return a safe summary of resolved authentication."""

    return {
        "has_headers": bool(auth.headers),
        "header_names": sorted(auth.headers),
        "has_query_credentials": bool(auth.query),
        "has_basic_auth": auth.username is not None and auth.password is not None,
    }


def event_summary(event: ExecutionEvent) -> dict[str, Any]:
    """Return a redacted event dictionary."""

    return dict(redact_secrets(event.as_dict()))


def request_summary(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    query: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a safe request diagnostic summary."""

    return dict(
        redact_secrets(
            {
                "method": method,
                "url": url,
                "headers": headers or {},
                "query": query or {},
            }
        )
    )
