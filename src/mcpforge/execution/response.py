"""HTTP response parsing and normalization."""

import json
from typing import Any

import httpx

from mcpforge.execution.errors import (
    ExecutionError,
    ExecutionFailure,
    error_for_status,
)
from mcpforge.execution.limits import enforce_response_limit


def parse_response(
    response: httpx.Response,
    *,
    max_response_bytes: int,
) -> dict[str, Any]:
    """Parse a successful response into a stable result object."""

    content = response.content
    enforce_response_limit(content, max_response_bytes)

    if response.status_code >= 400:
        error = error_for_status(response.status_code)
        details: dict[str, Any] = {}
        if content:
            try:
                payload = json.loads(content)
                if isinstance(payload, dict):
                    details = payload
            except json.JSONDecodeError:
                details = {"body_available": True}
        raise ExecutionFailure(
            ExecutionError(
                category=error.category,
                message=error.message,
                status_code=error.status_code,
                retryable=error.retryable,
                details=details or None,
            )
        )

    if not content:
        success_payload: Any = None
    else:
        try:
            success_payload = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise ExecutionFailure(
                ExecutionError(
                    "invalid_json",
                    "The upstream response was not valid JSON.",
                    status_code=response.status_code,
                )
            ) from exc

    return {
        "ok": True,
        "status_code": response.status_code,
        "data": success_payload,
    }
