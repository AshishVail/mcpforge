"""Async HTTP execution engine."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Any
from urllib.parse import urlparse

from mcpforge.auth.resolver import resolve_auth
from mcpforge.config.models import ProjectConfig
from mcpforge.domain.errors import ConfigurationError
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
    """Build, validate, and execute normalized endpoint requests."""

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

    def _base_url(self) -> str:
        """Resolve the upstream API base URL from project configuration."""

        configured = self.config.source.base_url
        if configured is not None:
            return str(configured).rstrip("/")

        source_location = self.config.source.location
        parsed = urlparse(source_location)

        if parsed.scheme in {"http", "https"} and parsed.hostname:
            origin = f"{parsed.scheme}://{parsed.netloc}"
            return origin.rstrip("/")

        raise ExecutionFailure(
            ExecutionError(
                category="configuration_error",
                message=(
                    "No API base URL is configured. Set source.base_url "
                    "before executing an endpoint."
                ),
                retryable=False,
            )
        )

    def _request_limit(self) -> int:
        """Return the configured request-body limit.

        Part 1 exposes one payload limit, so it is applied consistently to
        request and response payloads until a separate request limit exists.
        """

        return self.config.security.max_response_bytes

    async def execute(
        self,
        endpoint: Endpoint,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute one endpoint invocation and return a normalized result."""

        started = perf_counter()

        try:
            auth = resolve_auth(self.config)
            request = build_request(
                endpoint=endpoint,
                base_url=self._base_url(),
                arguments=arguments,
                auth=auth,
                max_request_bytes=self._request_limit(),
            )
        except ConfigurationError as exc:
            raise ExecutionFailure(
                ExecutionError(
                    category="authentication_configuration_error",
                    message=str(exc),
                    retryable=False,
                )
            ) from exc
        except ValueError as exc:
            raise ExecutionFailure(
                ExecutionError(
                    category="request_validation_error",
                    message=str(exc),
                    retryable=False,
                )
            ) from exc

        async def send() -> dict[str, Any]:
            try:
                # Perform the network-policy checks for every attempt so a
                # changing DNS answer cannot bypass the configured policy.
                validate_endpoint_request(
                    endpoint=endpoint,
                    url=request.url,
                    config=self.config.security,
                )

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
            except PermissionError as exc:
                raise ExecutionFailure(
                    ExecutionError(
                        category="host_blocked",
                        message="The request was blocked by the security policy.",
                        retryable=False,
                    )
                ) from exc

        log_event(
            self.logger,
            ExecutionEvent.create(
                "request_started",
                operation_id=endpoint.operation_id,
                method=request.method,
                path=endpoint.path,
            ).as_dict(),
        )

        try:
            result = await run_with_retries(send, self.config.http.retry)
        except ExecutionFailure as exc:
            log_event(
                self.logger,
                ExecutionEvent.create(
                    "request_failed",
                    operation_id=endpoint.operation_id,
                    method=request.method,
                    path=endpoint.path,
                    duration_ms=(perf_counter() - started) * 1000,
                    details={"category": exc.error.category},
                ).as_dict(),
                level=logging.WARNING,
            )
            raise
        except Exception as exc:
            error = ExecutionError(
                category="execution_failed",
                message="The upstream request could not be completed.",
                retryable=False,
                details={"type": type(exc).__name__},
            )
            log_event(
                self.logger,
                ExecutionEvent.create(
                    "request_failed",
                    operation_id=endpoint.operation_id,
                    method=request.method,
                    path=endpoint.path,
                    duration_ms=(perf_counter() - started) * 1000,
                    details={"category": error.category},
                ).as_dict(),
                level=logging.ERROR,
            )
            raise ExecutionFailure(error) from exc

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
