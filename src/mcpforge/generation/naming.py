"""Deterministic MCP tool naming."""

import re

from mcpforge.domain.models import Endpoint

_STOP_WORDS = {"a", "an", "the", "by", "with", "for"}


def _words(value: str) -> list[str]:
    value = re.sub(r"\{([^}]+)\}", r" \1 ", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return [word.lower() for word in re.split(r"[^A-Za-z0-9]+", value) if word]


def _singular(value: str) -> str:
    if value.endswith("ies"):
        return value[:-3] + "y"
    if value.endswith("ses"):
        return value[:-2]
    if value.endswith("s") and not value.endswith("ss"):
        return value[:-1]
    return value


def default_tool_name(endpoint: Endpoint) -> str:
    """Create a stable snake_case name from operationId or path."""

    if endpoint.operation_id:
        words = _words(endpoint.operation_id)
        return "_".join(words)

    segments = [segment for segment in endpoint.path.split("/") if segment]
    resources = [_singular(segment) for segment in segments if not segment.startswith("{}")]
    method = endpoint.method.value.lower()

    if method == "get" and segments and segments[-1].startswith("{"):
        verb = "get"
    elif method == "post":
        verb = "create"
    elif method in {"put", "patch"}:
        verb = "update"
    elif method == "delete":
        verb = "delete"
    elif method == "get":
        verb = "list"
    else:
        verb = method

    return "_".join([verb, *resources]) or method
