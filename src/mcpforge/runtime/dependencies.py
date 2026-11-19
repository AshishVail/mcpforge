"""Runtime dependency composition."""

import logging
from dataclasses import dataclass
from pathlib import Path

from mcpforge.config.loader import load_config
from mcpforge.config.models import ProjectConfig
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.engine import ExecutionEngine
from mcpforge.filtering.evaluator import filter_document
from mcpforge.generation.models import ToolDefinition
from mcpforge.generation.service import generate_tools
from mcpforge.ingestion.service import ingest_path
from mcpforge.mcp.server import create_server
from mcpforge.observability.logging import configure_logging


@dataclass(frozen=True, slots=True)
class RuntimeDependencies:
    """Fully composed dependencies for a running MCP application."""

    config: ProjectConfig
    client: HTTPClient
    engine: ExecutionEngine
    tools: tuple[ToolDefinition, ...]
    server: object
    logger: logging.Logger


def build_dependencies(
    config_path: str | Path = "mcpforge.yaml",
    *,
    logger_name: str = "mcpforge",
) -> RuntimeDependencies:
    """Load configuration and compose the complete runtime graph."""

    config = load_config(config_path)
    logger = configure_logging(logger_name=logger_name)

    document = ingest_path(
        config.source.location,
        format=config.source.format,
        timeout_seconds=config.source.timeout_seconds,
    )

    if config.source.base_url is not None:
        document = document.model_copy(
            update={"base_url": str(config.source.base_url)}
        )

    filtered = filter_document(
        document,
        filters=config.filters,
        security=config.security,
    )
    tools = generate_tools(filtered)

    client = HTTPClient(
        timeout_seconds=config.http.timeout_seconds,
        verify_tls=config.http.verify_tls,
    )
    engine = ExecutionEngine(config, client, logger=logger)

    server = create_server(
        engine=engine,
        endpoints=tuple(filtered.endpoints),
        tools=tools,
        name=config.name,
    )

    return RuntimeDependencies(
        config=config,
        client=client,
        engine=engine,
        tools=tools,
        server=server,
        logger=logger,
    )
