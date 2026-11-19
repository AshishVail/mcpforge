"""Operation safety enforcement."""

from mcpforge.config.models import SecurityConfig
from mcpforge.domain.enums import HttpMethod, OperationSafety
from mcpforge.domain.models import Endpoint


def classify_method(method: HttpMethod) -> OperationSafety:
    """Classify an HTTP method by mutation risk."""

    if method is HttpMethod.DELETE:
        return OperationSafety.DELETE
    if method in {HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH}:
        return OperationSafety.WRITE
    return OperationSafety.READ


def is_operation_allowed(endpoint: Endpoint, config: SecurityConfig) -> bool:
    """Return whether an endpoint is permitted by the configured policy."""

    safety = endpoint.safety or classify_method(endpoint.method)
    if safety is OperationSafety.DELETE:
        return config.allow_delete_operations
    if safety is OperationSafety.WRITE:
        return config.allow_write_operations
    return True


def enforce_operation_safety(
    endpoint: Endpoint,
    config: SecurityConfig,
) -> None:
    """Raise ``PermissionError`` when an operation is not allowed."""

    if not is_operation_allowed(endpoint, config):
        safety = endpoint.safety or classify_method(endpoint.method)
        raise PermissionError(
            f"{safety.value} operation is disabled for {endpoint.method.value} {endpoint.path}"
        )
