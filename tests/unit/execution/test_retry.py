import pytest

from mcpforge.config.models import RetryConfig
from mcpforge.execution.errors import ExecutionError, ExecutionFailure
from mcpforge.execution.retry import retry_delay, run_with_retries


@pytest.mark.asyncio
async def test_retry_retries_retryable_execution_failure() -> None:
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ExecutionFailure(
                ExecutionError("temporary", "temporary", retryable=True)
            )
        return "ok"

    result = await run_with_retries(
        operation,
        RetryConfig(max_attempts=3, backoff_seconds=0),
    )

    assert result == "ok"
    assert attempts == 3


def test_retry_delay_is_exponential() -> None:
    config = RetryConfig(max_attempts=3, backoff_seconds=0.5)

    assert retry_delay(config, 1) == 0.5
    assert retry_delay(config, 2) == 1.0
