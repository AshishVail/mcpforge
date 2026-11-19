"""Normalization of complete API operations."""

from collections.abc import Mapping, Sequence
from typing import Any

from mcpforge.domain.enums import HttpMethod, OperationSafety
from mcpforge.domain.models import Endpoint, Parameter, RequestBody
from mcpforge.ingestion.errors import SpecificationError
from mcpforge.ingestion.normalization.parameters import (
    normalize_parameter,
    normalize_request_body,
    normalize_response,
)
from mcpforge.ingestion.normalization.references import ReferenceResolver


def operation_safety(method: HttpMethod) -> OperationSafety:
    """Classify an HTTP method for later safety policy evaluation."""

    if method is HttpMethod.DELETE:
        return OperationSafety.DELETE
    if method in {HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH}:
        return OperationSafety.WRITE
    return OperationSafety.READ


def _method(value: str) -> HttpMethod:
    try:
        return HttpMethod(value.upper())
    except ValueError as exc:
        raise SpecificationError(f"unsupported HTTP method: {value}") from exc


def endpoint_from_operation(
    path: str,
    method: str,
    raw: Mapping[str, Any],
    resolver: ReferenceResolver,
    path_parameters: Sequence[Mapping[str, Any]] = (),
    swagger: bool = False,
) -> Endpoint:
    """Build a normalized endpoint from one raw operation."""

    http_method = _method(method)
    parameters: list[Parameter] = []
    body: RequestBody | None = None

    merged_parameters = [*path_parameters, *raw.get("parameters", [])]
    for parameter in merged_parameters:
        resolved = resolver.resolve(parameter)
        if not isinstance(resolved, Mapping):
            raise SpecificationError("parameter reference must resolve to a mapping")
        if resolved.get("in") == "body":
            body = normalize_request_body(resolved, resolver)
        else:
            parameters.append(normalize_parameter(resolved, resolver))

    if not swagger and isinstance(raw.get("requestBody"), Mapping):
        body = normalize_request_body(raw["requestBody"], resolver)

    raw_responses = raw.get("responses", {})
    if not isinstance(raw_responses, Mapping):
        raise SpecificationError(f"responses for {method} {path} must be a mapping")

    responses = [
        normalize_response(status, response, resolver, swagger=swagger)
        for status, response in raw_responses.items()
        if isinstance(response, Mapping)
    ]

    return Endpoint(
        operation_id=raw.get("operationId"),
        path=path,
        method=http_method,
        summary=raw.get("summary"),
        description=raw.get("description"),
        tags=[str(tag) for tag in raw.get("tags", [])],
        parameters=parameters,
        request_body=body,
        responses=responses,
        deprecated=bool(raw.get("deprecated", False)),
        safety=operation_safety(http_method),
    )
