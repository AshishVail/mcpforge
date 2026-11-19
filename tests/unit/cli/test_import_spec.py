from pathlib import Path

from typer.testing import CliRunner

from mcpforge.cli.commands.import_spec import app

runner = CliRunner()


def test_import_spec_accepts_manual_source(tmp_path: Path) -> None:
    source = tmp_path / "manual.yaml"
    source.write_text(
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

    result = runner.invoke(app, [str(source), "--format", "manual"])

    assert result.exit_code == 0
    assert "1 endpoint" in result.stdout


def test_import_spec_reports_invalid_source(tmp_path: Path) -> None:
    source = tmp_path / "missing.yaml"

    result = runner.invoke(app, [str(source)])

    assert result.exit_code != 0
