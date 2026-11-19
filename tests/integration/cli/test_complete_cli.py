from pathlib import Path

from typer.testing import CliRunner

from mcpforge.cli.app import app

runner = CliRunner()


def test_main_cli_help_lists_part_6_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.stdout
    assert "import" in result.stdout
    assert "inspect" in result.stdout
    assert "validate" in result.stdout
    assert "test" in result.stdout
    assert "serve" in result.stdout
    assert "run" in result.stdout


def test_complete_manual_workflow_validate_and_inspect(tmp_path: Path) -> None:
    specification = tmp_path / "manual.yaml"
    specification.write_text(
        """
name: Complete CLI API
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
security:
  allow_write_operations: false
  allow_delete_operations: false
""",
        encoding="utf-8",
    )

    validated = runner.invoke(
        app,
        ["validate", "--config", str(config)],
    )
    inspected = runner.invoke(
        app,
        ["inspect", "--config", str(config), "--format", "json"],
    )

    assert validated.exit_code == 0
    assert inspected.exit_code == 0
    assert "list_users" in inspected.stdout
