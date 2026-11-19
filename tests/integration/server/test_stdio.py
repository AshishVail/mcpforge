from unittest.mock import patch

from mcpforge.mcp.server import create_sdk_server
from mcpforge.mcp.transports import Transport, run_transport


def test_stdio_transport_uses_stdio_mode() -> None:
    server = create_sdk_server("test-server")

    with patch.object(server, "run") as run:
        run_transport(server, Transport.STDIO)
        run.assert_called_once_with(transport="stdio")
