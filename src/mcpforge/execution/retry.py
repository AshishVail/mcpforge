"""Retry policy and transient failure classification."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

from mcpforge.config.models import RetryConfig
from mcpforge.execution.errors import ExecutionError, ExecutionFailure

T = TypeVar("T")


def is_retryable_status(status_code: int) -> bool:
    """Return whether an HTTP status is transient."""

    return status_code == 429 or status_code >= 500


def retry_delay(config: RetryConfig, attempt: int) -> float:
    """Calculate exponential backoff delay."""

    backoff_seconds = float(str(config.backoff_seconds))
    multiplier = float(2 ** max(0, attempt - 1))
    return backoff_seconds * multiplier


async def run_with_retries(
    operation: Callable[[], Awaitable[T]],
    config: RetryConfig,
) -> T:
    """Run an async operation with bounded retries."""

    last_error: ExecutionFailure | None = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            return await operation()
        except httpx.TimeoutException as exc:
            last_error = ExecutionFailure(
                ExecutionError(
                    "timeout",
                    "The upstream request timed out.",
                    retryable=True,
                )
            )
            if attempt == config.max_attempts:
                raise last_error from exc
        except httpx.NetworkError as exc:
            last_error = ExecutionFailure(
                ExecutionError(
                    "network_error",
                    "The upstream network request failed.",
                    retryable=True,
                )
            )
            if attempt == config.max_attempts:
                raise last_error from exc
        except ExecutionFailure as exc:
            last_error = exc
            if not exc.error.retryable or attempt == config.max_attempts:
                raise

        await asyncio.sleep(retry_delay(config, attempt))

    if last_error is not None:
        raise last_error
    raise RuntimeError("retry loop completed without a result")
