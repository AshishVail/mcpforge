"""Response and request size limits."""

from mcpforge.execution.errors import ExecutionError, ExecutionFailure


def enforce_response_limit(content: bytes, max_bytes: int) -> None:
    """Reject response content exceeding the configured byte limit."""

    if len(content) > max_bytes:
        raise ExecutionFailure(
            ExecutionError(
                category="response_too_large",
                message="The upstream response exceeded the configured payload limit.",
                retryable=False,
                details={"max_bytes": max_bytes},
            )
        )


def enforce_request_limit(content: bytes, max_bytes: int) -> None:
    """Reject request bodies exceeding the configured byte limit."""

    if len(content) > max_bytes:
        raise ExecutionFailure(
            ExecutionError(
                category="request_too_large",
                message="The request body exceeded the configured payload limit.",
                retryable=False,
                details={"max_bytes": max_bytes},
            )
        )
