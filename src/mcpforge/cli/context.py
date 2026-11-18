"""Shared command-line context."""

from dataclasses import dataclass
from pathlib import Path

from mcpforge.config.models import ProjectConfig


@dataclass(slots=True)
class CLIContext:
    """Explicit state shared by command handlers."""

    config_path: Path = Path("mcpforge.yaml")
    config: ProjectConfig | None = None
