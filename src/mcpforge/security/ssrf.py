"""SSRF and unsafe-network protection."""

import ipaddress
import socket
from collections.abc import Iterable
from urllib.parse import urlparse


def is_blocked_ip(address: str) -> bool:
    """Return whether an address belongs to an unsafe or special range."""

    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return True

    return any(
        (
            ip.is_private,
            ip.is_loopback,
            ip.is_link_local,
            ip.is_multicast,
            ip.is_reserved,
            ip.is_unspecified,
        )
    )


def resolve_host_addresses(host: str, port: int) -> tuple[str, ...]:
    """Resolve all IPv4 and IPv6 addresses for a hostname."""

    results = socket.getaddrinfo(
        host,
        port,
        type=socket.SOCK_STREAM,
    )
    addresses = {str(result[4][0]) for result in results}
    return tuple(sorted(addresses))


def enforce_safe_addresses(addresses: Iterable[str]) -> None:
    """Reject any unsafe resolved address."""

    unsafe = [address for address in addresses if is_blocked_ip(address)]
    if unsafe:
        raise PermissionError(f"request resolves to blocked network address: {unsafe[0]}")


def validate_url_network(url: str) -> tuple[str, ...]:
    """Validate URL syntax and resolved network addresses."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise PermissionError("only HTTP and HTTPS URLs are allowed")

    host = parsed.hostname
    if host.lower() == "localhost":
        raise PermissionError("localhost requests are blocked")

    try:
        direct_ip = ipaddress.ip_address(host)
    except ValueError:
        direct_ip = None

    if direct_ip is not None:
        addresses: tuple[str, ...] = (str(direct_ip),)
    else:
        addresses = resolve_host_addresses(host, parsed.port or 443)

    enforce_safe_addresses(addresses)
    return addresses
