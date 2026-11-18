import pytest

from mcpforge.config.models import EnvReference
from mcpforge.config.secrets import resolve_env, validate_secret_references
from mcpforge.domain.errors import ConfigurationError


def test_resolve_required_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCPFORGE_TEST_TOKEN", "secret-value")

    result = resolve_env(EnvReference(env="MCPFORGE_TEST_TOKEN"))

    assert result == "secret-value"


def test_missing_required_environment_variable_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MCPFORGE_TEST_TOKEN", raising=False)

    with pytest.raises(ConfigurationError, match="MCPFORGE_TEST_TOKEN"):
        resolve_env(EnvReference(env="MCPFORGE_TEST_TOKEN"))


def test_empty_environment_variable_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCPFORGE_TEST_TOKEN", "")

    with pytest.raises(ConfigurationError, match="is empty"):
        resolve_env(EnvReference(env="MCPFORGE_TEST_TOKEN"))


def test_literal_secret_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="must be an environment"):
        validate_secret_references({"token": "hardcoded-secret"})
