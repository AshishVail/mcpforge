"""Strict environment-backed secret handling."""

import os
from collections.abc import Mapping, Sequence
from typing import Any

from mcpforge.config.models import EnvReference
from mcpforge.domain.errors import ConfigurationError


def resolve_env(reference: EnvReference) -> str:
    """Resolve a secret from the environment without exposing its value."""

    value = os.getenv(reference.env)
    if value is None:
        if reference.default is not None:
            return reference.default
        if reference.required:
            raise ConfigurationError(
                f"required environment variable {reference.env!r} is not set"
            )
        return ""
    if not value:
        raise ConfigurationError(f"environment variable {reference.env!r} is empty")
    return value


def validate_secret_references(value: Any, path: str = "config") -> None:
    """Reject literal values in fields that represent secrets.

    Secret-bearing configuration must use ``EnvReference``. This recursive
    guard also catches raw dictionaries such as ``{"token": "literal"}``
    before they can be used by runtime code.
    """

    secret_names = {"token", "password", "secret", "api_key", "key", "authorization"}

    if isinstance(value, EnvReference):
        return

    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in secret_names and not isinstance(child, EnvReference):
                raise ConfigurationError(
                    f"{path}.{key} must be an environment variable reference"
                )
            validate_secret_references(child, f"{path}.{key}")
        return

    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for index, child in enumerate(value):
            validate_secret_references(child, f"{path}[{index}]")
