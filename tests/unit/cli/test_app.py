from typer.testing import CliRunner

from mcpforge.cli.app import app

runner = CliRunner()


def test_version_option() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "MCPForge 0.1.0" in result.stdout


def test_help_option() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Turn any REST API into an AI-ready MCP server." in result.stdout
