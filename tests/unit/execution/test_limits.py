import pytest

from mcpforge.execution.errors import ExecutionFailure
from mcpforge.execution.limits import (
    enforce_request_limit,
    enforce_response_limit,
)


def test_response_limit_rejects_large_payload() -> None:
    with pytest.raises(ExecutionFailure) as raised:
        enforce_response_limit(b"12345", 4)

    assert raised.value.error.category == "response_too_large"


def test_request_limit_rejects_large_payload() -> None:
    with pytest.raises(ExecutionFailure) as raised:
        enforce_request_limit(b"12345", 4)

    assert raised.value.error.category == "request_too_large"
