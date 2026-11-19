"""Build HTTP requests from normalized endpoint arguments."""

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from mcpforge.auth.models import ResolvedAuth
from mcpforge.domain.enums import ParameterLocation
from mcpforge.domain.models import Endpoint
from mcpforge.execution.limits import enforce_request_limit


@dataclass(frozen=True, slots=True)
class BuiltRequest:
    """Transport-independent HTTP request data."""

    method: str
    url: str
    params: dict[str, Any]
    headers: dict[str, str]
    cookies: dict[str, Any]
    json_body: Any
    content: bytes | None
    auth: tuple[str, str] | None


def build_request(
    endpoint: Endpoint,
    base_url: str,
    arguments: dict[str, Any],
    auth: ResolvedAuth | None = None,
    *,
    max_request_bytes: int = 10_000_000,
) -> BuiltRequest:
    """Map tool arguments into path, query, header, cookie, and body values."""

    auth = auth or ResolvedAuth()
    path = endpoint.path
    params: dict[str, Any] = {}
    headers: dict[str, str] = {}
    cookies: dict[str, Any] = {}

    for parameter in endpoint.parameters:
        if parameter.name not in arguments:
            if parameter.required:
                raise ValueError(f"missing required parameter: {parameter.name}")
            continue

        value = arguments[parameter.name]
        if parameter.location is ParameterLocation.PATH:
            path = path.replace(
                "{" + parameter.name + "}",
                quote(str(value), safe=""),
            )
        elif parameter.location is ParameterLocation.QUERY:
            params[parameter.name] = value
        elif parameter.location is ParameterLocation.HEADER:
            headers[parameter.name] = str(value)
        elif parameter.location is ParameterLocation.COOKIE:
            cookies[parameter.name] = value

    body = arguments.get("body")
    content: bytes | None = None
    if body is not None:
        content = json.dumps(body, separators=(",", ":")).encode("utf-8")
        enforce_request_limit(content, max_request_bytes)
        headers.setdefault("Content-Type", "application/json")

    headers.update(auth.headers)
    params.update(auth.query)
    basic_auth = (
        (auth.username, auth.password)
        if auth.username is not None and auth.password is not None
        else None
    )

    return BuiltRequest(
        method=endpoint.method.value,
        url=f"{base_url.rstrip('/')}/{path.lstrip('/')}",
        params=params,
        headers=headers,
        cookies=cookies,
        json_body=body,
        content=content,
        auth=basic_auth,
    )
