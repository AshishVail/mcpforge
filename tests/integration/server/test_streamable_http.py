from unittest.mock import patch

from mcpforge.mcp.server import create_sdk_server
from mcpforge.mcp.transports import Transport, run_transport


def test_streamable_http_transport_uses_http_mode() -> None:
    server = create_sdk_server("test-server")

    with patch.object(server, "run") as run:
        run_transport(
            server,
            Transport.STREAMABLE_HTTP,
            host="127.0.0.1",
            port=8080,
        )
        run.assert_called_once_with(transport="streamable-http")
