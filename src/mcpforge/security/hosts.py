"""Allowed-host policy enforcement."""

from urllib.parse import urlparse


def normalize_host(host: str) -> str:
    """Normalize a hostname for case-insensitive comparison."""

    return host.strip().rstrip(".").lower()


def host_is_allowed(host: str, allowed_hosts: set[str]) -> bool:
    """Check a hostname against an explicit allowlist.

    Exact host matches are required. Wildcards are intentionally unsupported
    to prevent accidental exposure of unrelated subdomains.
    """

    if not allowed_hosts:
        return True
    normalized = normalize_host(host)
    return normalized in {normalize_host(item) for item in allowed_hosts}


def enforce_allowed_host(url: str, allowed_hosts: set[str]) -> None:
    """Raise ``PermissionError`` when a URL host is not allowed."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise PermissionError("only HTTP and HTTPS URLs with a hostname are allowed")
    if not host_is_allowed(parsed.hostname, allowed_hosts):
        raise PermissionError(f"host is not allowed: {parsed.hostname}")
