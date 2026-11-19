import httpx
import pytest

from mcpforge.execution.errors import ExecutionFailure
from mcpforge.execution.response import parse_response


def test_parse_success_response() -> None:
    response = httpx.Response(
        200,
        json={"id": 1},
        request=httpx.Request("GET", "https://api.example.com"),
    )

    result = parse_response(response, max_response_bytes=1000)

    assert result == {"ok": True, "status_code": 200, "data": {"id": 1}}


def test_parse_http_error() -> None:
    response = httpx.Response(
        404,
        json={"message": "missing"},
        request=httpx.Request("GET", "https://api.example.com"),
    )

    with pytest.raises(ExecutionFailure) as raised:
        parse_response(response, max_response_bytes=1000)

    assert raised.value.error.category == "not_found"
    assert raised.value.error.status_code == 404


def test_invalid_json_is_normalized() -> None:
    response = httpx.Response(
        200,
        content=b"not-json",
        request=httpx.Request("GET", "https://api.example.com"),
    )

    with pytest.raises(ExecutionFailure, match="not valid JSON"):
        parse_response(response, max_response_bytes=1000)
