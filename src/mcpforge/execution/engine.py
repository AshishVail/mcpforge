"""Async HTTP execution engine."""

import logging
from time import perf_counter
from typing import Any

from mcpforge.auth.resolver import resolve_auth
from mcpforge.config.models import ProjectConfig
from mcpforge.domain.models import Endpoint
from mcpforge.execution.client import HTTPClient
from mcpforge.execution.errors import ExecutionError, ExecutionFailure
from mcpforge.execution.request_builder import build_request
from mcpforge.execution.response import parse_response
from mcpforge.execution.retry import run_with_retries
from mcpforge.observability.events import ExecutionEvent
from mcpforge.observability.logging import log_event
from mcpforge.security.validation import validate_endpoint_request


class ExecutionEngine:
    """Build, validate, and execute endpoint requests."""

    def __init__(
        self,
        config: ProjectConfig,
        client: HTTPClient,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config = config
        self.client = client
        self.logger = logger or logging.getLogger("mcpforge.execution")

    async def execute(
        self,
        endpoint: Endpoint,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute one normalized endpoint invocation."""

        started = perf_counter()
        auth = resolve_auth(self.config)
        base_url = str(self.config.source.base_url or endpoint.path)
        request = build_request(
            endpoint,
            base_url,
            arguments,
            auth,
            max_request_bytes=self.config.security.max_response_bytes,
        )

        validate_endpoint_request(
            endpoint,
            request.url,
            self.config.security,
        )

        log_event(
            self.logger,
            ExecutionEvent.create(
                "request_started",
                operation_id=endpoint.operation_id,
                method=request.method,
                path=endpoint.path,
            ).as_dict(),
        )

        async def send() -> dict[str, Any]:
            response = await self.client.client.request(
                method=request.method,
                url=request.url,
                params=request.params,
                headers=request.headers,
                cookies=request.cookies,
                content=request.content,
                auth=request.auth,
            )
            return parse_response(
                response,
                max_response_bytes=self.config.security.max_response_bytes,
            )

        try:
            result = await run_with_retries(send, self.config.http.retry)
        except PermissionError as exc:
            error = ExecutionError(
                "host_blocked",
                "The request was blocked by the security policy.",
            )
            raise ExecutionFailure(error) from exc
        except ExecutionFailure:
            raise
        except Exception as exc:
            raise ExecutionFailure(
                ExecutionError(
                    "execution_failed",
                    "The request could not be completed.",
                    details={"type": type(exc).__name__},
                )
            ) from exc

        log_event(
            self.logger,
            ExecutionEvent.create(
                "request_completed",
                operation_id=endpoint.operation_id,
                method=request.method,
                path=endpoint.path,
                status_code=result.get("status_code"),
                duration_ms=(perf_counter() - started) * 1000,
            ).as_dict(),
        )
        return result
