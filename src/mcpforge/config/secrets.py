"""Environment-backed secret handling without configuration-model imports."""

import os
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

from mcpforge.domain.errors import ConfigurationError


@runtime_checkable
class EnvironmentReference(Protocol):
    """Structural contract for an environment-backed configuration value."""

    env: str
    required: bool
    default: str | None


def _is_environment_reference(value: Any) -> bool:
    """Return whether a value has the EnvReference runtime shape."""

    if isinstance(value, Mapping):
        keys = set(value)
        return (
            isinstance(value.get("env"), str)
            and keys <= {"env", "required", "default"}
        )

    return (
        isinstance(value, EnvironmentReference)
        and isinstance(value.env, str)
        and isinstance(value.required, bool)
        and (value.default is None or isinstance(value.default, str))
    )


def resolve_env(reference: EnvironmentReference) -> str:
    """Resolve a required or optional environment variable."""

    if not _is_environment_reference(reference):
        raise ConfigurationError(
            "secret values must be environment-variable references"
        )

    environment_name = reference.env
    value = os.getenv(environment_name)

    if value is None:
        if reference.default is not None:
            return reference.default
        if reference.required:
            raise ConfigurationError(
                f"required environment variable {environment_name!r} is not set"
            )
        return ""

    if not value:
        raise ConfigurationError(
            f"environment variable {environment_name!r} is empty"
        )

    return value


def _is_secret_key(key: object) -> bool:
    normalized = str(key).strip().lower().replace("-", "_")
    return normalized in {
        "token",
        "password",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
        "client_secret",
        "authorization",
    }


def validate_secret_references(value: Any, path: str = "config") -> None:
    """Reject literal values in secret-bearing configuration fields.

    This function intentionally depends only on structural typing and standard
    library protocols, so ``config.models`` can import it without a cycle.
    """

    if _is_environment_reference(value):
        return

    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"

            if _is_secret_key(key) and not _is_environment_reference(child):
                raise ConfigurationError(
                    f"{child_path} must be an environment variable reference"
                )

            validate_secret_references(child, child_path)
        return

    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        for index, child in enumerate(value):
            validate_secret_references(child, f"{path}[{index}]")
