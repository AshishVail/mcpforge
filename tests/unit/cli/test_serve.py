from typer.testing import CliRunner

from mcpforge.cli.commands.serve import app
from mcpforge.mcp.transports import Transport

runner = CliRunner()


def test_serve_command_accepts_streamable_http_options() -> None:
    assert Transport.STREAMABLE_HTTP.value == "streamable-http"

    result = runner.invoke(
        app,
        [
            "--transport",
            "streamable-http",
            "--host",
            "127.0.0.1",
            "--port",
            "8080",
        ],
    )

    # Runtime startup without a real project is intentionally not tested here.
    assert result.exit_code != 0
