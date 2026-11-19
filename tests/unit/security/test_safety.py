import pytest

from mcpforge.config.models import SecurityConfig
from mcpforge.domain.enums import HttpMethod
from mcpforge.domain.models import Endpoint
from mcpforge.security.safety import (
    enforce_operation_safety,
    is_operation_allowed,
)


def test_get_is_allowed_by_default() -> None:
    endpoint = Endpoint(path="/items", method=HttpMethod.GET)
    assert is_operation_allowed(endpoint, SecurityConfig())


def test_write_requires_opt_in() -> None:
    endpoint = Endpoint(path="/items", method=HttpMethod.POST)

    assert not is_operation_allowed(endpoint, SecurityConfig())

    with pytest.raises(PermissionError):
        enforce_operation_safety(endpoint, SecurityConfig())


def test_delete_has_independent_opt_in() -> None:
    endpoint = Endpoint(path="/items/{id}", method=HttpMethod.DELETE)

    with pytest.raises(PermissionError):
        enforce_operation_safety(
            endpoint,
            SecurityConfig(allow_write_operations=True),
        )

    enforce_operation_safety(
        endpoint,
        SecurityConfig(allow_delete_operations=True),
    )
