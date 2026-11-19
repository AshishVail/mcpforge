from typer.testing import CliRunner

from mcpforge.cli.commands.init import app

runner = CliRunner()


def test_init_scaffolds_project(tmp_path) -> None:
    result = runner.invoke(app, [str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "mcpforge.yaml").is_file()
    assert (tmp_path / ".env.example").is_file()


def test_init_rejects_existing_files_without_force(tmp_path) -> None:
    (tmp_path / "mcpforge.yaml").write_text("source:\n  location: ./api.yaml\n")

    result = runner.invoke(app, [str(tmp_path)])

    assert result.exit_code != 0
    assert "file already exists" in result.stdout
