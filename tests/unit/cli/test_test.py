from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from mcpforge.cli.commands.test import app

runner = CliRunner()


def test_test_command_supports_dry_run(tmp_path: Path) -> None:
    specification = tmp_path / "manual.yaml"
    specification.write_text(
        """
name: Test API
base_url: https://api.example.com
endpoints:
  - operation_id: health
    method: GET
    path: /health
    responses:
      - status_code: 200
        description: Healthy
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

    with patch(
        "mcpforge.cli.commands.test.asyncio.run",
        return_value={"status_code": 200},
    ):
        result = runner.invoke(
            app,
            ["--config", str(config), "--dry-run"],
        )

    assert result.exit_code == 0
    assert "Dry run valid" in result.stdout
