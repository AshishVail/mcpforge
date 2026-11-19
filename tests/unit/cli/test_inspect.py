from pathlib import Path

from typer.testing import CliRunner

from mcpforge.cli.commands.inspect import app

runner = CliRunner()


def test_inspect_command_lists_generated_tool(tmp_path: Path) -> None:
    specification = tmp_path / "manual.yaml"
    specification.write_text(
        """
name: Test API
base_url: https://api.example.com
endpoints:
  - operation_id: list_users
    method: GET
    path: /users
    responses:
      - status_code: 200
        description: Users
""",
        encoding="utf-8",
    )

    config = tmp_path / "mcpforge.yaml"
    config.write_text(
        f"""
source:
  location: {specification}
  format: manual
  base_url: https://api.example.com
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["--config", str(config), "--format", "json"],
    )

    assert result.exit_code == 0
    assert "list_users" in result.stdout
