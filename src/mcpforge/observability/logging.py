"""Secret-redacted structured logging."""

import json
import logging
from typing import Any

from mcpforge.security.redaction import redact_secrets


class RedactedFormatter(logging.Formatter):
    """Format log records after recursive secret redaction."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return str(redact_secrets(message))


def configure_logging(
    level: int = logging.INFO,
    logger_name: str = "mcpforge",
) -> logging.Logger:
    """Configure and return the MCPForge logger."""

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            RedactedFormatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s"
            )
        )
        logger.addHandler(handler)

    logger.propagate = False
    return logger


def log_event(
    logger: logging.Logger,
    event: dict[str, Any],
    *,
    level: int = logging.INFO,
) -> None:
    """Write a structured redacted event."""

    safe_event = redact_secrets(event)
    logger.log(level, json.dumps(safe_event, default=str, sort_keys=True))
