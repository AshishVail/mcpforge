# MCPForge

Turn any REST API into an AI-ready MCP server.

MCPForge converts OpenAPI, Swagger, or manual YAML API definitions into
secure, typed Model Context Protocol tools.

## Part 1

Part 1 provides:

- Python package metadata and CLI entry point
- Framework-independent Pydantic domain models
- YAML and JSON configuration loading
- Environment-variable-backed secret references
- Configuration merging and validation
- Initial Typer and Rich CLI foundation

API ingestion, HTTP execution, MCP transport, and server runtime are added
in later parts.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src
mcpforge --version
