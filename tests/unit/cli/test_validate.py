from pathlib import Path

from typer.testing import CliRunner

from mcpforge.cli.commands.validate import app

runner = CliRunner()


def test_validate_command_accepts_valid_project(tmp_path: Path) -> None:
    specification = tmp_path / "openapi.yaml"
    specification.write_text(
        """
openapi: 3.0.3
info:
  title: Test API
  version: "1.0.0"
paths:
  /health:
    get:
      operationId: health
      responses:
        "200":
          description: Healthy
""",
        encoding="utf-8",
    )

    config = tmp_path / "mcpforge.yaml"
    config.write_text(
        f"""
source:
  location: {specification}
  format: openapi
security:
  allow_write_operations: false
  allow_delete_operations: false
""",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["--config", str(config)])

    assert result.exit_code == 0
    assert "Configuration valid" in result.stdout
