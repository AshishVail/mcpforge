"""Structured execution errors."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionError:
    """An LLM-friendly normalized execution failure."""

    category: str
    message: str
    status_code: int | None = None
    retryable: bool = False
    details: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        """Serialize the error into a stable response shape."""

        result: dict[str, Any] = {
            "ok": False,
            "error": {
                "category": self.category,
                "message": self.message,
                "status_code": self.status_code,
                "retryable": self.retryable,
            },
        }
        if self.details:
            result["error"]["details"] = self.details
        return result


class ExecutionFailure(Exception):
    """Exception carrying a normalized execution error."""

    def __init__(self, error: ExecutionError) -> None:
        super().__init__(error.message)
        self.error = error


def error_for_status(status_code: int) -> ExecutionError:
    """Map an HTTP status code to a normalized error."""

    if status_code == 400:
        return ExecutionError("bad_request", "The upstream API rejected the request.", status_code)
    if status_code == 401:
        return ExecutionError(
            "authentication_failed",
            "The upstream API rejected the provided authentication.",
            status_code,
        )
    if status_code == 403:
        return ExecutionError(
            "authorization_failed",
            "The upstream API denied access to this operation.",
            status_code,
        )
    if status_code == 404:
        return ExecutionError(
            "not_found",
            "The requested upstream resource was not found.",
            status_code,
        )
    if status_code == 429:
        return ExecutionError(
            "rate_limited",
            "The upstream API rate limit was exceeded.",
            status_code,
            retryable=True,
        )
    if status_code >= 500:
        return ExecutionError(
            "upstream_server_error",
            "The upstream API returned a server error.",
            status_code,
            retryable=True,
        )
    return ExecutionError(
        "upstream_http_error",
        "The upstream API returned an unsuccessful response.",
        status_code,
    )
