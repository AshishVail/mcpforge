from unittest.mock import AsyncMock

import pytest

from mcpforge.execution.client import HTTPClient
from mcpforge.runtime.lifecycle import RuntimeLifecycle


@pytest.mark.asyncio
async def test_runtime_lifecycle_starts_and_closes_client() -> None:
    client = HTTPClient()
    client.start = AsyncMock()
    client.close = AsyncMock()

    lifecycle = RuntimeLifecycle(client)

    async with lifecycle:
        client.start.assert_awaited_once()

    client.close.assert_awaited_once()
