from pathlib import Path

import pytest

from mcpforge.ingestion.errors import SourceLoadError
from mcpforge.ingestion.loaders.file import load_file
from mcpforge.ingestion.source import Source


def test_load_file_reads_yaml(tmp_path: Path) -> None:
    path = tmp_path / "api.yaml"
    path.write_text("openapi: 3.0.3\ninfo: {}\npaths: {}\n", encoding="utf-8")

    loaded = load_file(Source(str(path)))

    assert loaded.document["openapi"] == "3.0.3"


def test_load_file_rejects_oversized_file(tmp_path: Path) -> None:
    path = tmp_path / "api.yaml"
    path.write_text("openapi: 3.0.3\n", encoding="utf-8")

    with pytest.raises(SourceLoadError, match="exceeds"):
        load_file(Source(str(path), max_bytes=1))


def test_load_file_rejects_non_mapping(tmp_path: Path) -> None:
    path = tmp_path / "api.yaml"
    path.write_text("- item\n", encoding="utf-8")

    with pytest.raises(SourceLoadError, match="root must be a mapping"):
        load_file(Source(str(path)))
