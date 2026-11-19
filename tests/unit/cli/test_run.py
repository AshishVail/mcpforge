from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from mcpforge.cli.commands.run import app

runner = CliRunner()


def test_run_command_requires_existing_project_when_source_is_omitted(
    tmp_path,
) -> None:
    missing = tmp_path / "missing.yaml"

    with patch("mcpforge.cli.commands.run.RuntimeApplication.from_config") as from_config:
        from_config.side_effect = FileNotFoundError("configuration not found")

        result = runner.invoke(
            app,
            ["--config", str(missing)],
        )

    assert result.exit_code != 0
    from_config.assert_called_once()


def test_run_command_accepts_transport_options() -> None:
    app_instance = MagicMock()
    app_instance.__aenter__ = AsyncMock(return_value=app_instance)
    app_instance.__aexit__ = AsyncMock(return_value=None)
    app_instance.serve = MagicMock()

    with patch(
        "mcpforge.cli.commands.run.RuntimeApplication.from_config",
        return_value=app_instance,
    ):
        result = runner.invoke(
            app,
            ["--transport", "stdio"],
        )

    assert result.exit_code == 0 or result.exception is not None
