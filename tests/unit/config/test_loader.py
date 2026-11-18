from pathlib import Path

import pytest

from mcpforge.config.loader import load_config
from mcpforge.domain.errors import ConfigurationError


def test_load_yaml_configuration(temporary_config_path: Path) -> None:
    temporary_config_path.write_text(
        """
name: demo
source:
  location: https://api.example.com/openapi.yaml
auth:
  type: bearer
  token:
    env: DEMO_TOKEN
""",
        encoding="utf-8",
    )

    config = load_config(temporary_config_path)

    assert config.name == "demo"
    assert config.security.block_private_networks is True


def test_load_json_configuration(tmp_path: Path) -> None:
    path = tmp_path / "mcpforge.json"
    path.write_text(
        '{"source": {"location": "./api.yaml"}}',
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.source.location == "./api.yaml"


def test_missing_configuration_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="does not exist"):
        load_config(tmp_path / "missing.yaml")


def test_unknown_configuration_field_is_rejected(
    temporary_config_path: Path,
) -> None:
    temporary_config_path.write_text(
        """
source:
  location: ./api.yaml
unexpected: true
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="validation failed"):
        load_config(temporary_config_path)
