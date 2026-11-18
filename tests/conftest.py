"""Shared pytest fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def temporary_config_path(tmp_path: Path) -> Path:
    """Return a path suitable for a temporary project configuration."""

    return tmp_path / "mcpforge.yaml"
