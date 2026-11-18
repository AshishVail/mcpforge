"""Framework-independent normalized API domain contracts."""

from mcpforge.domain.enums import (
    AuthType,
    HttpMethod,
    OperationSafety,
    ParameterLocation,
)
from mcpforge.domain.errors import DomainValidationError, MCPForgeError
from mcpforge.domain.models import (
    ApiDocument,
    Endpoint,
    JsonSchema,
    Parameter,
    RequestBody,
    ResponseDefinition,
)
from mcpforge.domain.parameters import ParameterCollection
from mcpforge.domain.schemas import JsonObject, JsonValue

__all__ = [
    "ApiDocument",
    "AuthType",
    "DomainValidationError",
    "Endpoint",
    "HttpMethod",
    "JsonObject",
    "JsonSchema",
    "JsonValue",
    "MCPForgeError",
    "OperationSafety",
    "Parameter",
    "ParameterCollection",
    "ParameterLocation",
    "RequestBody",
    "ResponseDefinition",
]
