from mcpforge.execution.errors import ExecutionError, ExecutionFailure
from mcpforge.mcp.errors import execution_error_result, failure_result


def test_execution_error_result_has_mcp_safe_shape() -> None:
    error = ExecutionError(
        category="not_found",
        message="Missing resource",
        status_code=404,
    )

    result = execution_error_result(error)

    assert result["ok"] is False
    assert result["error"]["category"] == "not_found"
    assert result["error"]["status_code"] == 404


def test_failure_result_converts_execution_failure() -> None:
    failure = ExecutionFailure(
        ExecutionError(
            category="timeout",
            message="Timed out",
            retryable=True,
        )
    )

    result = failure_result(failure)

    assert result["error"]["category"] == "timeout"
    assert result["error"]["retryable"] is True
