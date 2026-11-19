"""YAML and JSON configuration loader."""

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from mcpforge.config.models import ProjectConfig
from mcpforge.domain.errors import ConfigurationError

DEFAULT_CONFIG_FILENAME = "mcpforge.yaml"


def _read_document(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"cannot read configuration {path}: {exc}") from exc

    try:
        document: Any = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"invalid configuration syntax in {path}") from exc

    if not isinstance(document, dict):
        raise ConfigurationError(f"configuration root in {path} must be a mapping")
    return document


def load_config(path: str | Path = DEFAULT_CONFIG_FILENAME) -> ProjectConfig:
    """Load and validate a YAML or JSON project configuration."""

    config_path = Path(path)
    if not config_path.is_file():
        raise ConfigurationError(f"configuration file does not exist: {config_path}")

    try:
        return ProjectConfig.model_validate(_read_document(config_path))
    except ValidationError as exc:
        raise ConfigurationError(
            f"configuration validation failed for {config_path}: {exc}"
        ) from exc
