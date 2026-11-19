"""Runtime resource lifecycle management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcpforge.execution.client import HTTPClient


class RuntimeLifecycle:
    """Own the lifecycle of shared runtime resources."""

    def __init__(self, client: HTTPClient) -> None:
        self.client = client
        self._started = False

    async def start(self) -> None:
        """Start all runtime resources."""

        if not self._started:
            await self.client.start()
            self._started = True

    async def close(self) -> None:
        """Close all runtime resources."""

        if self._started:
            await self.client.close()
            self._started = False

    async def __aenter__(self) -> "RuntimeLifecycle":
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        await self.close()

    @asynccontextmanager
    async def context(self) -> AsyncIterator["RuntimeLifecycle"]:
        """Expose the lifecycle as an async context manager."""

        await self.start()
        try:
            yield self
        finally:
            await self.close()
