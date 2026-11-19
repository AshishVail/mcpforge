"""Cross-cutting request security validation."""

from urllib.parse import urlparse

from mcpforge.config.models import SecurityConfig
from mcpforge.domain.models import Endpoint
from mcpforge.security.hosts import enforce_allowed_host
from mcpforge.security.safety import enforce_operation_safety
from mcpforge.security.ssrf import validate_url_network


def validate_request_target(
    url: str,
    config: SecurityConfig,
) -> None:
    """Validate host allowlists, URL syntax, and SSRF protections."""

    parsed = urlparse(url)
    if not parsed.hostname:
        raise PermissionError("request URL has no hostname")

    enforce_allowed_host(url, config.allowed_hosts)

    if config.block_private_networks:
        validate_url_network(url)


def validate_endpoint_request(
    endpoint: Endpoint,
    url: str,
    config: SecurityConfig,
) -> None:
    """Validate both operation safety and network target."""

    enforce_operation_safety(endpoint, config)
    validate_request_target(url, config)
