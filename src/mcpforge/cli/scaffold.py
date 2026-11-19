"""Project scaffolding helpers."""

from pathlib import Path

DEFAULT_CONFIG = """name: mcpforge-project
source:
  location: ./openapi.yaml
  format: openapi
auth:
  type: none
filters:
  include_deprecated: false
security:
  allow_write_operations: false
  allow_delete_operations: false
  allowed_hosts: []
  block_private_networks: true
  max_response_bytes: 5000000
http:
  timeout_seconds: 30
  verify_tls: true
  retry:
    max_attempts: 3
    backoff_seconds: 0.5
"""

DEFAULT_ENV = """# MCPForge runtime secrets
# MCPFORGE_API_TOKEN=
"""

DEFAULT_OPENAPI = """openapi: 3.0.3
info:
  title: Example API
  version: "1.0.0"
servers:
  - url: https://api.example.com
paths:
  /health:
    get:
      operationId: health_check
      summary: Check API health
      responses:
        "200":
          description: Healthy
"""

def scaffold_project(
    directory: Path,
    *,
    force: bool = False,
    with_example: bool = True,
) -> tuple[Path, ...]:
    """Create a starter MCPForge project."""

    directory.mkdir(parents=True, exist_ok=True)
    files: dict[Path, str] = {
        directory / "mcpforge.yaml": DEFAULT_CONFIG,
        directory / ".env.example": DEFAULT_ENV,
    }
    if with_example:
        files[directory / "openapi.yaml"] = DEFAULT_OPENAPI

    created: list[Path] = []
    for path, content in files.items():
        if path.exists() and not force:
            raise FileExistsError(f"file already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(path)
    return tuple(created)
