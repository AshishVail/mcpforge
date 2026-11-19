import pytest

from mcpforge.security.ssrf import (
    enforce_safe_addresses,
    is_blocked_ip,
    validate_url_network,
)


def test_private_and_loopback_addresses_are_blocked() -> None:
    assert is_blocked_ip("127.0.0.1")
    assert is_blocked_ip("10.0.0.1")
    assert is_blocked_ip("169.254.1.1")
    assert is_blocked_ip("::1")


def test_public_address_is_not_blocked() -> None:
    assert not is_blocked_ip("8.8.8.8")


def test_unsafe_address_collection_is_rejected() -> None:
    with pytest.raises(PermissionError, match="blocked"):
        enforce_safe_addresses(["8.8.8.8", "192.168.1.1"])


def test_literal_private_url_is_rejected() -> None:
    with pytest.raises(PermissionError):
        validate_url_network("http://127.0.0.1:8080")
