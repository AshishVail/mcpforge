"""Shared lifecycle-managed HTTPX client."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx


class HTTPClient:
    """Own one reusable asynchronous HTTP client."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        verify_tls: bool = True,
    ) -> None:
        self._timeout = httpx.Timeout(timeout_seconds)
        self._verify_tls = verify_tls
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        """Open the shared client."""

        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                verify=self._verify_tls,
                follow_redirects=False,
            )

    async def close(self) -> None:
        """Close the shared client."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Return the active client."""

        if self._client is None:
            raise RuntimeError("HTTPClient has not been started")
        return self._client

    @asynccontextmanager
    async def lifecycle(self) -> AsyncIterator["HTTPClient"]:
        """Start and close the client around an async context."""

        await self.start()
        try:
            yield self
        finally:
            await self.close()
