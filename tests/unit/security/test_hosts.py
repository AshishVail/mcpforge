import pytest

from mcpforge.security.hosts import (
    enforce_allowed_host,
    host_is_allowed,
)


def test_exact_host_allowlist() -> None:
    assert host_is_allowed("api.example.com", {"api.example.com"})
    assert not host_is_allowed("evil.example.com", {"api.example.com"})


def test_allowed_host_is_enforced() -> None:
    enforce_allowed_host("https://api.example.com/users", {"api.example.com"})

    with pytest.raises(PermissionError, match="not allowed"):
        enforce_allowed_host("https://evil.example.com/users", {"api.example.com"})
