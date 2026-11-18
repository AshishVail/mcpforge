from io import BytesIO
from pathlib import Path
from urllib.request import Request

import pytest

from mcpforge.ingestion.errors import SourceLoadError
from mcpforge.ingestion.loaders import remote
from mcpforge.ingestion.source import Source


class FakeResponse(BytesIO):
    def __init__(self, body: bytes, content_type: str = "application/json") -> None:
        super().__init__(body)
        self.headers = {"Content-Type": content_type}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def test_load_remote_reads_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
        return FakeResponse(b'{"openapi": "3.0.3"}')

    monkeypatch.setattr(remote, "urlopen", fake_urlopen)

    loaded = remote.load_remote(Source("https://example.com/openapi.json"))

    assert loaded.document["openapi"] == "3.0.3"


def test_load_remote_enforces_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
        return FakeResponse(b"12345")

    monkeypatch.setattr(remote, "urlopen", fake_urlopen)

    with pytest.raises(SourceLoadError, match="exceeds"):
        remote.load_remote(Source("https://example.com/api.yaml", max_bytes=2))
