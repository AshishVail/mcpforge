"""MCP-facing error conversion."""

from typing import Any

from mcpforge.execution.errors import ExecutionError, ExecutionFailure


class MCPAdapterError(Exception):
    """Base error for MCP adapter failures."""


class ToolRegistrationError(MCPAdapterError):
    """Raised when a generated tool cannot be registered."""


def execution_error_result(error: ExecutionError) -> dict[str, Any]:
    """Convert an execution error into an MCP-safe structured result."""

    return error.as_dict()


def failure_result(failure: ExecutionFailure) -> dict[str, Any]:
    """Convert an execution failure into an MCP-safe structured result."""

    return execution_error_result(failure.error)
