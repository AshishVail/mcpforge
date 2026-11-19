"""MCP transport selection and compatibility helpers."""

from enum import StrEnum
from typing import Any


class Transport(StrEnum):
    """Supported MCP transports."""

    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"


def configure_http_settings(
    server: Any,
    *,
    host: str,
    port: int,
) -> None:
    """Apply HTTP settings when the installed SDK exposes mutable settings."""

    settings = getattr(server, "settings", None)
    if settings is not None:
        if hasattr(settings, "host"):
            settings.host = host
        if hasattr(settings, "port"):
            settings.port = port


def run_transport(
    server: Any,
    transport: Transport | str,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> Any:
    """Run a FastMCP-compatible server using the selected transport."""

    selected = Transport(transport)
    configure_http_settings(server, host=host, port=port)

    run = getattr(server, "run", None)
    if not callable(run):
        raise RuntimeError("MCP server does not expose a run method")

    try:
        return run(transport=selected.value)
    except TypeError:
        if selected is Transport.STDIO:
            return run()
        return run(transport=selected.value)
